---
id: PL-2BZY
title: branches_in_flight keeps one ref per id before the taken-on-base guard runs, so a spent claim on a bystander branch drops a live one: PL-HWW1 and PL-6TP8 read startable while keen-cannon and eager-brown carry them
priority: P2
effort: S
status: ready
classes: defect
feature: carrier-collapse
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-19
verify: grep -q 'def test_a_spent_claim_on_a_bystander_branch_does_not_drop_a_live_one' subprojects/docket/tests/test_vcs.py
---

**Problem.** branches_in_flight keeps one ref per id before the taken-on-base guard runs, so a spent claim on a bystander branch drops a live one: PL-HWW1 and PL-6TP8 read startable while keen-cannon and eager-brown carry them

**Observed, 2026-09-19 ~04:45, on the fetched remote.** Two live design rounds
were invisible to the in-flight mark for a reason unrelated to `PL-VYSP`'s
annotation rule. `origin/claude/keen-cannon-xjx373` carried `2e530ce PL-HWW1:
record the ratified decision...` (touching `ROADMAP.md`) and
`origin/claude/eager-brown-n820cl` carried `9c98ede PL-6TP8, PL-0M32, PL-6TN8,
PL-D0K3: write the verify: exit-status contract...` (touching `checks.py` and
`verify.py`) - ordinary claims by every rule. `bin/docket flight` listed the
three riders on eager-brown and nothing for `PL-6TP8` or `PL-HWW1`; `show`
called both startable.

**Mechanism.** `_unmerged_commits` keeps **one ref per id** in `_Walk.ids`,
chosen by candidate order - alphabetical among remote refs - before any guard
runs. `origin/claude/clever-fermat-qp7s60` sorts first and carries `efea697
PL-6TP8, PL-HWW1, PL-4FBP, PL-4Q9B: make the four tracking items the heads of
their own clusters`, the commit `#675` squash-merged, so its copies of the
`PL-HWW1` and `PL-6TP8` files are byte-identical to `origin/main`'s.
`_taken_on_base` then correctly finds clever-fermat's claim on those two ids
spent (the base took a commit leading with the id since the fork, and the
ref's copy equals the base's) and deletes the ids from `in_flight` - taking
keen-cannon's and eager-brown's live claims with them, because the walk had
already discarded those refs as carriers. `PL-4FBP` survived only because
clever-fermat is the session actually working it, so its copy differs.

Confirmed by `_taken_on_base({PL-HWW1: clever-fermat, PL-6TP8: clever-fermat,
PL-4FBP: clever-fermat}) == {PL-HWW1, PL-6TP8}` against the live refs, and by
`walk.staked` holding a stake for each of the three refs on each id.

**Why it matters.** It removes the guard from exactly the items ranked at the
top of `bin/docket next` - two of the five generator heads, while five sessions
were running on them - and it fails silently: `flight` prints the riders and
omits the head, which reads as a report that was made rather than one that
was collapsed. The collapse to one carrier is fine for the question `flight`
answers ("is this startable"); it is wrong as the input to a per-ref guard.

**Candidate fix.** Keep every ref per id in the walk (ordered by candidate
rank), let `_taken_on_base` judge each `(id, ref)` pair, and drop the id only
when every carrier's claim is spent - reporting the first survivor. `precedence`
already reads all carriers from `staked`, so the shape exists one function
down. Belongs beside `PL-BHVM`'s Q3 items (`PL-SH9Q`, `PL-KSCW`, `PL-MBTZ`),
which are the same content test applied per file; whether it is one build with
them is a triage judgment.

**Done when.** `_Walk.ids` maps an id to *every* ref whose subjects led with
it, in candidate order; `_taken_on_base` judges each `(id, ref)` pair and
`branches_in_flight` reports the first carrier whose claim is not spent,
dropping the id only where every carrier's is. Two tests pin the pair: a
bystander branch whose claim on an id the base has taken leaves a live
carrier's claim standing and the id is reported against the live branch; and
an id whose every carrier is spent still leaves the report. The `--source`
walk stays one `git log`, and the base side of each blob comparison is read
once per path rather than once per carrier.
