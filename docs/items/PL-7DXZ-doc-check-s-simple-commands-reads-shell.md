---
id: PL-7DXZ
title: doc_check's _simple_commands reads shell commands with its own REDIRECTIONS copy, a digit-only descriptor and words[0] == "make", so {fd}>log, FOO=1 make check and timeout 60 make check read differently from docket.shell and the hooks
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; filed and classed by PL-5DZ8's closing sweep, 2026-10-12
added: 2026-10-12
payoff: a make target named in a fenced command is found by the grammar docket and the hooks read
verify: grep -q 'def test_a_fenced_make_run_is_found_past_an_assignment' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _simple_commands reads shell commands with its own REDIRECTIONS copy, a digit-only descriptor and words[0] == "make", so {fd}>log, FOO=1 make check and timeout 60 make check read differently from docket.shell and the hooks

- `doc_check.REDIRECTIONS` is the same twelve operators as `shell_split.REDIRECTIONS`; `docket.shell` exports no such set.
- `doc_check._simple_commands` takes a redirection's descriptor as digits only, so on `exec {fd}>log` it keeps `{fd}` as an argument where `shell._names_a_descriptor` reads a descriptor.
- Its program word is `words[0] == "make"`, so a fenced `FOO=1 make check` or `timeout 60 make check` names no target, where `shell_split.command_words` finds `make`.

**Why it matters.** Each copy is held to the others by nothing, so the first input they part on is answered one way by docket and another by the hook or check a session trusts at that moment; every pair below was read at both sites by the sweep, and the parting input is the sweep's reading, to re-confirm at start.

**Done when.** doc_check finds a command's program and redirections through `docket.shell`, and a test pins `FOO=1 make check` and `{fd}>log`.

**Generator check.** A member of `PL-5DZ8`, filed by that head's closing sweep on 2026-10-12 and named in its `root-cause-of:`. The fact is the head's: which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it. It is neither a post-close instance nor a new generator.
