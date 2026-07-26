---
name: submit-application
kind: recipe
last_verified: never
requires: chrome-devtools-mcp (browser MCP) connected; the client's own logged-in browser if the form needs auth
summary: Fill a Greenhouse application form by label and hand off to the client to submit
---

# Recipe: Greenhouse — submit-application

Fill a Greenhouse application form for one role, then **hand the live tab to the client to submit**.
Runs **explore → answer → validate → hand off**. This recipe drives a browser via the
**chrome-devtools-mcp** tool — it is an adaptive browser procedure, not a script, and it contains no
custom code.

`last_verified: never` — this is the intended procedure; it is verified only once it has been run
against a real Greenhouse form with the MCP connected (fields located by label, self-check passing).

## Preconditions
- The role is a captured application past the pursue gate, with rendered `docs/` (resume + cover
  letter) and its **application questions captured** (via `get-posting` — each with a `label`).
- **chrome-devtools-mcp is available.** If it is not, do not improvise a browser driver: tell the
  client, offer to set it up (https://github.com/ChromeDevTools/chrome-devtools-mcp), and fall back to
  **assisted-manual** — give the client the grounded answers + the `docs/` files as a fill-in
  checklist for their own browser. (§4: hand off rather than guess.)

## Steps

1. **Answer — grounded, once.** For each captured question, resolve the answer from the vault:
   - standard fields (name, email, phone, links) → `profile/`;
   - **work authorization / immigration sponsorship** → `logistics.md` (the truthful yes/no);
   - résumé / cover letter uploads → the rendered files in `docs/`.
   **Never guess a required field.** If a required question cannot be grounded, **stop and hand the
   live form to the client** — never fabricate an answer.

2. **Explore.** Open the role's apply URL in a **headed, client-visible** browser via
   chrome-devtools-mcp. Enumerate the live form's fields.

3. **Fill by label.** For each captured question, locate its field by its **label text** (robust to
   markup changes) and enter the grounded answer; set file inputs to the `docs/` files; choose the
   correct option for selects (e.g. the sponsorship question).

4. **Validate by readback.** Re-read every field; confirm each **required** one is non-empty and
   matches the intended grounded answer. If any required field could not be located or filled, **stop,
   hand off, and flag** — do not submit a half-filled form.

5. **Hand off.** Leave the filled form in the client's browser. **The client** solves any CAPTCHA,
   reviews, and clicks **Submit** — the engine never clicks it. On the client's confirmation, advance
   `status.yaml` → `applied`.

## Self-check (validate by readback)
Before hand-off, confirm every required field is filled and matches its grounded source, and that the
live form's fields correspond to the captured questions. If they have drifted, stop and flag the
recipe stale rather than trusting it.

## Must not
Click Submit · guess a required answer · skip a required question · fabricate a work-authorization
answer · submit without the client.
