---
id: PL-MB3F
title: make check runs tools/doc_check.py under bare python3 while CI also runs it under uv's newer interpreter, and _docstrings silently skips a source file the running interpreter cannot parse, so on Python 3.11 a broken docs quotation in app/bookmarks.py or app_metadata.py passes make check and fails CI
priority: P2
effort: M
status: ready
classes: defect, infra
touches: tools/doc_check.py, tools/possessive_section_check.py, tests/unit/test_doc_check.py, .github/workflows/quality.yml, Makefile
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-23
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
