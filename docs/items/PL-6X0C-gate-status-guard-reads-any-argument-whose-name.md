---
id: PL-6X0C
title: gate-status-guard reads any argument whose name ends _check.py as the check an interpreter runs, so a script handed such a file as an argument is refused when piped, though no check runs; met in PL-R417's link 24 with a copy of test_doc_check.py
priority: P3
effort: S
status: ready
classes: defect
feature: bash-guard-bound
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-11
payoff: a scratch script handed a tools check or its test as an argument is no longer refused as running that check, so reading a check's own files costs no retry
verify: grep -q 'def test_only_the_script_an_interpreter_runs_is_read_as_a_check' tests/unit/test_gate_status_guard.py
reenters: PL-61FT
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

**Reproduced 2026-10-11** on `main` at `16a20a4f`, piping each command to the
hook as a Bash payload: the command above is refused as running
`main_test_doc_check.py` and throwing its status away, and `python3 scratch.py
tools/glyph_check.py | head`, which runs `scratch.py`, is refused as running
`tools/glyph_check.py`. `python3 tools/glyph_check.py | head` is refused
correctly.

**Why it matters.** Reading or comparing a check's own source or test with a
scratch script is ordinary work beside these tools, and each such pipe costs
the retry the guard's header names as the whole price of a false refusal. A
guard that refuses correct commands is the one sessions learn to route around,
and its remedy (`set -o pipefail`) is no help here, since no check runs.

**Generator check.** The fact misread is `PL-61FT`'s - what a shell command
does when run, here which of an interpreter's arguments it runs - and this is
an instance of that head's fact filed after it closed on 2026-09-26, met in
ordinary work, so worked at its own rank under that head's ratified bound,
whose reopening number counts `KNOWN_GAPS` rows met (none has been). It is the
fourth such instance, after `PL-ZS13`, `PL-0FGH` and `PL-RC4S`; triage's
general rule reads three post-close instances as a fix that did not hold, and
the head's own bound says a met false refusal does not move its number. The
two disagree, and this pass raised it rather than recording a head.

**Done when.** `check_script` takes as the check only the script an
interpreter runs - its first argument past the interpreter's own options, and
none after `-c` or `-m` - so the two commands above are admitted while
`python3 tools/glyph_check.py | head` is still refused, each a case in
`tests/unit/test_gate_status_guard.py`.
