#!/usr/bin/env python3
"""Structural validator for the Job-Search Copilot engine.

Proves the .claude/ engine is internally consistent WITHOUT running an agent or touching the network.
This is the deterministic backbone of "a fresh pull works out of the box": if this fails, the engine
is broken regardless of what any agent does.

It enforces, mechanically, the two conventions the project committed to:
  1. No rotting cross-links. Runtime files (.claude/**/*.md) must not link to other .md files
     (each is self-contained; global rules live once in CLAUDE.md). The element graph is expressed
     as structured frontmatter and RESOLVED here, so a broken reference fails the build.
  2. No untested recipes. A recipe claiming a last_verified DATE must carry a verified_by note;
     otherwise it must say last_verified: never. Fabricated-but-dated recipes fail the build.

Stdlib only. Run:  python3 tools/validate_structure.py
Exit code 0 = all checks pass, 1 = at least one failure.
"""
from __future__ import annotations
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAUDE = os.path.join(ROOT, ".claude")

errors: list[str] = []
checks = 0


def fail(msg: str) -> None:
    errors.append(msg)


def ok() -> None:
    global checks
    checks += 1


def rel(p: str) -> str:
    return os.path.relpath(p, ROOT)


def read(p: str) -> str:
    with open(p, encoding="utf-8") as f:
        return f.read()


def parse_frontmatter(path: str) -> dict[str, str] | None:
    """Minimal flat 'key: value' frontmatter parser (no external YAML dep).

    Returns a dict of the leading --- fenced block, or None if there is no frontmatter.
    Only flat scalar keys are supported — that is all the engine's frontmatter uses.
    """
    text = read(path)
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end].strip("\n")
    data: dict[str, str] = {}
    for line in block.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        data[key.strip()] = val.strip().strip('"').strip("'")
    return data


def md_files(base: str) -> list[str]:
    out: list[str] = []
    for dirpath, _dirs, files in os.walk(base):
        for fn in files:
            if fn.endswith(".md"):
                out.append(os.path.join(dirpath, fn))
    return out


# --- Check 1: no cross-links between runtime .md files -----------------------------------------
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def check_no_cross_links() -> None:
    for path in md_files(CLAUDE):
        for m in LINK_RE.finditer(read(path)):
            target = m.group(1).split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if target.endswith(".md"):
                fail(f"cross-link: {rel(path)} links to '{target}' "
                     f"(runtime files must be self-contained; put shared rules in CLAUDE.md)")
    ok()


# --- Check 2: commands have valid frontmatter and their routes resolve ---------------------------
def skill_path(name: str) -> str:
    return os.path.join(CLAUDE, "skills", name, "SKILL.md")


def agent_path(name: str) -> str:
    return os.path.join(CLAUDE, "agents", name + ".md")


def recipe_route_resolves(name: str) -> bool:
    """True if a recipe route target resolves to at least one recipe file.

    Collections are **one folder per outside system**: collections/<system>/<recipe>.md. Targets are
    collections-relative ('greenhouse/submit-application'), and **family routes** may carry a '<...>'
    placeholder — e.g. '/submit' routes to <ats>/submit-application, which passes as long as >=1
    system provides that recipe. The placeholder becomes a glob wildcard."""
    pat = re.sub(r"<[^>]+>", "*", name)  # <ats> -> *  (family route)
    return bool(glob.glob(os.path.join(CLAUDE, "collections", *pat.split("/")) + ".md"))


def check_commands() -> None:
    cmd_dir = os.path.join(CLAUDE, "commands")
    if not os.path.isdir(cmd_dir):
        fail("missing .claude/commands/ directory")
        return
    for path in sorted(md_files(cmd_dir)):
        fm = parse_frontmatter(path)
        if fm is None:
            fail(f"{rel(path)}: command has no frontmatter")
            continue
        if fm.get("kind") != "command":
            fail(f"{rel(path)}: expected kind: command, got {fm.get('kind')!r}")
        if not fm.get("name"):
            fail(f"{rel(path)}: command missing 'name'")
        rk = fm.get("route_kind")
        rt = fm.get("route_target", "")
        if rk == "vault":
            pass  # /track, /status act directly on the vault; no target required
        elif rk == "skill":
            if not os.path.isfile(skill_path(rt)):
                fail(f"{rel(path)}: routes to skill '{rt}' but {rel(skill_path(rt))} is missing")
        elif rk == "agent":
            if not os.path.isfile(agent_path(rt)):
                fail(f"{rel(path)}: routes to agent '{rt}' but {rel(agent_path(rt))} is missing")
        elif rk == "recipe":
            if not recipe_route_resolves(rt):
                fail(f"{rel(path)}: routes to recipe '{rt}' but no matching recipe file exists")
        else:
            fail(f"{rel(path)}: invalid route_kind {rk!r} (want skill|agent|recipe|vault)")
    ok()


