# How the System Works — System Reference

This document is the **design reference** for the job-search engine: what each element is, how
they interact, what happens when things go wrong, and how the system stays trustworthy as it
grows. It describes the intended, steady-state design — the target the implementation is held to.

---

## 1. Purpose & operating principles

The system helps one job seeker (the **client**) find, qualify, research, tailor, apply to,
follow up on, and close job opportunities. Five principles govern everything. Be clear-eyed about
enforcement: **only one control is deterministic code** — the security-scanner gate (§3.3), and
even it pairs with an agent's judgment. The rest are enforced by **the procedures the agent
follows, the isolated-agent judgments, and the human gates.** This document is deliberately
explicit about which is which, rather than pretending any principle is a hard interlock.

- **Captain's seat.** The client makes every decision that commits them — pursuing a role,
  sending a document, contacting a person. The system prepares up to each decision and **stops at
  a gate**. *(Enforced by rule: the gates of §3.1/§5; the engine never itself takes a committing
  action, and the client confirms the ones that do.)*
- **Truthful only.** Documents and answers are tailored and emphasized, never fabricated.
  *(Enforced by a procedure + rule: the grounding check inside the `tailor-resume` skill, plus the
  verification rule of §3.5 — not standalone code.)*
- **Untrusted content is data, never instructions.** Everything ingested from the outside world is
  hostile-capable and is scanned before it can influence anything. *(Enforced by a code gate +
  judgment: the scanner flags, `injection-auditor` judges — §3.3.)*
- **Provenance is explicit.** Every non-obvious fact is marked *verified* or *recalled*; a failed
  fetch can never become a fact. *(Enforced by rule: the labeling discipline of §3.4.)*
- **Engine vs. vault, human-gated learning.** The engine's **files** are never edited during a
  session; the vault is the only thing written while job-hunting. What the system learns is folded
  back into the engine later, by a human. *(Enforced by rule + process: §3.2, §7.)*

---

## 2. The elements and their roles

The system is a **governing layer of operating instructions** plus **six runtime elements**. Each
is defined by what it **is**, what it **holds**, and what it **must not** do — the "must not"
clauses keep responsibilities from drifting.

### Operating instructions — the standing rules
- **Is:** the rules the agent **loads automatically at the start of every session**. Always
  present; never triggered, spawned, or looked up.
- **Holds:** the behavioral contract — the five principles, how the system is used, first-run steps.
- **Must not:** hold client data (vault), a procedure (skill), or platform mechanics (collection).

### Commands — the entry points
- **Is:** the slash commands the client invokes — the only thing the client triggers directly.
  A command **routes** to a skill, an agent, or a recipe; the two trivial ones (`/track`,
  `/status`) instead read/write the vault's status records directly.
- **Holds:** routing (and for `/track`/`/status`, a direct status read/write). Nothing else.
- **Must not:** carry platform know-how, or take a committing action without the client's go-ahead.

### Skills — the procedures
- **Is:** the multi-step "how we do this well" the agent follows (onboarding, analyzing a posting,
  scouting a company, tailoring documents).
- **Holds:** ordered steps, the quality bar, the hand-offs, and where to gate.
- **Must not:** hold client data (vault) or platform mechanics (collection).

### Agents — the isolated specialists
- **Is:** focused workers spawned in their **own context** for one judgment, isolated so the
  result isn't anchored by the main thread.
- **Holds:** a narrow mandate and its own reasoning; returns a result, not a running dialogue.
- **Must not:** be where durable knowledge lives; anything worth keeping is written to the vault.

### Collections — the compounding recipe base
- **Is:** verified, runnable console recipes for how the outside world works — finding jobs and
  submitting forms on each platform, and each research task. **This is the part designed to grow.**
  A recipe is a *procedure the agent runs and adapts each time* (it may drive a browser); it is not
  deterministic code.
- **Holds:** exact commands, field maps, gotchas, and per-recipe a **self-check (validate by
  readback)** and a **last-verified date**, so a rotted recipe is detected, not trusted blindly.
- **Organized by how a recipe is FOUND:** *platform recipes* discovered by key (job URL host →
  platform folder); *named recipes* an agent or command calls by name. *(Growth + staleness: §7.)*
- **Must not:** hold anything about the specific client (vault).

