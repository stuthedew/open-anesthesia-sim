---
id: PL-MB3F
title: make check runs tools/doc_check.py under bare python3 while CI also runs it under uv's newer interpreter, and _docstrings silently skips a source file the running interpreter cannot parse, so on Python 3.11 a broken docs quotation in app/bookmarks.py or app_metadata.py passes make check and fails CI
priority: P2
effort: M
status: done
classes: defect, infra
milestone: v0.5.11
touches: tools/doc_check.py, tools/possessive_section_check.py, tests/unit/test_doc_check.py, .github/workflows/quality.yml, Makefile, tests/unit/test_possessive_section_check.py, tests/unit/test_tools_portability.py, tools/ruff.toml, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-23
closed: 2026-09-24
pr: 999
payoff: no source file goes unread by doc_check or the possessive-citation check without the run saying so
verify: grep -q 'def test_a_source_file_the_running_interpreter_cannot_parse_is_reported_not_skipped' tests/unit/test_doc_check.py
---

**Problem.** make check runs tools/doc_check.py under bare python3 while CI also runs it under uv's newer interpreter, and _docstrings silently skips a source file the running interpreter cannot parse, so on Python 3.11 a broken docs quotation in app/bookmarks.py or app_metadata.py passes make check and fails CI

**Found 2026-09-23, under `PL-TH9K`'s audit of `PL-0HPV`.** The gap is at the
level of which interpreter runs the script, not which scripts run.
`check_gate_parity` compares the two gates' scripts and never the interpreter
each one uses. `quality.yml` runs `tools/doc_check.py` under the floor's
`python3` and again under `uv run`. `make check` runs it under bare `python3`
only, which is 3.11 in the cloud container.

`_docstrings` skips any source file the running interpreter cannot parse.
Reproduced on `4e065310`:

1. Point the quotation in `app/bookmarks.py` at a heading that does not exist.
2. Run `tools/doc_check.py` under `python3.11`. It exits 0.
3. Run it under `python3.13`. It exits 1 with "quotes docs/ARCHITECTURE.md as
   ..., which is not in that file".

The comment in `quality.yml` saying that those steps read "never project
source" is wrong for `doc_check`. No run has failed this way yet.

**Generator check.** A one-off. No instance is recorded, so it is not a
post-close instance of `PL-0HPV`, whose verdict is `spent`.

**Re-checked at triage, 2026-09-24.** Bare `python3` here is 3.11.15.

- **Which interpreter runs `tools/doc_check.py`.** `make check` runs it under
  bare `python3`, in the `check` recipe and the `doc-check` target.
  `quality.yml` runs it under setup-python 3.11, and again under `uv run
  python`, which is 3.14.7.
- **The skip.** `_docstrings` returns on `SyntaxError` or `ValueError`,
  commented `# pragma: no cover - not this tool's question`.
- **The files it skips.** Two tracked files fail to parse under 3.11:
  - `app/bookmarks.py`, which uses PEP 695 generics.
  - `app_metadata.py`, which uses PEP 758's unparenthesised `except`. This one
    also fails under 3.12 and 3.13, so a broken quotation in it passes under
    both 3.11 and 3.13; only 3.14 catches it.
- **A second tool with the same hole.** `tools/possessive_section_check.py`
  reads through the same `_quoting_sources`, and both gates run it only under
  3.11. So nothing checks possessive citations in either file.

**Why it matters.** Because of `tools/possessive_section_check.py`, the merge
gate has the same hole as `make check`: for those two files the check passes
while its guarantee is void. For doc_check itself, a local gate that passes
where the merge gate fails costs a CI round trip. Either way the skip is
silent: nothing says two files went unread. `check_gate_parity` cannot see
this gap, because it compares scripts and never the interpreter each one runs
under.

**Done when.**

- `_docstrings` reports a source file it cannot parse in the run's declined
  list, rather than skipping it.
- `tools/possessive_section_check.py` gets that behaviour too.
- A test in `tests/unit/test_doc_check.py` pins it.
- The `quality.yml` comment saying those steps read "never project source" is
  corrected.
- The two comments in the `Makefile` and `quality.yml` that cite the deleted
  `app/chart_downsampling.py` are repaired in the same commit, since the item
  already touches both files.

**Why reporting the skip rather than switching the interpreter** (decided at
triage). The alternative was running `make check` under `uv run python`.
Reporting the skip is the smaller change, and it ends the silence wherever the
tool runs. Switching the interpreter can follow if the declined line shows up
on most runs.

**Generator check, at triage.** The capture's line above calls this a one-off
because no run has failed yet. But the fact is not a failed run. It is where
the local gate and the merge gate differ, which is `PL-0HPV`'s `misread:`.
`PL-0HPV` closed on 2026-09-22, the day before this was filed. So this is one
instance of that head's fact after its close. One instance is not enough for
anything more to follow.

**Worked 2026-09-24: both, the switch included** (project owner, 2026-09-24,
ratified, over reporting the skip alone as triage decided). The triage
condition for switching was met on the first run rather than on most of them:
under 3.11 the declined line names `app/bookmarks.py:451` and
`app_metadata.py:92` every time, and it grows with each file that takes 3.12+
syntax, which `ruff format` at `py314` writes on its own for a multi-exception
`except`. A line that fires on every run is one nobody reads, and reporting
alone left the possessive check reading neither file in either gate.

- `doc_check._quoting_sources` takes the caller's declined list, and appends
  one line per `.py` file it cannot parse or read. The line names the file and
  the line where the parse stopped, the interpreter's version, and the
  parser's message. `_docstrings` now takes a parsed tree. The possessive
  check's `sites` takes the same list and prints it under "Not checked"; a
  decline does not fail either tool. Each file is parsed as bytes, as Python
  reads source, so a byte-order mark or a coding cookie is not declined.
- `make check` runs both tools under `uv run python`, and `make doc-check`
  runs `doc_check`, the only one it runs, the same way. CI's
  floor section keeps both bare as the no-virtualenv proof, where they now
  decline by name. CI's `uv run` group adds the possessive check beside
  `doc_check`.
- The comments and docs that said these tools read only Markdown, or that
  `make check` runs `doc_check` bare, are corrected: `Makefile`,
  `quality.yml`, `tools/ruff.toml`, `docs/ARCHITECTURE.md` and
  `tests/unit/test_tools_portability.py`'s docstrings. `ARCHITECTURE.md` and
  the portability docstring now name these two as the tools run both ways.
