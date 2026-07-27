# Platform: Workday

Enterprise ATS hosted on `myworkdayjobs.com`. Each employer is a Workday **tenant** with one or more
career **sites**; a posting is reachable both as a rendered React page and through Workday's public
`cxs` JSON API, which returns the role's content without scraping.

## Recognize
- Host: `<tenant>.wd<N>.myworkdayjobs.com` (e.g. `acme.wd3.myworkdayjobs.com`). The leftmost label is
  the **tenant**; `wd<N>` is the Workday data-center number.
- Posting URL: `https://<host>/<site>/job/<Location>/<slug>_<JR-id>` — the first path segment is the
  **site** (e.g. `Professional`, `External`); the last segment ends in the requisition id
  (`_JR<digits>[-<n>]`).
- Usually reached from an aggregator's "apply" link or the employer's own careers page. Record `host`,
  `tenant`, `site`, and the requisition id in `company.yaml` so later steps rebuild the same cxs URLs.

## Surface — the `cxs` JSON API
Workday exposes an unauthenticated read API that mirrors the public board, so reading a posting needs
no scraping of the rendered page.
- **One posting:** `GET https://<host>/wday/cxs/<tenant>/<site>/job/<jobPath>`, where `<jobPath>` is
  the posting URL's path after `/job/`. Returns `{ "jobPostingInfo": { ... } }` carrying (among
  others): `title`, `jobDescription` (HTML), `location` + `additionalLocations`, `timeType`
  (e.g. "Full time"), `startDate`, `postedOn`, `country`, `externalUrl`,
  `questionnaireId` / `secondaryQuestionnaireId`, `jobRequisitionLocation`.
- **Parse:** `jobDescription` is an HTML blob — strip tags for `posting.md`. It carries the
  requirements, any language demands, and listed comp/benefits.
- Send a normal browser `User-Agent`; a descriptive/empty UA still returns JSON but is more likely to
  be throttled.

## Traps
- **The requisition suffix is required.** The path must keep its full tail, including any `-<n>`
  (e.g. `..._JR10027074-1`). Dropping it returns **HTTP 502** ("type mismatch in the API definition"),
  not a 404 — easy to misread as the API being down.
- **The `<Location>` segment is not the identifier.** It can be omitted from the cxs `job/` path; the
  `<slug>_<JR-id>` tail is what resolves the posting.
- **The cxs JSON is content-only — no CSS.** Presentation-layer traps (hidden or low-contrast text)
  cannot appear in this response, so a clean scan of the JSON is not evidence the *rendered* form is
  clean. When trust matters (e.g. before `/submit`), scan the rendered page too.
- **Application questions need a candidate session.** `questionnaireId` is referenced but the
  questionnaire's fields are not returned by the anonymous cxs job endpoint — reading them requires the
  applicant flow (browser MCP + the client's Workday account).

## Recipes
- `get-posting` — read one posting's content from the cxs API (verified).
- `find-jobs` — **not yet mapped.** Workday board search is generally
  `POST https://<host>/wday/cxs/<tenant>/<site>/jobs` with a JSON facet/pagination body; treat this as a
  lead to verify live, **not** a fact. Never invent the request shape — confirm it before use.
- `submit-application` — **not yet mapped.** Workday applications use a candidate-account flow
  (login + multi-step form), like Rippling; no recipe exists yet.
