---
name: casual-tone
description: >-
  Rewrites overly formal, stiff, or corporate-sounding writing into a casual,
  human, "typed-on-your-phone" tone. Built for LinkedIn and social posts but
  works on any prose (emails, captions, announcements, bios). Use this whenever
  the user says a draft feels "too formal," "too buttoned up," "too stiff," "too
  corporate," or "too LinkedIn," or asks to "casualize this," "loosen this up,"
  "make it sound human," "make it sound like a real person," "dial down the
  formality," or "less press-release-y." Also apply proactively when reviewing a
  social or marketing post draft that reads stiff or buttoned-up, even if the
  user doesn't name the tone. Invoke manually with /casual-tone.
---

# Casual Tone

A tone card for taking writing that sounds buttoned-up, corporate, or
press-release-y and making it sound like a real person wrote it. The job is to
lower the formality and add humanity without losing the point or the facts.

This is **not** a topic skill. It carries no subject matter of its own. It is a
register: how the words sound, not what they say. Apply it to anything.

## Why this works

Formal writing fails on social and in most personal-voice contexts because it
sounds like an institution talking, not a person. Readers have spent their
whole lives learning to tune out institutional voice (ads, memos, press
releases), so the moment a post reads like one, attention drops. A casual,
specific, slightly self-aware voice does the opposite: it sounds like a friend,
so people actually read it and believe it.

The goal is earned casualness, not lazy casualness. You are tightening and
humanizing, not dumbing down.

## The tone moves

Apply the ones that fit. Not every move belongs in every piece.

- **Sound like a person on their phone, not a brand.** First person, direct,
  unguarded. If a sentence could appear in a corporate newsletter, rewrite it.
- **Short and burst-y.** Fragments are fine. Line breaks do real work. White
  space lets a short post breathe. Resist long, subordinate-clause sentences.
- **Confidence without performance.** Understated beats grand. "we shipped the
  thing" lands harder than "we are proud to announce the launch of."
- **Self-aware, a little self-deprecating.** Undercut your own importance. A
  small honest admission ("only got lost twice") buys more trust than a
  highlight reel.
- **Concrete small details over abstractions.** A specific real thing (the
  coffee, the carry-on, the 6am call) beats a category ("an incredible
  experience"). Specificity is what makes it sound true.
- **Show the feeling, don't declare it.** "I didn't want to leave" beats "it was
  a transformative and rewarding experience." Let the reader feel it instead of
  being told.
- **Kill the LinkedIn tells.** No "thrilled," "humbled," "honored to,"
  "excited to share," "game-changer," "synergy," "leverage," no mission-speak,
  no buzzword stacking, no throat-clearing intros ("I am pleased to...").
- **Punctuation stays human.** No em dashes ever (use commas, periods,
  parentheses, or a trailing "..."). This is a hard rule for this user.
- **Emoji sparingly.** Zero to two, only where natural. More than that reads
  try-hard.

## The two dials

The moves above are the shared DNA. Tune these two dials to the person and the
moment. When you don't know the author's style, default to mid-low dryness,
freeform structure, and lean understated.

**Dryness** — deadpan and minimal at one end, warm and expressive at the other.
- *Low (dry/minimal):* fewer words, deadpan humor, almost no setup. Fits
  understated people. ("helped launch the thing. anyway, photos.")
- *High (warm/expressive):* more feeling words, more energy, an exclamation
  point or an emoji, a little vulnerability. Fits expressive people.

**Structure** — freeform at one end, light list at the other.
- *Freeform:* flowing short lines, no scaffolding.
- *Light structure:* a playful mini-frame like "a few things I didn't expect:"
  followed by 2-4 punchy lines. Use it when the content has natural parts or the
  author likes a little order. Keep it loose and fun, never report-like.

If you know how the author actually writes (a sample, their role, prior posts),
bias the dials toward that. A casual voice that sounds like *them* beats a
generic casual voice.

## How to apply

1. **Read the draft and find the formality tells:** cliches, hedges, long
   windups, abstractions, passive voice, and announcement-y intros.
2. **Find the one real thing it's actually saying or feeling.** That is the
   post. Cut the scaffolding wrapped around it.
3. **Rewrite short and first person,** applying the moves above. Keep the
   author's original length intent: a one-liner stays a one-liner, don't pad it
   back up.
4. **Set the two dials** to the person and the moment.
5. **Read it aloud.** If it still sounds like a press release, or like a bot
   trying to sound cool, redo it. Both failures are equally bad.

When the user is iterating ("more casual," "too much," "warmer"), treat their
note as a dial adjustment and re-tune, don't rebuild from scratch.

## Guardrails (where this goes wrong)

- **Casual is not vague.** Keep the author's actual point and any real facts.
  Don't delete substance to sound relaxed. A short post still has to say
  something.
- **Don't fabricate specifics.** The concrete-detail move only works with real
  details the author gives you. If a detail would land but you don't have it,
  leave a `[bracket]` placeholder or ask. Inventing facts to sound authentic is
  the worst failure mode.
- **Don't pile on slang, emoji, or internet-speak.** One or two natural touches.
  Forced casual reads worse than honest formal.
- **Credibility still matters in serious contexts.** Lowering formality
  shouldn't make someone sound unserious about something serious. Read the room.
- **Match the person, not a house "casual voice."** When in doubt, understated.

## Relationship to /humanizer

This skill changes *register* (formal to casual, and adds personality).
`/humanizer` removes *AI-writing tells* (em dashes, rule of three, AI
vocabulary, fake-balanced "it's not X, it's Y" constructions). They are
complementary and stack well: casualize first, then run /humanizer for a final
sweep before anything ships. Don't duplicate humanizer's job here.

## Before / after

**Example 1 — feature launch**
Before: "We are thrilled to announce the launch of our latest feature, designed
to streamline your workflow and empower your team to achieve more."
After: "new feature's live. it does the annoying part of your workflow for you.
that's the whole pitch."

**Example 2 — new job**
Before: "I am humbled and honored to share that I have joined an incredible team
of passionate professionals on a mission to transform the industry."
After: "started a new job this week. the team's sharp and the work's hard in the
fun way. glad to be here."

**Example 3 — event recap** (light-structure dial)
Before: "It was a privilege to attend this year's conference, where I had the
opportunity to engage with thought leaders and gain invaluable insights into
emerging trends."
After:
"[conference] takeaways:

the hallway conversations beat half the talks.
nobody actually knows what they're doing, everyone's just moving fast.
i have a notebook full of ideas and zero free evenings to build them.

worth the trip."
