# System: LinkedIn

The brain and recipe index for LinkedIn's **public guest surface** — the logged-out job board and
company pages. **Discovery only:** LinkedIn is where roles are *found*, never where they are
*submitted*. There is deliberately no `submit-application` recipe here (see Traps → "No apply path").

## Recognize
- **Job:** `linkedin.com/jobs/view/<id>` (often `<country>.linkedin.com/jobs/view/<slug>-<id>` — the
  trailing digits are the id).
- **Company:** `linkedin.com/company/<slug>`.
- Regional host prefixes (`ca.`, `uk.`, `www.`) are interchangeable for reading.

## Surface — the public guest API, no login

Base: `https://www.linkedin.com/jobs-guest/jobs/api`

| Recipe | Endpoint |
|---|---|
| `find-jobs` | `…/seeMoreJobPostings/search?keywords=&location=&start=N` |
| `get-posting` | `…/jobPosting/<id>` |
| `get-company` | `linkedin.com/company/<slug>` (an ordinary page, not the guest API) |

These endpoints are **undocumented and unversioned** — they power the logged-out widgets and can
change without notice. Send a normal browser `User-Agent`. They are **rate-limited and return 429**
when pushed, so space requests out and cap how many you make in a run.

The official LinkedIn APIs (Talent / Marketing Solutions) are **OAuth partner-gated** and offer no
open job search. Nothing here uses them, and nothing here touches the authenticated app.

## Traps (platform-wide)

- **⚠ Terms of service — a standing caveat, not a footnote.** Unlike a documented public API,
  **LinkedIn's User Agreement prohibits automated access**, and LinkedIn has litigated over scraping.
  Every recipe here reads only public, logged-out pages and never bypasses an auth wall or anti-bot
  control — but that is a narrower claim than "sanctioned." Treat this collection as **the client's
  standing decision to accept that risk**; if the client has not made that call, say so and offer the
  alternative: reach the same roles through the employer's own careers page and its ATS collection,
  which needs no LinkedIn request at all.

- **No apply path from here.** The Apply control on a public job page carries **no destination** — it
  opens a sign-in modal (the word *offsite* in the modal confirms the application lives elsewhere),
  and the real URL is **not in the public HTML**; it requires a logged-in session. Easy Apply likewise
  needs auth. **So the handoff is the point:** LinkedIn gives the company → `get-company`'s `sameAs`
  gives the official website → the employer's `/careers` page reveals the ATS and its slug → that
  ATS's collection folder takes the application.

- **Rate limiting.** Sustained requests return **429**. A sign-in page or 429 in place of expected
  markup means back off, not parse harder.

## Recipes
- `find-jobs` — keyword/location/work-type search over the guest endpoint; returns job leads to rank.
- `get-posting` — one role's title, company and full description (the advert only — no apply form).
- `get-company` — a company's public firmographics for company research.
