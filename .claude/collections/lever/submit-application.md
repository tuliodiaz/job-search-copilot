---
name: submit-application
kind: recipe
last_verified: 2026-07-26
verified_by: "Trackforce 'Senior Data Engineer' apply form (jobs.lever.co/tracktik/86aea528-0707-4e81-8cc8-8f53fa5b475a/apply) via chrome-devtools-mcp: 58 form controls enumerated; upload_file succeeded directly against input[type=file][name=resume] (visible) — input.files.length 1, hidden resumeStorageId populated with a UUID, UI showed 'Success!'; 10 text fields written by name attribute, all byte-exact (name, email, phone, location, org, urls[LinkedIn|Twitter|GitHub|Portfolio|Other]); confirmed by screenshot; then cleared. Measured traps: <select> option values are ISO codes so assigning the label 'Canada' silently blanked it while selectedIndex worked; input[name=location] left hidden selectedLocation as {\"name\":\"\"}; resume renders '✱' while required=false; SUBMIT APPLICATION is never disabled; hidden h-captcha-response present. Submit deliberately never clicked. Confirmed live 2026-07-26. Re-verified on a second board with employer screening questions — Match Group 'Android Engineer III' (jobs.lever.co/matchgroup/3414ba28-35f7-45d3-8e13-35c883959635/apply), 72 controls: résumé uploaded (resumeStorageId 4558ac22…), 9 text fields by name, and all 5 required cards[<uuid>][fieldN] screening questions answered (4 radios by label text, 1 select by option text + selectedIndex); unanswered required screening controls carried invalid=\"true\" and the count fell to 0 once complete; EEO/pronouns/accommodations left blank; confirmed by full-page screenshot; form left filled, not submitted. Match Group screening blocks were headed ACCOMMODATIONS REQUEST, HINGE - LOCATION, VISA - US and PRONOUNS; the five required questions were: Are you located in the NYC area? · are you open to relocating? · are you willing to come into the office 3 days a week? · Are you authorized to work in the United States? · will you now or in the future require sponsorship?"
requires: chrome-devtools-mcp (browser MCP) connected
summary: Fill a Lever application form and hand off to the client to submit
---

# Recipe: Lever — submit-application

Fill a Lever application form for one role, then **hand the live tab to the client to submit**.
Runs **answer → open → upload → fill by name → validate → hand off**.

## Preconditions
- The role is past the pursue gate, with rendered `docs/` and the posting captured via `get-posting`.
- **chrome-devtools-mcp is available.** If not, fall back to **assisted-manual**: give the client the
  grounded answers + the `docs/` files as a fill-in checklist for their own browser.
- Note the API gave **no question schema** (see `get-posting` *Limits*), so the form is read live.

## Steps

1. **Answer — grounded, once.** Resolve each answer from the vault: identity and links → `profile/`;
   **work authorization / availability** → `logistics.md`; résumé and cover letter → `docs/`.
   **Never guess a required field.** If a required answer cannot be grounded, **stop and hand the live
   form to the client**.

2. **Open** `applyUrl` (= `hostedUrl` + `/apply`) in a **headed, client-visible** browser.

3. **Upload the résumé first.** The file input is a **real, visible `input[type=file][name=resume]`**,
   so the MCP's `upload_file` works against it directly — no un-hiding needed.
   Verify by **all three**: `input.files.length` is 1, the hidden `resumeStorageId` is populated with
   a UUID (server-side confirmation), and the UI shows "Success!".
   Do this before typing: Lever parses the résumé to auto-complete fields.

4. **Fill by `name` attribute** — Lever's are real and stable, unlike some systems':

   | Field | `name` |
   |---|---|
   | Full name | `name` |
   | Email | `email` |
   | Phone | `phone` |
   | Current location | `location` |
   | Current company | `org` |
   | Links | `urls[LinkedIn]`, `urls[Twitter]`, `urls[GitHub]`, `urls[Portfolio]`, `urls[Other]` |
   | Résumé | `resume` |

   Write text with the native `value` setter off `HTMLInputElement.prototype`, then dispatch `input`
   **and** `change` with `bubbles: true`. No masking or format rewriting was observed.

   **For a `<select>`, never assign the visible label.** Option values are codes, not labels (the
   country select uses ISO codes — `CA`, `AF`, `DZ`). Assigning `"Canada"` blanks the field silently.
   Find the option whose **text** matches, then set `selectedIndex`, and dispatch `change`.

