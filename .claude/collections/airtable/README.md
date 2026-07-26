# Platform: Airtable Forms

The platform "brain" and recipe index for **Airtable-hosted application forms** — used when an
employer, or its recruiting partner, runs the application outside their ATS.

## How to recognize it (key)
- Form URLs: `airtable.com/app<APP_ID>/pag<PAGE_ID>/form`.
- Usually reached by **redirect from an ATS posting**, often behind a shortener. The ATS listing is
  the advert; the Airtable page is the actual application. (Example confirmed live 2026-07-26:
  Anthropic's Fellows Program posting on Greenhouse routes to a Constellation-run Airtable form.)
- Record the form URL in the company's `company.yaml` alongside the posting URL — they differ, and the
  posting is authoritative about which one takes applications.

## Public API
No public endpoint for a form's questions is known — unlike Greenhouse, nothing here was reachable by
plain HTTP. The field list is read from the rendered page instead, so everything needs the browser MCP
and there is no schema to reconcile the live form against.

There is no board to enumerate either: an Airtable form URL is **one form for one role**, so this
platform has no `find-jobs` counterpart.

## Recipes here
- `get-form` — read the form's application questions from the rendered page, for the eligibility check
  and later `/submit`. **Verified 2026-07-26.**
- `submit-application` — fill the form, verify visually, hand the tab to the client to submit.
  **Verified 2026-07-26.**

The posting and the form are usually on **different platforms**: the role description comes from the
ATS it was advertised on, and only the questions come from here.

## Gotchas
- **Two field types, and they need different writers.** Short answers are real `textarea`/`input`
  elements. Long answers are `contenteditable="plaintext-only"` divs, each shadowed by a **hidden
  mirror `<input>`**. Writing to the mirror succeeds in a DOM read-back and does nothing on screen —
  on the form verified below, 16 of 33 text fields were of this kind.
- The MCP's `fill` / `fill_form` are **unsafe here** — they corrupt and skip fields while reporting
  success. See `submit-application`.
- A **Transcend cookie-consent modal** blocks all interaction on first load.
- Radio groups carry **no `aria-label`**; their question text is only reachable via `aria-labelledby`.
- Controls report their **old** state if read immediately after a click — the re-render has not
  happened yet.
- `Clear form` opens a separate confirm dialog ("This can't be undone").
- **`Submit` sits directly beside `Clear form` in the DOM.** Match button text exactly, and guard
  against matching Submit, before clicking anything in that row.
- Résumé fields are **file dropzones**, not text inputs.
- These forms often ask for **references** — a third party's name, email, title, and public profiles.
  Those are world-claims about a real person, not client-claims; see `submit-application`.
