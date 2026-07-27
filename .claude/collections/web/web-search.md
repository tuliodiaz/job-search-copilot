---
name: web-search
kind: recipe
last_verified: 2026-07-24
verified_by: "WebSearch 'Affirm company employee reviews Glassdoor culture layoffs 2026' -> results incl. Glassdoor (rating 4.0/5, 616 reviews, 73% would recommend) plus layoff and post-IPO culture signals with source URLs; confirmed live 2026-07-24"
requires: WebSearch tool
summary: Gather public reputation / stability / red-flag signals about a company via web search
---

# Recipe: web-search (company signals)

## Preconditions
- `company` — display name (add location if the name is ambiguous).
- WebSearch available.

## Steps
1. Run several **targeted queries** across distinct dimensions, not one vague query. The dimensions
   that surface useful signal:
   - **reputation / employee reviews** — e.g. "<company> employee reviews Glassdoor Blind",
   - **stability** — layoffs / restructuring / hiring freeze (recency matters most here),
   - **financial health** — funding, earnings, IPO / valuation news,
   - **red flags** — scandals, lawsuits, "is <company> legit / a scam".
2. Collect result **titles, snippets, and URLs**. Save the key source pages under the company's
   `vault/companies/<company>/_sources/`.
3. Summarize into concise **signals**, split into green flags / red flags / neutral. Weight by
   recency — a 2-year-old review is weaker than a last-quarter one.

## Self-check (validate by readback)
Confirm WebSearch returned real URLs for at least the reputation and stability queries. If it returns
nothing usable (blocked, empty), degrade to recalled. A single search that "found nothing" is **not**
evidence the company is clean — absence of signal is not a green flag.

## Limits (honest scope)
Web search yields ratings and snippets, not full review corpora. Structured review/network data (full
Glassdoor/Blind, LinkedIn) needs a dedicated source recipe plus auth/MCP.
