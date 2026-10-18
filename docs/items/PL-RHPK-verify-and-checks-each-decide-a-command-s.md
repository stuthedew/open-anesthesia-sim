---
id: PL-RHPK
title: verify and checks each decide a command's structure beside docket.shell - verify's SHELL_PREFIXES, INTERPRETERS, _programs and _docket_runs, checks' _STATUS_REPLACED and _after_pytest, gate-status-guard.sh's DOCKET_GATES, cli's shlex.split - so time python3, ;;, python3 -c pytest.main and python3 -m docket check each read two ways
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/shell.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/shell_split.py, tools/doc_check.py, tools/fact_home_check.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_cli.py, tests/unit/test_gate_status_guard.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
closed: 2026-10-18
pr: 1567
payoff: docket answers which program a verify: command runs, and where its status ends, by one grammar
verify: grep -q 'def test_a_command_program_is_read_through_docket_shell' subprojects/docket/tests/test_verify.py
falsifies: assert list(doc_check._make_mentions(fence)) == [("check", 2)]
---

**Problem.** verify and checks each decide a command's structure beside docket.shell - verify's SHELL_PREFIXES, INTERPRETERS, _programs and _docket_runs, checks' _STATUS_REPLACED and _after_pytest, gate-status-guard.sh's DOCKET_GATES, cli's shlex.split - so time python3, ;;, python3 -c pytest.main and python3 -m docket check each read two ways

- The program word: `verify.SHELL_PREFIXES`, `INTERPRETERS` and `_programs` beside `shell.OPENS_A_COMMAND` and the hooks' openers. On `time python3 tools/x.py` verify takes `time` for the program and counts `tools/x.py` as a path read; docket.shell and the hooks take `python3`. `python3.11 x.py` matches the hooks' `INTERPRETER` and not `verify.INTERPRETERS`.
- Whether a command runs `docket <subcommand>`: `verify._docket_runs` beside `gate-status-guard.sh`'s `DOCKET_GATES` and `gate`. On `python3 -m docket check` verify finds the run and the hook reports no gate (`PL-BM3Z`, dropped, held only the first-argument assumption).
- Which operators end a command's status inside an `&&` clause: `checks._STATUS_REPLACED` beside `verify.COMMAND_ENDS` and `PIPES`, both hand subsets of `shell.HEADS`. They part on `;;`.
- Whether a command runs pytest: `checks._after_pytest` (a word `pytest` or ending `/pytest`) beside `verify.PYTEST_RE` over raw text. On `python3 -c "import pytest,sys; sys.exit(pytest.main(['-k','x','tests/unit']))"` verify classifies exit 5 and checks' `-k` rule never fires.
- How a configured command splits into words: `cli._run_forge_command` uses `shlex.split` beside `shell.shell_words`; on `gh pr list # newest` shlex hands `#` and `newest` to gh, and on `$'.[0]'` the two give `$.[0]` and `.[0]`.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**The program word has a home now.** `docket.shell.simple_commands` (`PL-7DXZ`) cuts a reading into simple commands, lifts redirections, and names each one's `program` past its leading assignments. It does not yet read past a wrapper: `timeout 60 make check` names `timeout`, where the hooks' `shell_split.program_words` reads past it by `WRAPPERS`. Moving that wrapper grammar into `docket.shell` beside `simple_commands` gives verify, checks, the hooks and doc_check's fenced `make` finder one answer.

**Done when.** Each reader asks `docket.shell` for the program, the command ends and the words, and a test per pair pins the parting input.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