### Scripts — the deterministic code core
- **Is:** the small set of real programs kept because a task must be **deterministic** (identical
  output every run) or is a **safety gate**. Exactly two: the **security scanner** and the
  **document renderer**. (The renderer happens to drive headless Chromium, but the reason it's code
  is that its output must be identical and inspectable — not merely that a browser is involved.)
- **Holds:** deterministic logic only.
- **Must not:** absorb work a recipe can do. The dividing line is determinism/safety, **not**
  "uses a browser" — an adaptive browser procedure (like filling a live form) is a recipe.

### Memory (the vault) — the client's private record
- **Is:** the client's private, cumulative store and the system's long-term memory of *this*
  person and *this* search. Gitignored; never shared with the engine.
- **Holds — two kinds of thing:**
  - **Client-private data** — profile, applications, pipeline state, contacts, research outputs.
  - **Discovered *public* facts about a company** — e.g. its ATS + board slug, recorded in that
    company's `company.yaml`. This is generic knowledge, not client-private; it lives in the vault
    *only because the engine's files are read-only during a session*, and is a candidate for
    promotion into the engine (§7).
- **Must not:** hold anything the engine's own files should hold long-term (that's what promotion
  is for).

> "Memory" here means the vault — the durable record of the search. It is distinct from ephemeral
> session context and from any general-purpose memory facility of the host.

### The roster — every named element (so this document is self-contained)

**Commands:** `/onboard` set up the profile · `/scout` scan one company's board and rank fits ·
`/lead` capture one posting URL as a new application · `/apply` qualify a lead and, once the client
approves, draft its documents · `/recon` research a company · `/interviewer` profile an interviewer ·
`/submit` fill an application form and hand off for the client to submit · `/track` log an update ·
`/status` show the pipeline. *(Routing: `/onboard`→`onboard` skill; `/scout`→`scout-company` skill;
`/lead`→**capture-posting** recipe; `/apply`→`analyze-posting` + `fit-assessor`, then `tailor-resume`;
`/recon`→`company-recon` agent; `/interviewer`→`interviewer-recon` agent; `/submit`→platform
**submit-application** recipe; `/track` and `/status` act directly on the vault. So the four commands
backed by neither a skill nor an agent are `/lead`, `/submit`, `/track`, `/status` (`/lead` and
`/submit` → recipes; `/track` and `/status` → direct vault access).)*

**Skills:** `onboard` · `analyze-posting` (parses the posting **and records the single security
disposition** for it) · `scout-company` · `site-playbooks` (the discipline for *when* to read platform
know-how and record per-company facts — the mechanics themselves live in the platform recipes) ·
`tailor-resume` (draft → ground-check → verify → voice-check → render).

**Agents:** `fit-assessor` (apply/stretch/skip + 0–100) · `company-recon` (orchestrates public-asset
research; dispatches `mobile-recon`) · `mobile-recon` (downloads a **public** APK, decompiles it with
jadx/apktool, reads manifest/endpoints/SDKs) · `interviewer-recon` (behavioral read from public
footprint → coaching) · `injection-auditor` (on a scanner flag, **judges whether the flagged content
is a genuine trap** — never executes it) · `voice-auditor` (removes AI-writing tells, truthfully).

**Collections:** *platform recipes* (per platform: **find-jobs**, **submit-application**) for
Greenhouse, Lever, Ashby, Workday, LinkedIn; *named recipes* **capture-posting**, **github-org-repos**,
**web-bundles**, **source-capture**, **apk-decompile**.

**Scripts:** **security scanner** (screens untrusted content; feeds `injection-auditor`) ·
**document renderer** (tailored markdown → PDF).

**Supporting engine files:** `templates/` (the blank vault scaffolding `onboard` copies in) and
`config/` (engine configuration — defaults). These are engine data, not runtime elements; the
`onboard` skill reads `templates/`.

### Where each element lives — folder structure

Two homes only: `.claude/` is the entire engine; `vault/` is the client's private memory.
`CLAUDE.md`, `README.md`, `SYSTEM.md` are the engine's top-level docs at the repo root.

