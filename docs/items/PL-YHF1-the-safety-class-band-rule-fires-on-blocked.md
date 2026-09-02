---
id: PL-YHF1
title: The safety-class band rule fires on blocked items, so an unworkable safety item gets re-classed to satisfy the checker
priority: P1
effort: S
classes: safety, infra
status: done
feature: dev-tooling
touches: subprojects/docket
added: 2026-09-02
closed: 2026-09-02
commit: 92a8e55
pr: 220
---

**Problem.** `checks.py` refused a `safety` or `science` class at P2 or P3
regardless of status. A blocked item is not in the set `bin/docket next`
chooses from, so its band is a claim about work nobody can start; the rule
still demanded one. Triaging `PL-WZVZ` — presentation-safety work that cannot
be built until the anesthesia-machine abstraction exists — hit it, and the
first answer reached for was to drop the `safety` class and put it back later.

**Why it matters.** That answer is worse than the rule it works around, and it
is the failure mode the rule exists to prevent. `classes` is a fact about the
item, not a scheduling knob: every other reader of it — delegability, gate
membership, any later report — then reads something false, and for the one
class where a false reading matters most. It also makes the correction depend
on somebody remembering, at an unspecified future moment, to change it back.
Nothing fires. The project owner caught it during triage and named it: the
check should not fire when the item is blocked, and mis-classing to avoid the
fire is a poor workflow choice.

Classed `safety` rather than `infra` alone because the thing being corrupted
is the safety classification itself — a rule that pressures sessions into
under-classing safety work is a safety defect in the queue, not a tooling nit.

**Where.** `subprojects/docket/src/docket/checks.py`, the `safety` band rule;
`subprojects/docket/tests/test_checks.py`.

**Fixed.** A blocked item may sit outside the top band. The exemption does not
become a parking space: unblocking re-fires the rule, so the band is decided
at the moment the work becomes workable, by the checker rather than by recall.

The first cut inferred the exemption from the *absence* of a `defect` class,
which made forgetting to write one the way to obtain it. `PL-P909` corrected
that in the same branch: the exemption is now claimed with an explicit
`anticipated` class and fails closed, so an omission or a misspelling leaves
the strict band in force.

`PL-WZVZ` is classed `safety, anticipated, ux` at P3 while blocked, which is
what it actually is.

**Done when.** A blocked safety item may sit outside the top band, unblocking
it is refused until the band is set, and both directions have a test.
