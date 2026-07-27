---
name: get-form
kind: recipe
last_verified: 2026-07-26
verified_by: "Anthropic Fellows / Constellation form (airtable.com/appCHLjgoTUCJMLct/pagUhpiBE5KxoU3lX/form) via chrome-devtools-mcp: enumerated 33 visible text fields (17 plain input/textarea + 16 contenteditable) while excluding 16 hidden mirror inputs, 7 radiogroups (options read from [role=radio]), and 3 multi-select listboxes; labels resolved by document order for all 33 and confirmed against a screenshot. Confirmed live 2026-07-26. Recognition: the source posting was Anthropic's Fellows Program on Greenhouse, which redirects to this Constellation-run Airtable form (confirmed live 2026-07-26). Ancestor-innerText label heuristics were observed to mislabel — four consecutive distinct fields all reporting 'Reference 1: Name' (observed 2026-07-26) — which is why labels are resolved by document order. See Limits — writing questions.json was not exercised."
requires: chrome-devtools-mcp (browser MCP) connected
summary: Read an Airtable form's application questions from the rendered page, for the eligibility check and later /submit
---

# Recipe: Airtable — get-form

Capture an Airtable form's **application questions** — labels, whether each is required, and the legal
options for each choice field — and save them alongside the application.

The questions are needed **early**: `fit-assessor` checks eligibility (work authorization,
availability) against `logistics.md` **before the pursue gate**, and `/submit` fills from the same list
long after. Reading the form only at submit time would surface a hard eligibility gate after the client
has already committed. On an Airtable-hosted application the posting and the form are usually on
different platforms — this recipe supplies only the questions.

## Preconditions
- `form_url` — `airtable.com/app<APP_ID>/pag<PAGE_ID>/form`.

## Steps

1. **Open the form and clear the consent modal** (Transcend — see README Traps) before reading
   anything.

2. **Enumerate, classify, and label the visible controls per README "Surface".** Use the visible-only
   filter (excludes the hidden mirror inputs), the field-type table to classify each control and read
   its options, and label-by-document-order.

3. **Record which questions are required** (README: the accessibility tree marks `required`; the label
   carries a `*`). This is what separates "must be grounded before submitting" from "optional".

4. **Save** as `questions.json` in the application folder, each entry carrying `label`, `required`, and
   the control type plus its options — the same shape `/apply` and `/submit` already consume, so
   downstream steps do not need to know which platform produced it.

## Self-check (validate by readback)
Confirm the count of captured questions matches the count of visible controls found in step 2, that
every entry has a non-empty `label`, and that every single- or multi-select entry has at least one
option. Then **screenshot the form** and confirm the capture accounts for what is on screen: a DOM
read alone cannot tell you it missed a section. If the page renders no recognisable controls (auth
wall, empty render), the capture failed — say so and hand off; never record an empty question list as
"no questions".

## Limits (honest scope)
Enumeration, classification and label resolution were verified live. **Writing `questions.json` was
not exercised**, so treat the saved shape as the intended procedure until a real capture has run.
