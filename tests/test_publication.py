"""Publication boundary: posts without a `date` must not reach the built site.

The managed `zola` on PATH (flake.nix wraps scripts/zola.py) hides undated posts
in date-sorted sections from `build`, `check` and `serve`. These tests drive that
executable end to end against a temporary copy of the real site plus fixtures:
the complete `scripts/build.sh` pipeline (pages, OG cards, Pagefind), native
Zola options (drafts, output-dir guards, --root), and live `serve` refreshes.

Run inside the dev shell so the managed launcher is the `zola` found on PATH:

    nix develop --command python3 -m unittest discover -s tests -v

No network access is needed; serve binds to an ephemeral loopback port.
"""

import gzip
import hashlib
import importlib.util
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import tempfile
import time
import tomllib
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from unittest import mock
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SITE_INPUTS = ("zola.toml", "content", "templates", "static", "scripts")
ATOM = "{http://www.w3.org/2005/Atom}"
TEXT_SUFFIXES = {".html", ".xml", ".txt", ".json", ".xsl"}

# Fixtures. Each undated post carries a slug, an alias, a tag no published post
# uses, and a body marker, so every way it could leak has something to find.
UNDATED = {
    "zq-undated-yaml": ("zqundatedyamlmarker", "zqyamlonlytag"),
    "zq-undated-toml": ("zqundatedtomlmarker", "zqtomlonlytag"),
    "zq-null-date": ("zqnulldatemarker", "zqnulldateonlytag"),
    # Zola would otherwise take the date from the filename.
    "zq-filename-dated": ("zqfilenamedatedmarker", "zqfilenameonlytag"),
    "zq-bundle": ("zqundatedbundlemarker", "zqbundleonlytag"),
}
PRIVATE_ASSET_MARKER = "zqprivateassetmarker"
DATED_MARKER = "zqdatedfixturemarker"
FUTURE_MARKER = "zqfarfuturemarker"
DRAFT_MARKER = "zqdateddraftmarker"
STANDALONE_MARKER = "zqstandalonesectionmarker"
STANDALONE_PAGE_MARKER = "zqstandalonepagemarker"

FIXTURES = {
    "content/zq-undated-yaml.md": """---
title: "Undated YAML fixture"
description: "Undated YAML fixture description"
slug: zq-undated-yaml
template: page.html
aliases: ["/old/zq-undated-yaml-alias/"]
taxonomies:
  tags:
    - zqyamlonlytag
    - technology
---
Body zqundatedyamlmarker.
""",
    "content/zq-undated-toml.md": """+++
title = "Undated TOML fixture"
description = "Undated TOML fixture description"
slug = "zq-undated-toml"
template = "page.html"
aliases = ["/old/zq-undated-toml-alias/"]
[taxonomies]
tags = ["zqtomlonlytag", "nix"]
+++
Body zqundatedtomlmarker.
""",
    "content/zq-null-date.md": """---
title: "Null date fixture"
description: "Null date fixture description"
slug: zq-null-date
date:
template: page.html
aliases: ["/old/zq-null-date-alias/"]
taxonomies:
  tags: [zqnulldateonlytag]
---
Body zqnulldatemarker.
""",
    "content/2024-05-06-zq-filename-dated.md": """---
title: "Filename dated fixture"
description: "Filename dated fixture description"
slug: zq-filename-dated
template: page.html
aliases: ["/old/zq-filename-dated-alias/"]
taxonomies:
  tags: [zqfilenameonlytag]
---
Body zqfilenamedatedmarker.
""",
    "content/zq-bundle/index.md": """---
title: "Undated bundle fixture"
description: "Undated bundle fixture description"
template: page.html
aliases: ["/old/zq-bundle-alias/"]
taxonomies:
  tags: [zqbundleonlytag]
---
Body zqundatedbundlemarker. [asset](private-asset.txt)
""",
    "content/zq-bundle/private-asset.txt": "zqprivateassetmarker\n",
    "content/zq-dated.md": """---
title: "Dated fixture"
description: "Dated fixture description"
slug: zq-dated
date: 2020-01-02
template: page.html
taxonomies:
  tags: [zqdatedtag]
---
Body zqdatedfixturemarker.
""",
    "content/zq-far-future.md": """+++
title = "Far future fixture"
description = "Far future fixture description"
slug = "zq-far-future"
date = 2999-12-31
template = "page.html"
[taxonomies]
tags = ["zqfuturetag"]
+++
Body zqfarfuturemarker.
""",
    "content/zq-dated-draft.md": """---
title: "Dated draft fixture"
description: "Dated draft fixture description"
slug: zq-dated-draft
date: 2021-03-04
draft: true
template: page.html
taxonomies:
  tags: [zqdrafttag]
---
Body zqdateddraftmarker.
""",
    # A section that is not date-sorted holds standalone pages, dated or not.
    "content/zq-standalone/_index.md": """+++
title = "Standalone fixture"
template = "zq-fixture-section.html"
+++
Body zqstandalonesectionmarker.
""",
    "content/zq-standalone/plain.md": """+++
title = "Standalone page fixture"
template = "zq-fixture-page.html"
+++
Body zqstandalonepagemarker.
""",
    # Test-only templates (the blog's page.html assumes a dated post). They
    # extend the real base.html, so they inherit its default og:image and stay
    # visible to gen_og_cards' card verification; data-pagefind-body opts them
    # into search like the real templates do.
    "templates/zq-fixture-section.html": (
        '{% extends "base.html" %}{% block content %}<article data-pagefind-body>'
        "<h1>{{ section.title }}</h1>{{ section.content | safe }}</article>"
        "{% endblock %}\n"),
    "templates/zq-fixture-page.html": (
        '{% extends "base.html" %}{% block content %}<article data-pagefind-body>'
        "<h1>{{ page.title }}</h1>{{ page.content | safe }}</article>"
        "{% endblock %}\n"),
}

