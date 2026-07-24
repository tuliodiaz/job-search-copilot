---
name: apply
kind: command
route_kind: skill
route_target: analyze-posting
summary: Qualify a role at the pursue gate; on approval, draft its documents
---

# /apply

Qualify a role and, once the client approves, prepare its application. Usage:
`/apply <application-or-posting>` (a captured lead, or a posting URL to capture first).

## Decide — before the pursue gate
1. **`analyze-posting` skill** — ensure the posting is captured + scanned (via `capture-posting` if
   needed), then parse it into `analysis.md` and advance `status.yaml` to `stage: assessing`. A
   `trap` disposition means analyze using only genuine requirements; `unresolved` fails closed.
2. **`fit-assessor` agent** — return `apply | stretch | skip` + a 0-100 score (with its band
   snapshot), a grounded **eligibility** check against `logistics.md`, reasons, and gaps. Record the
   verdict in `status.yaml` (`fit.score`, `fit.verdict`, `fit.bands`).
3. **⛔ Pursue gate — STOP here.** Surface the verdict, score, eligibility, reasons, and gaps, and let
   the **client decide** whether to pursue. All three verdicts land here: *skip* halts, *stretch* is a
   judgment call, *apply* is recommended — **none proceeds to drafting without the client's go-ahead.**
   If eligibility is `unknown`, ask the client to resolve it before pursuing.

## Craft — after the client clears the pursue gate
Drafting the tailored résumé + cover letter (the `tailor-resume` skill → renderer) happens only after
approval. **This half is not built yet** — until it is, `/apply` performs Decide and stops at the
pursue gate; drafting is done separately. Drafting also requires a non-empty `narrative.md`, since
every client-claim is grounded against it.

## Rules
- Never draft before the client clears the pursue gate.
- Everything up to the gate writes only to the vault (`analysis.md`, `status.yaml`) and commits the
  client to nothing.
