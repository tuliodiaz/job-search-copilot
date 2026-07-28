# System: Indeed

The brain and recipe index for **Indeed's job search**. **Discovery only:** Indeed is an aggregator —
it is where roles are *found*, and the posting it shows is a copy. The authoritative posting is the
employer's own ATS, so a lead from here is confirmed there before it is trusted (see Traps).

## Recognize
- **Search:** `<cc>.indeed.com/jobs?q=&l=` — regional hosts (`ca.`, `www.`, `uk.`) select the country.
- **Job:** `<cc>.indeed.com/viewjob?jk=<jobkey>`; the `jobkey` is a 16-char hex id. A search URL also
  carries the currently previewed role as `&vjk=<jobkey>`.
- Card links of the form `/pagead/clk?...` are **sponsored-slot redirects**, not canonical job URLs.
- Record `ats: indeed` only for the *lead's source*. Indeed is not an employer's ATS — resolve the
  real one from the posting before capture.

## Surface — the rendered page's embedded JSON, via the browser

**There is no usable public API and no unauthenticated HTTP path.** Verified 2026-07-27: the retired
Publisher API (`api.indeed.com/ads/apisearch`) no longer resolves, `/rss` returns 404, and plain
`curl` to `ca.indeed.com/jobs` — with a browser `User-Agent` — returns **403 "Security Check -
Indeed.com"**, a Cloudflare challenge. Indeed is reached **only** through `web/browser-fetch`.

The search page embeds its full result set as JSON in an inline script:

```
window.mosaic.providerData["mosaic-provider-jobcards"]
  -> .metaData.mosaicProviderJobCardsModel
     .results[]      one object per role
     .pageNumber     1-based
     .loggedIn       false on the public surface
```

Read that object rather than the cards — the DOM carries sponsored-slot wrappers and truncated
labels, while `results[]` is clean and complete.

| Field | Meaning |
|---|---|
| `jobkey` | the id; canonical URL is `https://<cc>.indeed.com/viewjob?jk=<jobkey>` |
| `title` · `company` | as listed |
| `formattedLocation` | may be a city, a province, `Canada`, or `Remote` |
| `salarySnippet.text` | listed pay, or absent |
| `jobTypes` | e.g. `Full-time`, `Contract`; often `[]` |
| `formattedRelativeTime` | e.g. `6 days ago`, `30+ days ago` |
| `remoteWorkModel` | present only on some roles; absent ≠ on-site |

**Query parameters** (verified live): `q` keywords · `l` location · `radius` km · `start` absolute
offset · `sc=0kf%3Aattr(DSQF7)%3B` the **remote** facet (the UI's `Remote` chip; confirmed by the
chip showing active and every result reading `Remote`).

## Traps

- **⚠ Cloudflare, and it fingerprints the browser, not the pace.** A Chrome launched *by* automation
  is challenged almost immediately: Puppeteer's `--enable-automation` sets `navigator.webdriver`,
  shows the "controlled by automated test software" banner, and uses an empty throwaway profile. The
  browser MCP must therefore **attach to the client's own running Chrome**
  (`chrome-devtools-mcp --autoConnect`, with remote debugging enabled at
  `chrome://inspect/#remote-debugging`), where `navigator.webdriver` is `false`. Verified 2026-07-27:
  a launched instance was challenged on its second navigation; an attached one paged three times
  without a challenge. A challenge page (`Just a moment…` / `Security Check`) is an **anti-bot wall**
  — stop and hand it to the client, never try to defeat it.

- **⚠ Terms of service — a standing caveat.** Indeed's Terms prohibit automated access. These recipes
  read only the public, logged-out search surface and defeat no control, but that is narrower than
  "sanctioned". Treat this collection as **the client's standing decision to accept that risk**; the
  alternative that needs no Indeed request is reaching the same employer through its own careers page
  and that ATS's collection.

- **An aggregator's listing is a copy, and copies go stale or wrong.** Work mode, location and
  requirements are frequently mislabelled relative to the employer's own posting, and a role may
  already be closed. A lead from here is `recalled`; it becomes `verified` only when re-fetched from
  the real ATS.

- **`start` steps by 10 while a page returns 15.** Advancing by 15 can skip roles. Advance by 10 and
  dedupe.

- **Result ordering is not stable** between requests, so adjacent pages overlap unpredictably —
  measured overlap between `start=0` and `start=10` was a single role, not the five a fixed slice
  would give. Dedupe by `jobkey`; never infer "no new results" from a small overlap.

## Recipes
- `find-jobs` — keyword/location/remote search over the rendered search page; returns job leads.
- `get-posting` — **not yet mapped.** Lead: `viewjob?jk=<jobkey>` renders the description, but for an
  aggregator the authoritative capture is the employer's own ATS posting — resolve and capture there
  instead of adding this.
- `submit-application` — **deliberately absent.** Indeed Apply requires a signed-in Indeed account and
  submits on Indeed's behalf; applications go through the employer's ATS.
