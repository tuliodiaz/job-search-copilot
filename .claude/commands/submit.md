---
name: submit
kind: command
route_kind: recipe
route_target: greenhouse/submit-application
summary: Fill an application form for the client to review and submit
---

# /submit

Fill a role's application form and hand it to the client to submit. Usage: `/submit <application>`.

## What it does
Routes to the platform **submit-application** recipe for the application's ATS (resolved from
`company.yaml` → `.claude/collections/platforms/<ats>/submit-application.md`). The recipe drives the
browser to fill every field from the vault, validates by readback, and **stops for the client** to
solve any CAPTCHA and click Submit.

## Rules — the send gate
- **The engine never clicks Submit.** The client reviews, does the CAPTCHA, and submits.
- Answers must be **grounded** (profile / `logistics.md` for work-authorization) — never guess a
  required field; if one can't be grounded, stop and hand the live form to the client.
- Runs only after the pursue gate and after the documents are drafted (`docs/`).
- On the client's confirmation they submitted, advance `status.yaml` → `applied`.
