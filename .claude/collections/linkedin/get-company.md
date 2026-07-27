---
name: get-company
kind: recipe
last_verified: 2026-07-26
verified_by: "GET https://ca.linkedin.com/company/dialogue-md -> 200, 362811 bytes, no authwall; one application/ld+json Organization block keyed @context/@type/address/description/logo/name/numberOfEmployees/sameAs/slogan/url — numberOfEmployees.value 960, sameAs https://dialogue.co/, address 2200 Rue Stanley, Montreal, Quebec H3A 3G3. Page <dt>/<dd> facts: Website, Industry 'Health and Human Services', Company size '501-1,000 employees', Headquarters 'Montreal, Quebec', Type 'Privately Held', Specialties; 94,848 followers. Slug non-derivable confirmed: linkedin.com/company/orderco -> 404. Confirmed live 2026-07-26. End-to-end handoff confirmed 2026-07-26: LinkedIn job 4444374252 -> Dialogue -> dialogue.co/en/careers -> data-job-board-id=\"dialogue-en\" -> collections/rippling/."
requires: network access (HTTP GET) with a browser User-Agent; an HTML parser; no client login
summary: Read a company's public LinkedIn firmographics for company-recon
---

# Recipe: LinkedIn — get-company

Read one company's **public** LinkedIn page for firmographics. A research source for `company-recon`:
it supplies *verifiable facts* about a company — size, industry, headquarters, official website — and
deliberately **not** sentiment.

## Preconditions
- `company_url` — `linkedin.com/company/<slug>`.

  **The slug cannot be guessed** — it is not simply the company name, and a wrong guess returns a 404
  (or, worse, the wrong company). Obtain it from a job card's employer link (`find-jobs`) or a job
  page's `topcard__org-name-link` (`get-posting`). If you have only a company name and no LinkedIn
  URL, **stop** — there is no public name→id lookup.

## Steps

1. Fetch the company page with a normal browser `User-Agent`.

2. **Prefer the structured block.** Parse `<script type="application/ld+json">` for the `Organization`
   object:

   | Field | Use |
   |---|---|
   | `sameAs` | **the official company website** — the highest-value field here |
   | `numberOfEmployees.value` | exact headcount |
   | `address` | full postal address |
   | `name`, `description`, `slogan`, `logo` | identity |

3. **Then the page fact list** (`<dt>`/`<dd>`), which carries what JSON-LD omits: **Website**,
   **Industry**, **Company size** (a band, e.g. "501–1,000 employees"), **Headquarters**, **Type**
   (e.g. "Privately Held"), **Specialties** — plus the follower count in page text.

   Where both give a size, keep both: the band is LinkedIn's own bucket, the JSON-LD figure is exact.

4. **`sameAs` is the handoff.** The official website is the input to finding the employer's real
   application system — its `/careers` page reveals the ATS and its slug, and that ATS's collection
   folder takes the application. Record it in the company's `company.yaml` alongside the ATS.

## Self-check (validate by readback)
Confirm the response was the company page (a non-empty `Organization` name) and not a 404, a sign-in
page, or a 429. If the JSON-LD block is absent, fall back to the `<dt>`/`<dd>` facts and say the
capture was partial. A 404 means the **slug is wrong**, not that the company is absent from LinkedIn —
re-derive it from a job link rather than trying variants.

## Limits (honest scope)
**Verified against a single company page**, so treat the exact field set as single-source until
confirmed elsewhere. Fields are employer-maintained and may be stale or absent.

**This is firmographics, not sentiment.** It gives no employee reviews, no ratings, no layoff or
stability signal, and no red flags — those need a separate web search. People data (for interviewer
research) is **auth-gated and out of scope here**.
