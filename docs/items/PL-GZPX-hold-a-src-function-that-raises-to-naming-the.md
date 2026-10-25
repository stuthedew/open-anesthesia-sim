---
id: PL-GZPX
title: Hold a src/ function that raises to naming the failure in its docstring, as a doc_check rule, once the backlog it would fire on is clear
priority: P3
effort: S
status: done
classes: infra, docs
feature: documentation-standard
touches: tools/doc_check.py, tests/unit/test_doc_check.py, src/anesthesia_sim/app/playback.py
blocked-by: PL-HXKC
added: 2026-09-05
closed: 2026-10-24
pr: 1775
payoff: a new public simulator function that raises without saying so in its docstring is refused by make check, so the backlog PL-HXKC cleared cannot regrow
verify: grep -q 'def test_a_public_function_that_raises_names_the_failure_in_its_docstring' tests/unit/test_doc_check.py && grep -q 'check_raising_docstrings(root, report)' tools/doc_check.py
---

**Problem.** "A public function that raises says so in its docstring" is
decidable by reading the tree: walk `src/` with `ast`, find the functions
containing a `Raise`, and read their docstring. `PL-HXKC` fixes today's eight
violations by hand, and nothing then stops the ninth.

**Why it matters.** This is `CLAUDE.md`'s standing preference for deterministic
tooling over repeated model work, in the shape `tools/import_boundary_check.py`
and `check_prose_provenance` already take here. The judgment half — whether the
sentence is *true* — is explicitly not scripted; only whether one exists.

**Where.** A new check in `tools/doc_check.py`. It parses `src/`, so it needs
the project interpreter rather than the bare `python3` the stdlib-only checks
run under — the same constraint `tools/import_boundary_check.py` has and for
the same reason (PEP 695 syntax in `app/`). Decide whether it belongs in
`doc_check.py` at all for that reason, or alongside the import guard.

**Done when.** A public function under `src/` that raises and whose docstring
never names a failure fails `make check`, and the check passes on the tree with
`PL-HXKC` landed. Do not build it before then: a check that fires eight times
on the day it ships is one a session learns to skim.

**Closed 2026-10-24.** `check_raising_docstrings` in `tools/doc_check.py` reads the public functions under the package: top-level functions and the methods of public classes, skipping names with a leading underscore and nested functions. One that contains a `raise` must use "raise", "reject" or "refus" in its docstring. The file is parsed as bytes, as the citation check parses it, so a byte-order mark is honoured. A file the running interpreter cannot parse is declined in its own line, which names this check, because CI's floor runs the tool under a bare `python3` that cannot parse some 3.14 syntax. The existing decline test now picks out each check's line rather than expecting one line per file.
