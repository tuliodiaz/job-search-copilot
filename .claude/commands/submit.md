---
name: submit
kind: command
route_kind: recipe
route_target: <ats>/submit-application
summary: Fill an application form for the client to review and submit
---

# /submit

Fill a role's application form and hand it to the client to submit. Usage: `/submit <application>`.

## What it does
Routes to the **submit-application** recipe in the ATS's collection folder (resolved from
`company.yaml` → `.claude/collections/<ats>/submit-application.md`; if it isn't recorded, match the
form URL against the recognition key in each `.claude/collections/<system>/README.md`). The recipe
drives the browser to fill every field from the vault, validates by readback, and **stops for the
client** to solve any CAPTCHA and click Submit.

**The application may not be on the posting's system.** Some ATS postings are adverts that route
applications elsewhere — resolve to the system of the *form*, not the posting. If it has no
collection folder, follow §"When you're short a capability"; never improvise a form procedure.

## Rules — the send gate
- **The engine never clicks Submit.** The client reviews, does the CAPTCHA, and submits.
- Answers must be **grounded** (profile / `logistics.md` for work-authorization) — never guess a
  required field; if one can't be grounded, stop and hand the live form to the client.
- Runs only after the pursue gate and after the documents are drafted (`docs/`).
- On the client's confirmation they submitted, advance `status.yaml` → `applied`.
