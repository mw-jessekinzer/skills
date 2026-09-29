---
name: yoto-podcast-card
description: Use when putting a podcast on a Yoto card or Yoto player, when a kid wants a show that is only on Spotify, when a Make Your Own (MYO) card needs an RSS feed, or when yt-dlp refuses a podcast link with a DRM error.
---

# Yoto Podcast Card

## Overview

**The deliverable is an RSS feed URL.** Yoto's podcast cards take a feed link and handle the rest. Spotify links don't work directly: its streams are DRM-encrypted and yt-dlp hard-refuses them. But nearly every podcast on Spotify is syndicated from a public RSS feed, so the job is finding that feed and handing it over.

Downloading MP3s is a **fallback**, not the default. Only go there if the user asks for offline playback or no feed exists.

## Step 1: Ask for the source (REQUIRED)

**Do not skip this and do not guess the show.** Ask, then wait:

> What show do you want on the card? A link from Apple Podcasts, Spotify, or the podcast's own site all work, or just the show name.

Spotify links are fine as input. The user does not have to find the RSS feed themselves — that is this skill's job.

## Step 2: Resolve the feed

```bash
python3 ~/.claude/skills/yoto-podcast-card/podfeed.py resolve "<link or show name>"
```

Prints the show name, RSS URL, and how it was matched.

**Confirm the show name is the one they meant** before handing over the URL. Name searches and Spotify episode links match through fuzzy search and can land on the wrong show.

If it fails, the show is likely a Spotify or Apple exclusive with no public feed. Say so plainly — there is no workaround and it cannot go on a Yoto card.

## Step 3: Hand over the feed and the steps

Give them the RSS URL in a copyable block, then these steps. Getting the tab wrong is the single most common failure:

1. Go to [yotoplay.com/create](https://yotoplay.com/create) and log in with the same email as the app.
2. On the **Library** page, find the **Podcasts** tab. It is **not** the Playlists tab. You may need to swipe or scroll sideways to see it.
3. **Add Podcast**, paste the RSS URL, pick an icon.
4. **Get Podcast Details**, wait for the episode list, then **Save**.
5. **Link to Card**, then hold the MYO card to the player.

If they land in a dialog saying "Please enter a direct link to the audio stream" and their feed URL is rejected, they are in Playlists → Add a Radio Stream. Wrong box. Send them back to the Podcasts tab.

Worth mentioning once, without belaboring it: podcast cards stream, so they need WiFi and won't play in the car, and they carry the 25 most recent episodes.

## Fallback: downloading for offline

Use only when the user asks for offline or car playback, or when no feed exists.

```bash
python3 ~/.claude/skills/yoto-podcast-card/podfeed.py list "<link>"
python3 ~/.claude/skills/yoto-podcast-card/podfeed.py download "<link>"          # all episodes
python3 ~/.claude/skills/yoto-podcast-card/podfeed.py download "<link>" --only 1,2,5
```

Files land in `~/Downloads/<show>/`, numbered oldest-first so Yoto's filename ordering matches listening order. Reruns skip what is already there, so a failed episode just needs the same command again. The download reports total size and flags anything over Yoto's caps.

Then: [yotoplay.com/create](https://yotoplay.com/create) → **Make Your Own** → new playlist → drag the files in → tap the card to the player.

**Run downloads outside the sandbox.** Writes to `~/Downloads` are blocked by default and fail as a 200 response with 0 bytes.

Yoto MYO caps: 100 tracks per card, 100 MB and 60 minutes per track, 500 MB per card, MP3 or AAC/M4A only. Over the per-track cap, re-encode to 96 kbps mono (fine for spoken word) or split at a chapter break. Renaming or zipping does nothing; the uploader reads the audio.

## Common mistakes

| Mistake | Fix |
|---|---|
| Pasting RSS into "Add a Radio Stream" | Wrong tab. Library → Podcasts, not Playlists. |
| Jumping straight to downloading MP3s | The feed URL is the answer. Download only on request. |
| Trying yt-dlp on a Spotify URL | Refuses on DRM by design. Find the RSS feed instead. |
| Using a podcast's web page URL as the feed | Feed URLs usually contain `feed`, `rss`, or `.xml`. |
| Assuming a Spotify link cannot be resolved | It usually can. Run `resolve` before giving up. |
| Adding episodes one at a time as streams | Per-episode stream tracks still need WiFi. No benefit. |
