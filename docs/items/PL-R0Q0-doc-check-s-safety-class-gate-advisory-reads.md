---
id: PL-R0Q0
title: doc_check's safety-class gate advisory reads only the frozen list, so a safety item deferred with a written reason advises forever
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-16
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_deferred_safety_item_still_re_enters_the_gate' tests/unit/test_doc_check.py
---

**Problem.** `tools/doc_check.py` raises two gate advisories per open debt item:
one for a missing disposition, which a `### Declined to Gate ...` entry answers,
and one for a `safety`- or `science`-classed item not placed *on the frozen
list*, which nothing but the frozen list answers. The second names three
remedies - "Record each on the list, place it in Required scope, or defer it
with a reason" - but only recognises the first two. A deferral with a reason,
which the advisory's own wording offers and the gate rule grants, leaves it
firing.

**Why it matters.** The list is frozen - v0.5.0's on 2026-09-06 - so a safety
item captured afterwards *cannot* go on it without falsifying the freeze, and
"The gate is a snapshot" already places such an item in the next gate. So for
any safety item captured after a freeze, the advisory has no reachable clean
state and fires on every `make check` until the item closes. `CLAUDE.md`: "A
check that fires every run without changing a decision is a defect in the check
- it costs attention forever and trains a session to skim the output where a
real advisory also appears."

**The instance.** `PL-MN4J`, captured 2026-09-16 and deferred in v0.5.0's
declined subsection with a reason of its own (the display it concerns does not
exist outside the feature the milestone builds, so the gate cannot precede it).
The disposition advisory cleared; the safety-class one did not.

**Shape.** Read the declined subsection for this advisory as well as for the
disposition one, so a written deferral answers both - or, if a safety item is
deliberately held to a higher bar than the disposition rule, say so in the
advisory text, which currently offers a remedy it does not accept.

**Where.** `tools/doc_check.py`; `tests/unit/test_doc_check.py`;
`ROADMAP.md` § "The debt gate" is the rule being enforced.

**Found 2026-09-16** while closing `PL-8PSW`.

**Done when.** The advisory offers no remedy it will not accept. Either it reads
the current gate's `### Declined to Gate ...` subsection, so a deferral with a
written reason clears it exactly as it already clears the disposition advisory -
or its text stops offering deferral and says why a `safety`- or `science`-classed
item is held to a higher bar than the disposition rule. A test in
`tests/unit/test_doc_check.py` pins whichever rule is taken, against a
safety-classed item deferred with a reason.
