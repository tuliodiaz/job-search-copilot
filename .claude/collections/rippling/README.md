# Platform: Rippling ATS

The platform "brain" and recipe index for job applications hosted on **Rippling's ATS**.

Rippling is not somewhere you *find* work — you arrive at it from a company's own careers page or from
LinkedIn. This collection is what you need **once you know a role lives on Rippling**: how to read the
posting and its questions, and how to fill the application form.

## How to recognize it (key)

**From the company's careers page — the usual route.** The board is embedded, so the page host is the
company's own domain and tells you nothing. The fingerprint is in the page source, and it carries the
slug:

```html
<div id="rr-job-board" data-job-board-id="orderco"></div>
<script src="https://static-assets.ripplingcdn.com/ats/embeds/job-board.v1.js" async></script>
```

`data-job-board-id` **is** the slug. One `curl` of the careers page plus a grep resolves it — no
browser needed, and no guessing slugs against `ats.rippling.com`. (Confirmed live 2026-07-26:
`order.co/careers` → slug `orderco` → `ats.rippling.com/orderco/jobs`, "Careers at Order.co", 12 open
roles.)

**From a URL:**
- Board: `ats.rippling.com/<slug>/jobs`
- Posting: `ats.rippling.com/<slug>/jobs/<uuid>` — the job id is a **UUID**, not a number
- Apply form: `ats.rippling.com/<slug>/jobs/<uuid>/apply?jobBoardSlug=<slug>&jobId=<uuid>&step=application`
- Locale-prefixed variants of every path exist (`/en-CA/`, `/en-GB/`, `/fr-FR/`, …)
- `jobPost.board.boardType` is `"RIPPLING"`

Record the slug in the company's `company.yaml`.

## No REST API — but no scraping either

There is no documented endpoint. The board is a **Next.js app**, and every page embeds its full server
payload in `<script id="__NEXT_DATA__" type="application/json">`. Fetch the page with plain `curl` and
parse that script: structured JSON, no browser. `get-posting` works this way.

The payload is at `props.pageProps.apiData`; React-Query caches sit under
`props.pageProps.dehydratedState.queries[]`.

**Do not use the versioned data route.** `/_next/data/<buildId>/en-US/<slug>/jobs/<uuid>.json` returns
equivalent `pageProps`, but `buildId` changes on every deploy, so a recorded URL silently breaks.

## Recipes here
- `get-posting` — capture one role incl. its application question schema. **Verified 2026-07-26.**
- `submit-application` — fill the apply form via **chrome-devtools-mcp**, then hand the tab to the
  client to submit. **Verified 2026-07-26** — filled end to end until the platform's own `Apply`
  button unlocked; see its *Limits*.

There is no `find-jobs` here: enumerating a board is `scout-company`'s job, and this collection exists
for reaching and filling an application. If you do enumerate a board, note the pagination rule below —
it is the one thing that will silently cost you roles.

## Gotchas

- **Board pagination is `?page=N`, 0-indexed**, `pageSize` 20. Verified on `dialogue-en`
  (`totalItems: 37`, `totalPages: 2`): `page=0` → 20 items, `page=1` → 17, `page=2` → empty. Reading
  the board page without paging returns 20 and looks complete — `totalItems` is only in the JSON.
- **`additionalQuestions` can be `null`, not `[]`.** Confirmed on Order.co's Support Specialist.
  Guard for it before iterating.
- **The API schema is not the whole form.** An SMS-consent radio pair appearing in neither
  `basicQuestions` nor `additionalQuestions`, and carrying no `*`, was present on **both** boards
  checked; on Order.co it kept `Apply` blocked until answered. Always reconcile against the live page.
- **`KNOCKOUT` questions are eligibility screeners that auto-reject.** Confirmed on Dialogue: *"Are you
  eligible to work in Canada?"*, required, `['Yes','No']`. They must be grounded in `logistics.md` and
  resolved **before the pursue gate** — which is what `get-posting` is for.
- **The question set differs per board.** Order.co returned 11 `basicQuestions` including
  `website_link`; Dialogue returned 10 without it, and made `linkedin_link` required rather than
  optional. Never hard-code the field list or its required flags.
- **`hasAIEvaluationsEnabled: true` is rendered to the candidate** as "…uses AI to analyze
  applications. To learn more or opt out click here". Surface it — and the opt-out — to the client.
- The apply form is **multi-step**: the URL carries `step=application` and the progress bar sits at 50%
  with everything filled. What follows `Apply` has not been observed.
- The domain sits behind **Cloudflare** (`/cdn-cgi/challenge-platform` requests observed). Plain `curl`
  worked on 2026-07-26; treat a sudden HTML challenge page as the failure mode.
- `jobPost.description` is split into **two** HTML blocks, `company` and `role` — concatenate both, or
  the company blurb is lost.
