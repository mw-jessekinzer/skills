---
name: anti-ai-humanization
description: Standalone 3-pass humanization skill for LinkedIn executive ghostwriting drafts. Runs after structural drafting and Voice DNA application. Pass 1 = Structural Humanization (eradicate rhetorical theater, enforce burstiness, kill transition chains). Pass 2 = Cognitive Grounding (inject mundane specificity, simulate asymmetric expertise, install knowledge boundaries). Pass 3 = Lexical Verification (vocabulary distribution check, emerging pattern sweep, read-aloud test). Outputs a polished, cognitively authentic draft with a change log.
---

# Anti-AI Humanization Skill

This skill runs on a completed draft — one that has already passed fact-checking and Voice DNA application. Its job is not to restructure the post or change the argument. Its job is to make the writing feel like it came from a specific human brain, not a statistical average of all human brains.

**Input:** A completed draft with Voice DNA applied  
**Output:** A humanized draft + change log ready for human review

The three passes run sequentially with no human input between them. Do not expose intermediate drafts.

---

## THE CORE PROBLEM THIS SKILL SOLVES

AI writing fails at three levels:

1. **Surface** — wrong vocabulary (the obvious tells: "pivotal," "delve," em dash soup)
2. **Structure** — uniform rhythm, false lists, theatrical setups, significance inflation
3. **Cognition** — no mundane detail, no knowledge boundaries, no asymmetric expertise, no hapax legomena

Most humanization attempts only fix Level 1. This skill addresses all three. The "robotically authentic" failure mode — where the post sounds like the right person but still feels lifeless — lives almost entirely at Level 3.

---

## PASS 1 — STRUCTURAL HUMANIZATION

Scan the draft for structural AI patterns. Fix every instance silently. Do not flag these for the human — just fix them.

### 1A: Rhetorical Theater — Hard Removal List

These patterns announce authenticity instead of achieving it. Every instance must be removed or rewritten.

**Contrarian pivots**
- Pattern: "That's not X. That's Y." / "This isn't a technology problem. It's a people problem."
- Why it fails: Antithesis as a mathematical formula. The model identifies "insight" as binary reversal of a common assumption. Without contradictory field data behind it, the pivot is unearned.
- Fix: Replace with the specific observation that would have led a real person to that conclusion. Ground the contrast in a real event or data point.

**Fake setup phrases**
- Pattern: "Here's the thing:" / "Let me be direct:" / "Here's what nobody talks about:" / "But here's the kicker:"
- Why it fails: These signal depth by promising an uncomfortable truth. The sentence that follows is almost always a safe, widely accepted platitude. The mismatch is the tell.
- Fix: Delete the setup. Start with the sentence that was supposed to follow it. If that sentence can't stand on its own, it wasn't worth saying.

**Manufactured vulnerability**
- Pattern: "I'll be honest..." / "I used to think X. I was wrong." / "Honestly? Most people don't realize..."
- Why it fails: Maps the semantic structure of confession without supplying actual reputational risk. The "wrong" belief is invariably a socially acceptable or subtly boastful trait. Real vulnerability involves professional failure, embarrassment, or material loss.
- Fix: Either supply the actual failure (specific, low-status, real) or remove the vulnerability framing entirely. A factual statement of what happened is more powerful than a performed confession.

**Single-word paragraph emphasis**
- Pattern: "Wild." / "Exactly." / "Think about that." / "Seriously."
- Why it fails: An algorithmic attempt to simulate burstiness. It mimics the look of genuine astonishment without the underlying feeling that produced it.
- Fix: Remove entirely, OR replace with a short sentence (3–6 words) that names the actual reaction. "That number stopped me." is human. "Wild." is not.

**Significance inflation closers**
- Pattern: "This is just the beginning." / "The future belongs to those who..." / "We're at an inflection point."
- Why it fails: The model requires conclusive resolution to terminate generation. It defaults to sweeping generalization because it cannot let an observation stand without extracting a lesson.
- Fix: End on the specific. The last sentence should be the most concrete thing in the post, not the most abstract. If the post is about a real event, end on the event. Let it breathe.

**Unsolicited life lesson arc**
- Pattern: Problem → Realization → Universal Principle (with therapist tone)
- Why it fails: The model compulsively extracts a macro-lesson from every micro-event. Real executive journeys are messy and non-universal.
- Fix: Cut the universal principle. End on the realization itself. Trust the reader to draw their own conclusion. If a lesson must be included, make it explicitly bounded: "At least in B2B SaaS. Your mileage may vary."

