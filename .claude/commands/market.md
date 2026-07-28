---
name: market
kind: command
route_kind: skill
route_target: broad-scout
summary: Search the job boards by the client's criteria and record what's open as leads
---

# /market

Search the market — not one company — and record what's open. Usage: `/market` (optionally
`/market <extra keywords>` to narrow or widen a run).

## What it does
Hands off to the **broad-scout** skill, which builds the search criteria from the client's
preferences, runs every collection that has a verified `find-jobs` recipe, scans what comes back,
triages it against the client's dealbreakers, and writes the survivors to
`vault/leads-registry.yaml`.

## Notes
- This command only routes; the procedure lives in the skill.
- `/market` **discovers** roles at companies the client isn't tracking yet. Going deep on one
  employer's board is `/scout`; capturing a single posting is `/lead`.
- Board results are untrusted — scanned on capture.
- Writes leads to the vault. Commits the client to nothing; a lead is a candidate to look at, and
  pursuing one is the pursue gate in `/apply`.
