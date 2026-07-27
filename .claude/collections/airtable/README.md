# Platform: Airtable Forms

Airtable-hosted application forms — used when an employer, or its recruiting partner, runs the
application outside its ATS.

## Recognize
- Form URLs: `airtable.com/app<APP_ID>/pag<PAGE_ID>/form`.
- Usually reached by **redirect from an ATS posting**, often behind a shortener. The ATS listing is
  the advert; the Airtable page is the actual application.
- Record the form URL in the company's `company.yaml` alongside the posting URL — they differ, and the
  posting is authoritative about which one takes applications.
- **No public endpoint** for a form's questions is known — unlike Greenhouse, nothing here is reachable
  by plain HTTP. Read the field list from the rendered page: everything needs the browser MCP and there
  is no schema to reconcile the live form against.
- An Airtable form URL is **one form for one role** — there is no board to enumerate, so this platform
  has no `find-jobs` counterpart.

## Surface — reading and writing the fields
- **Enumerate only genuinely visible controls:** require `offsetParent` truthy **and**
  `getBoundingClientRect().width > 0`. Every long-answer field is shadowed by a hidden mirror
  `<input>`; this filter excludes them, and without it a capture double-counts.
- **Resolve labels by document order,** not by ancestry. Walk the form with a `TreeWalker`, tracking
  the last non-field element carrying direct text; each control takes the most recent preceding label.
  Ancestor-`innerText` heuristics silently mislabel. Radio groups carry **no `aria-label`** — their
  question text is only reachable via `aria-labelledby`. Section headings (`h2`) give the groupings.
- **Required marking:** the accessibility tree marks required controls (`required`); the rendered
  label carries a `*`.
- **Two field types plus choice controls, each needing its own reader/writer:**

  | Type | Matches | Options | Writer |
  |---|---|---|---|
  | text short (plain) | `textarea`, `input[type=text\|email]` | — | take the `value` setter off `HTMLInputElement.prototype` / `HTMLTextAreaElement.prototype`, `.call(el, val)`, then dispatch `input` **and** `change` with `bubbles: true` |
  | text long (rich) | `[role=textbox][contenteditable="plaintext-only"]`, shadowed by a hidden mirror `<input>` — writing the mirror **passes a DOM read-back but does nothing on screen** | — | `focus()`, select contents with a `Range`, then `document.execCommand('insertText', false, val)` |
  | single-select | `[role=radiogroup]` | text of each child `[role=radio]` | plain `.click()` |
  | multi-select | `[role=listbox]` | text of each child `[role=option]` | plain `.click()` |
  | file (résumé) | a dropzone button, not an input | — | untested — hand to the client |

## Traps
- **Transcend cookie-consent modal** blocks all interaction on first load. Dismiss it (prefer "Reject
  All, Except Strictly Necessary") before anything else — a click that lands on the overlay reports
  success too.
- **The MCP's `fill` / `fill_form` are unsafe here.** They dispatch real keystrokes that race the
  re-render, corrupting and skipping fields — dropped leading characters, no-ops, appends instead of
  replaces — while **every call returns success**. Use the per-type writers above instead. A mangled
  email address is silent and unrecoverable once submitted.
- **Controls report their old state if read immediately after a click** — the re-render has not
  happened yet. Wait ~1s; `aria-checked` read immediately returns the **pre-click** value.
- **`Clear form` opens a separate confirm dialog** ("This can't be undone").
- **`Submit` sits directly beside `Clear form` in the DOM.** Match button text exactly, and guard
  against matching Submit, before clicking anything in that row.
- **Reference fields ask for a third party's details** — a real person's name, email, title, and public
  profiles. Those are world-claims about a real person, not client-claims.

## Recipes
- `get-form` — read the form's application questions from the rendered page, for the eligibility check
  and later `/submit`.
- `submit-application` — fill the form, verify visually, hand the live tab to the client to submit.
