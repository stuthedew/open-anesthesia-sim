---
id: PL-LC6Z
title: docket.arming.renders_owner_ask has no caller outside its tests since PL-X4MD removed the owner-ask guard's wording match; retiring it edits tests in subprojects/docket/tests/test_cli.py that pin arm's answers, so it waits on the owner's read
priority: P3
effort: S
status: done
classes: refactor
feature: owner-ask-by-state
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py, subprojects/docket/tests/test_cli.py, tools/regex_baseline.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-04
closed: 2026-11-04
pr: 2015
payoff: no unused wording check is left for a later session to wire back in, and the owner-ask code says only what is true
verify: ! grep -rq 'renders_owner_ask' subprojects/docket/src subprojects/docket/tests
---

**Problem.** docket.arming.renders_owner_ask has no caller outside its tests since PL-X4MD removed the owner-ask guard's wording match; retiring it edits tests in subprojects/docket/tests/test_cli.py that pin arm's answers, so it waits on the owner's read

**Why it matters.** A function that nothing calls still has to be read, kept in step with the ask templates and tested. Its docstring says the coordinator's posts were checked through it, which is no longer true, so a later session could wire it back in as a wording check, the approach the owner rejected in `PL-X4MD`.

**Done when.** `renders_owner_ask` and the patterns built only for it (`_SHOWN_ASKS`, `_shown_pattern` and its field patterns) are gone from `subprojects/docket/src/docket/arming.py`. The two tests in `subprojects/docket/tests/test_arming.py` that exercise it are gone, and the one assertion in `subprojects/docket/tests/test_cli.py` that calls it is removed with the rest of that test kept. The comment above the ask templates no longer names it. The owner has read the test change, since it edits a test that pins `arm`'s answers.

**Generator check.** None. It is the clean-up `PL-X4MD` step 4 named, and adds no head of its own.