5. **Answer the employer's screening questions — `cards[<uuid>][fieldN]`.**

   These are the employer's own questions, and they are where the **eligibility and knockout** content
   lives — work authorization, sponsorship, location, relocation, on-site willingness. Each `<uuid>`
   is one titled block and `fieldN` is a question within it.

   **Ground every one of these in `logistics.md`.** A wrong work-authorization or sponsorship answer is
   not a typo — it is a false statement to an employer, and on a knockout question it also ends the
   application. If any cannot be grounded, **ask the client; never pick the likely option.**

   Read the question text from the block, not from the field name — `fieldN` is opaque. Then:
   - **radio** → find the input whose label text equals the intended option, and `.click()` it;
   - **select** → match the option's **text**, set `selectedIndex` (never assign the label as `value`);
   - **textarea** → the native `value` setter, as for text fields.

   Types observed: `radio` (2- and 3-option), `select-one`, `textarea`.

   Some blocks are **not** the engine's to answer even when they sit among the screening questions —
   an accommodations request, or a pronouns question. See *Fields the engine leaves for the client*.

6. **Know the two fields that lie.**
   - **`location` has a hidden `selectedLocation` companion.** Typing text fills the visible box but
     leaves `selectedLocation` as `{"name":""}`, so the structured value the employer receives is
     empty. If a properly resolved location matters, the client must pick from the autocomplete — say
     so at hand-off rather than assuming the typed text carried.
   - **`required` is unreliable — trust the ✱.** The résumé renders "Resume/CV ✱" while its
     `required` attribute is `false`. Derive required-ness from the rendered marker.

7. **Validate by readback — and by screenshot.** Re-read every field you wrote and confirm it matches.

   **Do not use the Submit button as a completeness signal**: Lever never disables it, so an enabled
   button means nothing. **Use the invalid flags instead** — unanswered required controls carry
   `invalid="true"` / `aria-invalid="true"`, and that count falling to **0** is the real signal that
   every required field is satisfied.

   Finish with a screenshot showing the form visibly populated.

8. **Hand off.** Leave the filled form in the client's browser. **The client** solves the **hCaptcha**,
   answers anything left blank, and clicks **SUBMIT APPLICATION** — the engine never clicks it. Tell
   them plainly what you left blank. Surface any AI-usage notice on the page and its opt-out. On the
   client's confirmation, advance `status.yaml` → `applied`.

## Fields the engine leaves for the client
- **Pronouns** — both the checkbox group and any free-text pronouns question in a `cards[]` block.
- The **Demographic Survey** — ethnicity, gender, LGBTQIA+ and similar voluntary self-identification.
- **Accommodations requests** — e.g. "will you require a reasonable accommodation to complete the
  hiring process?". Disability-adjacent and the client's own disclosure, even though it renders as an
  ordinary `cards[]` question alongside the screening ones.
- **Marketing / data-retention consent** (`consent[marketing]`, or a consent line above Submit).
- **"Apply with LinkedIn"** — an embedded LinkedIn widget that needs the client's own session. Never
  drive it; fill from the vault instead.

Leaving these blank is deliberate: say so explicitly at hand-off so the client knows to complete them.

## Self-check (validate by readback)
Every grounded field non-empty and matching its source; **every `cards[]` screening question answered
from `logistics.md`**; the résumé confirmed by `files.length`, `resumeStorageId` **and** the "Success!"
indicator; the count of `invalid="true"` controls at **0**; and a **screenshot** showing the form
visibly populated. If a required field could not be grounded or located, **stop, hand off, and flag**.

## Limits (honest scope)
Verified on one form, filled to completion and cleared. **Submit was never clicked** — an hCaptcha
gates it and only the client passes that, so nothing downstream of submission is known.

Résumé **parsing** did not fire: the placeholder PDF carried no extractable text, so whether Lever's
parse overwrites already-filled answers is unconfirmed. Step 3's ordering is a precaution, not a
measured behaviour.

Two distinct namespaces carry employer-authored questions, and they mean different things:
- **`cards[<uuid>][fieldN]`** — the employer's own questions, including **screening and knockout**
  content.
- **`surveysResponses[<uuid>][responses][fieldN]`** — the demographic/EEO survey. Observed on both
  verified boards used only for that. A board repurposing this namespace for screening has not been
  seen; if one appears, reconcile carefully rather than assuming it is optional.

`cards[]` `checkbox` and free-text-required variants have not been observed — only `radio`,
`select-one` and an optional `textarea`.

## Must not
Click SUBMIT APPLICATION · **guess a `cards[]` screening or knockout answer** (work authorization,
sponsorship, location, relocation, on-site willingness — ground them or ask) · answer pronouns, a
demographic survey, an accommodations request, or a consent checkbox on the client's behalf · drive
"Apply with LinkedIn" · assign a `<select>` its visible label · trust `required` over the ✱ · treat
the enabled Submit button as proof of completeness · hand off without a screenshot.