```
job-search/
├── CLAUDE.md · README.md · SYSTEM.md          # engine docs (CLAUDE.md auto-loads each session)
│
├── .claude/                     ═══ ENGINE — files read-only at runtime ═══
│   ├── commands/                #  the entry points (one .md each)
│   │   ├── onboard.md  scout.md  lead.md  apply.md  recon.md
│   │   └── interviewer.md  submit.md  track.md  status.md
│   ├── skills/                  #  the procedures (one folder each, holding SKILL.md)
│   │   ├── onboard/  analyze-posting/  scout-company/
│   │   └── site-playbooks/  tailor-resume/
│   ├── agents/                  #  the isolated specialists (one .md each)
│   │   ├── fit-assessor.md  company-recon.md  mobile-recon.md
│   │   └── interviewer-recon.md  injection-auditor.md  voice-auditor.md
│   ├── collections/             #  the compounding recipe base (grows with use — §7)
│   │   ├── platforms/           #    found BY KEY: job URL host → folder
│   │   │   └── <greenhouse|lever|ashby|workday|linkedin>/
│   │   │        ├── README.md      #  platform "brain" + index to its recipes
│   │   │        └── *.md           #  find-jobs, submit-application (each carries a self-check)
│   │   └── recipes/             #    called BY NAME by an agent or command (flat)
│   │        └── capture-posting.md  github-org-repos.md  web-bundles.md  source-capture.md  apk-decompile.md
│   ├── scripts/                 #  code core — the two deterministic tools
│   │   ├── scan…                #    security scanner
│   │   └── render…              #    document renderer
│   ├── templates/               #  blank vault scaffolding — copied into vault/ by onboard
│   └── config/                  #  engine configuration
│
└── vault/                       ═══ MEMORY — the client's PRIVATE record (gitignored) ═══
    ├── profile/                 #  who the client is — the source everything tailors from
    │   ├── cv.md  narrative.md  preferences.md
    │   └── cv-source/           #    the original CV file(s) as ingested
    ├── companies/               #  one folder per employer — forget a company = rm this one folder
    │   └── <company>/
    │       ├── company.yaml     #    CANONICAL per-company facts: ATS + board slug, form quirks
    │       ├── applications/    #    one per role pursued (a "lead" is just stage=lead)
    │       │   └── <role--date>/
    │       │       ├── posting.md · posting.raw.html   # captured posting ← scanned (§3.3)
    │       │       ├── analysis.md          # posting analysis + fit verdict
    │       │       ├── status.yaml          # schema_version, stage, timeline, contacts,
    │       │       │                        #   next_action, next_action_date, security_disposition,
    │       │       │                        #   source (e.g. a recruiters/<id> that sent the lead)
    │       │       └── docs/                # resume.pdf, cover-letter.pdf
    │       ├── research/        #    roles.json/md, company-research.md, bundles/ (scanned)
    │       ├── people/          #    people who work INSIDE this company — interviewers, hiring
    │       │                    #      managers; what we know about them (gone when company forgotten)
    │       └── _sources/        #    saved primary sources a verified claim points to (§3.4)
    ├── recruiters/              #  EXTERNAL lead-generators — not tied to one company; tracked
    │   └── <recruiter>/         #      separately (who they are + leads sent). forget = rm one folder
    ├── company-registry.yaml    #  OPTIONAL derived index (fast company→ATS lookup; not-yet-pursued
    │                            #    targets). Canonical source is each company.yaml — §7
    ├── playbook-notes.md        #  learnings captured mid-session, to promote into the engine — §7
    └── .sessions/               #  the client's OWN browser logins (e.g. LinkedIn) for /submit
        └── linkedin/
```

The vault has **three top-level entities**: the client (`profile/`), **companies** (each with its
own applications, research, insider people, and sources), and **recruiters** (external, cross-company
lead-generators). Company research is written once per company and reused across its roles.
**Rule the tree encodes:** the engine's files under `.claude/` are never edited at runtime;
everything under `vault/` is the private, writable memory.

---

## 3. Interaction rules (invariants)

### 3.1 Captain's seat — the three gates
Exactly three actions commit the client, and each has a gate where the client must approve first:
1. **Pursue a role** — at the end of Decide, after the fit verdict, before any drafting.
2. **Send a document / submit a form** — the client reviews and clicks Submit; the engine never clicks it.
3. **Contact a person** — the client sends the message; the system only drafts it.

Everything between gates is preparation and writes only to the vault. This is a rule the agent
obeys and the human confirms — not a hard interlock; the design states that honestly (§1).

