---
id: PL-LL9F
title: plan.promotable skips any blocked item that also names a milestone in blocked-by, so closing an item blocker never refuses or names a dependent whose milestone blocker had already cleared: PL-K88Z's closure in #1712 left PL-JS6P, PL-WM5P, PL-VWXL and PL-SH0W (blocked-by v0.6.0, PL-K88Z) at blocked with only a grooming advisory
status: untriaged
feature: blocked-means-blocked
added: 2026-10-24
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
