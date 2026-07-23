---
name: lead
kind: command
route_kind: recipe
route_target: capture-posting
summary: Capture one job posting (URL or file) as a new application at stage=lead
---

# /lead

Capture a single posting the client found, as a new application. Usage: `/lead <posting-url-or-file>`.

## What it does
Hands off to the **capture-posting** recipe, which fetches (or reads) the posting, **scans it on
capture**, records the security disposition once, and scaffolds the application folder at
`vault/companies/<company>/applications/<role--date>/` with `status.yaml` at `stage=lead`.

## Notes
- This command only routes; the mechanics and the fail-closed handling live in the recipe.
- A recruiter-sourced lead should record `source: recruiters/<id>` in `status.yaml`.
- A "lead" is just an application at `stage=lead`; `/apply` later qualifies it at the pursue gate.
- Requires `python3` (the scanner is a standard-library Python script). The recipe checks this.
