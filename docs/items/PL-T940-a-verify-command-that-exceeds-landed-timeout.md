---
id: PL-T940
title: A verify: command that exceeds LANDED_TIMEOUT returns 1 and reads as one that correctly fails
priority: P2
effort: S
status: done
classes: bug, infra
feature: dev-tooling
milestone: v0.2.10
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_checks.py
added: 2026-09-02
closed: 2026-09-02
pr: 195
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -rq 'def test_a_timed_out_command_is_not_checked' subprojects/docket/tests
---

**Problem.** `verify._run` catches `subprocess.TimeoutExpired` in the same
clause as every other `SubprocessError` and returns status `1`. `1` is the
status an ordinary failing test gives, so a `verify:` command killed at
`LANDED_TIMEOUT` (120 s) is indistinguishable to `already_passing` from one
that ran and correctly failed: it is not `0`, so it is not `passing`; not
`127`, so it is not counted `unavailable`; and `selects_no_test` is false, so
it is not `vacuous`. The item drops out of every finding and out of
`considered`'s meaning, and nothing anywhere says so.

**Why it matters.** This is the failure mode the module is otherwise built to
refuse - `already_passing`'s own docstring says an empty result that means
"could not look" must never render as "looked, found nothing", and `declined`
exists for exactly that. A timeout is the one path that gets it wrong, and it
gets it wrong silently and per-item rather than for the whole run.

It is reachable rather than theoretical, and the heavier the pool gets the
likelier it is. Measured on this checkout, four cores, `uv run pytest
--cov=anesthesia_sim.core.tissue --cov-fail-under=100`:

| Concurrent full-suite runs | Slowest single command | Headroom to the 120 s timeout |
| --- | --- | --- |
| 2 | 54.5 s | 2.20x |
| 6 | 76.0 s | 1.58x |

Six is not a hypothetical width: `core-guard-coverage` has held six such
commands at once, and they are all `done` only because the feature is
between coverage items. On a two-core machine the six-wide case is roughly
150 s and crosses the ceiling, at which point six items silently stop being
checked and the run still prints a clean report.

**Where.** `subprojects/docket/src/docket/verify.py` - `_run`'s except
clauses and the result loop in `already_passing`;
`subprojects/docket/src/docket/checks.py` - `_check_landed`, which owns what
the run says about itself.

**Done when.** A command killed by the timeout is reported under "Not
checked" naming the item and the limit it hit, never counted as a command
that ran, and a test holds that a timed-out probe is reported rather than
silently dropped.

**Found.** 2026-09-02, while working `PL-5TN8` (whether full-suite `--cov`
commands belong in the landed check). The timeout is what makes the heavy
case unsafe rather than merely slow, so it is fixed regardless of how
`PL-5TN8` is answered.

**Worked.** `_run` catches `subprocess.TimeoutExpired` ahead of the broader
`SubprocessError` clause and returns `TIMED_OUT`, a status outside the range a
shell can report (0-255, or a small negative for a signal death) so that no
real command can collide with it. `already_passing` takes that status and 127
first in the result loop, keeps the identifiers in `timed_out` and
`unavailable`, and counts neither in `considered` - which is rendered to a
reader as "checked" and was counting commands that had not been.
`_check_landed` reports both under "not checked", where a whole declined run
already goes.

Demonstrated end-to-end against this store with the limit lowered to 3 s,
which exercises the same path a heavy command on a loaded box would:

```
  PL-7QKY, PL-K2YF, PL-NV9W, PL-WB0X, PL-X2XX: `verify:` command killed at the
  3s limit, so nothing is claimed about them - the command is either too slow
  for a check that runs on every `make check`, or it hangs
```

Before the change those five appeared nowhere and were counted among the
commands the run said it had checked.

**The not-found half came along deliberately**, though the brief above names
only the timeout. Both statuses mean "this command produced no evidence", and
`considered` cannot exclude one while counting the other without the word
"checked" being true of one and false of the other in the same sentence.
Subtracting the not-found case without reporting it would also have replaced
one silent gap with a quieter one, so it is named too. The all-missing decline
that existed for 127 now covers both, and says which happened, because a
missing toolchain and a limit set too low want different repairs.

**Not addressed here.** Whether 120 s is the right limit. Nothing measured
here exceeds it - six concurrent full-suite runs peaked at 76 s on four cores
- and the point of this item is that crossing it is now visible rather than
silent, which is what makes the number safe to leave alone until something
does.

**Documentation swept.** `subprojects/docket/README.md`'s section on the
landed check is the only prose making claims about this behavior, and it was
already stale before this item touched it: it described the decline conditions
without the timeout case, and costed the check at "29 candidates, about 17
seconds, on the store as it stood on 2026-09-01" - a serial figure `PL-LXR3`
superseded without updating it. Both are corrected, and the concurrency it
never recorded is now written down with the measured figures. Checked and left
alone: `README.md` (its not-checked paragraph is about the three checks
needing full history, which is unchanged), `docs/worker.md`,
`docs/ARCHITECTURE.md` and `.claude/skills/docket/SKILL.md`, none of which
makes a claim this changes.
