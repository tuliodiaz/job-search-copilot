#!/usr/bin/env python3
"""Security scanner — deterministic first-pass flagger for untrusted ingested content.

One of the engine's two deterministic scripts. Its job is NOT to judge intent — it FLAGS, cheaply,
predictably, and inspectably, so that:
  - flagged content is handed to the injection-auditor agent for the trap/benign judgment, and
  - the system can FAIL CLOSED: if this scanner cannot run, the caller blocks the content from
    influencing any document or decision.

High recall by design: it over-flags and lets the auditor filter false positives. Deterministic —
same input always yields the same output; no network, no randomness, Python standard library only.

Usage:
    python3 scan.py <file>

Output: a JSON report on stdout (see REPORT SHAPE below).
Exit codes:
    0   ran, no flags            -> status "clean"    (proceed)
    10  ran, one or more flags   -> status "flagged"  (hand findings to injection-auditor)
    2   could not run            -> status "error"    (caller FAILS CLOSED)

REPORT SHAPE (stdout, always valid JSON):
    {
      "scanner_version": "1",
      "scanned_file": "<path>",
      "status": "clean" | "flagged" | "error",
      "flag_count": <int>,
      "findings": [ {"rule": "...", "why": "...", "line": <int>, "snippet": "..."}, ... ],
      "error": "<message, only when status == error>"
    }
"""
from __future__ import annotations
import json
import re
import sys
import unicodedata

SCANNER_VERSION = "1"
SNIPPET_MAX = 120

# Deterministic detection rules, evaluated in this fixed order. Each is (rule_id, why, compiled
# regex). These target the SHAPE of prompt-injection / hidden-instruction content, not any specific
# employer. Recall over precision: a false positive costs one auditor judgment; a miss costs a trap.
TEXT_RULES: list[tuple[str, str, re.Pattern[str]]] = [
    ("imperative-override",
     "instruction to ignore/override prior instructions",
     re.compile(r"(?i)\b(ignore|disregard|forget)\b[^.\n]{0,40}\b(previous|prior|above|earlier|all)\b"
                r"[^.\n]{0,30}\b(instruction|instructions|prompt|prompts|context|rule|rules)?")),
    ("role-reassignment",
     "attempt to reassign the assistant's role/behavior",
     re.compile(r"(?i)\b(you\s+are\s+now|from\s+now\s+on\s+you|act\s+as\s+an?|pretend\s+to\s+be|"
                r"your\s+new\s+(instructions|role|task)\s+(is|are))\b")),
    ("ai-addressed",
     "content that addresses the AI/assistant or its system prompt directly",
     re.compile(r"(?i)\b(as\s+an?\s+(ai|language\s+model|assistant)|system\s+prompt|"
                r"your\s+(instructions|system\s+prompt|guidelines|rules))\b")),
    ("role-marker",
     "chat/role delimiter that could inject a new turn",
     re.compile(r"(?im)(^\s*(system|assistant|user)\s*:|<\|im_(start|end)\|>|\[/?INST\]|"
                r"###\s*(system|instruction))")),
    ("suppression",
     "instruction to hide information from the user",
     re.compile(r"(?i)\bdo\s+not\s+(tell|inform|mention|reveal|disclose)\b")),
    ("scoring-injection",
     "instruction to force a rating/recommendation/score",
     re.compile(r"(?i)\b(rate|score|recommend|rank|approve)\b[^.\n]{0,40}"
                r"(100|full\s+marks|highest|top|maximum|automatically)")),
    ("exfil-or-tool",
     "instruction referencing data exfiltration or command execution",
     re.compile(r"(?i)\b(curl|wget|base64\s+decode|send\s+(the\s+)?(email|data|message)\s+to)\b|fetch\(")),
    ("css-hidden",
     "CSS that hides text from a human reader but not from the model",
     re.compile(r"(?i)(display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0|"
                r"color\s*:\s*#?(fff(fff)?|white)\b)")),
]

# Zero-width / bidi / invisible control characters used to hide instructions.
HIDDEN_CHARS = {
    "​": "ZERO WIDTH SPACE", "‌": "ZERO WIDTH NON-JOINER",
    "‍": "ZERO WIDTH JOINER", "⁠": "WORD JOINER", "﻿": "ZERO WIDTH NO-BREAK SPACE",
    "\u200E": "LEFT-TO-RIGHT MARK", "\u200F": "RIGHT-TO-LEFT MARK",
    "\u202A": "LEFT-TO-RIGHT EMBEDDING", "\u202B": "RIGHT-TO-LEFT EMBEDDING",
    "\u202C": "POP DIRECTIONAL FORMATTING", "\u202D": "LEFT-TO-RIGHT OVERRIDE",
    "\u202E": "RIGHT-TO-LEFT OVERRIDE",
}

HTML_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _snippet(text: str, start: int, end: int) -> str:
    frag = text[start:end].replace("\n", " ").replace("\r", " ").strip()
    if len(frag) > SNIPPET_MAX:
        frag = frag[:SNIPPET_MAX] + "…"
    return frag


def scan_text(text: str) -> list[dict]:
    """Return a deterministic, ordered list of findings for the given content."""
    findings: list[dict] = []

    for rule_id, why, pattern in TEXT_RULES:
        for m in pattern.finditer(text):
            findings.append({
                "rule": rule_id,
                "why": why,
                "line": _line_of(text, m.start()),
                "snippet": _snippet(text, m.start(), m.end()),
            })

    # Hidden HTML comments containing letters (a common place to smuggle instructions).
    for m in HTML_COMMENT.finditer(text):
        body = m.group(1)
        if re.search(r"[A-Za-z]{3,}", body):
            findings.append({
                "rule": "html-comment",
                "why": "hidden HTML comment containing text (not visible to a human reader)",
                "line": _line_of(text, m.start()),
                "snippet": _snippet(text, m.start(), m.end()),
            })

    # Invisible / directional control characters.
    seen_lines: set[tuple[str, int]] = set()
    for i, ch in enumerate(text):
        if ch in HIDDEN_CHARS:
            key = (ch, _line_of(text, i))
            if key in seen_lines:
                continue  # one finding per (char, line) keeps output stable and readable
            seen_lines.add(key)
            name = HIDDEN_CHARS[ch]
            findings.append({
                "rule": "hidden-unicode",
                "why": f"invisible character {name} (U+{ord(ch):04X}) can hide instructions",
                "line": _line_of(text, i),
                "snippet": f"U+{ord(ch):04X} {name}",
            })

    # Sort by line, then rule, for stable deterministic ordering regardless of detection order.
    findings.sort(key=lambda f: (f["line"], f["rule"]))
    return findings


def scan_file(path: str) -> dict:
    report = {
        "scanner_version": SCANNER_VERSION,
        "scanned_file": path,
        "status": "clean",
        "flag_count": 0,
        "findings": [],
    }
    try:
        with open(path, "r", encoding="utf-8", errors="surrogateescape") as f:
            text = f.read()
    except OSError as e:
        report["status"] = "error"
        report["error"] = f"cannot read file: {e}"
        return report

    findings = scan_text(text)
    report["findings"] = findings
    report["flag_count"] = len(findings)
    report["status"] = "flagged" if findings else "clean"
    return report


_EXIT = {"clean": 0, "flagged": 10, "error": 2}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        report = {
            "scanner_version": SCANNER_VERSION, "scanned_file": None, "status": "error",
            "flag_count": 0, "findings": [], "error": "usage: scan.py <file>",
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return _EXIT["error"]
    report = scan_file(argv[1])
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return _EXIT[report["status"]]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
