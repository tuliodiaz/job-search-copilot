# BUILD — how this engine is written and validated

This is the **build discipline** for contributors (human or agent). It is distinct from:
- **README.md** — the design *rationale* (why the system is shaped this way). Human-only; nothing at
  runtime reads it.
- **CLAUDE.md** — the runtime *invariants*, auto-loaded into every session. The single source of
  truth for the rules the agent obeys.

## Two hard conventions

1. **Runtime files are self-contained; they never link to each other or to SYSTEM.md.**
   Each command / skill / agent / recipe is loaded on its own, so it must be complete on its own. The
   *element graph* (which command routes to which skill, etc.) is expressed as structured
   **frontmatter**, not prose links, and `tools/validate_structure.py` resolves it on every run — a
   broken reference fails the build instead of rotting silently. Global rules are stated **once** in
   CLAUDE.md and assumed everywhere; they are not restated per file.

2. **We ship no recipe we have not verified at 100%.**
   A recipe is a *verified* artifact: "I ran this against the live platform and it worked; here is the
   readback proof and the date." That cannot come from a model's memory. Until a platform recipe is
   verified live by a human, it does not exist in the repo. The validator enforces this: a recipe
   with a `last_verified` date but no `verified_by` proof fails the build; the only other allowed
   value is `last_verified: never`.

## Frontmatter contract

- **command** — `name`, `kind: command`, `route_kind: skill|agent|recipe|vault`, `route_target`
  (omit for `vault`).
- **skill** — `name` (must equal the folder name), `kind: skill`.
- **agent** — `name` (must equal the filename), `kind: agent`.
- **recipe** — `last_verified` (a date **with** `verified_by`, or `never`), plus a `Self-check` block
  in the body.

## Validating the structure (deterministic, offline)

```
python3 tools/validate_structure.py    # structure: graph resolves, no cross-links, schema-pinned
python3 tests/test_scanner.py          # behavior: the deterministic scanner's contract
```

`validate_structure.py` exit 0 = the engine graph is consistent, templates/config are schema-pinned,
no cross-links, no untested-but-dated recipes, and `templates/` contains only vault scaffolding. It
runs with no network and no agent — the backbone of "a fresh pull works out of the box."

`test_scanner.py` proves the one piece of deterministic *behavior* in the engine: clean content
passes (exit 0), poisoned content is flagged with the expected rules (exit 10), and an unreadable
file fails closed (exit 2). Deterministic scripts get real tests; recipes and agent judgment are
proven by the fresh-agent acceptance run.

## Acceptance test — the real bar

Structural validity is necessary but not sufficient. The real bar is behavioral: **a fresh agent,
given only a clean pull of this repo, behaves as architected.** The agreed cadence:

1. Build one thin slice (see below).
2. `python3 tools/validate_structure.py` passes.
3. Spin a **new agent in a new folder from a clean pull** and confirm it does exactly what the slice
   specifies — no more, no less.
4. **If the agent deviates from the architecture, stop and fix the engine before adding anything.**

### Slice status
- [x] **Slice 0** — skeleton, CLAUDE.md, validator, fixtures.
- [x] **Slice 1** — `/onboard` + vault templates + config. *Bar: a fresh agent given only "hi"
  **self-orients** — detects the missing vault, explains onboarding is step one, and offers to start,
  without being told the command; then produces a valid `vault/` with the profile populated and
  writes nothing outside `vault/`.*
- [x] **Slice 2** — deterministic scanner (+ tests) + injection-auditor agent + `/lead` +
  capture-posting. *Bar: a fresh agent capturing a poisoned posting runs the scanner, gets flags,
  has the auditor judge it a trap, and blocks the injected instruction from influencing anything —
  recording `security_disposition` and telling the client — while a clean posting captures normally.
  Scanner detection stays deterministic; the LLM judgment lives in the auditor.*
- [x] **Slice 3 (scout / company capture)** — `/scout` + `scout-company` skill + **live-verified**
  Greenhouse `find-jobs` recipe + `company.yaml` facts (schema in `.claude/config/`). *Bar: a fresh
  agent given `/scout affirm` resolves the ATS (Greenhouse), lists Affirm's real open roles via the
  public API, ranks them by the client's preferences, records `company.yaml`, and writes nothing
  outside `vault/`.* The Greenhouse `find-jobs` recipe was verified live (2026-07-23) against
  `boards-api.greenhouse.io/v1/boards/affirm/jobs` before shipping.
- [x] **Slice 4a (Decide)** — `/apply` + `analyze-posting` skill + `fit-assessor` agent + the pursue
  gate. *Bar: a fresh agent given a captured lead parses it, returns apply/stretch/skip + a 0-100
  score with its band snapshot, runs the **grounded eligibility** check (never inferring work auth —
  flags `unknown` when `logistics.md` is silent), records the verdict in `status.yaml`, and **stops at
  the pursue gate** for the client's decision.*
- [x] **Company-fit + get-posting** — `company-recon` agent that **sources from a growing collection
  of research recipes** (`web-search` verified live) rather than hard-coding a source; wired into
  `/apply` Decide as a company-fit **signals** read at the pursue gate, and exposed standalone via
  `/recon` (deep mode). Greenhouse `get-posting` (verified) captures a role's application questions.
  *Bar: at the pursue gate the client sees company signals (e.g. Affirm's Glassdoor rating + recent
  layoffs) beside role fit; research sources are scanned on capture and provenance-marked.*
- [ ] **Slice 4b (Craft)** — `tailor-resume` skill + document renderer script. *Bar: after the pursue
  gate, drafts a résumé/cover letter that drops an ungrounded claim (grounding check) and a
  world-claim without a source (verification), then renders. Needs a non-empty `narrative.md`.*
- [ ] **Slice 5** — platform `submit-application` recipes, verified live per ATS. *Bar: recipe passes
  its self-check against the live form, with `verified_by` proof; never auto-submits.*

Do not start a slice until the previous one clears its bar.