### 3.2 Engine files read-only, vault writable
"Read-only at runtime" means the engine's **own files** (`.claude/…`) are never edited during a
session. The engine's running logic — skills and agents — *does* write, but only ever to the
**vault**. Changing the engine itself is separate "build the tool" work (§7).

### 3.3 Scan every ingestion surface; one adjudication per artifact
Any untrusted external content — job postings (`/lead`, `/apply`), scraped boards (`/scout`), web
bundles, **decompiled APK strings**, and recon sources — is **treated as data and scanned before it
can influence a document or decision**, whether or not it is saved to disk. The deterministic
**scanner** flags suspicious content; on a flag, the **`injection-auditor`** agent judges intent:
- **Trap** → handle per §4 (stop, use only genuine requirements).
- **Benign** (false positive) → record a clean disposition and proceed.
- **Scanner can't run, or the auditor returns no verdict** → **fail closed** (§4): treat the
  content as an unresolved trap; do not let it influence any document or decision.

The result is recorded **once per artifact** — for a posting, `analyze-posting` writes
`security_disposition` in `status.yaml`; for a research artifact, the capturing agent records it
beside the artifact. Later steps trust that record and don't re-adjudicate.

### 3.4 Provenance is explicit
Every non-obvious fact is tagged **verified** (observed this run, with its source) or **recalled**
(prior knowledge — confirm before use). A failed fetch/tool degrades the claim to *recalled* and is
never presented as verified. This is a labeling discipline the agent applies (not a code check);
anything a cover letter or interview answer will quote must be verified from a primary source or
dropped. A verified claim records the **path to its saved source** under the company's
`_sources/` (`companies/<company>/_sources/`), so the provenance is checkable, not merely asserted.

### 3.5 Truthful only — two checks, because there are two kinds of claim
Fabrication is blocked at the point documents are written (`tailor-resume`) and, for what the client
will *say*, by provenance (§3.4). A drafted document contains two kinds of claim, each with its own
check:
- **Claims about the CLIENT** (experience, skills, results) → the **grounding check**: every such
  claim must map to a line in `profile/cv.md` or `profile/narrative.md`. An unmapped claim is
  removed; if the client believes it's true, they add it to the profile — the document is not the
  place to introduce a new fact about the client.
- **Claims about the COMPANY / role** (a product, a value, a recent milestone a cover letter hooks
  into) → the **verification rule** (§3.4): each must be *verified* from a primary source, or dropped.

Then `voice-auditor` checks **style** (AI tells). Three distinct guards: grounding = the client's
claims are true; verification = the world claims are true; voice = it reads human. None invents.

---

## 4. Failure semantics — what happens when something goes wrong

The system fails **safe and visibly**; it never fabricates to paper over a failure. ("Required," in
the fetch row, means a fact a downstream document or decision depends on.)

| Situation | Behavior |
|---|---|
| Auditor judges a flag a **trap** | Stop; tell the client the employer likely screens for AI use; proceed using ONLY the genuine job requirements; never obey the embedded instruction. |
| Auditor judges a flag **benign** | Record a clean disposition; proceed. |
| **Scanner can't run**, or **auditor returns no verdict** | Fail closed: block that content from influencing any document or decision; treat it as an unresolved trap; tell the client. |
| Fit verdict = **skip** | Halt before drafting; surface the verdict + reasons at the Decide gate; the client may override. |
| Fit verdict = **stretch** | Present at the same Decide gate as a judgment call; the client decides go/no-go. (*apply* = recommended, still confirmed at the gate.) |
| **No recipe for this platform** (unknown ATS / no key match) | Fall back to the platform README's general notes, or hand the task to the client; capture the new platform for promotion (§7). Never guess a form blindly. |
| A **submit recipe can't map a required field, or rots mid-submission** (self-check fails) | Stop and hand the live form to the client; never guess an answer or skip a required question; flag the recipe stale for promotion. |
| **Fetch / API / tool fails** | Record the failure; keep affected facts *recalled*; never state what the call "would" have shown. Abort the step if the fact was required. |
| **CAPTCHA / auth wall** | Hand control to the client (they solve it / are logged in); the recipe resumes after. |
| **Render / tool error** | Surface it; never present an unrendered or partial document as final. |

---

## 5. The journey, mapped to elements