**Epistemic cowardice hedges**
- Pattern: "Some might argue..." / "It's worth considering both sides..." / "Many would say..."
- Why it fails: RLHF fine-tuning trains models to avoid taking definitive stances. The result is fake academic balance — projecting authority without commitment.
- Fix: Replace with the executive's actual position. Strip the hedge. If the post won't commit, it has nothing to say. Add a knowledge boundary (see Pass 2) if appropriate, but do not hedge.

**Emerging patterns to sweep (identified 2025–2026):**
- "Quietly" qualifiers: "the quiet truth," "quietly revolutionizing" → remove or rephrase directly
- Unsolicited coaching questions mid-post: "Are you ready to sit with that?" → cut entirely
- Near-miss metaphors that almost land then don't → rewrite with the literal observation instead
- Excessive internal coherence markers: "as I mentioned earlier," "circling back to" → remove; human posts have loose ends

---

### 1B: Structural Rhythm — Burstiness Enforcement

**The problem:** Language models optimize for low entropy, producing uniform sentence length. A post where every sentence is 12–18 words is a mathematical tell. Detection tools and human readers both identify this pattern.

**The rule:** After every sentence longer than 25 words, there must be a sentence shorter than 8 words somewhere within the next 3 sentences. This is not a suggestion. Apply it mechanically.

**Target sentence length range:** 3 words (minimum, used sparingly for emphasis) to 40+ words (maximum, for complex ideas). The standard deviation across the post must reflect real variation — not uniform rhythm.

**Applying burstiness:**
- Find the longest sentence in the post. What is the first short sentence after it? If there isn't one within 3 sentences, add one.
- Find clusters of similarly-lengthed sentences (3+ sentences all between 12–20 words). Break the cluster with a short sentence or a long one.
- One deliberate fragment per post is acceptable if it creates emphasis. "Real contacts. Real conversations." is a fragment. Use once, maximum.

**Symmetry check on lists:**
- If the post contains a list, check whether all items are roughly the same length and syntactic structure. Symmetrical lists = algorithmic scaffolding.
- Fix: Make list items unequal in length and structure. Or convert the list to flowing prose if the content would read better that way.

---

### 1C: Transition Chain Removal

**The problem:** "Additionally," "Moreover," "Furthermore," "In conclusion," and similar adverbs are algorithmic glue — they hold disjointed ideas together when the model can't create a real thematic transition.

**Hard removal list:**
- Additionally / Moreover / Furthermore / In conclusion / To that end / It's worth noting / It is important to note / On that note / With that said / That being said / This underscores / This highlights / This demonstrates

**Fix:** Replace with one of three options:
1. A hard paragraph break. Let the ideas be adjacent without a connector.
2. A conceptual leap — the last word of the previous sentence creates tension that the first word of the next sentence releases.
3. A concrete transitional detail: "Three weeks later..." / "The same meeting, different outcome." — specific not generic.

**Em dash audit:**
- Count em dashes in the post. If there are more than 2, reduce to 1 or 0.
- Em dashes are not inherently wrong, but they are statistically overrepresented in AI text at 5–10x human rates. One, used for a genuine interruption, is acceptable. More than two reads as performed thinking.
- Default to a comma or a period. Reserve the em dash for cases where neither works.

---

## PASS 2 — COGNITIVE GROUNDING

This is the highest-signal pass. It addresses Level 3 failures — the ones that make a post feel like a wax figure: technically correct, somehow lifeless. No surface fix resolves these. They require injecting the cognitive signatures of human experience.

### 2A: Mundane Detail Injection

**The principle:** Authentic memory is signaled by low-status, mundane, specific physical details. While AI summarizes abstractly ("We faced significant logistical challenges"), humans anchor memory in physical reality ("The barcode scanner on dock four kept freezing, and the shipment sat in the rain").

**What to look for:**
- Any sentence that describes a business event, challenge, or realization in abstract corporate language
- Any "we" or "I" statement that could apply to any executive in any company in any industry
- Any realization or turning point that floats free of a specific moment

**What to do:**
- Add or strengthen one mundane physical or operational anchor per major claim. It does not need to be dramatic. It needs to be specific.
- The anchor can be a tool, a time, a place, a person's name, a number, a weather condition, a piece of equipment. Anything that proves the writer was actually there.
- Examples of cognitive specificity vs. abstraction:
  - ❌ "We realized our onboarding process was broken."
  - ✅ "Week three. Same question from the same new hire. That's when I knew."
  - ❌ "The meeting changed my perspective on customer success."
  - ✅ "She had 47 tabs open and had been on hold with us for 22 minutes before anyone picked up."

