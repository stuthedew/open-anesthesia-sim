---
id: PL-BB5W
title: docket set skips the roadmap-dependent rules because cmd_set calls analyze without milestones, so a debt item it accepts at a triaged status then fails docket check for having no v0.6.0 gate disposition
priority: P3
effort: S
status: done
classes: defect
feature: set-parity
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
closed: 2026-09-26
payoff: a triage pass learns the gate rule from the write that breaks it rather than from a later docket check, so set's promise to refuse what check would fail holds for every rule
verify: grep -q 'def test_set_refuses_a_debt_capture_with_no_gate_disposition' subprojects/docket/tests/test_cli.py
---

**Problem.** docket set skips the roadmap-dependent rules because cmd_set calls analyze without milestones, so a debt item it accepts at a triaged status then fails docket check for having no v0.6.0 gate disposition

Reproduced 2026-09-25 against 46954a81: `cmd_set` in `subprojects/docket/src/docket/cli.py` validates the write with `analyze(after, today, config, written=written)` and compares against `analyze(items, today, config)`, passing no `milestones`, so every rule that needs the roadmap is skipped. In this session's triage pass `bin/docket set` accepted `PL-384P`, `PL-L8VP`, `PL-NQ3X`, `PL-QQCD`, `PL-SN2T`, `PL-XGYH` and `PL-YKBF` as `defect` items at a triaged status. `bin/docket check` then refused each with "open debt ... neither places nor defers", and each was repaired with `--deferred-from`.

**Why it matters.** `.claude/skills/docket/modes/triage.md` tells a session that `set` refuses "any write `docket check` would then fail, in the checker's own words". For the gate rule that promise is void, so every triage pass that classes a capture as debt learns the gate rule one `check` later. `make docket` still catches it before a merge, so the cost is a round trip per pass, not a wrong record. That is also why it is P3.

**Done when.** `cmd_set` reads the milestones the way `cmd_check` does, where the roadmap is readable, and passes them to both of its `analyze` calls. `bin/docket set <id> --classes defect --status ready ...` on a post-freeze capture with no gate disposition is then refused, naming the `--deferred-from` command. A test in `subprojects/docket/tests/test_cli.py` holds that refusal.

**Generator check.** The fact misread is "which rules a write must satisfy". `set` assembles a narrower input than `check` for the same `analyze`. No head's `misread:` states it: `PL-XBV4` is about how fresh a command's inputs are, not which inputs it reads. It is a one-off at one call site.

**Worked.** 2026-09-26, on `claude/pl-batch-04-d15tqm`. `cmd_set` now reads
the roadmap through `_milestones`, the reader `cmd_check`'s `_complete_report`
and `cmd_list` already use, from `_invocation(args).root`, and passes the result
to both `analyze` calls, so an error the roadmap settles counts against the
write only where it is new. An unreadable roadmap still declines as it does for
`check`. The test needed a roadmap recording a *current* gate, which the
suite's `WAVE_ROADMAP` does not (it has no version table, so `baseline_gate`
places nothing), so it adds `GATE_ROADMAP`, a copy of `test_checks.py`'s
`GATED_ROADMAP` cut down to the baseline row and one frozen list. The test
checks the refusal names the `--deferred-from` command, that nothing is written,
that the write with the deferral is accepted, and that `check` then passes. It
was run against the tree without the fix and failed there, `set` exiting 0.
