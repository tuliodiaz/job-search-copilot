# Platform: Greenhouse

Platform brain and recipe index for Greenhouse-hosted job boards. Loaded with any Greenhouse recipe.

## Recognize
- Board URLs: `boards.greenhouse.io/<slug>` or `job-boards.greenhouse.io/<slug>`.
- A company may host the board on its own domain but still call `boards-api.greenhouse.io` — inspect
  network requests to find the real `<slug>` when the URL host is not a greenhouse domain.
- `<slug>` is the company's board token — record it in the company's `company.yaml`.

## Surface (public API — prefer over scraping)
Greenhouse exposes an unauthenticated JSON API; use it instead of the rendered board.
- `GET boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true` → every open role with its full
  description, in one response (no pagination).
- `GET boards-api.greenhouse.io/v1/boards/<slug>/jobs/<job_id>?questions=true` → one role plus its
  application `questions[]` and the separate `demographic_questions` object.

## Traps
- **`questions[]` is not the whole live form.** The voluntary EEO / demographic survey returns under a
  *separate* top-level key, `demographic_questions` — a capture that reads only `questions[]` misses
  it. And some controls (e.g. a phone-country picker) appear in neither the API nor
  `demographic_questions`. Reconcile the API against the live form before filling; "not in
  `questions[]`" never means "not on the form".
- **The posting may be an "apply-elsewhere" stub.** Some roles use the Greenhouse page as an advert
  only: the form's single required field is a dropdown confirming you applied elsewhere, and the page
  says so ("You do not need to submit this Greenhouse application"). Filling it accomplishes nothing.
  Check the application section for an outbound apply link before filling; if present, the real form is
  on another platform — resolve any shortener and follow that platform's own recipe. Surface the
  redirect to the client.
- **Selects are react-select comboboxes**, not `<select>` elements — no `<select>` to set, and the
  value lives in component state. The API returns each select's legal option labels in
  `fields[].values[]` — pick the option by label, don't approximate a string. See `submit-application`
  for how to drive them.
- Payloads may include AI-disclosure fields (`ai_disclaimer`, `include_ai_disclaimer`,
  `ai_opt_out_request_url`): a signal the employer discloses / screens for AI use — surface it to the
  client.
- Apply forms carry a **reCAPTCHA**; the client solves it.

## Recipes
- `find-jobs` — list + rank open roles via the public API.
- `get-posting` — capture one role incl. its application questions (`?questions=true`).
- `submit-application` — fill the apply form via **chrome-devtools-mcp**, then hand the tab to the
  client to submit. Falls back to assisted-manual (grounded answers + `docs/` as a checklist) when the
  MCP isn't available.