**Hapax legomena check:**
- Scan the post for vocabulary diversity. If the same 4–5 content words appear repeatedly without variation, the post has low lexical diversity — a statistical AI fingerprint.
- Introduce at least 2–3 domain-specific, hyper-specific nouns or verbs that appear only once in the post. These are the hapax legomena — words so specific they could only appear in this context: a piece of machinery, a proprietary process name, an exact job title, a specific client scenario.
- These rare, specific words raise the vocabulary distribution curve toward human statistical baselines and make the post feel like it came from someone with real domain knowledge.

---

### 2B: Asymmetric Expertise Simulation

**The principle:** Real experts don't explain everything they know. They assume peer-level competence in the reader, use industry shorthand without defining it, and focus entirely on the delta — the specific new information they're adding to an existing expert discourse. AI models over-explain by default due to helpfulness fine-tuning.

**What to look for:**
- Definitions of industry-standard terms that any professional in the field would already know
- Over-contextualizing: long preambles explaining the background before getting to the point
- Uniform confidence across all claims — the model is equally certain about everything, which is itself a tell

**What to do:**
- Remove definitions of any term the target reader would already know. Trust the audience.
- Cut preamble. The first sentence should assume the reader is already in the conversation.
- Check for uniform confidence. Find one claim the exec would realistically be uncertain about and introduce a genuine knowledge boundary (see 2C).

---

### 2C: Knowledge Boundary Installation

**The principle:** Research (University of Arizona, 2025, n=5,000+) found that readers rate content as significantly more trustworthy when it admits what the writer doesn't know — regardless of actual authorship. AI models project universal authority because safety fine-tuning trains them to avoid uncertainty. This is both inauthentic and counterproductive.

**What to look for:**
- Universal claims: anything that asserts a principle applies broadly, always, or to everyone
- Conclusions that don't acknowledge the specific context that produced them
- Advice that could apply to any executive, any company, any industry

**What to do:**
- Find the post's broadest claim. Add a boundary. This is not a hedge — it is a precision adjustment.
- Boundary examples:
  - "At least in our segment of the market."
  - "This is true for companies past Series B. Pre-revenue is a different game."
  - "I don't know if this translates to enterprise. We never tried."
  - "That math worked for us. It may not for you."
- One knowledge boundary per post is sufficient. More than two starts to read as false modesty.
- The boundary should be specific, not generic. "Your mileage may vary" is too vague. "This assumes you have a sales-led motion, not PLG" is specific enough to be useful and human.

---

### 2D: Anti-Consensus Pressure

**The principle:** AI models aggressively seek the middle ground due to RLHF training. This produces content that argues passionately for universally accepted norms — "communication is key," "leadership requires adaptability" — which signals machine authorship to any experienced reader and fails to establish genuine thought leadership.

**What to look for:**
- The post's central claim. Ask: would 95% of professionals in this field agree with this without hesitation?
- If yes, the claim is consensus. It has no thought leadership value and will not generate expert engagement.

**What to do:**
- Sharpen the claim toward the specific, non-obvious version. Not "great teams communicate well" but "our team communicates worst when things are going well — complacency is harder to diagnose than conflict."
- The sharpened claim should be true and defensible — not contrarian for its own sake. It should be the thing the exec actually believes that most people in the field haven't said clearly yet.
- If no sharpening is possible without fabricating a position the exec doesn't hold, flag this for the human reviewer. Do not invent a controversial stance.

---

## PASS 3 — LEXICAL VERIFICATION

Final sweep for vocabulary-level AI tells. This pass catches what Passes 1 and 2 didn't.

### 3A: Banned Vocabulary — Full Removal List

Replace every instance. No exceptions.

| Remove | Replace with |
|--------|--------------|
| Additionally (sentence start) | Also / Plus / And / or cut entirely |
| align with | matches / fits / works with |
| boasts / features | has |
| crucial / critical | important / key / or name the specific consequence |
| delve | explore / look at / dig into |
| enhance | improve / boost / strengthen |
| ensure | make sure / guarantee (if accurate) |
| fostering | building / creating / encouraging |
| game-changing / transformative / revolutionary | name the specific change |
| garner | gain / get / attract |
| highlight (as verb) | show / point out / reveal |
| impactful | effective / or specific to the actual impact |
| in today's rapidly evolving landscape | cut entirely |
| intricate / intricacies | complex / details / nuances |
| it is worth noting | cut entirely; if worth noting, just note it |
| landscape (abstract) | field / area / space |
| leverage (as verb) | use / apply |
| navigate (abstract) | handle / manage / work through |
| pivotal | important / key / or name the actual significance |
| robust | strong / reliable / or name the specific quality |
| seamless | smooth / frictionless / or name the specific quality |
| serves as / stands as | is |
| showcase | show / display |
| significant / significantly | name the actual magnitude ("by 40%" / "across three quarters") |
| tapestry | mix / combination / or cut |
| testament | proof / sign / example |
| thrilled / excited / humbled to announce | cut the framing; just say the thing |
| underscore (verb) | emphasize / show / prove |
| unlock | open / enable / access |
| valuable | useful / helpful / or name the specific value |
| vibrant | lively / active / or name the specific quality |

