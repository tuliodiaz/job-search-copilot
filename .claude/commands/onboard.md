---
name: onboard
kind: command
route_kind: skill
route_target: onboard
summary: Set up the client profile — scaffold the vault and ingest CV + preferences
---

# /onboard

Run this **first**. Nothing else in the system has a profile to work from until it completes.

## What it does
Hands off to the **onboard skill**, which:
1. Scaffolds the vault (copies `.claude/templates/` into `vault/`) if it does not yet exist.
2. Ingests the client's CV into `vault/profile/` and captures their preferences.

## Notes
- This command only routes; the procedure and quality bar live in the skill.
- The profile is **living** — re-running `/onboard`, or editing `vault/profile/` directly, updates
  the source that everything downstream tailors from.
- Writes only to the vault.
