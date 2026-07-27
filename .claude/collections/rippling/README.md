# Platform: Rippling ATS

Platform brain and recipe index for applications hosted on **Rippling's ATS**. You don't *find* work on
Rippling — you arrive at it from a company's own careers page or from LinkedIn. This collection is what
you need once you know a role lives on Rippling: how to read the posting and its questions, and how to
fill the application form.

## Recognize

**From the company's careers page — the usual route.** The board is embedded, so the page host is the
company's own domain and tells you nothing. The fingerprint is in the page source, and it carries the
slug:

```html
<div id="rr-job-board" data-job-board-id="<slug>"></div>
<script src="https://static-assets.ripplingcdn.com/ats/embeds/job-board.v1.js" async></script>
```

`data-job-board-id` **is** the slug. One `curl` of the careers page plus a grep resolves it — no browser
needed, and no guessing slugs against `ats.rippling.com`. Record the slug in the company's `company.yaml`.

**From a URL:**
- Board: `ats.rippling.com/<slug>/jobs`
- Posting: `ats.rippling.com/<slug>/jobs/<uuid>` — the job id is a **UUID**, not a number
- Apply form: `ats.rippling.com/<slug>/jobs/<uuid>/apply?jobBoardSlug=<slug>&jobId=<uuid>&step=application`
- Locale-prefixed variants of every path exist (`/en-CA/`, `/en-GB/`, `/fr-FR/`, …)
- `jobPost.board.boardType` is `"RIPPLING"`

**Reading it — no REST API, but no scraping either.** There is no documented endpoint. The board is a
**Next.js** app, and every page embeds its full server payload in
`<script id="__NEXT_DATA__" type="application/json">`, at `props.pageProps.apiData` (React-Query caches
sit under `props.pageProps.dehydratedState.queries[]`). Fetch the page with plain `curl` and parse that
script: structured JSON, no browser. `get-posting` works this way.

## Surface to the client
- **`hasAIEvaluationsEnabled: true`** — the employer runs AI analysis on applications and says so on the
  form, with an opt-out link. Surface both the notice and the opt-out.
- **`KNOCKOUT` questions** are eligibility screeners that auto-reject on a wrong answer. Ground them in
  `logistics.md` and resolve them **before the pursue gate** — which is what `get-posting` captures them
  for.
- The apply form is **multi-step**: the URL carries `step=application` and the progress bar sits at 50%
  with everything filled. What follows the platform's `Apply` button has not been observed.

## Traps
- **Do not use the versioned data route.** `/_next/data/<buildId>/en-US/<slug>/jobs/<uuid>.json` returns
  equivalent `pageProps`, but `buildId` changes on every deploy, so a recorded URL silently breaks. Fetch
  the page and read `__NEXT_DATA__` instead.
- **Cloudflare.** The domain sits behind Cloudflare (`/cdn-cgi/challenge-platform` requests observed).
  Plain `curl` has worked; treat a sudden HTML challenge page as the failure mode.
- **Board pagination is `?page=N`, 0-indexed, `pageSize` 20.** `totalItems` / `totalPages` live only in
  the JSON; an unpaged read returns 20 items and looks complete. Enumerating a board is `scout-company`'s
  job, not this collection's — but this is the one rule that will silently cost you roles.

## Recipes
- `get-posting` — capture one role incl. its application question schema.
- `submit-application` — fill the apply form via **chrome-devtools-mcp**, then hand the tab to the client
  to submit.

There is no `find-jobs` here: enumerating a board is `scout-company`'s job. This collection exists for
reaching and filling one application.
