---
id: PL-2GY0
title: docket check's own-status reader reads 'left `needs-decision`' in the sense of departing it as a claim the item still sits there: PL-JNWS's brief tripped it with 'Every one of the 17 then left `needs-decision`', a past-tense sentence about seventeen other items, so OWN_STATUS's optional 'at' cannot tell 'left at X' from 'left X'
priority: P3
effort: S
status: ready
classes: defect
feature: brief-state-agreement
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-09-30
payoff: the brief-state check stops flagging a sentence that narrates other items leaving a status, so correct prose is never reworded to satisfy it
verify: grep -q 'def test_a_sentence_about_other_items_leaving_a_status_is_no_claim' subprojects/docket/tests/test_checks.py
---

**Problem.** PL-JNWS's brief tripped docket check's own-status reader with 'Every one of the 17 then left `needs-decision`', a past-tense sentence about seventeen other items. The reader takes *left* in the sense of departing a status as a claim that the item still sits at it, since `OWN_STATUS`'s optional `at` cannot tell 'left at X' from 'left X'. Quoted with no earlier item id in its sentence, as this brief first had it, the phrase trips the reader on this brief too.

**Why it matters.** The own-status reader keeps a brief's prose from claiming a state its front matter has moved past (`PL-8YXJ`). A false positive on an ordinary past-tense sentence makes a session reword correct prose to satisfy it, and a check that fires on correct text trains skimming.

**Done when.** A test in the docket suite holds that a sentence narrating other items departing a status is read as no claim about this brief's own status, while a sentence saying this item still sits at one is.

**Reproduced 2026-10-01.** `OWN_STATUS.search` from `subprojects/docket/src/docket/checks.py` matches both `PL-JNWS`'s past-tense sentence and the standing form with *at*, so it cannot tell them apart.

**Generator check.** A defect in `OWN_STATUS`'s grammar, its optional *at*, rather than a reader misreading a recorded fact. One-off.
