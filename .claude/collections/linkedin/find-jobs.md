---
name: find-jobs
kind: recipe
last_verified: 2026-07-26
verified_by: "GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=software%20engineer&location=Canada&start=N -> 200 text/html (~29KB), 10 <li> cards per response with data-entity-urn ids, h3 title, h4 subtitle + company href, .job-search-card__location. Page size measured as 10 with start as an absolute offset: start=0 -> 10 ids; start=10 -> 10, overlap 1; start=25 -> 10, overlap 0. Work-type facet confirmed honored: f_WT=1 overlapped only 2/10 with the unfaceted query. Company-name search disproved: keywords=Order.co returned Synthesia, ACV Auctions, The Farmer's Dog. Confirmed live 2026-07-26."
requires: network access (HTTP GET) with a browser User-Agent; an HTML parser; no client login
summary: Search LinkedIn's public guest job endpoint by keyword, location and work type
---

# Recipe: LinkedIn — find-jobs

Search the **public guest** job endpoint — the one behind the logged-out board — and return job leads.
No login. Undocumented, rate-limited, and under LinkedIn's standing ToS caveat (README → Surface,
Traps).

## Preconditions
- `keywords` — free text (role, skill, or company name — see the company caveat below).
- `location` *(optional)* — a **region** string, e.g. `Canada`, `United States`.
- `remote` / `onsite` *(optional)* — a work-type **facet**, not a location.

## Steps

1. **Split "remote" out of the location.** LinkedIn treats it as a work-type facet and **silently
   ignores** it inside `location`. Set `f_WT=2` for remote or `f_WT=1` for on-site, and pass only the
   remaining words as `location`.

2. **Page in steps of 10.** Fetch:
   ```
   GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
       ?keywords=<kw>&location=<region>&start=<N>[&f_WT=1|2]
   ```
   with a normal browser `User-Agent`. Each response is an HTML fragment of **10** `<li>` cards, and
   `start` is an **absolute offset** — so advance `start` by **10**. Any other step size skips roles
   silently. Continue until a page yields no new ids, then stop.

3. **Be polite and finite.** Pause between pages, and cap the run (a page cap, and a cap on detail
   fetches). The endpoint returns **429** when pushed.

4. **Parse each card.** Take the id from `data-entity-urn` (fall back to the trailing digits of the
   `/jobs/view/…` href). A card with **no id is not a real card** — skip it rather than emitting a
   placeholder. Then:

   | Field | Source |
   |---|---|
   | `title` | `h3.base-search-card__title` |
   | `company` | `h4.base-search-card__subtitle` |
   | `companyUrl` | that subtitle's `<a href>` → `linkedin.com/company/<slug>`, the input to `get-company` |
   | `location` | `.job-search-card__location` |
   | `updatedAt` | `<time datetime>` |
   | `url` | `https://www.linkedin.com/jobs/view/<id>` |

   A missing field stays empty.

5. **Scoping to one company is a client-side filter.** There is no name→id lookup, and `keywords`
   matches *job text*, not employer — searching a company name returns unrelated employers. Filter the
   parsed cards by `company`, and tell the client the result is best-effort rather than that
   company's board.

6. Return the leads. Descriptions are **not** in the cards — fetch them per role with `get-posting`,
   and only for the shortlist, to bound request volume.

## Self-check (validate by readback)
Confirm the first request returned HTML containing at least one `<li>` with a `data-entity-urn` and a
non-empty title. **If page 0 fails, stop and report it** — you have nothing real. A *later* page
failing is different: keep what you have and say where you stopped. If the response is a sign-in page,
a 429, or the card classes have been renamed, the recipe is **stale** — flag it for promotion rather
than parsing harder.

## Limits (honest scope)
Verified on one query shape. Result ordering shifts between calls, so
a small overlap between adjacent pages is normal — dedupe by id. The 10-per-page figure is measured,
not documented, and could change with the endpoint.

`f_WT=2` returned the same 10 ids as the unfaceted query for the verification query; the facet's
effect was proven via `f_WT=1`. Don't read an unchanged result set as "the facet was ignored".