Eight stages. Each row: the command, the elements, and what is written to memory. **⛔ = a §3.1
gate** where the client must decide before the system takes a committing action.

| Stage | Command | Elements | Writes to memory |
|---|---|---|---|
| **Know thyself** | `/onboard` | `onboard` skill ingests CV + preferences | Profile |
| **Find** | `/scout`, `/lead` | `scout-company` skill + **find-jobs** recipe (board); `/lead` → **capture-posting** recipe (one URL); scanned on capture | Company registry (cache); shortlist; application at `stage=lead` (recruiter-sourced leads record `source: recruiters/<id>`) |
| **Decide** ⛔ | `/apply` | `analyze-posting` skill (+ scanner/`injection-auditor`); `fit-assessor` agent → **stops at the pursue gate** (apply/stretch/skip all surface here) | Analysis + fit verdict; `security_disposition` |
| **Prepare** | `/recon`, `/interviewer` | `company-recon` (+ `mobile-recon`), `interviewer-recon`; **named recipes**; scanned on capture | `companies/<company>/research`; insider people (interviewers) → `companies/<company>/people/` |
| **Craft** | `/apply` (after the pursue gate) | `tailor-resume` skill → grounding + verification checks + `voice-auditor` → renderer script | Draft résumé + cover letter (PDF) |
| **Apply** ⛔ | `/submit` | `/submit` command → **submit-application** recipe (explore → answer → validate); client does CAPTCHA + Submit | `status.yaml` → applied |
| **Follow up** | `/track`, `/status` | `/track` and `/status` act directly on `status.yaml`; `/status` **surfaces threads whose `next_action_date` is overdue** | Timeline, contacts, next action |
| **Close** ⛔ | `/interviewer`, `/track` | `interviewer-recon` agent drafts prep; **the client sends any outreach** (contact gate) | Interview prep; outcome screen → interview → offer |

