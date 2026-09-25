---
id: PL-BB5W
title: docket set skips the roadmap-dependent rules because cmd_set calls analyze without milestones, so a debt item it accepts at a triaged status then fails docket check for having no v0.6.0 gate disposition
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-25
payoff: a triage pass learns the gate rule from the write that breaks it rather than from a later docket check, so set's promise to refuse what check would fail holds for every rule
verify: grep -q 'def test_set_refuses_a_debt_capture_with_no_gate_disposition' subprojects/docket/tests/test_cli.py
---

**Problem.** docket set skips the roadmap-dependent rules because cmd_set calls analyze without milestones, so a debt item it accepts at a triaged status then fails docket check for having no v0.6.0 gate disposition

Reproduced 2026-09-25 against 46954a81: `cmd_set` in `subprojects/docket/src/docket/cli.py` validates the write with `analyze(after, today, config, written=written)` and compares against `analyze(items, today, config)`, passing no `milestones`, so every rule that needs the roadmap is skipped. In this session's triage pass `bin/docket set` accepted `PL-384P`, `PL-L8VP`, `PL-NQ3X`, `PL-QQCD`, `PL-SN2T`, `PL-XGYH` and `PL-YKBF` as `defect` items at a triaged status. `bin/docket check` then refused each with "open debt ... neither places nor defers", and each was repaired with `--deferred-from`.

**Why it matters.** `.claude/skills/docket/modes/triage.md` tells a session that `set` refuses "any write `docket check` would then fail, in the checker's own words". For the gate rule that promise is void, so every triage pass that classes a capture as debt learns the gate rule one `check` later. `make docket` still catches it before a merge, so the cost is a round trip per pass, not a wrong record. That is also why it is P3.

**Done when.** `cmd_set` reads the milestones the way `cmd_check` does, where the roadmap is readable, and passes them to both of its `analyze` calls. `bin/docket set <id> --classes defect --status ready ...` on a post-freeze capture with no gate disposition is then refused, naming the `--deferred-from` command. A test in `subprojects/docket/tests/test_cli.py` holds that refusal.

**Generator check.** The fact misread is "which rules a write must satisfy". `set` assembles a narrower input than `check` for the same `analyze`. No head's `misread:` states it: `PL-XBV4` is about how fresh a command's inputs are, not which inputs it reads. It is a one-off at one call site.
