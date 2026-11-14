#!/usr/bin/env python3
"""Run Zola on a private snapshot with undated blog posts omitted.

The Nix environment installs this as `zola`, supplying the real binary as argv[1].
Source content is never edited. Build/check use one snapshot; serve replaces the
snapshot only while its child is stopped, including when a date is removed.
"""

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

import yaml


SITE_DIRS = ("content", "templates", "static", "sass", "themes")


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    for fence, parse in (("+++", tomllib.loads), ("---", yaml.safe_load)):
        if text.startswith(fence + "\n"):
            end = text.find("\n" + fence, len(fence))
            if end < 0:
                raise ValueError(f"{path}: unterminated front matter")
            return parse(text[len(fence) + 1:end]) or {}
    raise ValueError(f"{path}: missing front matter")


def unpublished(content):
    """Date-sorted sections contain posts; other sections contain standalone pages.

    Bundles use index.md. Section indexes (_index.md) are never posts. Follow the
    closest section, just as Zola does, rather than classifying by template name.
    A date in a filename does not override an absent publication-date field.
    """
    sections = {
        path.parent: front_matter(path)
        for path in content.rglob("_index.md")
    }
    excluded = set()
    for path in content.rglob("*.md"):
        if path.name == "_index.md":
            continue
        parent = path.parent
        while parent not in sections and parent != content:
            parent = parent.parent
        if sections.get(parent, {}).get("sort_by") != "date":
            continue
        if front_matter(path).get("date") is None:
            excluded.add(path)
    return excluded


def prepare(root, snapshot, config, output):
    content = root / "content"
    excluded = unpublished(content)
    # An unpublished bundle's assets are private too, not standalone downloads.
    bundles = {p.parent for p in excluded if p.name == "index.md"}

    omitted = excluded | bundles

    def ignore(directory, names):
        return [name for name in names if Path(directory) / name in omitted]

    for name in SITE_DIRS:
        source = root / name
        target = snapshot / name
        if target.exists():
            shutil.rmtree(target)
        if source.exists():
            shutil.copytree(source, target, ignore=ignore)
    # Preserve native default-output behavior (no explicit -o existence guard),
    # but resolve the default against the original root rather than the snapshot.
    text = config.read_text(encoding="utf-8")
    setting = "output_dir = " + json.dumps(str(output))
    if "output_dir" in tomllib.loads(text):
        text = re.sub(r"(?m)^\s*output_dir\s*=.*$", lambda _: setting, text, count=1)
    else:
        text = setting + "\n" + text
    if tomllib.loads(text)["output_dir"] != str(output):
        raise ValueError("cannot resolve output_dir in the temporary configuration")
    (snapshot / "zola.toml").write_text(text, encoding="utf-8")


def fingerprint(root, config):
    """Watch source inputs, never output, .git, or the snapshot itself."""
    paths = [config]
    for name in SITE_DIRS:
        source = root / name
        if source.exists():
            paths.extend(p for p in source.rglob("*") if p.is_file())
    result = []
    for path in sorted(paths):
        try:
            stat = path.stat()
        except FileNotFoundError:  # editor rename/delete; the next scan sees it
            continue
        result.append((str(path), stat.st_mtime_ns, stat.st_size))
    return tuple(result)


def stop(child):
    if child.poll() is None:
        # Zola's SIGINT handler also removes serve output, avoiding stale assets.
        child.send_signal(signal.SIGINT)
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()


def clean_serve_output(output, preserve_dotfiles):
    """Serve falls back to disk, so stale HTML/search/assets must not survive."""
    if output.exists():
        for path in output.iterdir():
            if preserve_dotfiles and path.name.startswith("."):
                continue
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()


