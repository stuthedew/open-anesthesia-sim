---
id: PL-VJPJ
title: bin/docket next raises BrokenPipeError and prints a traceback when its output is piped into a command that closes early, so next | head looks like a crash to every session that pipes it
priority: P2
effort: S
status: done
classes: defect
feature: dev-tooling
milestone: v0.5.9
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_git_runner.py, subprojects/docket/tests/test_portability.py, subprojects/docket/README.md
added: 2026-09-19
closed: 2026-09-23
pr: 964
payoff: stops bin/docket next printing a Python traceback that reads as the queue tool crashing whenever a session pipes it into head
verify: grep -q 'BrokenPipeError' subprojects/docket/src/docket/cli.py
recurrences: 2026-09-22 PL-QC0Y
---

**Problem.** bin/docket next raises BrokenPipeError and prints a traceback when its output is piped into a command that closes early, so next | head looks like a crash to every session that pipes it

**Reproduced 2026-09-20**, on `origin/main` at `a0c023d`:

```
$ bin/docket next 2>/tmp/err | head -3 >/dev/null; cat /tmp/err
Traceback (most recent call last):
  ...
  File "subprojects/docket/src/docket/cli.py", line 1179, in cmd_next
    _say_answer_lane(items, flight, config, args, plan, lane, picks[0].item)
  File "subprojects/docket/src/docket/cli.py", line 1298, in _say_answer_lane
    print(
BrokenPipeError: [Errno 32] Broken pipe
```

**Why it matters.** `bin/docket next` prints the lane answer, the reason line
and the payoff for several items, and a session that wants only the pick pipes
it into `head`. That is the documented way to read it cheaply, and it ends in a
Python traceback on stderr - which reads as the queue tool crashing at the exact
moment a session is deciding whether to trust its answer. The pick that was
printed is correct, so the cost is a session stopping to diagnose a fault that
is not there, and possibly re-running the command at full output to check.

It is the ordinary CPython interpreter-shutdown behaviour for a writer whose
reader has closed: the exception is raised, caught by nothing, and reported.
The fix is the standard one - handle `BrokenPipeError` at the command boundary
and exit quietly - and it belongs once at that boundary rather than at each of
the several `print` calls that can hit it.

**Done when.** `bin/docket next | head -3` prints the first three lines and
exits without a traceback, and a test drives a closed stdout against the
command.

**Not `next` alone (seen 2026-09-22).** `bin/docket show PL-WZVZ | head -3`
raised the same `BrokenPipeError` from `cmd_show`'s `print`, so the fix belongs
where every command's output passes - `main()` in `cli.py` - rather than in
`cmd_next`.
