# System: Lever

The brain and recipe index for job boards hosted on **Lever**.

## Recognize

- Hosted board: `jobs.lever.co/<slug>`
- Posting: `jobs.lever.co/<slug>/<postingId>` (id is a **UUID**)
- Apply form: `jobs.lever.co/<slug>/<postingId>/apply`
- Page footer reads "Jobs powered by **Lever**".

**The board is often embedded, and then the host page carries no `jobs.lever.co` link.** A company's
careers page may render the board itself, with the slug visible only in an inline API call. Sweep the
careers-page source for `lever.co` and take the slug from the inline
`api.lever.co/v0/postings/<slug>` URL — host-based detection alone misses these, and the slug
frequently does not match the company's public name.

## Public API — documented and stable, no login

Base: `https://api.lever.co/v0/postings/<slug>`

| Purpose | Call |
|---|---|
| All open roles | `?mode=json` |
| One role | `/<postingId>?mode=json` |
| Grouped | `?group=team` (also `location`, `commitment`, `department`) |

**No pagination and no page size** — the whole board comes back in one response, whatever its size.

**A 404 and an empty board are different things, and the distinction matters:**
- unknown slug → **HTTP 404**, body `{"ok":false,"error":"Document not found"}`
- valid board with nothing open → **HTTP 200** and `[]`

So `[]` means "this employer has no open roles", never "wrong slug".

**The API does not carry the application form.** No question schema, no EEO survey — those exist only
on the rendered apply page. `get-posting` returns the advert; `submit-application` reads the form live.

## Recipes

- `find-jobs` — list every open role for a board.
- `get-posting` — capture one role.
- `submit-application` — fill the apply form, hand off to the client.
