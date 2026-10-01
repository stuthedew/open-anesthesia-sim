---
id: PL-W560
title: Five reads restate sets docket.model exports: config's default safety and process classes, whose process set adds housekeeping that model.PROCESS_CLASSES lacks; cli's effort choices; and generator_check's two thresholds of three, which are MIN_ROOT_CAUSE_ITEMS
status: untriaged
feature: read-facts-through-docket
touches: subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/cli.py, tools/generator_check.py
added: 2026-10-01
---

**Problem.** Five reads restate sets docket.model exports: config's default safety and process classes, whose process set adds housekeeping that model.PROCESS_CLASSES lacks; cli's effort choices; and generator_check's two thresholds of three, which are MIN_ROOT_CAUSE_ITEMS

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `subprojects/docket/src/docket/config.py:31` defaults `safety_classes` to `model.SAFETY_CLASSES`' values; `:42` defaults `process_classes` to `model.PROCESS_CLASSES` plus `housekeeping`, and the sweep found no caller of `Item.is_process_work`. `subprojects/docket/src/docket/cli.py:5370` lists the effort choices `model.EFFORTS` holds. `tools/generator_check.py:98` (`MIN_OPEN`) and `:103` (`CITED_BY`) are each three for the definition's reason, which is `model.MIN_ROOT_CAUSE_ITEMS`. All agree today, `:42` aside.
