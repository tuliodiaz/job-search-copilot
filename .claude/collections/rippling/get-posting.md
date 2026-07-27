---
name: get-posting
kind: recipe
last_verified: 2026-07-26
verified_by: "GET https://ats.rippling.com/orderco/jobs/cb243ee4-b893-4700-a2e8-a288ba4d7ecd -> 200; __NEXT_DATA__ -> props.pageProps.apiData keyed department/jobBoard/jobPost/payRangeDetails/workLocations; jobPost.activeJobApplication.basicQuestions = 11 entries keyed oid/fieldType/title/required (SHORT_ANSWER, PRONOUN, PHONE_NUMBER, FILE), additionalQuestions = null; hasAIEvaluationsEnabled true, eeocQuestionnaireEnabled false. Also GET .../cars-and-bids-job-board/jobs/bf862d9c-06f6-4221-abaf-911afb094208 -> 200, same shape with description {company:217 chars, role:13608 chars} and additionalQuestions = 1 block of 2 LONG_ANSWER questions. Careers-page embed resolves the slug: order.co/careers carried data-job-board-id 'orderco' -> ats.rippling.com/orderco/jobs, page title 'Careers at Order.co', 12 open roles. basicQuestions vary by board: Order.co returned 11 including website_link; dialogue-en returned 10 without website_link and with linkedin_link required rather than optional; verified across two boards (orderco, dialogue-en) and four postings. Dialogue KNOCKOUT 'Are you eligible to work in Canada?' dataType select, strChoices ['Yes','No'], isRequired true. All confirmed live 2026-07-26."
requires: network access (HTTP GET); python3 or equivalent to parse embedded JSON; no client login
summary: Capture one Rippling role incl. its full description AND its application question schema
---

# Recipe: Rippling — get-posting

Capture a **single** Rippling role with both its description and its **application question schema**,
from one plain HTTP fetch.

## Preconditions
- `slug` — the board token (from `company.yaml`, or from the careers-page embed — see README).
- `job_id` — the role's **UUID** (from the posting URL `.../jobs/<uuid>`).

## Steps

1. Fetch the posting page verbatim:
   ```
   GET https://ats.rippling.com/<slug>/jobs/<job_id>
   ```
   Do **not** use the `/_next/data/<buildId>/…` route — `buildId` changes on every deploy (README).

2. Extract the JSON inside `<script id="__NEXT_DATA__" type="application/json">…</script>` and read
   `props.pageProps.apiData`, keyed `department`, `jobBoard`, `jobPost`, `payRangeDetails`,
   `workLocations`.

3. Extract from `apiData.jobPost`:
   - `description` — an object with **two** HTML blocks, `company` and `role`. Concatenate both
     (HTML → text) for `posting.md`; `role` alone drops the company blurb.
   - `name`, `uuid`, `url`, `companyName`, `createdOn`, `workLocations`, `department.name`,
     `employmentType` (`{label, id}`, e.g. `SALARIED_FT` / "Salaried, full-time"),
     `payRangeDetails`, `unlistedFromSearch`.
   - `eeocQuestionnaireEnabled` / `eeocQuestionnaireEnabledForJobPost` — whether the EEOC survey is
     part of this application.
   - **`hasAIEvaluationsEnabled`** — when true, the employer runs AI analysis on applications and says
     so on the form, with an opt-out link. Surface both to the client.

4. Extract the question schema from `jobPost.activeJobApplication` and **save it** (e.g. as
   `questions.json`). It has two parts, which render in this order:
   - `basicQuestions[]` — each `{oid, fieldType, title, required}`. **`oid` is the stable key**
     (`first_name`, `email`, `phone_number`, `resume`, …); nothing on the rendered page is stable, so
     map answers to `oid`. `fieldType` observed: `SHORT_ANSWER`, `PRONOUN`, `PHONE_NUMBER`, `FILE`.
   - `additionalQuestions` — employer-authored blocks, each `{id, name, form:{questions:[…]}}`, with
     each question carrying `title`, `questionType`, `dataType`, `isRequired`, `strChoices` /
     `intChoices`, `isMultiSelectEnabled`, `isOtherEnabled`, `uniqueKey`.
     **This may be `null` rather than an empty list** — guard before iterating.

     `questionType` values observed live: `LONG_ANSWER`, `SHORT_ANSWER`, `SINGLE_SELECT_DROPDOWN`,
     and **`KNOCKOUT`**. For the two choice types, `strChoices` holds the legal options.

5. **Flag `KNOCKOUT` questions to the eligibility check** — they auto-reject on a wrong answer, so
   ground them in `logistics.md` and resolve them **before the pursue gate**, never at submit time.

   Two kinds seen alongside them are the **client's own to answer** — mark them rather than plan to
   fill them: a **consent** question (`SINGLE_SELECT_DROPDOWN` whose `strChoices` is a single `['Yes']`)
   and a **compensation expectation** (`SHORT_ANSWER`, expected salary range).

   Note `isMultiSelectEnabled` was `true` on a plainly single-answer Yes/No knockout — do not read it
   as a reliable multi-select signal.

## Self-check (validate by readback)
Confirm the page contained a parseable `__NEXT_DATA__`, that `apiData.jobPost` exists with a non-empty
`description.role`, and that `basicQuestions` is a non-empty array whose entries carry an `oid` and a
`title`. A `null` `additionalQuestions` is normal; an empty `basicQuestions` means the capture failed.
If the fetch returns a Cloudflare challenge page, a 404, or a re-keyed shape → the recipe is **stale**:
stop, hand off, and flag it for promotion (fix + re-date).

**Record that this schema is not the whole form.** The live apply form can carry required controls
(e.g. a consent radio pair) present in neither list, so `/submit` reconciles against the live page. This
capture must not be presented to the client as the complete set of questions.

## Limits (honest scope)
**`basicQuestions` and their required flags vary by board** — never hard-code the set. `intChoices` has
not been seen populated, and the EEOC questionnaire was disabled on every posting checked, so its shape
in the payload is unknown.
