---
name: get-posting
kind: recipe
last_verified: 2026-07-26
verified_by: "GET https://boards-api.greenhouse.io/v1/boards/affirm/jobs/7793217003?questions=true -> 200 JSON; 'content' (9005 chars) + 'questions' array (20), each with label/required/fields[]; fields[] keyed name/type/values with types input_text, input_file, textarea, multi_value_single_select; select values[] keyed {label, value} (e.g. Pronouns -> 6 labels matching the rendered options exactly); separate top-level 'demographic_questions' object (header/description/questions[], 2 optional questions). Confirmed live 2026-07-26. Prior verification 2026-07-24 on affirm/7710978003 (25 questions incl. sponsorship + residence)."
requires: network access (HTTP GET); no client login
summary: Capture one Greenhouse role incl. its full description AND its application questions
---

# Recipe: Greenhouse — get-posting

Capture a **single** Greenhouse role with both its description and the **actual application form
questions**, in one call. This is the richer path `capture-posting` should prefer for a Greenhouse
role: the questions (e.g. work-authorization/sponsorship, residence) feed the fit-assessor's
eligibility check now and the `/submit` flow later.

## Preconditions
- `slug` — the board token.
- `job_id` — the numeric role id (from `find-jobs`, or the `absolute_url` `.../jobs/<id>`).

## Steps
1. Fetch, verbatim:
   ```
   GET https://boards-api.greenhouse.io/v1/boards/<slug>/jobs/<job_id>?questions=true
   ```
2. Extract:
   - `content` (HTML → text) — the role description, for `posting.md`.
   - `questions[]` — each with `label`, `required`, and `fields[]`. **Save these** (e.g. as
     `questions.json` in the application folder) — they carry the work-authorization/sponsorship and
     residence questions. Each entry in `fields[]` has `name`, `type`, and `values`:
     - `type` observed on a real posting: `input_text`, `input_file`, `textarea`,
       `multi_value_single_select`.
     - For a select, `values[]` is a list of `{label, value}` — the field's **legal options**. Save
       them: `/submit` picks the option by `label` instead of guessing or approximating an option
       string.
   - `demographic_questions` — a **separate top-level object** (`header`, `description`,
     `questions[]`), the voluntary EEO survey. It is **not** inside `questions[]`, so a capture that
     reads only `questions[]` silently misses it. Save it, but note it is the client's own to answer.
   - `location.name`, `title`, `absolute_url`, `updated_at`.

## Self-check (validate by readback)
Confirm the response is JSON with a non-empty `content` field and a `questions` array whose entries
carry a `label`. If either is missing, the endpoint returned HTML/404/a re-keyed shape → the recipe
is **stale**: stop, fall back to `find-jobs`' content (no questions) or hand off, and flag for
promotion (fix + re-date).

**A passing self-check does not mean you have the whole form.** `questions[]` plus
`demographic_questions` is what the API returns; the rendered page can still carry a control that
appears in neither (e.g. a phone-country picker). Treat the capture as the API's account of the form,
not the form itself, and reconcile against the live page at `/submit`.
