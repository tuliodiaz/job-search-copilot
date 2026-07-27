---
name: get-posting
kind: recipe
last_verified: 2026-07-27
verified_by: "iA Financial Group 'Principal Solution Designer' (posting ia.wd3.myworkdayjobs.com/Professional/job/Quebec-Quebec/Concepteur-trice--principal-e--logiciel_JR10027074-1) via curl 2026-07-27: GET https://ia.wd3.myworkdayjobs.com/wday/cxs/ia/Professional/job/Concepteur-trice--principal-e--logiciel_JR10027074-1 -> HTTP 200 with jobPostingInfo (title, jobDescription HTML, location 'Quebec, Quebec' + additionalLocations ['Montreal, Quebec'], timeType 'Full time', startDate, postedOn, country, questionnaireId, externalUrl); jobDescription stripped to posting.md; response re-scanned clean. Dropping the trailing '-1' suffix -> HTTP 502 'type mismatch in the API definition'. find-jobs and submit-application not exercised."
requires: curl (public HTTP); python3 (scan.py)
summary: Read one Workday posting's content from the cxs JSON API, for capture and the eligibility check
---

# Recipe: Workday — get-posting

Read a single Workday posting through the public `cxs` JSON API — no page scraping. Supplies the
posting content for capture and the fit/eligibility check. Application questions are **not** available
here (see README Traps); enumerate those at `/submit` via the candidate flow.

## Preconditions
- `host`, `tenant`, `site`, and the posting's `jobPath` — all derivable from the posting URL
  (README "Recognize"). `tenant` is the host's leftmost label; `site` is the first path segment;
  `jobPath` is everything after `/job/`.

## Steps
1. **Build the cxs URL:** `https://<host>/wday/cxs/<tenant>/<site>/job/<jobPath>`. Keep the full
   `_JR<id>[-<n>]` tail (dropping the `-<n>` suffix returns HTTP 502, not 404).
2. **GET it** with a normal browser `User-Agent`. On any non-200, **stop and record the failure** — do
   not invent posting content (a failed fetch never becomes a fact). A 502 almost always means the
   requisition suffix was dropped; re-check the path before concluding the API is down.
3. **Save the raw response** verbatim as `posting.raw.json` in the application folder, and **scan it**
   (`python3 .claude/scripts/scan.py posting.raw.json`) as the capture-time gate, per the ingesting
   discipline the caller enforces.
4. **Extract `posting.md`** from `jobPostingInfo`: strip the HTML from `jobDescription`, and record
   `title`, `location` + `additionalLocations`, `timeType`, `postedOn`, and `externalUrl`.

## Self-check (validate by readback)
Confirm the response parsed as JSON with a non-empty `jobPostingInfo.title` and `jobDescription`, and
that `posting.md` is non-empty. If the endpoint returned non-200 or an error object, the capture
failed — hand off and say so; never record an empty posting as "no content".

## Limits (honest scope)
Verified for the **single-posting** read only. `find-jobs` (board search) and `submit-application` are
not mapped for Workday — see README. Because the cxs JSON is content-only (no CSS), it cannot reveal
presentation-layer traps (hidden / low-contrast text); a clean scan here is not evidence the rendered
form is clean.
