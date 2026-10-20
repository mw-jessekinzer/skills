# Brand basics

## Colors

| Name | Hex | Use |
|---|---|---|
| Off-white | `#F6F7FE` | Text on dark and blue. Background of light slides shown on screen. |
| Paper | `#FFFFFF` | Background of every printed page and light deck. `#F6F7FE` prints as a faint tint. |
| Near-black | `#010313` | All reading text on light. Background of dark slides and the one dark page. |
| Blue | `#2237F1` | One meaning: the decision or next step (see below). |
| Green | `#C7FA50` | One highlight on a dark slide, at most. Never on light or blue. |
| Muted | `#666666` on light, off-white at 60 to 75% on dark and blue | Labels, kickers, captions, footers only. Reading text is never muted. |

Chart bars: the one key bar is near-black on paper, green on a dark slide, off-white on a dark page or a blue page; every other bar is `#A8A8A8` on paper, off-white at 30 to 40% on dark. Image frames before the real image arrives: `#E9E9E9` on paper, `#1C1E2D` on dark. No other colors.

**Blue has one meaning: the decision or next step.** It marks the ask line, the page or slide that carries the decision (a proposal's investment page, a deck's closing ask), and nothing else. Key statements stay dark with the green highlight; the key bar on paper is near-black. The one approved exception is the blue field with a line glyph on a document cover. Blue is never a label color, a link color on every link, a heading color, a chart color or a decoration.

**Blue on near-black is banned.** No blue text, bars or shapes on a dark slide or dark page. On dark, the single highlight is green; a blue slide is its own full-bleed slide.

## Logo

Files in `assets/logos/`, all `fill="currentColor"`, so they take the text color:

- `mw-logo.svg`: horizontal wordmark (811 x 127). The default for everything client-facing. The templates carry it as an inline `<symbol id="mw-logo">`.
- `mw-icon.svg`: the mark alone (282 x 150). Only where the wordmark will not fit (avatars, favicons, a 20px corner).
- `mw-logo-stacked.svg`: stacked (285 x 212). Square formats only (social tiles).

Rules:
- One logo per page. On a cover or one-pager the head logo replaces the footer logo (the templates hide it).
- Near-black on paper, off-white on dark. Never on blue or green; the templates hide the footer logo on blue pages.
- Sizes: 13px tall at the top of a document cover, 9px in a document footer, 36px on a deck cover, 22px in a deck footer.
- Top right on a cover, bottom left in a footer. Never centered, never stretched, never recolored, never in a box.
- Never place a white-background logo image on top of a color area. Use the inline SVG.

## Shape and type

- Radius 0. Square corners on everything: frames, images, bars, tables.
- Sentence case for every title, heading, label and button. Never title case, never all caps. Approved taglines copied verbatim keep their approved form.
- One family, TT Hoves, with DM Sans as the approved fallback (see `fonts.md`). Regular weight. No italic.
- The company name is "Midwestern" in copy. Never "MWI".
- Website: `midwestern.com`. It goes in footers and web links. Email addresses use the `@buildmidwestern.com` domain; never print buildmidwestern.com as the website.
- Service lines are names and keep their capital inside sentence case: Embedded, Scoped, Recruiting. Recruiting offerings as the Service Offerings Taxonomy lists them: Managed Sourcing, Retained Search, Contract to Hire. Generic phrases stay lower case ("an embedded team", "a scoped project").

## What we sell

From the Service Offerings Taxonomy and Messaging Patterns. Do not add positioning beyond this.

- **Embedded:** Midwestern talent joins the client's own team and works in their process. Roles: engineering (front end, backend, data, AI, forward deployed), product and project management, product design. Typical placement: under 2 weeks (under 10 business days).
- **Scoped:** fixed-scope engagements with defined deliverables: discoveries, builds (POC, MVP, web application), product and AI consulting, audit and research, maintenance.
- **Recruiting:** sourcing and placement of permanent and contract-to-hire talent: Managed Sourcing, Retained Search, Contract to Hire (90 or 180 day). Client-facing phrasing: "fill a role in under 20 days". Internal and sales documents may use the underlying form: full-time roles in under 3 weeks (under 15 business days).
- **Why one partner:** the three models sit under one roof, so the buyer picks the model. No long-term staff: Scoped. A team without a fixed deliverable: Embedded. W-2 hires: Recruiting.
- **Speed figures are typical delivery windows, not guarantees.** Write "in under" or "typically". Never promise a date for a specific role or phrase a figure as a contract term.
- **Positioning line, verbatim only:** "Talent Partner for the AI era of work" (Messaging Patterns v1.2, capital P as approved). Do not paraphrase it or invent another tagline.

## Headline voice

Full voice rules live in the Marketing Hub's Messaging Patterns. What a layout needs:

- Specific over abstract. "Engineers who ship in your stack and join your standup" beats "specialized technical talent".
- Confident, direct, peer to peer. Write for a CTO at a mid-market tech company: would they trust this line?
- Titles state the finding or the outcome. "Re-keying is the biggest single loss" passes; "Time analysis" fails.
- State the positive claim. No "X, not Y", "rather than" or "isn't X, it's Y" framing in titles, statements or captions. Approved Messaging Patterns phrases copied verbatim are the only exception.
- No parentheses in titles, headlines or display type. The business-day equivalent of a proof point goes in the figure label or body.
- Never write: staffing firm, outsourcing, resources (for people), future of work, AI-powered, AI-first, cutting-edge, world-class, synergy, leverage, innovative, "We believe", solutions.

## Three kinds of content

- **User facts** (anything in the request: client name, team size, price, dates, results) are real content. Use them; never replace them with a Placeholder.
- **Draft content** (phases, deliverables, features, approach, team roles, a story consistent with the user facts, recommendations, a payment schedule that splits a price the user marked as sample) is yours to write. Write it plainly and specifically, and list it in the handover as draft to confirm.
- **Midwestern facts** (proof points, company figures, commercial terms for a real price, named people, contacts, quotes, client names, guarantees, response times) are never invented. Use Proof Points or the user, or write "Placeholder: ...".
- Sample status follows the number: if the user marked the price as sample, a milestone split of it is sample draft content, not an invented term.
- Proof points: only the ones above, with their qualifier every time ("under 2 weeks"). Never round them, restate them as "in two weeks", or say when the clock starts. No other company figure (years in business, client counts, hours) unless the user supplies it.
- Never invent commitments Midwestern would be held to (guarantees, response times, notice periods, terms on a real price). Draft phases and process steps are allowed and flagged in the handover.
- A Placeholder reads "Placeholder: what is missing" ("Placeholder: name, email, phone"), at body or label size, on one line. Never in a title, statement, display or lead slot. If a title would have to be a Placeholder, the slide or block is not ready: delete it or ask. No square brackets, no vague stand-ins like "your representative".
- Sample numbers are marked twice only: in the footer document or deck name (", sample data") and in the kicker of the first page or slide where they appear.
