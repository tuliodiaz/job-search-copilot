# Session retrospective — 2026-07-27

First full run of the engine end-to-end: onboarding → scout → recon → apply (pursue gate) → craft
docs → submit (send gate) → applied, plus a referral hand-off. This retro is about the **process and
the engine**, not the specific company.

## TL;DR verdict
The engine's *skeleton is sound* — the invariants (captain's-seat gates, truthful-only, scan-untrusted,
provenance, engine-vs-vault) gave a safe, legible frame, and the collection recipes (esp. Rippling)
carried real, correct know-how. The **weak point this session was the truthfulness/quality of what gets
written**: grounding accepted an overstatement, no guard evaluated emphasis/reader-effect, and the
voice guard missed an obvious AI tell. Nearly every document-quality problem was caught by the
*client*, not by a guard. That is the **strongest signal from this one session** — a hypothesis to
confirm across future retros, not a settled conclusion. (n = 1; see "signals to watch" below.)

---

## Client feedback (Tulio) — primary

### Liked
- **The top-down interaction evolution makes sense.** Asking for the CV → questions → investigation →
  apply → submit is a natural arc; the flow of the engagement felt right.
- **Session persistence / state recovery is solid.** Verified by opening a *new* session and having it
  correctly identify the application's state. This means real-world use works: receive a call or email,
  input the update into the repo, and it tracks and keeps the evolution of the application over time.

### Did not like
- **Had to correct the CV and the cover letter — the agent didn't write like a human thinking about
  what the reader (recruiter) would think.** Concretely:
  - Put **"19 years of experience" in the first line**; only after push-back did it recognize that
    isn't ideal to lead with.
  - **Inserted "AI"** prominently where AI was *not* a main requirement of the role.
  - **Tried to justify a missed requirement (lack of React experience)** in a way that pushed a
    narrative / argued for it — incorrectly written. It could have presented the information a different
    way, or simply **not mentioned it**, to get the intended effect on the recruiter.
  → The documents should be redacted for **the effect on the reader**, not to defend or justify. This
  is the biggest miss and the reason the docs had to be reworked repeatedly.
- **Recon went short.** It did not proactively try to review the **HR suggestions / applicant-facing
  documentation the company publishes** (their "how we hire" guidance, tips for candidates). The client
  had to **actively ask** for that research; it should be part of recon by default.
- **Too many loops with the ATS despite existing engine documentation for that ATS.** Either the
  documentation isn't useful, or it had missing/incomplete gaps the agent had to figure out live.
  Figuring it out is fine, but the client **expected fewer loops** — the recipe should get more done
  per round-trip.

---

## What the engine did well

- **The gates worked and the client valued them.** The pursue gate (fit verdict before any drafting)
  and the send gate (engine fills the form, client clicks Submit) kept the human in control at exactly
  the committing moments. The Cloudflare CAPTCHA at submit was correctly left to the client.
- **Scan → injection-auditor → fail-closed** ran cleanly and repeatedly (posting, careers page,
  transcripts). The discipline of scanning *every* ingested source — including a machine transcript —
  held.
- **Isolated fit-assessor** gave an honest, non-anchored verdict, and re-running it after the client
  added grounded evidence (55 → 72) was the right move — the isolation kept it from rubber-stamping.
- **Collection recipes were battle-tested and accurate.** Rippling `get-posting` and
  `submit-application` predicted the real form precisely: map-by-order, `div[role=combobox]` selects,
  hidden file inputs, résumé-parse autofill, `Apply` reporting `data-disabled` not `.disabled`. This
  saved a lot of trial and error.
- **The vault structure** (profile/, companies/<slug>/{_sources,research,applications}) held durable
  knowledge well and made "gather once, reuse" natural.
- **playbook-notes + memory** gave a real place to capture learnings so they aren't lost.
- **Determinism of render.py** meant "what you reviewed is what you send" — and when a real bug
  surfaced, it was fixable at the client's direction.

## Where the engine misled or fell short (fix these)

1. **Grounding check = "mapped", not "faithful" (highest-value fix).** Both CLAUDE.md invariant #2 and
   the tailor-resume grounding step define a client claim as valid if it *maps to a line* in the
   profile. That let an **overstatement** through: "I work across Vue, React, and React Native" mapped
   to a skills line but flattened production-Vue and pet-project-React/RN into peers. Grounding must
   check **fidelity/proportion**, not just existence — a claim that stretches beyond what its source
   supports fails, like an unmapped claim.
2. **No emphasis/persuasion guard.** The three Craft guards (grounding, verification, voice) never ask
   "does this lead with strengths? does it foreground a weakness just because the rubric asked?" I made
   three rubric-chasing errors — defending React, headlining an "AI" buzzword, opening with a tenure
   number — and **no guard caught any of them; the client did.** Needs a doc-critic pass (or fold
   "lead with substance/fit, don't foreground required weaknesses" into a guard).
3. **voice-auditor missed em-dashes.** A textbook AI-writing tell, all over both docs, and the style
   guard passed them. Its explicit tell-list should include em-dashes (and likely arrow "→" glyphs and
   "not just X but Y" constructions).
