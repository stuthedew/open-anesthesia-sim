---
id: PL-W560
title: Five reads restate sets docket.model exports: config's default safety and process classes, whose process set adds housekeeping that model.PROCESS_CLASSES lacks; cli's effort choices; and generator_check's two thresholds of three, which are MIN_ROOT_CAUSE_ITEMS
priority: P3
effort: S
status: ready
classes: defect
feature: read-facts-through-docket
touches: subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/cli.py, tools/generator_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: the class sets, effort sizes and the three-item threshold are each stated once, so housekeeping is process work by one definition rather than two
verify: ! grep -qF '("session-cost", "docs", "infra", "housekeeping")' subprojects/docket/src/docket/config.py && ! grep -qF 'MIN_OPEN = 3' tools/generator_check.py && ! grep -qF 'choices=("S", "M", "L")' subprojects/docket/src/docket/cli.py
---

**Problem.** Five reads restate sets docket.model exports: config's default safety and process classes, whose process set adds housekeeping that model.PROCESS_CLASSES lacks; cli's effort choices; and generator_check's two thresholds of three, which are MIN_ROOT_CAUSE_ITEMS

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `subprojects/docket/src/docket/config.py:31` defaults `safety_classes` to `model.SAFETY_CLASSES`' values; `:42` defaults `process_classes` to `model.PROCESS_CLASSES` plus `housekeeping`, and the sweep found no caller of `Item.is_process_work`. `subprojects/docket/src/docket/cli.py:5370` lists the effort choices `model.EFFORTS` holds. `tools/generator_check.py:98` (`MIN_OPEN`) and `:103` (`CITED_BY`) are each three for the definition's reason, which is `model.MIN_ROOT_CAUSE_ITEMS`. All agree today, `:42` aside.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites** reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.
