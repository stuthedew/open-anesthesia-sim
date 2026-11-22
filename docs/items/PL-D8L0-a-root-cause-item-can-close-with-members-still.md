---
id: PL-D8L0
title: A root-cause item can close with members still open and with a 'spent' verdict that names no check: 37 of 90 heads closed the day they were added, 11 of them with members open
priority: P2
effort: M
status: done
classes: defect
feature: generator-heads
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md
deferred-from: v0.7.0 - found by the 2026-11-10 audit after the freeze; apparatus, and it changes no displayed value, so the release does not wait on it
added: 2026-11-10
closed: 2026-11-22
pr: 2238
payoff: a root cause closed on a sweep, on silence or before its members are fixed reads differently from one closed by a check
tests: subprojects/docket/tests/test_checks.py::test_a_head_closed_from_the_rule_date_names_its_mechanism, subprojects/docket/tests/test_cli.py::test_generators_marks_a_head_closed_early_or_on_no_mechanism
---

**Problem.** A root-cause item can close with members still open and with a 'spent' verdict that names no check: 37 of 90 heads closed the day they were added, 11 of them with members open

**Checked 2026-11-10:** `generator_faults` in `subprojects/docket/src/docket/model.py` asks nothing of a closed item; its docstring says a verdict on a closed item is read by nothing. A script over the store's front matter found 11 heads with no `generator:` field: `PL-2T03`, `PL-4FBP`, `PL-4Q9B`, `PL-6TP8`, `PL-9HD1`, `PL-BHVM`, `PL-G21K`, `PL-G424`, `PL-HWW1`, `PL-L4YG`, `PL-TZ7T`. Three heads are marked spent on a verdict that names no check or type: `PL-GTH6` and `PL-VDWT` ("no member filed since") and `PL-CMJ5` (a prose rule). The audit's reviewer reported that 37 of 90 heads closed on the day they were added, 11 of them with members open; the filing session did not recount that.

**Why it matters.** A head is the record that a root cause was found and stopped. The audit of 2026-11-10 found that the fixes which held each had a check or a checked type, and the ones that did not hold were sweeps or prose. A head that closes on a sweep, on silence, or before its members are fixed reads the same in every report as one closed by a check, and it sets no pause.

**Done when.** A head's verdict at close names the check, type or single writer that stops the next member, or says that none exists and why. `bin/docket generators` marks a closed head whose members are still open, and one whose verdict names no mechanism. Heads already closed are not rewritten.

**Generator check.** A defect in what a head records, which `.claude/skills/docket/modes/triage.md` places under work on the generators. A one-off as a mechanism.

**Checked 2026-11-22** against `d4e8200`: partly done, and the brief overstates one half. `bin/docket generators` already prints each closed head's open members, for example "PL-4FBP 24 members, 2 open - 22 closed since the head closed 2026-09-19" (`_drain_phrase` in `subprojects/docket/src/docket/render.py`). That line was in the tree before this item was filed. It does not flag such a head as a fault. What is left is the rest: a head's verdict at close does not have to name a check, type or single writer, `generator_faults` in `model.py` still asks nothing of a closed item, and no listing marks a verdict that names no mechanism.

**Done 2026-11-22.** A head closed `done` from 2026-11-23 must name what stops the next member: its `generator:` reads `spent - ` followed by one of `check:`, `type:`, `single writer:` or `none:`, then the mechanism or why there is none. `generator_faults` in `docket.model` refuses a close without one, so `docket check` and `docket set --status done` both say so; `model.verdict_mechanism` is the one reader of the kind. Heads closed earlier are not asked and not rewritten. `bin/docket generators` now marks a closed head `[closed with members open]` where any member is still open, and `[no mechanism named]` where its reason opens with none of the four kinds, with a key under the list. On 2026-11-22 that marks 3 heads with members open (`PL-4FBP`, `PL-BLN0`, `PL-B6YV`) and 85 with no mechanism named, all closed before the rule. The mark is on the head's own line, so the listing is no longer. Files checked in the docs sweep: `subprojects/docket/README.md` (the `generator` section and the `misread` paragraph that contrasted it), `.claude/skills/docket/modes/triage.md` § "Generators, how they rank, and the pause they set", and the docstrings of `generator_faults` and `ranks_as_generator` in `model.py`.
