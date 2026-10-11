---
id: PL-6X0C
title: gate-status-guard reads any argument whose name ends _check.py as the check an interpreter runs, so a script handed such a file as an argument is refused when piped, though no check runs; met in PL-R417's link 24 with a copy of test_doc_check.py
status: untriaged
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
added: 2026-10-11
---

**Problem.** gate-status-guard reads any argument whose name ends _check.py as the check an interpreter runs, so a script handed such a file as an argument is refused when piped, though no check runs; met in PL-R417's link 24 with a copy of test_doc_check.py

**Met 2026-10-11** (`#1392`), not probed for. A session counting `PL-R417`'s
guard cases ran a scratch script over two copies of `tests/unit/test_doc_check.py`,
`uv run python guard_keys.py main_test_doc_check.py
tests/unit/test_doc_check.py | sed -n '...'`, and the guard refused it as
discarding the status of `main_test_doc_check.py`. `check_script` in
`.claude/hooks/gate-status-guard.sh` returns the first of an interpreter's
arguments whose name ends `_check.py`, wherever it stands, so a file the
script reads is taken for the script; Python runs the first argument past its
own options and hands every later one to the script. The session worked round
it by writing the output to a file, which costs a retry, as the guard's header
says a false refusal does.