4. **render.py bugs.** (a) **Multi-line list items broke lists** — a hard-wrapped bullet in the source
   became `<li>` + a stray `<p>`, producing outdented "crowded" output. FIXED this session (parser now
   merges continuation lines; hanging-indent CSS; spacing; v2). (b) Header lines merged into one
   paragraph (worked around with blank lines; a hard-break rule would be the real fix).
5. **Recon scope too narrow in signals mode.** It gathered reputation/red-flags but **never fetched the
   company's own published hiring content** (careers-page "how we hire" videos, values, process) — the
   single richest primary source for tailoring and interview prep. Needs a careers-page research recipe.
6. **No media ingestion at all.** Both the deep-recon agent and the main loop **silently skipped
   embedded videos** — no attempt, no flag. A whole class of primary source (recruiter videos) was
   invisible. Built an ffmpeg+whisper transcript pipeline this session; needs promoting to a recipe.
7. **A blanket rule that was too rigid:** submit's "never answer the salary question" — the real rule
   is "don't *guess*; fill it if grounded and client-directed" (comp target was in preferences.md).
8. **No proactive capture of reusable application answers.** Standing answers (bilingual screener, SMS
   consent, employer-disclosure, pronouns, salary phrasing) only got saved because the *client*
   suggested it. logistics.md should have an "application defaults" section and the flow should offer to
   capture them.

## Agent-vs-engine failures (my behavior — and whether the engine could prevent them)

- **Premature closure / asserting unverified conclusions.** I stated "the French careers page reused
  the English video, not localized" as fact — it was false (a shallow grep on a shared ID instead of
  reading the page). I also enumerated videos non-exhaustively several times. The **provenance
  invariant existed and should have stopped this**, but nothing *enforced* "enumerate fully / mark
  unverified." Consider making enumeration + verified-vs-recalled an explicit checklist step in
  scout/recon, not just a principle.
- **Rubric-chasing over judgment.** I let an automated reviewer's "close the React gap" note push me to
  *foreground* the weakness. Meta-lesson: apply reviewer output with judgment; a "fix" suggestion can
  be wrong for the goal.
- **Broke isolation discipline once.** Ran the deep company-recon inline (in the main context) instead
  of via the isolated agent, after correctly using a subagent for signals mode. The engine relies on
  the operator to honor isolation; the mode (signals vs deep) and its isolation could be made more
  explicit in the recon entrypoint.
- These three are captured as memories: `anchor-on-truth-not-rubric`,
  `premature-closure-verify-before-concluding`, `lead-with-substance-not-labels`. **But memory is
  machine-local and does NOT travel with the repo** — so the durable fixes belong in `.claude/`, not
  just memory.

## Observed friction this session — signals to confirm across future retros

**n = 1 session. This is NOT a fix list and NOT prioritized.** These are raw observations to **confirm
or refute** as more retros accumulate. Some may not recur; some may not be fixable; the obvious fix for
some may be wrong. Prioritizing or prescribing solutions from a single session would be the same
premature-closure error this retro is about — that judgment needs a *pattern* across several sessions.
(Where a session-local fix was already made and verified — e.g. the render.py list bug — it's noted as
done above; that's different from prescribing engine changes from one data point.)

- Grounding accepted a claim that *mapped* to the profile but **overstated its proportion** (React/RN).
- **No guard evaluated the document for reader-effect / emphasis;** the client caught all such issues.
- voice-auditor **passed em-dashes** (an AI tell).
- Recon **didn't proactively seek the company's applicant-facing hiring guidance** (client had to ask).
- Recon / main-loop **skipped embedded media** without attempting or flagging it.
- **Many ATS round-trips** despite a detailed recipe (client expected fewer loops).
- **"Never answer salary" applied rigidly** to a grounded, client-directed value.
- **Standing application answers** weren't captured until the client suggested it.
- (Agent behavior) **asserted an unverified conclusion as fact**; enumerated non-exhaustively.

**The one signal cross-validated even within this single session:** the client's #1 dislike and the
agent's own evaluation *independently* landed on the same thing — "documents weren't written for the
reader's effect." Two independent sources in one session is a stronger signal than the rest, but it is
still one session. Treat it as the leading hypothesis to watch, not a settled conclusion.

## Meta / interaction notes

- The engine performed best as a **collaborative loop**, not autonomous. The client caught every
  document-quality defect the guards missed; the value was in fast iteration + the client's judgment,
  with the engine handling structure, safety, and mechanics.
- The **captain's-seat gates were the standout** — the client repeatedly exercised control (rejected
  renders, redirected drafts, directed the engine fix) and the framework accommodated it cleanly.
- A theme that connected several observations and the agent failures this session: **when what's
  asked-for / trendy / rubric-shaped diverged from what's true and strongest, no guard pulled back to
  truth-and-substance.** Noting it as the leading hypothesis from this session — whether it's real,
  general, or fixable is for future retros to confirm.
