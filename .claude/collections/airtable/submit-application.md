---
name: submit-application
kind: recipe
last_verified: 2026-07-26
verified_by: "Anthropic Fellows / Constellation form (airtable.com/appCHLjgoTUCJMLct/pagUhpiBE5KxoU3lX/form) via chrome-devtools-mcp: cleared, then filled 33/33 text fields (17 plain + 16 contenteditable), 7/7 radio groups and 3 multi-selects — 0 read-back mismatches, 0 fields flagged invalid, confirmed by screenshots at three points in the form. fill/fill_form measured as unsafe on the same form: fill_form on 15 fields landed 8 and dropped 1–2 leading characters from 6 of those (placeholder@… → aceholder@…); per-field fill produced no-ops and one append instead of a replace; every call returned success. Submit deliberately not exercised. Confirmed live 2026-07-26."
requires: chrome-devtools-mcp (browser MCP) connected
summary: Fill an Airtable application form and hand off to the client to submit
---

# Recipe: Airtable — submit-application

Fill an Airtable-hosted application form for one role, then hand the live tab to the client to submit.
Runs **explore → answer → fill → validate → hand off**.

## Preconditions
- The role is a captured application past the pursue gate, with rendered `docs/`.
- **chrome-devtools-mcp is available.** If it is not, fall back to **assisted-manual**: give the client
  the grounded answers plus the `docs/` files as a fill-in checklist for their own browser. (Setup:
  https://github.com/ChromeDevTools/chrome-devtools-mcp.)
- The form's **questions are already captured** (via `get-form` → `questions.json`). They are what the
  eligibility check ran against at the pursue gate; do not re-derive them here.

## Steps

1. **Open and clear the consent modal.** Load the form in a **headed, client-visible** browser; dismiss
   the Transcend cookie dialog (README Traps) before anything else.

2. **Locate the live fields and reconcile them against `questions.json`.** Enumerate and classify per
   README "Surface" (visible-only filter; plain vs rich). Every live field should match a captured
   question. A live field with no captured question means the form changed since capture: **stop and
   flag `get-form` stale** rather than filling something the eligibility check never saw.

3. **Answer — grounded, once.** Resolve each answer from the vault: identity/experience →
   `profile/cv.md` / `narrative.md`; work authorization, availability, employment type, start date →
   `logistics.md`; résumé → the rendered file in `docs/`.

4. **References are claims about a third party.** These forms commonly ask for three referees with
   name, email, title, employer, and Google Scholar. The **name, email, and the client's relationship
   to them can only come from the client** — they are not derivable from a CV. The referee's public
   details are **world-claims**: verify each from a primary source and save it under `_sources/`, or
   leave the field for the client. Note for the client that these forms often state referees may be
   contacted **without prior notice**.

5. **Fill, using the per-type writers in the README "Surface" field-type table** (plain via the
   prototype `value` setter + `input`/`change`; rich via `execCommand('insertText')`; options via
   `.click()`; file dropzone → hand to the client). **Do not use the MCP's `fill` / `fill_form`**
   (README Traps).

6. **Validate by readback — and by screenshot.** Read back **the same element you wrote** (`innerText`
   for rich fields, `value` for plain); a reader that queries only `input`/`textarea` cannot see rich
   fields at all, and will mistake "invisible to my selector" for "empty" — or report a perfect match
   while writing into a hidden mirror. Respect the post-click re-render lag (README Traps) before
   reading control state. Then **screenshot the filled form** — it is the only check the other two
   cannot fool. If any required field could not be located or filled, **stop, hand off, and flag**.

7. **Hand off.** Leave the filled form in the client's browser for them to review and submit. Tell them
   plainly which fields you deliberately left blank; those always include the **file upload**, any
   **attestation** (the client is the one attesting — e.g. "confirm your understanding of our AI
   policy"), and any **statement of the client's own intent** (e.g. "how likely are you to accept an
   offer, with a % estimate" — draft only from what they tell you, never invent the number). On the
   client's confirmation of submission, advance `status.yaml` → `applied`.

## Self-check (validate by readback)
Every required field non-empty and matching its grounded source; every required control answered; and
a **screenshot** confirming the form is visibly populated. If the readback passes but the screenshot
shows empty fields, you wrote to the mirrors — re-classify and rewrite. Never hand off on a readback
alone.

## Limits (honest scope)
Verified as far as **rendered form state**. That the values reach Airtable's submit payload is not
confirmed, because confirming it means submitting a real application — treat that last hop as proven
only after a real application goes through. **File upload is untested**; `chrome-devtools-mcp` exposes
`upload_file`, so verify it before relying on it and be ready to hand the upload to the client.
