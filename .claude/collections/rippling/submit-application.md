---
name: submit-application
kind: recipe
last_verified: 2026-07-26
verified_by: "Order.co 'Support Specialist' apply form (ats.rippling.com/orderco/jobs/cb243ee4-b893-4700-a2e8-a288ba4d7ecd/apply) via chrome-devtools-mcp: filled end to end until the platform's own Apply button unlocked (data-disabled false), confirmed by screenshot, then cleared. Order-based mapping re-verified on a second board with a different schema — Dialogue 'Partnerships Manager (West Territory)' (dialogue-en/e5703524-06ba-4d1f-9162-27a48a6a4e36) enumerated as 8 text + 4 combobox + 2 radio + 2 hidden file inputs, aligning with 10 basicQuestions + 3 additionalQuestions (KNOCKOUT, SHORT_ANSWER, SINGLE_SELECT_DROPDOWN both rendering KNOCKOUT and SINGLE_SELECT_DROPDOWN as comboboxes) plus an un-schema'd SMS-consent radio pair; that form was not filled. 10 visible controls + 2 hidden file inputs reconciled against 11 basicQuestions (phone rendering as 2 controls) with additionalQuestions null. Native value-setter wrote all text fields; Pronouns combobox opened on mousedown (7 options); upload_file FAILED on the dropzone button and SUCCEEDED against the hidden input[type=file] after un-hiding it; input.files stayed 0 while the UI read 'Total 1 file selected'. A required SMS-consent radio pair absent from the API blocked Apply until answered. Apply reported disabled=false while aria-disabled/data-disabled were true. Submit deliberately never clicked. Confirmed live 2026-07-26."
requires: chrome-devtools-mcp (browser MCP) connected
summary: Fill a Rippling application form and hand off to the client to submit
---

# Recipe: Rippling — submit-application

Fill a Rippling application form for one role, then **hand the live tab to the client to submit**.
Runs **answer → open → map by order → upload → fill → reconcile → validate → hand off**.

## Preconditions
- The role is past the pursue gate, with rendered `docs/` and its question schema captured via
  `get-posting` (`basicQuestions` + `additionalQuestions`).
- **chrome-devtools-mcp is available.** If not, fall back to **assisted-manual**: give the client the
  grounded answers + the `docs/` files as a fill-in checklist for their own browser.

## Steps

1. **Answer — grounded, once.** Resolve each question from the vault, mapping to
   `basicQuestions[].oid` (`first_name`, `email`, `phone_number`, …) — the **only** stable key, since
   nothing on the rendered page is. Work authorization / availability → `logistics.md`; résumé and
   cover letter → `docs/`. **Never guess a required field.**

2. **Open the apply form**, at
   `.../jobs/<uuid>/apply?jobBoardSlug=<slug>&jobId=<uuid>&step=application`, or by clicking
   **"Apply now"** on the posting — which is a `<button>`, not a link. Use a **headed,
   client-visible** browser.

3. **Map fields by ORDER, never by name or label.**
   - Field `name` attributes are **randomized per render** (`0i2gk28Yfb`) — useless as identifiers.
   - Fields have **no label association**: `el.labels` is empty and there is no `aria-labelledby`.
     A document-order label heuristic **mis-assigns** here — observed 2026-07-26, two long-answer
     questions both resolved to the first one's title.

   Enumerate visible controls in document order and align against the captured schema, which renders
   in the same order: **`basicQuestions` then `additionalQuestions`**, then any un-schema'd controls
   last. How each type renders:

   | Schema type | Renders as |
   |---|---|
   | `SHORT_ANSWER` | text input |
   | `LONG_ANSWER` | textarea |
   | `PRONOUN` | combobox |
   | `PHONE_NUMBER` | **two** controls — a country combobox (defaults `+1 US`) and a number input |
   | `SINGLE_SELECT_DROPDOWN`, `KNOCKOUT` | **combobox** — not radios |
   | `FILE` | dropzone button backed by a **hidden `input[type=file]`**, outside the text sequence |

   Verified alignments — the schema differs per board, so reconcile, never assume:
   - Order.co: 11 `basicQuestions` (2 `FILE`) + `null` additional → 10 visible controls + 2 hidden
     file inputs.
   - Dialogue: 10 `basicQuestions` (2 `FILE`) + 3 additional (`KNOCKOUT`, `SHORT_ANSWER`,
     `SINGLE_SELECT_DROPDOWN`) → 8 text inputs + 4 comboboxes + 2 hidden file inputs, **plus** an
     un-schema'd radio pair at the end.

   **If the counts do not reconcile, stop and flag `get-posting` stale.**

