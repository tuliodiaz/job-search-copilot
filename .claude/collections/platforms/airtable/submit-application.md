---
name: submit-application
kind: recipe
last_verified: 2026-07-26
verified_by: "Anthropic Fellows / Constellation form (airtable.com/appCHLjgoTUCJMLct/pagUhpiBE5KxoU3lX/form) via chrome-devtools-mcp: cleared, then filled 33/33 text fields (17 plain + 16 contenteditable), 7/7 radio groups and 3 multi-selects — 0 read-back mismatches, 0 fields flagged invalid, confirmed by screenshots at three points in the form. fill/fill_form measured as unsafe on the same form. Submit deliberately not exercised. Confirmed live 2026-07-26."
requires: chrome-devtools-mcp (browser MCP) connected
summary: Fill an Airtable application form and hand off to the client to submit
---

# Recipe: Airtable — submit-application

Fill an Airtable-hosted application form for one role, then **hand the live tab to the client to
submit**. Runs **explore → answer → fill → validate → hand off**. This recipe drives a browser via
the **chrome-devtools-mcp** tool — it is an adaptive browser procedure, not a script, and it contains
no custom code.

## Preconditions
- The role is a captured application past the pursue gate, with rendered `docs/`.
- **chrome-devtools-mcp is available.** If it is not, do not improvise a browser driver: tell the
  client, offer to set it up (https://github.com/ChromeDevTools/chrome-devtools-mcp), and fall back to
  **assisted-manual** — give the client the grounded answers + the `docs/` files as a fill-in
  checklist for their own browser. (§4: hand off rather than guess.)
- The form's **questions are already captured** (via `get-form` → `questions.json`). They are what the
  eligibility check ran against at the pursue gate; do not re-derive them here.

## Steps

1. **Open and clear the consent modal.** Load the form in a **headed, client-visible** browser. A
   Transcend cookie dialog blocks all interaction on first load; dismiss it (prefer "Reject All,
   Except Strictly Necessary") before anything else — a click that lands on an overlay reports
   success too.

2. **Locate the live fields and reconcile them against `questions.json`.** Enumerate the page exactly
   as `get-form` does — count only controls that are **genuinely visible** (`offsetParent` truthy
   **and** `getBoundingClientRect().width > 0`, which excludes the hidden mirror inputs shadowing every
   long-answer field), and resolve labels by document order rather than by ancestry.

   Every live field should match a captured question. A live field with no captured question means the
   form changed since capture: **stop and flag `get-form` stale** rather than filling something the
   eligibility check never saw. Classify each matched field as **plain** (`textarea`,
   `input[type=text|email]`) or **rich** (`[role=textbox][contenteditable]`) — they need different
   writers.

3. **Answer — grounded, once.** Resolve each answer from the vault: identity and experience claims →
   `profile/cv.md` / `narrative.md`; **work authorization, availability, employment type, start
   date** → `logistics.md`; résumé → the rendered file in `docs/`.
   **Never guess a required field.** A work-authorization or availability answer that isn't in the
   profile is **asked, never inferred**.

4. **References are claims about a third party.** These forms commonly ask for three referees with
   name, email, title, employer, and Google Scholar. The **name, email, and the client's relationship
   to them can only come from the client** — they are not derivable from a CV. The referee's public
   details are **world-claims**: verify each from a primary source and save it under `_sources/`, or
   leave the field for the client. Never generate a real person's credentials. Note for the client
   that these forms often state referees may be contacted **without prior notice**.

5. **Fill, using the right writer per field type.**

   | Field type | How to write it |
   |---|---|
   | plain (`textarea`, `input[type=text\|email]`) | take the `value` setter off `HTMLInputElement.prototype` / `HTMLTextAreaElement.prototype`, `.call(el, val)`, then dispatch `input` **and** `change` with `bubbles: true` |
   | rich (`[role=textbox][contenteditable]`) | `focus()`, select contents with a `Range`, then `document.execCommand('insertText', false, val)` |
   | radio / multi-select option | plain `.click()` |
   | file dropzone (résumé) | untested — see *Limits*; hand it to the client rather than skipping silently |

   **Do not use the MCP's `fill` / `fill_form`.** Measured 2026-07-26: they dispatch real keystrokes
   that race the re-render — `fill_form` on 15 fields landed 8 and dropped 1–2 **leading characters**
   from 6 of those (`placeholder@…` → `aceholder@…`); per-field `fill` produced no-ops and one append
   instead of a replace. **Every call returned success.** A mangled email address is silent and
   unrecoverable once submitted.

6. **Validate by readback — and by screenshot.** Read back **the same element you wrote** (`innerText`
   for rich fields, `value` for plain); a reader that queries only `input`/`textarea` cannot see rich
   fields at all, and will mistake "invisible to my selector" for "empty" — or report a perfect match
   while writing into a hidden mirror. Wait ~1s before reading control state: `aria-checked` returns
   the **pre-click** value if read immediately. Then **screenshot the filled form** — it is the only
   check the other two cannot fool. If any required field could not be located or filled, **stop, hand
   off, and flag**.

7. **Hand off.** Leave the filled form in the client's browser. **The client** completes the file
   upload, ticks any attestation, reviews every answer, and clicks **Submit** — the engine never
   clicks it. Tell them plainly which fields you deliberately left blank. On the client's
   confirmation, advance `status.yaml` → `applied`.

## Fields the engine leaves for the client
Beyond anything ungrounded: **attestations** ("confirm your understanding of our AI policy" — the
client is the one attesting) and **statements of the client's own intent** ("how likely are you to
accept an offer, with a % estimate" — draft only from what they tell you, never invent the number).

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

## Must not
Click Submit · tick an attestation on the client's behalf · guess a required answer · invent a third
party's credentials · use `fill` / `fill_form` · hand off on a readback without a screenshot · submit
without the client.
