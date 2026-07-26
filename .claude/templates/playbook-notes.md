# Playbook notes — learnings captured mid-hunt, awaiting promotion into the engine

<!--
When the agent solves a new platform, hits a wall, or learns a reusable fact, it appends a fixed
stanza here. Between hunts, a human promotes these into the engine (a new/updated recipe). Structured,
not free prose, so promotion is a mechanical read.

Stanza formats — one per learning.

Platform / task learning:

## <platform or task>
- what broke: <what didn't work / what changed since last time>
- what worked: <the exact steps/commands that succeeded>
- observed: <date the above was actually seen working>

Capability gap (the engine was short something):

## <capability needed>   (capability gap)
- needed: <what the task required that the engine lacked>
- element type: command | skill | agent | recipe | script | vault
- how solved / what to build: <the direction for whoever promotes it>
- dependency + install: <the tool + how to make it available (npx/brew/pip/...), or "none">
- verify by: <how to confirm it works before it ships>
-->
