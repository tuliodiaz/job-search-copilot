---
name: find-jobs
kind: recipe
last_verified: 2026-07-27
verified_by: "Browser MCP attached to the client's own Chrome (chrome-devtools-mcp --autoConnect; navigator.webdriver=false). GET ca.indeed.com/jobs?q=software&l=Montréal, QC&radius=25 -> 15 results from window.mosaic.providerData['mosaic-provider-jobcards'].metaData.mosaicProviderJobCardsModel, pageNumber 1, loggedIn false. start=10 -> pageNumber 2, 15 results, overlap 1 with page 1; start=20 -> pageNumber 3, 15 results, overlap 1. Fields read live: jobkey/title/company/formattedLocation/salarySnippet.text/jobTypes/formattedRelativeTime. Remote facet sc=0kf%3Aattr(DSQF7)%3B confirmed on q=software architect&l=Canada (Remote chip active, all results 'Remote'). Plain curl to the same URL -> 403 'Security Check - Indeed.com' (Cloudflare); api.indeed.com/ads/apisearch does not resolve; /rss -> 404. Confirmed live 2026-07-27."
requires: chrome-devtools-mcp ATTACHED to the client's own running Chrome (--autoConnect); no client login
summary: Search Indeed by keyword, location and remote facet, reading the search page's embedded result JSON
---

# Recipe: Indeed — find-jobs

Search Indeed's public, logged-out job search and return job leads. There is **no API path**: plain
HTTP is Cloudflare-blocked, so this runs in the browser via `web/browser-fetch`, and the browser must
be the client's own (README → Traps).

## Preconditions
- `keywords` — free text (role or skill).
- `location` *(optional)* — a city/province/country string, e.g. `Montréal, QC` or `Canada`.
- `radius` *(optional)* — km around `location`.
- `remote` *(optional)* — a **facet**, not a location.
- The browser MCP is **attached** to the client's running Chrome. If it launched its own, stop and say
  so — a launched instance is challenged almost at once, and retrying wastes the session.

## Steps

1. **Confirm the browser is attached, not launched.** Evaluate `navigator.webdriver`; `true` means a
   launched instance — stop and tell the client how to reattach rather than proceeding.

2. **Build the URL** against the country host (`ca.` for Canada):
   ```
   https://ca.indeed.com/jobs?q=<keywords>&l=<location>[&radius=<km>][&start=<N>]
                              [&sc=0kf%3Aattr(DSQF7)%3B]
   ```
   Put "remote" in `sc`, never in `l` — as a location string it silently narrows to places named
   "remote" instead of applying the facet.

3. **Navigate, then check for the wall before reading anything.** A document title of
   `Just a moment…` or `Security Check` is a Cloudflare challenge: **stop, report it, hand the tab to
   the client.** Never attempt to solve or evade it.

4. **Read the embedded result JSON**, not the cards:
   ```js
   const s = [...document.querySelectorAll('script')].map(x => x.textContent || '');
   const blob = s.find(t => t.includes('window.mosaic.providerData')
                         && t.includes('mosaic-provider-jobcards'));
   const m = blob.match(
     /window\.mosaic\.providerData\["mosaic-provider-jobcards"\]\s*=\s*(\{[\s\S]*?\});\s*$/m);
   const md = JSON.parse(m[1]).metaData.mosaicProviderJobCardsModel;   // md.results, md.pageNumber
   ```
   The regex must be **non-greedy and end-anchored** (`*?` with `;\s*$/m`); a greedy match runs past
   the assignment and fails to parse.

5. **Map each result:**

   | Field | Source |
   |---|---|
   | `id` | `jobkey` |
   | `url` | `https://ca.indeed.com/viewjob?jk=<jobkey>` — build it; card hrefs are `/pagead/clk` redirects |
   | `title` · `company` | `title` · `company` |
   | `location` | `formattedLocation` |
   | `salary` | `salarySnippet.text` (often absent) |
   | `employment_type` | `jobTypes` (often `[]`) |
   | `posted` | `formattedRelativeTime` |

   A missing field stays empty — never infer one. In particular, an absent `remoteWorkModel` does
   **not** mean on-site.

6. **Page in steps of 10.** `start` is an absolute offset; `start=10` reports `pageNumber` 2 and
   `start=20` reports 3. A page returns **15**, so pages overlap — dedupe by `jobkey` and keep
   advancing by 10, because a step of 15 can skip roles. Stop when a page yields no new ids.

7. **Be polite and finite.** Pause between navigations and cap the run (a page cap, and a cap on
   detail fetches). This surface is anti-bot-protected; pace is the second line of defence after the
   attached browser.

8. **Return the leads**, each marked as coming from an aggregator listing. Descriptions are not in
   the results, and Indeed's copy of a posting is not authoritative — the employer's own ATS is.

## Self-check (validate by readback)
Confirm the first navigation produced a page whose title is **not** a challenge, that the mosaic blob
parsed, and that `results` is a non-empty array whose first entry has a 16-char hex `jobkey` and a
non-empty `title`. **If page 1 fails, stop and report it** — you have nothing real. A *later* page
failing is different: keep what you have and say where you stopped. If the blob is missing or the
provider key was renamed, the recipe is **stale** — flag it for promotion rather than falling back to
scraping cards.

## Limits (honest scope)
Verified on two query shapes against the `ca.` host, to three pages. The 15-per-page figure and the
`start`-steps-by-10 behaviour are **measured, not documented**, and can change.

`sc=0kf%3Aattr(DSQF7)%3B` was confirmed as the remote facet by the active `Remote` chip and by every
returned role reading `Remote`; other `0kf` attribute tokens (pay, job type, date posted) were **not**
mapped. Result ordering shifts between requests, so a small overlap between adjacent pages is normal
and is not evidence of exhaustion.

Not verified: behaviour on other country hosts, sustained paging beyond three pages, and whether a
challenge appears under heavier use. `get-posting` is not mapped here on purpose — capture the
authoritative posting from the employer's ATS.
