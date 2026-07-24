---
name: recon
kind: command
route_kind: agent
route_target: company-recon
summary: Research a company from public sources (deep research for tailoring + interview prep)
---

# /recon

Research one company from public assets. Usage: `/recon <company>`.

## What it does
Hands off to the **company-recon** agent in **deep** mode — thorough public research (product, tech,
recent milestones) written to `vault/companies/<slug>/research/`, for tailoring documents and
interview prep. This is the Prepare-stage research, normally run **after** the pursue gate.

## Notes
- A lightweight company-fit **signals** read (reputation, layoffs, red flags) also runs automatically
  inside `/apply`'s Decide step, before the pursue gate — `/recon` is the deeper, standalone pass.
- Public assets and the client's own accounts only. All fetched sources are scanned on capture and
  marked verified/recalled with saved sources.
- `company-recon` sources from whatever research recipes exist in the collection (today: `web-search`);
  the collection grows as more sources are verified.
