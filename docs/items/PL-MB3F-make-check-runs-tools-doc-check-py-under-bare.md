---
id: PL-MB3F
title: make check runs tools/doc_check.py under bare python3 while CI also runs it under uv's newer interpreter, and _docstrings silently skips a source file the running interpreter cannot parse, so on Python 3.11 a broken docs quotation in app/bookmarks.py or app_metadata.py passes make check and fails CI
status: untriaged
added: 2026-09-23
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
