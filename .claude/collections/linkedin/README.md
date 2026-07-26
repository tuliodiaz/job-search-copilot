# System: LinkedIn

The "brain" and recipe index for LinkedIn's **public guest surface** — the logged-out job board and
company pages.

LinkedIn is **discovery only**. It is the mirror image of an ATS: it is where roles are *found*, never
where they are *submitted*. There is deliberately **no `submit-application` here** — see "You cannot
apply from here" below.

## How to recognize it (key)
- Job: `linkedin.com/jobs/view/<id>` (often `<country>.linkedin.com/jobs/view/<slug>-<id>` — the
  trailing digits are the id)
- Company: `linkedin.com/company/<slug>`
- Regional host prefixes (`ca.`, `uk.`, `www.`) are interchangeable for reading.

## Access — the public guest surface, no login

Base: `https://www.linkedin.com/jobs-guest/jobs/api`

| Recipe | Endpoint |
|---|---|
| `find-jobs` | `…/seeMoreJobPostings/search?keywords=&location=&start=N` |
| `get-posting` | `…/jobPosting/<id>` |
| `get-company` | `linkedin.com/company/<slug>` (an ordinary page, not the guest API) |

These are **undocumented and unversioned** — they power the logged-out widgets, and they can change
without notice. Send a normal browser `User-Agent`; requests are rate-limited and return **429** when
pushed, so space them out and cap how many you make in a run.

**The official LinkedIn APIs (Talent / Marketing Solutions) are OAuth partner-gated** and do not offer
open job search. Nothing here uses them, and nothing here touches the authenticated app.

## ⚠ Terms of service — a standing caveat, not a footnote

Unlike Greenhouse's documented public API, **LinkedIn's User Agreement prohibits automated access**,
and LinkedIn has litigated over scraping. Every recipe here reads only public, logged-out pages and
never bypasses an auth wall or anti-bot control — but that is a narrower claim than "sanctioned".

Treat this collection as **the client's standing decision to accept that risk**. If the client has not
made that call, say so and offer the alternative: reach the same roles through the employer's own
careers page and its ATS collection, which needs no LinkedIn request at all.

## You cannot apply from here

Verified 2026-07-26: the Apply control on a public job page carries **no destination**. It opens a
sign-in modal (`public_jobs_apply-link-offsite_contextual-sign-in-modal`). The word *offsite* confirms
the application lives elsewhere, but **the URL is not in the public HTML** — it requires a logged-in
session. Easy Apply likewise needs auth.

**So the handoff is the point.** LinkedIn gives the company; `get-company`'s `sameAs` gives the
official website; the employer's careers page gives the ATS and its slug; that ATS's collection folder
takes the application. Confirmed end to end 2026-07-26: LinkedIn job `4444374252` → Dialogue →
`dialogue.co/en/careers` → `data-job-board-id="dialogue-en"` → `collections/rippling/`.

## Recipes here
- `find-jobs` — keyword/location search over the guest endpoint. **Verified 2026-07-26.**
- `get-posting` — one role's title, company and full description. **Verified 2026-07-26.**
- `get-company` — firmographics for `company-recon`'s signals/deep research. **Verified 2026-07-26.**

## Gotchas
- **The guest search returns 10 results per call, not 25**, and `start` is an **absolute offset**.
  Measured: `start=0` → 10 ids; `start=10` → 10, overlap 1; `start=25` → 10, overlap **0**. Stepping
  `start` by anything other than 10 silently skips roles while still looking like a full run.
- **"Remote" is a facet, not a location.** Passing `remote` in `location` is silently ignored; use
  `f_WT=2` (remote) or `f_WT=1` (on-site). Verified honored — `f_WT=1` shifted 8 of 10 results.
- **There is no company-name lookup.** `keywords` matches *job text*, not employer: searching
  `Order.co` returned Synthesia, ACV Auctions and The Farmer's Dog. Company scoping can only be a
  client-side filter over each card's employer.
- **A company slug cannot be guessed.** `linkedin.com/company/orderco` → **404**; Dialogue's is
  `dialogue-md`, not `dialogue`. Read the company URL off a job card or job page instead.
- The full `/jobs/view/<id>` page carries **no JSON-LD** and is ~4× heavier than the guest
  `jobPosting/<id>` endpoint. Prefer the latter.