UNDATED_SERVE = """---
title: "Serve fixture"
description: "Serve fixture description"
slug: zq-serve
{date}template: page.html
---
Body zqservemarker.
"""


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    for fence, parse in (("+++", tomllib.loads), ("---", yaml.safe_load)):
        if text.startswith(fence + "\n"):
            end = text.find("\n" + fence, len(fence))
            return parse(text[len(fence) + 1:end]) or {}
    raise ValueError(f"{path}: no front matter")


def repo_posts():
    """(slug, tags, dated) for the real site's blog posts in content/*.md."""
    posts = []
    for path in sorted((REPO / "content").glob("*.md")):
        if path.name == "_index.md":
            continue
        meta = front_matter(path)
        tags = (meta.get("taxonomies") or {}).get("tags") or []
        posts.append((meta.get("slug") or path.stem, tags, meta.get("date") is not None))
    return posts


def make_site(parent):
    site = Path(parent) / "site"
    site.mkdir()
    for name in SITE_INPUTS:
        source = REPO / name
        if source.is_dir():
            shutil.copytree(source, site / name)
        else:
            shutil.copy2(source, site / name)
    for rel, text in FIXTURES.items():
        target = site / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return site


def tree_digest(root):
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class LauncherCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("zola") is None:
            raise RuntimeError("zola is not on PATH; run inside `nix develop`")
        cls._tmp = tempfile.TemporaryDirectory(prefix="publication-test-")
        cls.tmp = Path(cls._tmp.name)
        cls.site = make_site(cls.tmp)
        # Launcher snapshots go here so the tests can see they are cleaned up.
        cls.launcher_tmp = cls.tmp / "launcher-tmp"
        cls.launcher_tmp.mkdir()
        cls.env = {**os.environ, "TMPDIR": str(cls.launcher_tmp)}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def run_cmd(self, args, cwd=None, check=True, timeout=600):
        result = subprocess.run(
            args, cwd=cwd or self.site, env=self.env, timeout=timeout,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if check and result.returncode != 0:
            self.fail(f"{args} exited {result.returncode}:\n{result.stdout}")
        return result

    def assertSnapshotsCleaned(self):
        # Only the launcher's own snapshots: OG/Pagefind tooling shares TMPDIR.
        left = [p.name for p in self.launcher_tmp.iterdir()
                if p.name.startswith("blog-zola-")]
        self.assertEqual(left, [], "launcher left a temporary snapshot behind")


class PreparationSignalTest(unittest.TestCase):
    def test_signal_during_preparation_does_not_start_a_child(self):
        spec = importlib.util.spec_from_file_location("publication_launcher", REPO / "scripts/zola.py")
        launcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher)
        handlers = {}

        def install(signum, handler):
            previous = handlers.get(signum, signal.SIG_DFL)
            handlers[signum] = handler
            return previous

        def prepare(*_args):
            handlers[signal.SIGHUP](signal.SIGHUP, None)

        with mock.patch.object(launcher.signal, "signal", side_effect=install), \
                mock.patch.object(launcher, "fingerprint", return_value=()), \
                mock.patch.object(launcher, "prepare", side_effect=prepare), \
                mock.patch.object(launcher, "clean_serve_output"), \
                mock.patch.object(launcher.tomllib, "loads", return_value={}), \
                mock.patch.object(Path, "read_text", return_value=""), \
                mock.patch.object(launcher.subprocess, "Popen") as popen:
            status = launcher.run("zola", ["serve"], REPO, REPO / "zola.toml",
                                  "serve", REPO / "public", None)
        self.assertEqual(status, 128 + signal.SIGHUP)
        popen.assert_not_called()


