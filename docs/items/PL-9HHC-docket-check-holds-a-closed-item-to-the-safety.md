---
id: PL-9HHC
title: docket check holds a closed item to the safety band, so dropping an anticipated safety item that sat at P2 while blocked is refused until its priority is rewritten to P1 - a band that ranks nothing on a closed item and misstates the one it held: PL-Y04W's drop on 2026-09-26 needed it, as PL-TBMX's did
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py, docs/items/PL-Y04W-build-break-out-an-area-taken-into-its-own-top.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: an anticipated safety item that waited at P2 can be dropped as it stands, so its record keeps the priority it held rather than a P1 written only to pass the check
verify: grep -q 'def test_a_dropped_anticipated_safety_item_keeps_the_band_it_held' subprojects/docket/tests/test_checks.py
---

**Problem.** docket check holds a closed item to the safety band, so dropping an anticipated safety item that sat at P2 while blocked is refused until its priority is rewritten to P1 - a band that ranks nothing on a closed item and misstates the one it held: PL-Y04W's drop on 2026-09-26 needed it, as PL-TBMX's did

**Reproduced 2026-09-27.** With `PL-Y04W`'s priority put back to the `P2` it
held while blocked (`cb8ae41e`, the commit that dropped it, rewrote it to
`P1`), `bin/docket check` exits 1: "class 'safety' sits at P2; safety-critical
work starts at P0 or P1". The rule is in `_check_item` in
`subprojects/docket/src/docket/checks.py`: `exempt` is `status == "blocked" and
"anticipated" in classes`, and nothing reads whether the item is closed, where
the three `verify:` shape rules above it each open with `item.status not in
CLOSED_STATUSES`. `PL-TBMX`'s history records no earlier priority - it was
written at `P1` in the commit that dropped it, `93351966` - so only `PL-Y04W`
has one to restore.

**Why it matters.** Each drop of an anticipated safety item is refused until
its priority is rewritten, so the record says the item held `P1` when it held
`P2`, and the drop's commit carries an edit that is not the drop. Thirteen
anticipated `safety` or `science` items sit blocked at `P2` or `P3` today, and
each is a drop that pays it again if its milestone never comes.

**Done when.** `docket check` holds no closed item - `done` or `dropped` - to
the safety band; a test drops a blocked `anticipated` safety item at `P2` and
the check passes, while an open safety item at `P2` still fails it; and
`PL-Y04W` is returned to the `P2` it held until it was dropped.

**Generator check.** The fact is that a closed item's fields are its record and
rank nothing, so no ranking rule binds them. `_check_item` already encodes it
for the three `verify:` shape rules, and the safety band is the rule that does
not. No head's `misread:` states it and no open item misreads it: a one-off. It
sits beside `PL-WHQS` (ready, `refactor`), which centralizes the closed-item
filter those rules each spell out; whichever lands second uses the other's
form.
