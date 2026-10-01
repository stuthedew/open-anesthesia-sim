---
id: PL-W560
title: Five reads restate sets docket.model exports: config's default safety and process classes, whose process set adds housekeeping that model.PROCESS_CLASSES lacks; cli's effort choices; and generator_check's two thresholds of three, which are MIN_ROOT_CAUSE_ITEMS
priority: P3
effort: S
status: done
classes: refactor
feature: read-facts-through-docket
touches: subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/cli.py, tools/generator_check.py, subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_model.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-01
pr: 1277
payoff: each class set and threshold docket.model exports has one copy, so changing it changes every reader, and no dead property answers which classes are process work from a different list than the top-band rule
verify: ! grep -qF 'def is_process_work' subprojects/docket/src/docket/model.py && grep -qF 'MIN_OPEN = MIN_ROOT_CAUSE_ITEMS' tools/generator_check.py
---

**Problem.** Five reads restate sets docket.model exports: config's default safety and process classes, whose process set adds housekeeping that model.PROCESS_CLASSES lacks; cli's effort choices; and generator_check's two thresholds of three, which are MIN_ROOT_CAUSE_ITEMS

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `subprojects/docket/src/docket/config.py:31` defaults `safety_classes` to `model.SAFETY_CLASSES`' values; `:42` defaults `process_classes` to `model.PROCESS_CLASSES` plus `housekeeping`, and the sweep found no caller of `Item.is_process_work`. `subprojects/docket/src/docket/cli.py:5370` lists the effort choices `model.EFFORTS` holds. `tools/generator_check.py:98` (`MIN_OPEN`) and `:103` (`CITED_BY`) are each three for the definition's reason, which is `model.MIN_ROOT_CAUSE_ITEMS`. All agree today, `:42` aside.

**Why it matters.** Each of the five is a second copy of a set `docket.model` exports, and one already disagrees: `Config.process_classes` defaults to `model.PROCESS_CLASSES` plus `housekeeping`. That is harmless today only because nothing outside a test calls `Item.is_process_work`, the one reader of `model.PROCESS_CLASSES`, and that property reads the package's list where the top-band rule in `checks.py` reads the project's `config.process_classes`. A first caller would get a different answer from the rule it meant to apply.

**Done when.** `Config.safety_classes` defaults to `model.SAFETY_CLASSES`; `docket next --effort` takes its choices from `model.EFFORTS`; `generator_check`'s `MIN_OPEN` and `CITED_BY` are `model.MIN_ROOT_CAUSE_ITEMS`; and `model.PROCESS_CLASSES` and `Item.is_process_work` are deleted, leaving `Config.process_classes` the one record of which classes are process work.

**Decided at triage, 2026-10-01.** The process-class disagreement is settled by deleting the model's copy rather than adding `housekeeping` to it. Its only reader has no caller outside `subprojects/docket/tests/test_model.py`, and it reads the module constant where `checks.py` reads the project's setting, so making the two lists agree would still leave it wrong for any project that declares its own. The test pinning it goes with it, which `docket verify --self` reports as an assertion removed.

**Generator check.** A member of `PL-KGYT` (spent), filed by that head's own sweep in the commit that closed it; the fact is the head's. Not `impairs-generators`: `MIN_OPEN` and `CITED_BY` equal `MIN_ROOT_CAUSE_ITEMS` today, so the advisory surfaces the same clusters.
