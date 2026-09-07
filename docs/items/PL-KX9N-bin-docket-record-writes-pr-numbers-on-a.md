---
id: PL-KX9N
title: bin/docket record writes pr numbers on a shallow clone that docket check declines to verify on the same clone, so it silently records wrong provenance
priority: P2
effort: M
status: done
classes: defect, infra
feature: commit-provenance
milestone: v0.4.7
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-06
closed: 2026-09-07
pr: 419
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_record_declines_on_a_checkout_it_cannot_walk' subprojects/docket/tests/test_cli.py
---

**Problem.** Observed 2026-09-06 in a web session working `PL-GYH2`. The
container had no checkout, so the repository was cloned per the harness
instruction with `git clone --depth 1`, which is shallow *and* single-branch.
`bin/docket check` raised its ordinary advisory - five items closed on the base
recording no `pr`, each "recoverable from its merge commit" - and the `docket`
skill's instruction for that is to let `bin/docket record` ride the commit you
are already making. It did. **Four of the five numbers it wrote were wrong.**

| Item | `record` wrote | Actually merged in |
| --- | --- | --- |
| `PL-6Q8N` | 401 | **399** |
| `PL-GJDW` | 401 | **400** |
| `PL-N2X4` | 401 | **400** |
| `PL-VRMK` | 401 | **402** |
| `PL-S5LB` | 401 | 401 (correct) |

The mechanism: a depth-1 clone holds one commit of `main`, so the walk that
recovers a number from the newest merge subject naming an id reached only the
newest commit it had, whose subject named `PL-S5LB` and `#401`. Every other id
resolved to that same commit by default. Re-run after
`git fetch --depth=200`, `record` produced all four correctly.

**Why it matters, and why this is the silent-wrong-answer case rather than an
inconvenience.**
`docket check` on the *same* checkout already declines the verification half,
printing "recorded pull requests: the checkout is a shallow clone, so the
commits it is missing are the oldest ones and the longest-settled provenance
would read as broken" under **Not checked**. So the store knows the clone is
truncated when it would *verify* a number, and writes one anyway. After the
write, `docket check` reports `0 errors`: the field is present and
syntactically fine, and the one check that could have contradicted it has
already excused itself. This is `CLAUDE.md`'s first compounding-friction test
exactly - a check passing while the guarantee it stands for is void.

It survived only by accident. Four of the five collided at a merge conflict
against sessions that had written the right numbers with fuller history, which
is what surfaced it; had those sessions not existed, or had they run `record`
later, the wrong numbers would have merged unremarked. `pr` is provenance -
`PL-YDL6` and `PL-JZ1D` are both about recovering the right number - so a
wrong one is worse than an absent one, and the skill forbids hand-editing the
field precisely so the command is trusted.

**Fix, in the shape the store already has.** `record` should apply the same
completeness test its verifier applies and decline on a truncated checkout,
naming the fetch that would let it answer - the way `PL-99Y4` made the missing
`pr` advisory decline rather than error on an incomplete clone. Declining is
cheap: a session that wants the write runs one bounded fetch first.

**What was built, and the one place it differs.** The completeness test was
already in this module: `closed_by` refuses a revision whose parent the
checkout does not hold, with a docstring saying that answering anyway "would
stamp one pull request number across the whole store". It asks the same
question from the other end - of one commit rather than of one file - and the
two readings behind `closures_on_base` never got the guard. `_parent_in_reach`
is now shared by all three, and `_closed_at` gives the closure test a third
answer beside true and false, the way `is_shallow` has three.

So the decline is **per closure rather than per checkout**, and that is the
deliberate departure from the paragraph above. Keying it on `is_shallow` would
have refused the numbers a bounded fetch had just made provable, because a
clone deepened to any bounded depth is still shallow - including the `git fetch
--depth=200` recorded above as the recovery, against a 746-commit history. The
observable difference is confined to a partly deepened clone: measured against
real git on a 12-commit history fetched to depth 4, the three closures whose
commit *and its parent* are held resolve correctly and the nine at or below the
graft boundary decline. At `--depth 1`, where this was found, the two rules
agree exactly - nothing is written.

Fixing the derivation rather than the writer also covers the reader. `docket
check`'s advisory prints the derived number as a fact - "#401 is recoverable
from its merge commit" - so a `record` that declined while the advisory went on
naming 401 would have left the wrong number on screen and the skill's
instruction pointing at it.

**Where.** `subprojects/docket/src/docket/vcs.py`,
`subprojects/docket/src/docket/cli.py` (`cmd_record`); the completeness test
the checker already uses is the thing to reuse rather than to reinvent.

**Done when.** `bin/docket record` declines to write a `pr` on a checkout whose
history it cannot walk, naming the fetch that would let it answer - the same
completeness test the verifier already applies, reused rather than reinvented -
and a test covers the shallow clone at the depth this was found at.

`test_record_declines_on_a_checkout_it_cannot_walk` is that test, against real
git rather than a fake: the defect was a wrong belief about what git does at a
graft boundary - it reports every file in the boundary commit's tree as *added*
- and no fake would have been written with that shape unless somebody already
knew. It builds a remote whose last three commits each close one item under
`#399`, `#400` and `#401`, clones it `--depth 1`, and asserts that `record`
writes nothing and names `git fetch --unshallow origin`; then it runs that
fetch and asserts all three correct numbers land. Against the unfixed code it
writes `pr: 401` onto all three.

**Found by** `PL-GYH2`, whose own commit carried four of the wrong numbers
until the merge exposed them.