# --- Check 3: skills / agents have consistent frontmatter --------------------------------------
def check_element_kind(subdir: str, kind: str, name_from) -> None:
    base = os.path.join(CLAUDE, subdir)
    if not os.path.isdir(base):
        return  # not built yet in this slice; nothing to validate
    if kind == "skill":
        files = [os.path.join(base, d, "SKILL.md") for d in os.listdir(base)
                 if os.path.isdir(os.path.join(base, d))]
    else:
        files = [p for p in md_files(base) if os.path.basename(p) != "README.md"]
    for path in sorted(files):
        if not os.path.isfile(path):
            fail(f"missing {rel(path)}")
            continue
        fm = parse_frontmatter(path)
        if fm is None:
            fail(f"{rel(path)}: {kind} has no frontmatter")
            continue
        if fm.get("kind") != kind:
            fail(f"{rel(path)}: expected kind: {kind}, got {fm.get('kind')!r}")
        expected = name_from(path)
        if fm.get("name") != expected:
            fail(f"{rel(path)}: name {fm.get('name')!r} does not match location (expected {expected!r})")
    ok()


# --- Check 4: recipes are never shipped untested-but-dated --------------------------------------
def check_recipes() -> None:
    coll = os.path.join(CLAUDE, "collections")
    recipe_files: list[str] = []
    if os.path.isdir(coll):
        recipe_files += [p for p in md_files(coll) if os.path.basename(p) != "README.md"]
    for path in sorted(recipe_files):
        fm = parse_frontmatter(path) or {}
        lv = fm.get("last_verified")
        if lv is None:
            # allow last-verified stated in the body as a labelled line
            m = re.search(r"last[_-]verified:\s*(\S+)", read(path))
            lv = m.group(1) if m else None
        if lv is None:
            fail(f"{rel(path)}: recipe missing last_verified")
            continue
        if lv != "never":
            body = read(path)
            if "verified_by" not in body and not (fm.get("verified_by")):
                fail(f"{rel(path)}: recipe claims last_verified: {lv} but has no verified_by proof "
                     f"(no recipe ships dated without evidence it was actually run)")
        if "self-check" not in read(path).lower():
            fail(f"{rel(path)}: recipe has no self-check (validate-by-readback) block")
    ok()


# --- Check 5: vault templates + config are present and schema-pinned ---------------------------
def check_templates_and_config() -> None:
    required = [
        ".claude/templates/profile/cv.md",
        ".claude/templates/profile/narrative.md",
        ".claude/templates/profile/preferences.md",
        ".claude/templates/profile/logistics.md",
        ".claude/templates/company-registry.yaml",
        ".claude/templates/leads-registry.yaml",
        ".claude/templates/playbook-notes.md",
        ".claude/config/status.schema.yaml",
        ".claude/config/defaults.yaml",
    ]
    for r in required:
        p = os.path.join(ROOT, r)
        if not os.path.isfile(p):
            fail(f"missing required engine file: {r}")
    for r in [".claude/config/defaults.yaml",
              ".claude/templates/company-registry.yaml",
              ".claude/templates/leads-registry.yaml",
              ".claude/config/status.schema.yaml"]:
        p = os.path.join(ROOT, r)
        if os.path.isfile(p) and "schema_version" not in read(p):
            fail(f"{r}: missing schema_version (format commitment)")
    ok()


# --- Check 6: templates/ contains ONLY vault scaffolding (no engine reference can leak) ----------
def check_templates_are_vault_only() -> None:
    """`.claude/templates/` is copied verbatim into the client's vault by onboard, so it must contain
    ONLY vault-appropriate scaffolding. Anything else (engine reference, schemas, docs) would leak
    into every client's private vault. The vault's only top-level entities are profile/, companies/,
    recruiters/, company-registry.yaml, leads-registry.yaml, playbook-notes.md."""
    base = os.path.join(CLAUDE, "templates")
    allowed = {"profile", "companies", "recruiters",
               "company-registry.yaml", "leads-registry.yaml", "playbook-notes.md"}
    if os.path.isdir(base):
        for entry in sorted(os.listdir(base)):
            if entry.startswith("."):
                continue
            if entry not in allowed:
                fail(f".claude/templates/{entry}: not vault scaffolding. templates/ is copied verbatim "
                     f"into the client's vault, so engine reference material must live elsewhere "
                     f"(e.g. .claude/config/).")
    ok()


# --- Check 7: CLAUDE.md exists and is the single source of the invariants -----------------------
def check_claude_md() -> None:
    p = os.path.join(ROOT, "CLAUDE.md")
    if not os.path.isfile(p):
        fail("missing CLAUDE.md (the auto-loaded operating instructions)")
    else:
        body = read(p).lower()
        for token in ["captain", "truthful", "untrusted", "provenance", "fail"]:
            if token not in body:
                fail(f"CLAUDE.md does not mention the '{token}' invariant")
    ok()


def main() -> int:
    check_no_cross_links()
    check_commands()
    check_element_kind("skills", "skill", lambda p: os.path.basename(os.path.dirname(p)))
    check_element_kind("agents", "agent", lambda p: os.path.splitext(os.path.basename(p))[0])
    check_recipes()
    check_templates_and_config()
    check_templates_are_vault_only()
    check_claude_md()

    print(f"ran {checks} check groups over .claude/\n")
    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS — engine structure is internally consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