def run(real, args, root, config, command, output, explicit_output):
    scratch = ("/tmp/opencode" if not os.environ.get("TMPDIR")
               and Path("/tmp/opencode").is_dir() else None)
    with tempfile.TemporaryDirectory(prefix="blog-zola-", dir=scratch) as directory:
        snapshot = Path(directory)
        child = None
        interrupted = None
        restarted = False

        def interrupt(signum, _frame):
            nonlocal interrupted
            interrupted = signum
            if child is not None and child.poll() is None:
                child.send_signal(signal.SIGINT if command == "serve" else signum)

        previous = {s: signal.signal(s, interrupt)
                    for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
        try:
            while not interrupted:
                before = fingerprint(root, config)
                prepare(root, snapshot, config, output)
                # Retry if an editor changed inputs while copying the snapshot.
                if fingerprint(root, config) != before:
                    continue
                if command == "serve":
                    # Keep the initial explicit -o guard. Without --force let
                    # native Zola reject an existing directory without touching it.
                    effective = explicit_output or output
                    if not explicit_output or restarted or "--force" in args:
                        options = tomllib.loads(config.read_text(encoding="utf-8"))
                        clean_serve_output(effective, options.get("preserve_dotfiles_in_output", False))
                invocation = [real, "--root", str(snapshot), *args]
                if command == "serve" and restarted and explicit_output and "--force" not in args:
                    invocation.append("--force")
                if interrupted:
                    break
                child = subprocess.Popen(invocation)
                if interrupted and child.poll() is None:
                    child.send_signal(signal.SIGINT if command == "serve" else interrupted)
                if command != "serve":
                    return child.wait()
                while not interrupted and child.poll() is None:
                    time.sleep(0.2)
                    try:
                        changed = fingerprint(root, config) != before
                    except FileNotFoundError:
                        changed = True
                    if changed:
                        stop(child)
                        restarted = True
                        print("zola: source changed; refreshing publication snapshot", flush=True)
                        break
                else:
                    return child.wait()
        finally:
            if child is not None:
                stop(child)
            for signum, handler in previous.items():
                signal.signal(signum, handler)
        return 128 + interrupted


def main():
    real, *args = sys.argv[1:]
    # Non-site commands and help must retain native behavior, with no preparation.
    if any(a in ("--help", "-h", "--version", "-V") for a in args):
        os.execv(real, [real, *args])
    root_arg = None
    config_arg = None
    i = 0
    while i < len(args) and args[i].startswith("-"):
        arg = args[i]
        if arg in ("--root", "-r", "--config", "-c"):
            i += 1
            if i == len(args):
                os.execv(real, [real, *args])  # native usage error
            value = args[i]
        elif arg.startswith(("--root=", "--config=")):
            arg, value = arg.split("=", 1)
        elif arg.startswith(("-r", "-c")):
            arg, value = arg[:2], arg[2:].removeprefix("=")
        else:
            os.execv(real, [real, *args])
        if arg in ("--root", "-r"):
            root_arg = value
        else:
            config_arg = value
        i += 1
    if i == len(args) or args[i] not in ("build", "serve", "check"):
        os.execv(real, [real, *args])
    command = args[i]
    rest = args[i:]
    if command == "serve" and any(a.split("=", 1)[0] == "--extra-watch-path" for a in rest):
        raise ValueError("--extra-watch-path is not supported by the publication snapshot; "
                         "content, templates, static, sass, themes and config are watched")
    start = Path(root_arg).resolve() if root_arg else Path.cwd()
    config_names = [config_arg] if config_arg else ["zola.toml", "config.toml"]
    found = next(((p, name) for name in config_names for p in (start, *start.parents)
                  if (p / name).is_file()), None)
    root, config_name = found if found else (None, None)
    if root is None:
        os.execv(real, [real, *args])
    config = (root / config_name).resolve()
    explicit_output = None
    for index, arg in enumerate(rest[1:], 1):
        if arg in ("-o", "--output-dir") and index + 1 < len(rest):
            explicit_output = Path(rest[index + 1]).absolute()
        elif arg.startswith("--output-dir="):
            explicit_output = Path(arg.split("=", 1)[1]).absolute()
        elif arg.startswith("-o") and len(arg) > 2:
            explicit_output = Path(arg[2:].removeprefix("=")).absolute()
    output = root / tomllib.loads(config.read_text(encoding="utf-8")).get("output_dir", "public")
    # Explicit output options are passed untouched: Zola resolves them against cwd
    # and enforces its existing-directory guard on the initial invocation.
    return run(real, rest, root, config, command, output, explicit_output)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"zola: publication preparation failed: {error}", file=sys.stderr)
        sys.exit(1)
