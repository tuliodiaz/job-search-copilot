# System: Lever

The "brain" and recipe index for job boards hosted on **Lever**.

## How to recognize it (key)
- Hosted board: `jobs.lever.co/<slug>`
- Posting: `jobs.lever.co/<slug>/<postingId>` (id is a **UUID**)
- Apply form: `jobs.lever.co/<slug>/<postingId>/apply`
- Page footer reads "Jobs powered by **Lever**".

**The board is often embedded, and then the host tells you nothing.** A company's careers page may
render the board itself, with the slug only visible in an inline API call. Confirmed live 2026-07-26:
`trackforce.com/about-us/careers/` contains **no** `jobs.lever.co` link — its inline JavaScript calls

```
https://api.lever.co/v0/postings/tracktik?group=team&mode=json
```

so the slug is `tracktik`, not `trackforce`. **Sweep the careers page source for `lever.co` and take
the slug from the API URL** — host-based detection alone will miss these, and the slug frequently does
not match the company's public name (here, a pre-merger brand).

## Public API — documented and stable, no login

Base: `https://api.lever.co/v0/postings/<slug>`

| Purpose | Call |
|---|---|
| All open roles | `?mode=json` |
| One role | `/<postingId>?mode=json` |
| Grouped | `?group=team` (also `location`, `commitment`, `department`) |

**No pagination and no page size** — the whole board comes back in one response. Verified across three
boards of very different sizes: `tracktik` 19, `matchgroup` 83, **`veeva` 831**, all in a single call.

**A 404 and an empty board are different things, and the distinction matters:**
- unknown slug → **HTTP 404**, body `{"ok":false,"error":"Document not found"}`
- valid board with nothing open → **HTTP 200** and `[]`

So `[]` means "this employer has no open roles", never "wrong slug". Confirmed: `lever`, `plaid` and
`kraken` are real accounts currently returning `200 []`, while `netlify` and a nonsense slug 404.

## Recipes here
- `find-jobs` — list every open role for a board. **Verified 2026-07-26.**
- `get-posting` — capture one role. **Verified 2026-07-26.**
- `submit-application` — fill the apply form, hand off to the client. **Verified 2026-07-26.**

## Gotchas

- **The API does not carry the application form.** No question schema, no EEO survey — those exist only
  on the rendered apply page. `get-posting` gives the advert; `submit-application` reads the form.
- **Form fields have real, stable `name` attributes** — `name`, `email`, `phone`, `location`, `org`,
  `urls[LinkedIn]`, `urls[GitHub]`, `resume`. Map answers **by name**, not by position. (This is the
  opposite of Rippling, where names are randomized per render.)
- **`<select>` option values are codes, not labels.** The country select uses ISO codes (`CA`, `AF`,
  `DZ`). Assigning the visible label silently blanks the field — no error. Match the option **text**,
  then set `selectedIndex` (or the code).
- **The `location` field is an autocomplete with a hidden `selectedLocation` companion.** Typing text
  fills the visible box but leaves `selectedLocation` as `{"name":""}` — the structured value the
  employer receives stays empty. Verified 2026-07-26.
- **`required` is unreliable; the ✱ marker is authoritative.** The résumé field renders "Resume/CV ✱"
  while its `required` attribute is `false`.
- **The Submit button is never disabled.** Unlike Rippling, Lever does not gate it on completeness, so
  it is *not* a signal that the form is ready.
- **hCaptcha.** A hidden `h-captcha-response` field is present — the client solves it, which is another
  reason the engine never submits.
- Boards may carry an **AI-usage notice** ("We may use artificial intelligence (AI) tools to support
  parts of the hiring process…"). Surface it to the client, as with other systems' AI disclosures.
- An **"Apply with LinkedIn"** widget (an embedded LinkedIn iframe) can auto-complete the form. It
  needs the client's LinkedIn session — never drive it; the engine fills from the vault instead.
