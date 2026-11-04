---
id: PL-LC6Z
title: docket.arming.renders_owner_ask has no caller outside its tests since PL-X4MD removed the owner-ask guard's wording match; retiring it edits tests in subprojects/docket/tests/test_cli.py that pin arm's answers, so it waits on the owner's read
priority: P3
effort: S
status: blocked
classes: refactor
feature: owner-ask-by-state
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py, subprojects/docket/tests/test_cli.py
blocked-by: PL-J1ZM
deferred-from: v0.7.0 - captured after the freeze, and not safety or science; classed by the 2026-11-04 triage pass
added: 2026-11-04
---

**Problem.** docket.arming.renders_owner_ask has no caller outside its tests since PL-X4MD removed the owner-ask guard's wording match; retiring it edits tests in subprojects/docket/tests/test_cli.py that pin arm's answers, so it waits on the owner's read

**Checked 2026-11-04.** `renders_owner_ask` is defined in `subprojects/docket/src/docket/arming.py` and called only from `subprojects/docket/tests/test_arming.py` and `subprojects/docket/tests/test_cli.py`.

**Why it matters.** A function kept only by its own tests reads as a live rule. A later session may extend it or route a new guard through it.

**Blocked on the generator pause.** Retiring it is apparatus housekeeping, which `CLAUDE.md` holds while a workflow-lane head carries `generator: live`. `PL-J1ZM` is that head on 2026-11-04.

**Done when.** `renders_owner_ask`, its tests and the comment that names it at its data are gone, and `subprojects/docket/tests/test_cli.py` no longer asserts on it.

**Generator check.** One-off: dead code left by `PL-X4MD`'s change of design.
