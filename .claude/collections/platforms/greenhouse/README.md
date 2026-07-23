# Platform: Greenhouse

The platform "brain" and recipe index for Greenhouse-hosted job boards.

## How to recognize it (key)
- Board URLs: `boards.greenhouse.io/<slug>` or `job-boards.greenhouse.io/<slug>`.
- Embedded boards call `boards-api.greenhouse.io/v1/boards/<slug>/jobs`.
- The `<slug>` is the company's board token — record it in the company's `company.yaml`.
  (Example confirmed live 2026-07-23: Affirm → slug `affirm`.)

## Public API (preferred over scraping)
- `GET https://boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true` → all open roles, each
  with its full description, in one response.

## Recipes here
- `find-jobs` — list + rank open roles via the public API. **Verified 2026-07-23.**
- `submit-application` — **not yet built.** A submit recipe is only committed once it has been
  verified live end-to-end (fields mapped, self-check passing). Until then, `/submit` for a
  Greenhouse role falls back to handing the live form to the client.

## Gotchas
- Some companies host the board on their own domain but still call `boards-api.greenhouse.io` — check
  network requests to find the real slug.
- Payloads may include AI-disclosure fields (`ai_disclaimer`, `ai_opt_out_request_url`): treat as a
  signal the employer discloses/screens for AI use, and surface it to the client.
