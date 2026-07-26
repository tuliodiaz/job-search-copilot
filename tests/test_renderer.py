#!/usr/bin/env python3
"""Behavioral tests for the document renderer (.claude/scripts/render.py).

The markdown->HTML transform is deterministic and dependency-free, so it is unit-tested directly.
The HTML->PDF step needs a Chromium-family browser; that part is exercised end-to-end only when one
is present (skipped otherwise, and reported as skipped — never silently passed).

Run:  python3 tests/test_renderer.py
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDER = os.path.join(ROOT, ".claude", "scripts", "render.py")
FIX = os.path.join(ROOT, "tests", "fixtures", "sample-resume.md")

_spec = importlib.util.spec_from_file_location("render", RENDER)
render = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(render)


class TestTransform(unittest.TestCase):
    def test_headings_and_inline(self):
        html = render.markdown_to_html("# Title\n\nSome **bold** and *italic* and `code`.")
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)
        self.assertIn("<code>code</code>", html)

    def test_lists_links_hr(self):
        html = render.markdown_to_html("- one\n- two\n\n1. a\n2. b\n\n[site](https://x.io)\n\n---")
        self.assertIn("<ul>", html)
        self.assertIn("<li>one</li>", html)
        self.assertIn("<ol>", html)
        self.assertIn('<a href="https://x.io">site</a>', html)
        self.assertIn("<hr>", html)

    def test_html_is_escaped(self):
        html = render.markdown_to_html("a < b & c > d")
        self.assertIn("a &lt; b &amp; c &gt; d", html)

    def test_deterministic(self):
        with open(FIX, encoding="utf-8") as f:
            md = f.read()
        self.assertEqual(render.build_html(md, "default"), render.build_html(md, "default"))

    def test_full_doc_has_template_and_title(self):
        with open(FIX, encoding="utf-8") as f:
            md = f.read()
        html = render.build_html(md, "default")
        self.assertIn("<!doctype html>", html)
        self.assertIn("<title>Jordan Rivera</title>", html)
        self.assertIn("@page", html)  # the pinned CSS template is embedded


class TestCli(unittest.TestCase):
    def test_html_only_needs_no_browser(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "r.pdf")
            p = subprocess.run([sys.executable, RENDER, FIX, out, "--html-only"],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0)
            self.assertTrue(os.path.isfile(os.path.join(d, "r.html")))

    def test_missing_input_fails_cleanly(self):
        p = subprocess.run([sys.executable, RENDER, os.path.join(FIX, "nope.md"), "/tmp/x.pdf"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    @unittest.skipUnless(render.find_chrome(), "no Chromium-family browser in this environment")
    def test_end_to_end_pdf(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "resume.pdf")
            p = subprocess.run([sys.executable, RENDER, FIX, out], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertTrue(os.path.isfile(out))
            with open(out, "rb") as f:
                self.assertEqual(f.read(5), b"%PDF-")


if __name__ == "__main__":
    unittest.main(verbosity=2)
