---
name: gtme
description: Use when JK runs /gtme with one or more resource links (YouTube video, article, podcast, LinkedIn post) for his GTM Engineering research, or types "gtme <link>", "add this to GTME", or "save this GTME source", including from his phone over Remote Control. Creates the source's note in the GTME Notes folder with frontmatter and adds its row to the Notes Index. Does not summarize the source or write notes for JK.
---

# GTME source capture

JK researches GTM Engineering by watching and reading sources and taking his own notes. This skill does the setup grunt work so he only hands over a link. It creates an empty note with source facts in the frontmatter and adds a row to the index. JK writes the notes, the Main Takeaway, and changes the Status himself.

## Paths

- Notes folder: `/Users/jk/Documents/Vaults/Main/0_Marketing GIT/GTME/Organic research/Notes/`
- Index: `/Users/jk/Documents/Vaults/Main/0_Marketing GIT/GTME/Organic research/Notes Index.md`

## Never do

- Never write anything in the note body. No summary, no headings, no scaffold.
- Never fill the Main Takeaway column.
- Never change the Status of an existing row, except the one automatic change in the Status sweep step (`#not-started` to `#in-progress` when the note has content).
- Never guess a fact. If a fact can't be found, leave that field empty (key present, no value).
- Never invent a topic tag outside the list below.

## Topic tags (fixed list)

Pick 1 to 3 per source, based on the title, description, chapters, or the opening of the content.

- `GTME/role`: what the job is and where it sits in the company
- `GTME/skills`: what a person must know how to do
- `GTME/tools`: Clay, n8n, HubSpot, and other software
- `GTME/workflows`: the real plays and automations people build
- `GTME/metrics`: how to measure whether a GTM engineer is doing well

If a source clearly needs a topic that isn't here, ask JK. Add the new tag to this list only after he says yes.

## Steps (repeat for each link)

0. **Status sweep (every time a link is sent, before anything else, once per run).** Check every existing note in the Notes folder. If a note's body (everything after the closing `---` of the frontmatter) has any content, and its index row Status is `#not-started`, change that row's Status to `#in-progress`. Leave rows already `#in-progress` or `#done` alone, and never touch notes with an empty body. Edit only the Status cell. Do this before adding the new row, so the new row stays `#not-started`. Mention each changed row in the report.

1. **Duplicate check.** Search the index for the link. For YouTube, search for the video ID too, because `youtu.be/ID` and `youtube.com/watch?v=ID` are the same video. If found, skip this link and tell JK which note already has it.

2. **Get the facts.**
   - YouTube (and other sites yt-dlp supports, including many podcast hosts):
     ```bash
     yt-dlp --skip-download --no-warnings --print '%(title)s|%(uploader)s|%(upload_date)s|%(duration_string)s' --print description "<link>"
     ```
     Run it with `allowed_domains` set to `youtube.com`, `www.youtube.com`, `youtu.be`, `m.youtube.com` (add the podcast host's domain for non-YouTube links). The description often names the speaker and has chapters, which help pick topics.
   - Articles and posts: use `firecrawl_scrape` (markdown, onlyMainContent) or WebFetch. Pull the title, author, site name, publish date, and word count.
   - LinkedIn posts often block scraping. If blocked, use the first line of the post as the title if JK pasted it, otherwise ask JK for the author and a title.

3. **Pick the Type:** `Video`, `Article`, `Podcast`, or `Post`.

4. **Pick 1 to 3 topic tags** from the fixed list.

5. **Build the filename** from the source's title. Remove characters Obsidian can't use in filenames: `* " \ / < > : | ? # ^ [ ]`. Collapse double spaces and trim. Keep everything else, including curly apostrophes. If a file with that name already exists, stop and tell JK.

6. **Write the note** with exactly this frontmatter, in this order, and an empty body:

   ```yaml
   ---
   date: 2026-10-07T08:37:00
   tags:
     - GTME
     - research
     - GTME/role
   Link: https://youtu.be/VIDEO_ID
   Bread Crumb: "[[Notes Index]]"
   Creator: Everett Berry
   Source: YouTube, Brianne Kimmel
   Published: 2025-10-14
   Length: 27 min
   ---
   ```

   Field rules:
   - `date`: the time the note is created, from `date +%Y-%m-%dT%H:%M:00`.
   - `tags`: always `GTME` and `research` first, then the topic tags.
   - `Link`: the link exactly as JK gave it.
   - `Creator`: the person speaking or writing. If it's a brand video with a named host, use `Host (Brand)`, for example `Mishti (Clay)`. If no person is named, use the brand.
   - `Source`: `Platform, Channel or Site`, for example `YouTube, Clay Originals` or `Substack, Newsletter Name`.
   - `Published`: `YYYY-MM-DD`.
   - `Length`: video or audio rounded to minutes (`27 min`, `1h 12m`); articles as reading time at 230 words per minute (`8 min read`).
   - Wrap a value in double quotes if it contains `: ` or starts with `#`, `[`, `{`, `"`, or `'`.

7. **Add the index row.** Columns: `Type | Status | Link | Notes | Topics | Main Takeaway`.
   - Status: `#not-started`.
   - Notes: `[[Note filename without .md]]`.
   - Topics: plain words, comma separated, no `#` or `GTME/` prefix (for example `role, tools`). Plain words keep the index out of tag searches.
   - Main Takeaway: empty.
   - Put the row in the first empty placeholder row of the table. If there is no empty row, add it right after the last row. Don't touch other rows.

8. **Report to JK** with one line per link: the note name, the type, the topics, and any field left empty and why. Add a line listing any notes moved to `#in-progress` by the sweep.