4. **Upload files first, before typing anything.** The résumé field states *"The résumé will be parsed
   to fill in the application details"*, so uploading after filling risks overwriting grounded answers.

   The MCP's `upload_file` **fails against the dropzone button** ("could not accept the file directly,
   and clicking it did not trigger a file chooser"). What works: make the hidden input visible, take a
   fresh snapshot so it gets a uid, then `upload_file` against **that** uid.

   **Verify the attachment by the UI, not the input.** After a successful upload `input.files.length`
   is still **0** — the app moves the file into its own state. The truth is the rendered
   `Total N file selected` text and the file chip.

5. **Fill, using the right writer per control.**

   | Control | How to write it |
   |---|---|
   | text / long answer | native `value` setter off `HTMLInputElement.prototype` / `HTMLTextAreaElement.prototype`, then dispatch `input` **and** `change` with `bubbles: true` |
   | combobox (`input[role=combobox]`) | `focus()`, dispatch bubbling **`mousedown`** to open, wait ~500ms, dispatch `mousedown` on the matching `[role=option]` |
   | file | step 4 |

   Do **not** use `fill` / `fill_form`. Two field-level traps:
   - **The phone field applies a formatting mask** — writing `4155550100` yields `415-555-0100`. A
     byte-equality readback reports a false mismatch on a correct value. It also **strips non-numeric
     input entirely**: writing a URL into it left the field empty.
   - **URL fields validate** and differ from each other. `https://example.invalid/linkedin` was
     rejected with "This is an invalid URL."; a real `linkedin.com` URL was accepted.

6. **Reconcile against the live page before validating.** The captured schema is **not** the whole
   form. An **SMS-consent radio pair** present in neither `basicQuestions` nor `additionalQuestions`,
   and marked with no `*`, appeared on **both** boards checked — on Order.co it blocked `Apply` until
   answered. Treat un-schema'd controls as expected, not exceptional.

   Every live control must resolve to one of:
   - a captured question → fill it from the vault;
   - a **knockout** (`KNOCKOUT`) → answer only from `logistics.md`. A wrong answer auto-rejects, so if
     it cannot be grounded, **stop and hand off** rather than choosing the "likely" option;
   - a **consent or attestation** (the SMS radios; a `SINGLE_SELECT_DROPDOWN` whose only choice is
     `Yes`) or a **compensation expectation** → **the client's own to answer.** Leave it, and say so
     at hand-off;
   - otherwise drift → **flag `get-posting` stale**.

7. **Validate — and read the right attribute.** Re-read every control you wrote, allowing for the
   phone mask. Then check the `Apply` button, which is the platform's own completeness gate:
   **`button.disabled` is `false` even when the button is blocked** — the real state is
   `aria-disabled` / `data-disabled`. Reading `.disabled` reports a complete form when it is not.
   Finish with a **screenshot**.

8. **Hand off.** Leave the filled form in the client's browser. **The client** answers any consent
   question, reviews, and clicks **"Apply"** — the engine never clicks it. Tell them what you left
   blank, and surface the AI-analysis notice and its opt-out link when `hasAIEvaluationsEnabled` is
   true. On the client's confirmation, advance `status.yaml` → `applied`.

## Self-check (validate by readback)
Live control count reconciles with the captured schema; every required field filled and matching its
grounded source (phone allowing for the mask); the résumé shows as attached in the **rendered** file
status; `Apply` reports `data-disabled="false"`; and a **screenshot** shows the form visibly populated.
If any of these fails, stop, hand off, and flag.

## Limits (honest scope)
Verified up to the point where `Apply` unlocked; **it was never clicked**, so nothing downstream is
known — and the form is **multi-step** (`step=application`, progress bar at 50% when complete), so at
least one further step exists after Apply that this recipe has never seen.

The résumé-parsing autofill was **not** observed: the placeholder PDF used carried no extractable text,
so whether parsing overwrites already-filled answers is unconfirmed. Step 4's ordering is a precaution,
not a measured behaviour.

The **EEOC questionnaire** was disabled on every posting checked; if `eeocQuestionnaireEnabled` is true,
expect controls this recipe has never seen — and note the survey is the client's own to answer.

## Must not
Click Apply · answer a consent, EEOC, or salary-expectation question on the client's behalf · guess a
**knockout** answer · map a field by `name` or by rendered label · guess a required answer · use
`fill` / `fill_form` · trust `button.disabled` · trust `input.files` as proof of upload · hand off
without a screenshot · submit without the client.