class CompleteBuildTest(LauncherCase):
    """One full scripts/build.sh run, inspected from every published angle."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_digest = tree_digest(cls.site / "content")
        cls.out = cls.tmp / "out"
        result = subprocess.run(
            ["bash", "scripts/build.sh", str(cls.out)], cwd=cls.site, env=cls.env,
            timeout=900, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if result.returncode != 0:
            raise AssertionError(f"build.sh failed:\n{result.stdout}")
        cls.texts = {
            p: p.read_text(encoding="utf-8", errors="replace")
            for p in cls.out.rglob("*")
            if p.is_file() and p.suffix in TEXT_SUFFIXES
        }
        cls.fragments = []
        for frag in (cls.out / "pagefind" / "fragment").glob("*.pf_fragment"):
            raw = gzip.decompress(frag.read_bytes()).decode("utf-8")
            cls.fragments.append(json.loads(raw[raw.index("{"):]))
        cls.pagefind_blobs = [
            gzip.decompress(p.read_bytes())
            for p in (cls.out / "pagefind").rglob("*")
            if p.suffix in (".pf_fragment", ".pf_index", ".pf_meta", ".pf_filter")
        ]
        repo = repo_posts()
        cls.repo_undated = [slug for slug, _, dated in repo if not dated]
        cls.repo_dated = [slug for slug, _, dated in repo if dated]
        published_tags = {t for _, tags, dated in repo if dated for t in tags}
        cls.repo_hidden_tags = sorted(
            {t for _, tags, dated in repo if not dated for t in tags} - published_tags)

    def hidden_slugs(self):
        return [*UNDATED, *self.repo_undated]

    def test_undated_routes_aliases_and_bundle_assets_absent(self):
        for slug in self.hidden_slugs():
            self.assertFalse((self.out / slug).exists(), f"route /{slug}/ was built")
            self.assertFalse((self.out / "old" / f"{slug}-alias").exists(),
                             f"alias for {slug} was built")
        self.assertFalse(list(self.out.rglob("private-asset.txt")),
                         "an undated bundle's asset was published")

    def test_tags_used_only_by_undated_posts_absent(self):
        tags = [tag for _, tag in UNDATED.values()] + self.repo_hidden_tags
        for tag in tags:
            self.assertFalse((self.out / "tags" / tag).exists(), f"/tags/{tag}/ built")
            self.assertFalse((self.out / "og" / "tags" / f"{tag}.png").exists())
        for tag in ("zqdatedtag", "zqfuturetag"):
            self.assertTrue((self.out / "tags" / tag / "index.html").is_file())

    def test_social_cards_only_for_published_posts(self):
        for slug in self.hidden_slugs():
            self.assertFalse((self.out / "og" / f"{slug}.png").exists(),
                             f"social card for undated {slug}")
        for slug in ("zq-dated", "zq-far-future", *self.repo_dated):
            self.assertTrue((self.out / "og" / f"{slug}.png").is_file(), slug)

    def test_no_text_output_mentions_undated_posts(self):
        """Listings, archive, related posts, feeds, sitemap, tag pages, etc."""
        needles = [PRIVATE_ASSET_MARKER, "zq-dated-draft", DRAFT_MARKER]
        for slug, (marker, tag) in UNDATED.items():
            needles += [f"/{slug}", marker, tag]
        needles += [f"/{slug}/" for slug in self.repo_undated]
        needles += [f"/tags/{tag}/" for tag in self.repo_hidden_tags]
        for path, text in self.texts.items():
            for needle in needles:
                self.assertNotIn(needle, text,
                                 f"{path.relative_to(self.out)} mentions {needle}")

    def test_search_index_excludes_undated_posts(self):
        urls = [f["url"] for f in self.fragments]
        content = " ".join(f["content"] for f in self.fragments)
        # Positive controls: the index was read correctly and covers posts.
        self.assertIn("/zq-dated/", urls)
        self.assertIn(DATED_MARKER, content)
        self.assertIn(STANDALONE_MARKER, content)
        self.assertIn(STANDALONE_PAGE_MARKER, content)
        for slug in self.hidden_slugs():
            self.assertNotIn(f"/{slug}/", urls)
        for marker, _ in UNDATED.values():
            needle = marker.encode()
            for blob in self.pagefind_blobs:
                self.assertNotIn(needle, blob)

    def test_dated_posts_keep_dates_order_and_feeds(self):
        for slug in ("zq-dated", "zq-far-future", *self.repo_dated):
            self.assertTrue((self.out / slug / "index.html").is_file(), slug)
        page = self.texts[self.out / "zq-dated" / "index.html"]
        self.assertRegex(page, r'datetime="?2020-01-02T')
        future = self.texts[self.out / "zq-far-future" / "index.html"]
        self.assertRegex(future, r'datetime="?2999-12-31T')

        feed = ET.fromstring(self.texts[self.out / "atom.xml"])
        entries = [(e.findtext(f"{ATOM}id"), e.findtext(f"{ATOM}published"))
                   for e in feed.iter(f"{ATOM}entry")]
        ids = [i for i, _ in entries]
        published = [p for _, p in entries]
        self.assertEqual(published, sorted(published, reverse=True))
        self.assertTrue(ids[0].endswith("/zq-far-future/"), ids)
        dated = next(p for i, p in entries if i.endswith("/zq-dated/"))
        self.assertTrue(dated.startswith("2020-01-02"), dated)
        for slug in self.repo_dated:
            self.assertTrue(any(i.endswith(f"/{slug}/") for i in ids), slug)
        rss = self.texts[self.out / "rss.xml"]
        self.assertIn("/zq-dated/", rss)

        home = self.texts[self.out / "index.html"]
        positions = [home.find(f"/{s}/") for s in ("zq-far-future", "zq-dated")]
        self.assertTrue(all(p >= 0 for p in positions), positions)
        self.assertLess(positions[0], positions[1])

    def test_dated_draft_excluded_by_default(self):
        self.assertFalse((self.out / "zq-dated-draft").exists())

    def test_standalone_sections_and_pages_preserved(self):
        section = self.texts[self.out / "zq-standalone" / "index.html"]
        self.assertIn(STANDALONE_MARKER, section)
        plain = self.texts[self.out / "zq-standalone" / "plain" / "index.html"]
        self.assertIn(STANDALONE_PAGE_MARKER, plain)
        for name in ("about", "archive", "pgp"):
            self.assertTrue((self.out / name / "index.html").is_file(), name)

    def test_source_untouched_and_snapshot_removed(self):
        self.assertEqual(tree_digest(self.site / "content"), self.source_digest)
        self.assertSnapshotsCleaned()


class NativeOptionsTest(LauncherCase):
    """Native Zola behaviour that the launcher must keep."""

    def test_drafts_flag_includes_dated_drafts_not_undated_posts(self):
        out = self.tmp / "drafts-out"
        self.run_cmd(["zola", "build", "--drafts", "--output-dir", str(out)])
        self.assertIn(DRAFT_MARKER,
                      (out / "zq-dated-draft" / "index.html").read_text(encoding="utf-8"))
        for slug in UNDATED:
            self.assertFalse((out / slug).exists(), slug)
        self.assertSnapshotsCleaned()

    def test_check_skips_undated_posts(self):
        self.run_cmd(["zola", "check", "--skip-external-links"])
        self.assertFalse((self.site / "public").exists(), "check wrote output")
        self.assertSnapshotsCleaned()

    def test_default_output_dir_rebuilds(self):
        for _ in range(2):
            self.run_cmd(["zola", "build"])
            self.assertTrue((self.site / "public" / "zq-dated" / "index.html").is_file())
            self.assertFalse((self.site / "public" / "zq-undated-yaml").exists())
        shutil.rmtree(self.site / "public")
        self.assertSnapshotsCleaned()

    def test_existing_explicit_output_dir_needs_force(self):
        out = self.tmp / "existing-out"
        out.mkdir()
        (out / "keep.txt").write_text("keep", encoding="utf-8")
        refused = self.run_cmd(["zola", "build", "--output-dir", str(out)], check=False)
        self.assertNotEqual(refused.returncode, 0, refused.stdout)
        self.assertTrue((out / "keep.txt").exists())
        self.run_cmd(["zola", "build", "--force", "--output-dir", str(out)])
        self.assertTrue((out / "zq-dated" / "index.html").is_file())
        self.assertFalse((out / "zq-undated-yaml").exists())

    def test_custom_config_and_ancestor_discovery(self):
        config = self.site / "alternate.toml"
        config.write_text((self.site / "zola.toml").read_text(encoding="utf-8")
                          + '\n', encoding="utf-8")
        work = self.site / "scripts"
        self.run_cmd(["zola", "-c=alternate.toml", "check", "--skip-external-links"], cwd=work)
        self.assertSnapshotsCleaned()

    def test_relative_output_dir_with_root_is_cwd_relative(self):
        work = self.tmp / "work"
        work.mkdir()
        self.run_cmd(["zola", "--root", str(self.site), "build", "-o", "rel-out"], cwd=work)
        self.run_cmd(["zola", "--root", str(self.site), "build", "-orel-joined"], cwd=work)
        for name in ("rel-out", "rel-joined"):
            self.assertTrue((work / name / "zq-dated" / "index.html").is_file(), name)
            self.assertFalse((work / name / "zq-undated-yaml").exists(), name)
            self.assertFalse((self.site / name).exists(), f"{name} landed under --root")
        self.assertSnapshotsCleaned()


class ServeTest(LauncherCase):
    """Adding or removing a date while serving publishes or hides the post."""

    def get_status(self, url):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.status, response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as error:
            return error.code, ""
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
            return None, ""

    def wait_for(self, url, status, timeout, log):
        deadline = time.monotonic() + timeout
        last = None
        while time.monotonic() < deadline:
            last = self.get_status(url)
            if last[0] == status:
                return last[1]
            time.sleep(0.3)
        self.fail(f"{url}: wanted {status}, last {last[0]}\n{log.read_text(errors='replace')}")

    def test_serve_follows_date_changes(self):
        post = self.site / "content" / "zq-serve.md"
        post.write_text(UNDATED_SERVE.format(date=""), encoding="utf-8")
        # Simulate an older production build, including an old search index.
        stale = self.site / "public"
        (stale / "zq-serve").mkdir(parents=True)
        (stale / "zq-serve" / "index.html").write_text("stale private post")
        (stale / "pagefind").mkdir()
        (stale / "pagefind" / "stale.txt").write_text("stale private search")
        port = free_port()
        base = f"http://127.0.0.1:{port}"
        log = self.tmp / "serve.log"
        with log.open("w") as handle:
            child = subprocess.Popen(
                ["zola", "serve", "--interface", "127.0.0.1", "--port", str(port),
                 "--debounce", "100"],
                cwd=self.site, env=self.env, stdout=handle, stderr=subprocess.STDOUT)
        try:
            self.wait_for(f"{base}/zq-dated/", 200, 120, log)
            self.wait_for(f"{base}/zq-serve/", 404, 10, log)
            self.wait_for(f"{base}/zq-undated-yaml/", 404, 10, log)
            self.wait_for(f"{base}/pagefind/stale.txt", 404, 10, log)

            post.write_text(UNDATED_SERVE.format(date="date: 2022-02-02\n"), encoding="utf-8")
            body = self.wait_for(f"{base}/zq-serve/", 200, 60, log)
            self.assertIn("zqservemarker", body)

            post.write_text(UNDATED_SERVE.format(date=""), encoding="utf-8")
            self.wait_for(f"{base}/zq-serve/", 404, 60, log)
            self.wait_for(f"{base}/zq-dated/", 200, 60, log)
        finally:
            if child.poll() is None:
                child.send_signal(signal.SIGHUP)
                try:
                    child.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
                    self.fail(f"serve ignored SIGHUP\n{log.read_text(errors='replace')}")
            post.unlink(missing_ok=True)
        self.assertFalse((self.site / "public").exists(), "serve output left behind")
        self.assertSnapshotsCleaned()


if __name__ == "__main__":
    unittest.main()
