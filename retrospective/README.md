# Retrospective

Feedback loop for improving the engine between hunts. After a session, capture **what the tool did
well, where it misled, and what to change** — focused on *process and the engine*, not the details of
any one company or application.

Each session drops a timestamped retrospective here (`YYYY-MM-DDTHHMMSS-session-retro.md`) — the time
component keeps multiple sessions in the same day from colliding.

- **playbook-notes.md** (in the vault) = tactical, mid-hunt: "I hit X, here's the working fix."
- **retrospective/** (here, tracked in the repo) = per-session **observations**: "across this session,
  here's what the engine got right, where it misled, what felt off." Travels with the repo.

## One retro = observations, NOT a fix list

A single session is **n = 1**. An individual retro **records evidence — it does not prioritize,
prescribe fixes, or rank importance.** Doing so from one data point is premature closure: you can't
yet tell what recurs, what's fixable, or whether the obvious fix is the right one. (A session-local fix
that was already made and verified in the moment is fine to note as done — that's different from
prescribing engine changes.)

Prioritization and "what to actually change in `.claude/`" is a **separate, cross-retro synthesis**
done once there are *several* retros and patterns are visible — ideally its own document
(`SYNTHESIS.md`) a human writes after reading many sessions. Don't prioritize inside a single retro.

Structure of one retro: client feedback (primary) · what worked · where it misled / fell short ·
agent-vs-engine observations · signals to watch across future retros · meta/interaction notes.
