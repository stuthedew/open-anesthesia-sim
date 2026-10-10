---
id: PL-0C2S
title: No test holds docket.markdown's block reading to a reference CommonMark parser, so a rule the shared reader gets wrong - PL-B83V's closing pre tag line - is found by a sweep rather than failing CI the day a document first holds it
priority: P3
effort: M
status: done
classes: infra
feature: one-answer
touches: subprojects/docket/tests, subprojects/docket/src/docket/markdown.py, pyproject.toml, uv.lock
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
closed: 2026-10-10
pr: 1388
payoff: a block rule docket.markdown gets wrong fails CI against markdown-it-py the day a document or fixture first holds it, rather than waiting for a sweep to find it
verify: grep -qF '"markdown-it-py>=' pyproject.toml && grep -qF 'name = "markdown-it-py"' uv.lock && grep -qF 'from markdown_it import MarkdownIt' subprojects/docket/tests/test_markdown_reference.py
---

**Problem.** No test holds docket.markdown's block reading to a reference CommonMark parser, so a rule the shared reader gets wrong - PL-B83V's closing pre tag line - is found by a sweep rather than failing CI the day a document first holds it

**Decided 2026-10-06, in the thread for `PL-R417`'s closing sweep**
(project owner, 2026-10-06, ratified, over leaving `docket.markdown` held by
the one comparison of 2026-10-04). `docket.markdown` is the one block reader
every Markdown reader in docket and `tools/` takes, written by hand because
docket, the tools and the hooks run on the standard library alone. Its
docstring records a check against markdown-it-py 4.2.0 on every tracked
Markdown file on 2026-10-04, and nothing repeats it, so a block rule the
reader gets wrong is found only when a sweep probes for it. `PL-B83V`, a line
holding a closing `pre` tag that the reader does not take for an HTML block,
was found that way on 2026-10-06.

The tests can use what the tools cannot. markdown-it-py is MIT-licensed pure
Python (https://github.com/executablebooks/markdown-it-py), so as a dev
dependency it reaches the test environment without reaching the bare checkout
docket runs from, as `numpy.linalg.eig` serves the model's reference tests
(`PL-921Y`). Vendoring it into the tree was weighed and not taken, on
`PL-R417`'s next steps.

**Why it matters.** `docket.markdown` was checked against markdown-it-py once, on 2026-10-04. A test repeating that comparison on every run makes the next block rule the reader gets wrong a CI failure on the day a document or fixture first holds it, rather than a finding a later sweep makes.

**Done when.** A test compares the leaf blocks `docket.markdown.read` hands
back, their kinds and line spans, with markdown-it-py's block tokens and their
line maps over every tracked Markdown file, allowing only the three departures
the module's docstring names, with markdown-it-py pinned in the dev dependency
group. It fails on today's reader where a tracked file holds a form like
`PL-B83V`'s, or, where none does, on a fixture holding one.

**Generator check.** Not a member of `PL-R417`: it reads nothing wrong. It is
the check that would have found a member inside the shared reader, so it
carries `feature: one-answer` and lands with `PL-R417`'s Markdown batch.

**Built 2026-10-10 (`#1388`).**
`subprojects/docket/tests/test_markdown_reference.py` compares each leaf
block's kind, span of lines, depth and heading level with markdown-it-py's,
over all 2,507 tracked Markdown files in about six seconds, and over fixtures
holding `PL-B83V`'s four forms, which fail on main's reader; no tracked file
held one. The unclosed-block departure is met by comparing the reading `read`
starts from, before it re-reads such a block as written, rather than by
stopping at the block: that reading is `read`'s wherever nothing is left open,
and is compared whole where something is. markdown-it-py departs from cmark-gfm
once over the tree: it reads a bare run of hyphens under a line holding a pipe
as a one-column table, where cmark-gfm 0.29.0.gfm.13 reads a setext heading
(measured 2026-10-10) and `docket.markdown` follows cmark-gfm. Three items'
front matter holds the form, a `verify:` line with a pipe over the closing
`---` (`PL-2FM6`, `PL-D42Z`, `PL-PT7M`), so the test refuses that row to
markdown-it-py's table rule, and a fixture holds the setting. `pyproject.toml`
asks for `markdown-it-py>=4.2.0` and `uv.lock` pins 4.2.0, the dev group's
convention, rather than `==4.2.0` as this item's `verify:` first asked: an
exact pin would keep `drift.yml`'s `uv sync --upgrade` from ever testing a
newer release. `verify:` was rewritten to check the bound and the lock.
