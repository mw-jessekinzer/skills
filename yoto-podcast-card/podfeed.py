#!/usr/bin/env python3
"""Resolve a podcast link to its RSS feed, list episodes, and download them.

Stdlib only. Designed for getting podcasts onto Yoto cards.

Usage:
    podfeed.py resolve <url-or-show-name>
    podfeed.py list <url-or-show-name>
    podfeed.py download <url-or-show-name> [--dest DIR] [--only N,N,N]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

# Feeds are third-party XML. Prefer defusedxml when it is installed; CPython's
# ElementTree refuses external entities but can still be walked into an
# entity-expansion blowup by a hostile feed.
try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def get(url, binary=False, tries=3):
    """Fetch a URL. Apple's search API drops connections under load, so retry."""
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except Exception as exc:
            last = exc
            if attempt < tries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise last


def itunes_lookup(podcast_id):
    try:
        url = f"https://itunes.apple.com/lookup?id={podcast_id}&entity=podcast"
        results = json.loads(get(url)).get("results", [])
    except Exception:
        return None, None
    for r in results:
        if r.get("feedUrl"):
            return r["feedUrl"], r.get("collectionName", "")
    return None, None


def itunes_search(term, entity="podcast"):
    """Search Apple. Returns [] on failure so callers can try the next strategy."""
    try:
        q = urllib.parse.urlencode({"term": term, "entity": entity, "limit": 5})
        results = json.loads(get(f"https://itunes.apple.com/search?{q}")).get("results", [])
    except Exception:
        return []
    return [(r.get("feedUrl"), r.get("collectionName", "")) for r in results if r.get("feedUrl")]


def spotify_names(url):
    """Return (episode_or_show_title, show_title) for a Spotify link.

    Spotify serves a JS shell to plain HTTP clients, so the page has no og:
    tags to scrape. The public oEmbed endpoint carries the title, and the
    embed page's JSON payload carries the parent show name.
    """
    import html as htmlmod
    title = show = ""

    try:
        data = json.loads(get(f"https://open.spotify.com/oembed?url={urllib.parse.quote(url, safe='')}"))
        m = re.search(r'title="Spotify Embed:\s*([^"]*)"', data.get("html", ""))
        if m:
            title = htmlmod.unescape(m.group(1)).strip()
    except Exception:
        pass

    m = re.search(r"open\.spotify\.com/(episode|show)/([A-Za-z0-9]+)", url)
    if m:
        try:
            emb = get(f"https://open.spotify.com/embed/{m.group(1)}/{m.group(2)}")
            s = re.search(r'"subtitle":"([^"]*)"', emb)
            if s:
                show = htmlmod.unescape(s.group(1).encode().decode("unicode_escape")).strip()
        except Exception:
            pass

    return title, show


def resolve(source):
    """Return (feed_url, show_name, note). Accepts Apple/Spotify/RSS URL or a show name."""
    source = source.strip()

    # Already an RSS feed?
    if re.search(r"(feeds?\.|/rss|\.rss|/feed)", source, re.I) and source.startswith("http"):
        return source, "", "used the URL directly as an RSS feed"

    # Apple Podcasts
    m = re.search(r"podcasts\.apple\.com/.*?/id(\d+)", source)
    if m:
        feed, name = itunes_lookup(m.group(1))
        if feed:
            return feed, name, f"resolved via Apple Podcasts ID {m.group(1)}"
        return None, None, "Apple Podcasts ID found but Apple lists no public RSS feed (likely an Apple-exclusive show)"

    # Spotify -> get the name off Spotify, then find the same show on Apple
    if "open.spotify.com" in source:
        title, show = spotify_names(source)
        if not title and not show:
            return None, None, "could not read any title from Spotify for that link"

        # Episode title -> show + feed in one hop.
        if title:
            hits = itunes_search(title[:200], entity="podcastEpisode")
            if hits:
                return hits[0][0], hits[0][1], f"Spotify episode {title!r} matched Apple show {hits[0][1]!r}"

        # Fall back to matching the parent show by name.
        for term in filter(None, [show, title]):
            hits = itunes_search(term[:200], entity="podcast")
            if hits:
                return hits[0][0], hits[0][1], f"Spotify show {term!r} matched Apple show {hits[0][1]!r}"

        return None, None, (
            f"Spotify names it {(show or title)!r} but Apple Podcasts has no match - "
            "likely a Spotify exclusive, which has no public RSS feed and cannot go on a Yoto card"
        )

    # Bare show name
    hits = itunes_search(source)
    if hits:
        return hits[0][0], hits[0][1], f"name search matched {hits[0][1]!r}"
    return None, None, "no podcast matched that name"