**2025–2026 emerging vocabulary flags:**
- "Quietly" as a qualifier: "quietly revolutionizing" → remove the qualifier
- "Potential" used as adjective at high frequency (statistically overrepresented in AI corpora) → replace with specific projections or remove
- "Significant" at any frequency → always replace with actual magnitude
- Semantic echo chains: "robust," "seamless," "innovative" in sequence → cut to one specific descriptor

---

### 3B: Contraction and Register Check

**Human writing uses contractions.** AI defaults to formal register even when instructed to be casual.

- Scan for: do not / cannot / will not / it is / they are / we are / I am / would not / should not
- Replace with contractions wherever the tone supports it: don't / can't / won't / it's / they're / we're / I'm / wouldn't / shouldn't
- Exception: If the exec's Voice DNA specifies formal register, preserve it. Voice DNA overrides this rule.

**Conversational asides are allowed:**
- One parenthetical aside per post is acceptable and human: "(still figuring that one out)" / "(not an exaggeration)" / "(this took longer than I'd like to admit)"
- Use only where the Voice DNA would support it. One maximum.

---

### 3C: Read-Aloud Verification

Before completing Pass 3, run a mental read-aloud test against these five questions:

1. Does it sound like a real person talking, or like a press release?
2. Would someone who knows this exec say "yes, that's how they actually talk"?
3. Is there at least one sentence in this post that could only have been written by this specific person, about this specific situation?
4. Does the post end on something concrete, or does it drift into abstraction?
5. Is there anything in this post that a motivated generalist could have written without ever having done this exec's job?

If the answer to question 3 is no: return to Pass 2, section 2A. Inject a more specific mundane detail.

If the answer to question 5 is yes: find the sentence a generalist could have written. Either make it more specific or cut it.

---

## FINAL OUTPUT

After all three passes, output:

```
HUMANIZATION COMPLETE — [Exec Name / Post Topic]

PASS 1 — STRUCTURAL:
Rhetorical theater removed: [list patterns found and fixed, or "None detected"]
Burstiness: [sentence length range before → after, e.g., "12–19 words → 4–38 words"]
Transitions removed: [list any removed, or "None detected"]
Em dash count: [before → after]

PASS 2 — COGNITIVE GROUNDING:
Mundane detail: [describe the anchor injected, or "Sufficient specificity already present"]
Asymmetric expertise: [what was cut or tightened, or "No over-explanation found"]
Knowledge boundary: [the boundary installed, quoted, or "None needed — claim already bounded"]
Consensus sharpened: [before → after, or "Central claim was already specific"]

PASS 3 — LEXICAL:
Banned words removed: [list, or "None found"]
Contractions added: [count, or "Register already appropriate"]
Read-aloud check: [flag any remaining concern, or "Sounds like a person"]

────────────────────────────────────

HUMANIZED DRAFT:

[Full post text — post all three passes]

────────────────────────────────────
```

---

## HARD RULES

**Never fabricate specifics.** If the draft lacks a mundane detail and no real detail exists in the source material, flag it for the human reviewer. Do not invent a specific — an invented specific the exec doesn't recognize is worse than a vague one.

**Voice DNA wins.** If the exec's Voice DNA specifies formal register, keep it. If their Voice DNA includes single-word emphasis, allow it. This skill applies general humanization principles; the exec's documented voice is the override authority.

**Do not restructure the post.** This skill humanizes; it does not rewrite. The argument, structure, and core content are fixed. If a structural problem is so severe that humanization cannot fix it, flag it for the human reviewer.

**Never skip a pass.** All three run in sequence, every time.

**Knowledge boundaries are not hedges.** A hedge weakens a claim. A knowledge boundary precises it. "Some might argue" is a hedge. "This is true for PLG companies; sales-led is a different game" is a knowledge boundary. The distinction matters.

**On engagement as a signal:** AI-generated posts in leadership categories sometimes achieve 40–75% higher short-term engagement than unoptimized human content because they perfectly mimic viral structure. Engagement alone is not a reliable signal of authentic writing. The goal is not a post that performs well this week. It is a post that builds the executive's reputation over time — because it says something only they could have said.
