---
name: submit-application
kind: recipe
last_verified: 2026-07-26
verified_by: "Affirm 'Senior Software Engineer, Full Stack (Zero to One Labs)' (job-boards.greenhouse.io/affirm/jobs/7793217003) via chrome-devtools-mcp: 12/12 text fields written exactly, 6/6 react-select comboboxes set from the API's fields[].values[], 2 EEO questions correctly left blank, all confirmed by screenshot. fill/fill_form measured as unsafe on the same form. Submit deliberately not exercised. Confirmed live 2026-07-26."
requires: chrome-devtools-mcp (browser MCP) connected; the client's own logged-in browser if the form needs auth
summary: Fill a Greenhouse application form and hand off to the client to submit
---

# Recipe: Greenhouse — submit-application

Fill a Greenhouse application form for one role, then **hand the live tab to the client to submit**.
Runs **route → answer → explore → fill → validate → hand off**. This recipe drives a browser via the
**chrome-devtools-mcp** tool — it is an adaptive browser procedure, not a script, and it contains no
custom code.

## Preconditions
- The role is a captured application past the pursue gate, with rendered `docs/` (resume + cover
  letter) and its **application questions captured** (via `get-posting` — each with a `label`).
- **chrome-devtools-mcp is available.** If it is not, do not improvise a browser driver: tell the
  client, offer to set it up (https://github.com/ChromeDevTools/chrome-devtools-mcp), and fall back to
  **assisted-manual** — give the client the grounded answers + the `docs/` files as a fill-in
  checklist for their own browser. (§4: hand off rather than guess.)

## Steps

1. **Route — is this form the real application?** Check the posting's application section for an
   outbound apply link and do-not-submit wording (see README gotchas). If the application lives on
   another platform, **stop here** and follow that platform's recipe — do not fill this stub.

2. **Answer — grounded, once.** For each captured question, resolve the answer from the vault:
   - standard fields (name, email, phone, links) → `profile/`;
   - **work authorization / immigration sponsorship** → `logistics.md` (the truthful yes/no);
   - résumé / cover letter uploads → the rendered files in `docs/`.
   For each select, take the **legal option labels from the API** (`fields[].values[]`) and choose
   from them — never invent or approximate an option string.
   **Never guess a required field.** If a required question cannot be grounded, **stop and hand the
   live form to the client** — never fabricate an answer.

3. **Explore.** Open the role's apply URL in a **headed, client-visible** browser via
   chrome-devtools-mcp. Enumerate the live form's fields, counting only ones that are genuinely
   visible (`offsetParent` truthy **and** non-zero width).

4. **Reconcile the live form against the capture.** The API's `questions[]` is not the whole form:
   the voluntary **EEO / demographic survey** comes back separately under `demographic_questions`, and
   some controls (e.g. the phone-country picker) appear in neither. So every live field should resolve
   to one of three things — a captured question (fill it), a demographic question (**leave it blank**,
   it is the client's own to answer, and say so at hand-off), or genuine drift (**flag the recipe
   stale** rather than trusting it).

5. **Fill by label, using the right writer per field type.** Locate each field by its **label text**
   (robust to markup changes), then:

   | Field type | How to write it |
   |---|---|
   | text (`input[type=text\|email\|tel]`, `textarea`) | take the `value` setter off `HTMLInputElement.prototype` / `HTMLTextAreaElement.prototype`, `.call(el, val)`, then dispatch `input` **and** `change` with `bubbles: true` |
   | select (react-select `input[role=combobox]`) | `focus()`, dispatch bubbling **`mousedown`** to open (it does *not* open on `click`), wait ~400ms, then dispatch `mousedown` on the matching `[role=option]` |
   | file (résumé, cover letter) | set from `docs/`; if the upload cannot be driven, hand it to the client rather than skipping it silently |

   **Do not use the MCP's `fill` / `fill_form` on this form.** Measured 2026-07-26: they dispatch real
   keystrokes that race the re-render — `fill_form` on 15 fields landed 8 and dropped 1–2 **leading
   characters** from 6 of those (`TESTVALUE` → `ESTVALUE`); per-field `fill` produced no-ops and one
   append instead of a replace. **Every call returned success.** A mangled email address is silent and
   unrecoverable once submitted.

   **Close each dropdown before opening the next.** An open dropdown swallows the next one's open
   event — observed 2026-07-26: one of six selections failed silently for this reason and succeeded on
   a clean retry.

6. **Validate by readback — and by screenshot.** Re-read **the same element you wrote**; confirm each
   required field is non-empty and matches the intended grounded answer. Then **screenshot the filled
   form**: a readback alone can pass on a form that is blank on screen, and a react-select's chosen
   value is **not** readable from the `[role=combobox]` element (it renders into a sibling container,
   so a reader aimed at the input reports empty for a field that is visibly set — do not "fix" that by
   re-selecting, or you will clear correct answers chasing a phantom failure). If any required field
   could not be located or filled, **stop, hand off, and flag** — do not submit a half-filled form.

7. **Hand off.** Leave the filled form in the client's browser. **The client** solves the reCAPTCHA,
   reviews, and clicks **Submit** — the engine never clicks it. Tell them plainly which fields you
   deliberately left blank. On the client's confirmation, advance `status.yaml` → `applied`.

## Self-check (validate by readback)
Before hand-off, confirm every required field is filled and matches its grounded source, that a
**screenshot** shows the form visibly populated, and that the live form's fields correspond to the
captured questions plus the expected demographic appendix. If they have drifted, stop and flag the
recipe stale rather than trusting it.

## Limits (honest scope)
Verified as far as **rendered form state**. That the values reach Greenhouse's submit payload is not
confirmed, because confirming it means submitting a real application — treat that last hop as proven
only after a real application goes through. **File upload is untested**; `chrome-devtools-mcp` exposes
`upload_file`, so verify it before relying on it and be ready to hand the upload to the client.

## Must not
Click Submit · fill the EEO / demographic survey · guess a required answer · skip a required question ·
fabricate a work-authorization answer · use `fill` / `fill_form` · hand off on a readback without a
screenshot · submit without the client.
