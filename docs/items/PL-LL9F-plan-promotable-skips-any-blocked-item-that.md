---
id: PL-LL9F
title: plan.promotable skips any blocked item that also names a milestone in blocked-by, so closing an item blocker never refuses or names a dependent whose milestone blocker had already cleared: PL-K88Z's closure in #1712 left PL-JS6P, PL-WM5P, PL-VWXL and PL-SH0W (blocked-by v0.6.0, PL-K88Z) at blocked with only a grooming advisory
priority: P2
effort: S
status: done
classes: defect
feature: blocked-means-blocked
milestone: v0.6.3
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
added: 2026-10-24
closed: 2026-10-25
pr: 1768
payoff: closing an item's last blocker always names or refuses its dependents, whichever blocker cleared first
verify: grep -q 'def test_an_item_whose_milestone_cleared_first_is_promotable' subprojects/docket/tests/test_plan.py
reenters: PL-6T44
---

**Problem.** plan.promotable skips any blocked item that also names a milestone in blocked-by, so closing an item blocker never refuses or names a dependent whose milestone blocker had already cleared: PL-K88Z's closure in #1712 left PL-JS6P, PL-WM5P, PL-VWXL and PL-SH0W (blocked-by v0.6.0, PL-K88Z) at blocked with only a grooming advisory

**Found 2026-10-24** on `main` at `b2ae9e4d`, when the owner asked why the four check items were never marked unblocked.

**The path.**
1. On 2026-10-19 the four items were filed with `blocked-by: v0.6.0, PL-K88Z`. The answer on `PL-2LB5` (the design round) said that each "waits on v0.6.0 and on the inventory". In the store, though, `blocked-by: <version>` means "until that milestone is scoped" (`.claude/skills/docket/modes/triage.md`). v0.6.0 was already scoped, so the version blocker had cleared before the items were filed. Its only effect was to move them onto the milestone path below.
2. `plan.promotable` keeps only items with `not item.blocking_milestones`. So when `PL-K88Z` closed in #1712, `cli._say_unblocked` named nothing, and `checks._blocked_with_every_blocker_closed`, which reads the same set, raised no error. #1712 went green with all four still `blocked`.
3. The only remaining signal was the milestone branch in `checks._groom`, an advisory: "v0.6.0 is scoped and every other blocker has closed; it is ready to promote". `PL-2349` made the item-blocker case an error because that same advisory had been "named on every run and moved by nobody". The triage pass that followed (#1723) triaged 18 captures and did not move these four.

**Why the carve-out does not fit this case.** `promotable` leaves milestone blockers out because "a milestone blocker clears when a scoping round happens", which is not a closure and has no pull request of its own to refuse. That reasoning holds when the milestone clears last. When the milestone has already cleared and an item blocker clears last, there is a closure and a pull request, and it is the same falsehood `PL-2349` refuses.

**Measured.** On 2026-10-24, these four are the only blocked items whose `blocked-by` names both a version and an item.

**Decision for whoever builds it.** The narrow fix is to count an item as promotable when every item blocker has closed and every milestone blocker `milestones.is_cleared`, still excluding `ships_with`. `promotable` would then need the roadmap reading that `_groom` already has. The other option is to refuse a `blocked-by` that names a version that is already cleared at write time. That would have stopped the four at filing, but it does not handle a milestone that clears while the item waits.

**Why it matters.** `PL-2349` made "every blocker has closed" an error because the advisory alone was named on every run and moved by nobody. The carve-out lets the same silent case through whenever the milestone blocker cleared first, so a closure leaves its dependents `blocked` and hidden from `bin/docket next`. **Checked 2026-10-24:** all four items have since been promoted by hand and are `ready`, so no item is in this state now. The code is unchanged: `plan.promotable` still keeps only items with `not item.blocking_milestones`.

**Route decided 2026-10-24 at triage: the narrow fix.** Count an item as promotable when every item blocker has closed and every milestone blocker `milestones.is_cleared`, still excluding `ships_with`. Refusing a cleared version at write time would have stopped these four at filing, but it misses a milestone that clears while the item waits, which the narrow fix covers.

**Done when.** `plan.promotable` returns a blocked item whose item blockers have all closed and whose milestone blockers have all cleared, so `_say_unblocked` names it and `_blocked_with_every_blocker_closed` refuses it, and `subprojects/docket/tests/test_plan.py` has `test_an_item_whose_milestone_cleared_first_is_promotable`.

**Generator check.** An instance of the fact "an item's current queue state: its status, what blocks it, and what it must land after", which `PL-6T44`'s `misread:` states. `PL-6T44` built `promotable` and closed on 2026-09-20. Recorded as `reenters: PL-6T44`.
