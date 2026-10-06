---
id: PL-0C2S
title: No test holds docket.markdown's block reading to a reference CommonMark parser, so a rule the shared reader gets wrong - PL-B83V's closing pre tag line - is found by a sweep rather than failing CI the day a document first holds it
status: untriaged
feature: one-answer
touches: subprojects/docket/tests, pyproject.toml, uv.lock
added: 2026-10-06
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

**Done when.** A test compares the leaf blocks `docket.markdown.read` hands
back, their kinds and line spans, with markdown-it-py's block tokens and their
line maps over every tracked Markdown file, allowing only the three departures
the module's docstring names, with markdown-it-py pinned in the dev dependency
group. It fails on today's reader where a tracked file holds a form like
`PL-B83V`'s, or, where none does, on a fixture holding one.

**Generator check.** Not a member of `PL-R417`: it reads nothing wrong. It is
the check that would have found a member inside the shared reader, so it
carries `feature: one-answer` and lands with `PL-R417`'s Markdown batch.