def parse_feed(feed_url):
    root = ET.fromstring(get(feed_url))
    ch = root.find("channel")
    show = (ch.findtext("title") or "").strip()
    eps = []
    for item in ch.findall("item"):
        enc = item.find("enclosure")
        if enc is None or not enc.get("url"):
            continue
        eps.append({
            "title": (item.findtext("title") or "untitled").strip(),
            "url": enc.get("url").split("?")[0],
            "date": (item.findtext("pubDate") or "").strip(),
        })
    eps.reverse()  # oldest first, so track order reads correctly on a Yoto card
    return show, eps


def safe(name, limit=70):
    name = re.sub(r"[^A-Za-z0-9 .,'&-]", "", name).strip()
    name = re.sub(r"\s+", " ", name)
    return name[:limit].rstrip(" .")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["resolve", "list", "download"])
    p.add_argument("source", help="Apple Podcasts URL, Spotify URL, RSS URL, or show name")
    p.add_argument("--dest", default=None, help="download directory (default ~/Downloads/<show>)")
    p.add_argument("--only", default=None, help="comma-separated track numbers from `list`")
    a = p.parse_args()

    feed, name, note = resolve(a.source)
    if not feed:
        print(f"FAILED: {note}", file=sys.stderr)
        sys.exit(2)

    if a.command == "resolve":
        print(f"show: {name}")
        print(f"feed: {feed}")
        print(f"note: {note}")
        return

    show, eps = parse_feed(feed)
    if a.command == "list":
        print(f"show: {show}")
        print(f"feed: {feed}")
        print(f"episodes: {len(eps)} (oldest first)")
        for i, e in enumerate(eps, 1):
            print(f"{i:02d}  {e['title']}")
        return

    wanted = set(int(x) for x in a.only.split(",")) if a.only else set(range(1, len(eps) + 1))
    dest = a.dest or os.path.join(os.path.expanduser("~/Downloads"), safe(show))
    os.makedirs(dest, exist_ok=True)
    failures = []
    print(f"downloading {len(wanted)} of {len(eps)} episodes to {dest}", flush=True)
    for i, e in enumerate(eps, 1):
        if i not in wanted:
            continue
        path = os.path.join(dest, f"{i:02d} {safe(e['title'])}.mp3")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"skip  {os.path.basename(path)} (already there)")
            continue
        # curl, not urllib: podcast CDNs routinely send a Content-Length that
        # does not match the body, which urllib treats as a fatal IncompleteRead.
        rc = subprocess.run(
            ["curl", "-sL", "--retry", "3", "--retry-all-errors",
             "-A", UA, e["url"], "-o", path],
            capture_output=True,
        ).returncode
        size = os.path.getsize(path) if os.path.exists(path) else 0
        if rc == 0 and size > 0:
            print(f"ok    {os.path.basename(path)}  ({size/1048576:.1f} MB)", flush=True)
        else:
            print(f"FAIL  {os.path.basename(path)}  (curl exit {rc})", flush=True)
            failures.append(e["title"])
    if failures:
        print(f"\n{len(failures)} episode(s) failed; rerun the same command to retry just those:")
        for t in failures:
            print(f"  - {t}")

    check_yoto_limits(dest)
    print(f"\ndone: {dest}")


# Yoto Make Your Own card caps, per Yoto support.
MAX_TRACKS = 100
MAX_TRACK_MB = 100
MAX_CARD_MB = 500


def check_yoto_limits(dest):
    files = sorted(f for f in os.listdir(dest) if f.lower().endswith((".mp3", ".m4a", ".aac")))
    sizes = {f: os.path.getsize(os.path.join(dest, f)) / 1048576 for f in files}
    total = sum(sizes.values())
    print(f"\n{len(files)} tracks, {total:.0f} MB total")

    problems = []
    if len(files) > MAX_TRACKS:
        problems.append(f"{len(files)} tracks exceeds the {MAX_TRACKS}-track cap - split across two cards")
    if total > MAX_CARD_MB:
        problems.append(f"{total:.0f} MB exceeds the {MAX_CARD_MB} MB per-card cap - split across two cards")
    for f, mb in sizes.items():
        if mb > MAX_TRACK_MB:
            problems.append(f"{f} is {mb:.0f} MB, over the {MAX_TRACK_MB} MB per-track cap - re-encode lower or split it")

    if problems:
        print("Yoto limit problems:")
        for p in problems:
            print(f"  ! {p}")
    else:
        print("fits on one Make Your Own card")


if __name__ == "__main__":
    main()