**Notes:** Craft is *not* gated — it's preparation after the pursue gate, and writes only to the
vault. The **pursue gate** (Decide) is where every fit verdict lands: *skip* halts, *stretch* is a
judgment call, *apply* is recommended — but the client confirms before any drafting. The **contact
gate** (§3.1 #3) applies wherever the client would message a person — during **Follow up** as well
as Close, not only the row it's marked on. **"Scanned on capture"** in any row means the full §3.3
path — the scanner flags, `injection-auditor` judges, the disposition is recorded once — not only
the posting at Decide; the auditor engages on *any* flagged ingest (Find, Decide, Prepare alike).

**Pipeline stages** (`status.yaml`): `lead → assessing → drafting → ready → applied → screen →
interview → offer`, plus terminal `rejected` / `withdrawn`.

---

## 6. Classification table (one-glance check)

| Element | Role | Triggered by | Reads | Writes |
|---|---|---|---|---|
| **Operating instructions** | Standing rules governing the agent | Auto-loaded every session | — | — |
| **Command** | Entry point / router (`/track`,`/status` also touch state) | The client | `status.yaml` (track/status) | `status.yaml` (track only) |
| **Skill** | Procedure | A command / another skill | Vault, collections | Vault |
| **Agent** | Isolated specialist judgment | A skill / command | Vault, collections, public web (scanned) | Vault (result) |
| **Collection** | Compounding recipe base — grows with use | A skill, agent, **or command** (by key or name) | The live platform | — (engine files unchanged; refined via §7) |
| **Script** | Deterministic tool (scan, render) | A skill/agent | A file it's given | An output file in the vault |
| **Vault (memory)** | Client's private record + discovered-fact cache | Skills & agents | — | Written only by engine *logic* (skills/agents); engine *files* stay unchanged |

**Placing a new capability:** client-triggered entry point → **command**; multi-step procedure →
**skill**; one isolated judgment → **agent**; "how the outside world works," run as an adaptive
console procedure → **collection**; must be **deterministic or a safety gate** → **script** (note:
*not* "uses a browser"); specific to this client → **vault**.

---

## 7. How the system learns, compounds, and stays fresh

The engine's files are read-only *during* a session, so growth is a **deliberate two-step loop**,
never a silent runtime edit:

1. **Capture (runtime, automatic).** When the agent solves a new platform, hits a wall, or learns a
   reusable fact, it writes to the vault: generic learnings → `playbook-notes.md`; a discovered
   public fact (company → ATS + slug) → that company's `company.yaml`. This is why such generic
   facts live in the vault — the engine's files can't be written mid-hunt, so they wait there for
   promotion.
2. **Promote (between hunts, human-gated).** The client folds a captured learning into a collection
   (a new/updated recipe) or the registry into the engine. This is "build the tool" work — the only
   time the engine's files change. Captain's seat applies: a human decides what becomes permanent.

**Staleness.** Platforms change their forms. Every platform recipe carries a **self-check (validate
by readback)** and a **last-verified date**; when the self-check fails, the recipe is flagged stale
(§4) rather than trusted, and fixing it is the next promotion. A silently-rotting recipe is the
failure this prevents.

**Outcomes as data.** The vault accumulates pipeline outcomes (which postings reached a screen, how
fit scores compared to reality). `/status` surfaces this so the client can recalibrate what to
pursue and how to tailor. The profile is **living**, not write-once: re-running `/onboard` or
editing `profile/` updates the source everything tailors from.

### Format commitments — reserve the shape now (cheap now, expensive to retrofit)
These are fixed up front because retrofitting them once data exists is painful or impossible. The
*mechanism/policy* can come later; the *format* cannot.
- **One company-slug canonicalizer.** A single function maps a company name → its slug, used by
  both `companies/<company>/` and `company-registry.yaml`, so a company always resolves to the same
  folder/key. (Forked directories are hand-merge cleanup later.)
- **`schema_version` in every `status.yaml`,** from the first record — so a later promotion that
  renames a field can detect and migrate old records safely.
- **Provenance marker format:** a *verified* claim records the **path to its saved source** under
  `companies/<company>/_sources/` (§3.4). Enforcing it in the renderer can wait; the format can't —
  back-filling means re-fetching sources that may be gone.
- **Structured `playbook-notes.md`:** each learning is a fixed stanza — *platform / what broke /
  what worked* — not free prose, so promotion is a mechanical read, not an archaeology dig.
- **Every fit score carries its thresholds.** Store the band set in force when the score was
  assigned; a bare "74" from March isn't comparable to a "74" from June once bands move — and that
  comparability is the whole point of recalibration.
- **Every named person has exactly one home, so erasure is a single delete** (§8): people who work
  **inside** a company live under `companies/<company>/people/` (and are wiped when the company is
  forgotten); **recruiters**, who generate leads across companies, live top-level under
  `recruiters/`. A person is filed in one place, never both.
- **`last-verified` on every recipe from day one,** populated even before a staleness policy exists
  (§7 staleness). The policy is postponable; the field being absent on the first recipes is not.

---

## 8. Governance & risk boundaries

Stated plainly, because these are the system's highest-liability edges.

- **Truthful only** is enforced by the grounding + verification checks (§3.5), not good intentions.
- **Authenticated actions run under the client's OWN session.** `/scout` and `/submit` may use the
  client's logged-in browser (e.g. LinkedIn). The client is in the loop, and the terms-of-service
  and account risk are the client's — the system states this rather than hiding it inside a narrow
  definition of "acting outward." Public ATS APIs are preferred where available.
- **`interviewer-recon` profiles a named private person.** Public footprint only; each inference
  carries a confidence mark and follows the verified/recalled rule; it never exploits sensitive
  personal circumstances. Every named person has one home — company insiders under
  `companies/<company>/people/`, recruiters under `recruiters/` — so forgetting a **person**, a
  whole **company**, or a **recruiter** is each a single delete with nothing left scattered. These
  profiles inform rapport and communication — they are not a dossier.
- **Recon is public assets and the client's own accounts only** — served bundles, published APKs,
  exposed job APIs, the client's own demo/trial logins. No non-public systems, no impersonation, no
  anti-bot-bypass-as-a-service, no mass spam.

---

## 9. Summary

A client goes from "here's my CV" to a tracked pipeline of truthful, tailored, submitted
applications — deciding at every gate, on an engine that scans everything it ingests, checks every
claim (the client's against the profile, the world's against a primary source), fails safe and
visibly, and compounds its know-how through a human-gated learning loop. Commands are the entry
points, skills the procedures, agents the isolated judgments, collections the growing world-
knowledge, scripts the deterministic guarantees, and the vault the memory — all under operating
rules loaded fresh every session.
