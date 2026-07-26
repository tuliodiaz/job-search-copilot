---
name: tailor-resume
kind: skill
summary: Draft a tailored résumé + cover letter — grounded, verified, voice-checked, rendered
reads: vault/profile/ (cv.md, narrative.md, logistics.md), analysis.md, company research + _sources/
writes: docs/ (resume.pdf, cover-letter.pdf) in the application folder
requires: python3; a Chromium-family browser (for the renderer) — checked before rendering
---

# Skill: tailor-resume

The **Craft** procedure. Runs **only after the client clears the pursue gate** in `/apply`. Writes
only to the vault; Craft is preparation, not a gate. This is where **Truthful only** is enforced at
the point documents are written.

## Precondition
`narrative.md` must be non-empty — it is a grounding source, and drafting against an empty narrative
would force either a thin document or invention. If it's empty, **ask the client for a few sentences
first** (what's pulling them to move, a proudest result, working style) and do not draft until then.

## Pipeline: draft → ground-check → verify → voice-check → render

1. **Draft** a résumé + cover letter tailored to `analysis.md`'s genuine requirements and the
   company's verified research — emphasizing the most relevant real experience. The tone/emphasis is
   driven by the posting. **Tailor and emphasize; never fabricate.**

2. **Grounding check — claims about the CLIENT.** Every claim about experience, skills, or results
   must map to a line in `cv.md` or `narrative.md` (and eligibility/availability answers to
   `logistics.md`). An unmapped claim is **removed**; if the client believes it's true, they add it to
   the profile first — the document is not where new facts about the client are introduced.

3. **Verification — claims about the COMPANY / role.** Every world-claim the cover letter leans on (a
   product, value, milestone) must be **verified** from a primary source recorded under the company's
   `_sources/`, or **dropped**. A *recalled* fact is confirmed or cut — never presented as verified.

4. **Voice check.** Spawn the **`voice-auditor`** agent to remove AI-writing tells — **truthfully**;
   it edits style only and may not alter any fact.

5. **Render.** Pass the finished markdown to the renderer:
   ```
   python3 .claude/scripts/render.py <draft.md> <docs/resume.pdf>
   ```
   The renderer is deterministic and writes an inspectable `.html` beside the PDF. If it exits non-zero
   (e.g. exit 3 = no browser found), surface the error and **do not present an unrendered or partial
   document as final**; the environment check offers to install the browser.

## Three guards, none of which invents
Grounding = the client's claims are true · verification = the world's claims are true · voice = it
reads human.

## Hand-off
The rendered PDFs sit in `docs/`. **Sending them is the client's action** at `/submit` (the
send-document gate) — this skill never submits.
