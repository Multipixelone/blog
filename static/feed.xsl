<?xml version="1.0" encoding="UTF-8"?>
<!--
  Human-readable rendering for the Atom and RSS feeds.

  Clicking a feed link in a browser without a reader extension shows a wall of
  raw XML, which reads as "this is broken" to most people. A browser that sees
  an <?xml-stylesheet?> processing instruction runs this transform instead and
  renders a real page: what a feed is, the URL to copy, and the recent posts.

  One stylesheet serves both formats — the two top-level templates below match
  atom:feed and rss respectively, and everything after them is shared.

  Caveats worth knowing:
    - Feed readers ignore this entirely. It is presentation for browsers only.
    - It only runs when the file is served with an XML content type from the
      same origin. GitHub Pages does both.
    - Chrome has announced its intent to remove XSLT. When that lands, those
      browsers fall back to showing raw XML — exactly the status quo before
      this file existed, so nothing regresses.

  Styling is borrowed wholesale from the site's own stylesheet; only the few
  feed-specific rules live inline below.
-->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atom="http://www.w3.org/2005/Atom"
                exclude-result-prefixes="atom">
  <xsl:output method="html" encoding="UTF-8" indent="yes"
              doctype-system="about:legacy-compat"/>

  <!-- ============================ Atom ============================ -->
  <xsl:template match="/atom:feed">
    <xsl:call-template name="page">
      <xsl:with-param name="title" select="atom:title"/>
      <xsl:with-param name="subtitle" select="atom:subtitle"/>
      <xsl:with-param name="format" select="'Atom'"/>
      <xsl:with-param name="self" select="atom:link[@rel='self']/@href"/>
      <xsl:with-param name="site" select="atom:link[@rel='alternate']/@href"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="atom-entries">
    <ul class="feed-entries">
      <xsl:for-each select="/atom:feed/atom:entry">
        <li>
          <h2>
            <a href="{atom:link[@rel='alternate']/@href}">
              <xsl:value-of select="atom:title"/>
            </a>
          </h2>
          <p class="feed-date">
            <xsl:value-of select="substring(atom:published, 1, 10)"/>
          </p>
        </li>
      </xsl:for-each>
    </ul>
  </xsl:template>

  <!-- ============================ RSS ============================= -->
  <xsl:template match="/rss">
    <xsl:call-template name="page">
      <xsl:with-param name="title" select="channel/title"/>
      <xsl:with-param name="subtitle" select="channel/description"/>
      <xsl:with-param name="format" select="'RSS'"/>
      <xsl:with-param name="self"
                      select="channel/*[local-name()='link'][@rel='self']/@href"/>
      <xsl:with-param name="site" select="channel/link"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="rss-entries">
    <ul class="feed-entries">
      <xsl:for-each select="/rss/channel/item">
        <li>
          <h2><a href="{link}"><xsl:value-of select="title"/></a></h2>
          <p class="feed-date"><xsl:value-of select="pubDate"/></p>
        </li>
      </xsl:for-each>
    </ul>
  </xsl:template>

  <!-- ========================== Shared page ======================== -->
  <xsl:template name="page">
    <xsl:param name="title"/>
    <xsl:param name="subtitle"/>
    <xsl:param name="format"/>
    <xsl:param name="self"/>
    <xsl:param name="site"/>
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <meta name="robots" content="noindex, follow"/>
        <title><xsl:value-of select="$title"/> — <xsl:value-of select="$format"/> feed</title>
        <link rel="icon" href="/favicon.ico"/>
        <link rel="stylesheet" href="/giallo-light.css" media="(prefers-color-scheme: light)"/>
        <link rel="stylesheet" href="/giallo-dark.css" media="(prefers-color-scheme: dark)"/>
        <link rel="stylesheet" href="/style.css"/>
        <style>
          .feed-banner {
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent);
            background: var(--paper-shade);
            padding: 1rem 1.25rem;
            margin-bottom: 2.5rem;
            border-radius: 4px;
          }
          .feed-banner p:first-child { margin-top: 0; }
          .feed-banner p:last-child { margin-bottom: 0; }
          .feed-url {
            display: block;
            margin-top: 0.75rem;
            padding: 0.6rem 0.8rem;
            background: var(--code-bg);
            border: 1px solid var(--code-border);
            border-radius: 4px;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            word-break: break-all;
            user-select: all;
          }
          .feed-entries { list-style: none; padding-left: 0; margin: 0; }
          .feed-entries li {
            padding-bottom: 1.25rem;
            margin-bottom: 1.25rem;
            border-bottom: 1px dashed var(--border);
          }
          .feed-entries li:last-child { border-bottom: 0; }
          .feed-entries h2 { margin: 0 0 0.2rem; font-size: 1.15rem; }
          .feed-entries h2 a { color: var(--ink); text-decoration: none; }
          .feed-entries h2 a:hover { color: var(--accent); text-decoration: underline; }
          .feed-date {
            margin: 0;
            color: var(--muted);
            font-family: var(--font-mono);
            font-size: 0.72rem;
          }
        </style>
      </head>
      <body>
        <header>
          <nav>
            <a href="/">Home</a>
            <a href="/tags/">Tags</a>
            <a href="/about/">About</a>
          </nav>
        </header>
        <main>
          <h1><xsl:value-of select="$title"/></h1>
          <xsl:if test="$subtitle">
            <p><xsl:value-of select="$subtitle"/></p>
          </xsl:if>

          <div class="feed-banner">
            <p>
              <strong>This is a web feed</strong>. Feeds let
              you follow a site in the reader of your choice</p>
            <code class="feed-url"><xsl:value-of select="$self"/></code>
            <p style="margin-top:0.75rem">
              New to this? <a href="https://aboutfeeds.com/">aboutfeeds.com</a>
              explains it properly.</p>
          </div>

          <h2>Recent posts</h2>
          <xsl:choose>
            <xsl:when test="/atom:feed">
              <xsl:call-template name="atom-entries"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:call-template name="rss-entries"/>
            </xsl:otherwise>
          </xsl:choose>
        </main>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
