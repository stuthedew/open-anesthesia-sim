---
id: PL-W1LN
title: The in-flight walk guard cannot catch a false positive whose walk ends against a commit the base reaches by another path
priority: P3
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
milestone: v0.4.15
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-08-31
closed: 2026-09-13
pr: 505
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_flight_reports_below_an_uneven_horizon_which_is_the_accepted_limit' subprojects/docket/tests/test_cli.py
---

**Problem.** `PL-MGNC` made `_unmerged_commits` refuse a walk that ran off the
end of the history, detecting it by the commit with no parents such a walk
ends on. That catches every shape observed and the reproduction built for it,
but it is not the same claim as "the walk is complete".

A commit the default branch holds below its own grafted horizon is a false
positive whether or not the walk reaches a parentless commit afterwards. The
uncaught shape is a walk that descends past the horizon and then terminates
against some *other* commit the default branch does reach - possible where the
default branch's visible history is a merge structure whose paths are truncated
unevenly. The walk ends cleanly, and the ids it collected below the horizon are
reported.

**Why it matters.** Bounded rather than urgent: the failure direction is the
dangerous one - ids wrongly reported here are withheld from `docket next` - but
the topology needed is narrower than the one that fired on 2026-08-31, and
nothing has been seen taking it. Recorded so the guard's limit is written down
rather than inferred from its absence.

**Where.** `subprojects/docket/src/docket/vcs.py` - `_unmerged_commits`.

**Done when.** Either the shape is reproduced with real git and the guard
covers it, or it is shown to need a history this project cannot produce and
this is dropped with that reasoning in its `reason`.

**Triaged 2026-09-01.** P3, `defect`/`infra`, `parallel-sessions`. The
`verify:` command was run first and selects nothing today, so it exits 5 until
a test named for the horizon exists; `-k walk` and `-k contained` both select
passing tests and would prove nothing.

Left out of v0.2.8's frozen list: this records a limit of `PL-MGNC`'s guard
rather than an observed misfire, and its own **Done when.** allows the answer
to be that the topology cannot be produced here. An entry that may turn out to
be undemonstrable is not one to hold a release open with.

## Reproduced with real git, 2026-09-13, and the guard does not fire

The triage note above allowed that this might need a history the project cannot
produce. It does not: the shape is reproducible in seven commands, and the
uncaught walk reports three `main` commits as somebody's in-flight work.

The topology is a `main` whose two paths differ in length - a long one and a
short one joined by a merge - and a `--depth` that lands *between* them. Depth is
counted per path from the tip, so one number truncates the long path and reaches
the root down the short one, which is the uneven truncation this item predicted:

```text
git clone --depth 5 --no-single-branch --branch main <origin> c3
git fetch origin work:refs/remotes/origin/work      # forked from a main commit
git log --source --format='%S %h %p %s' ^origin/main origin/work --
```

`origin/main` is left grafted at `main A4` on the long path while reaching
`root` down the short one, so `^origin/main` excludes nothing below `A4` on that
path. The walk then reports:

```text
origin/work e54529e 0e8aff6 PL-HRZN: live work forked from a main commit
origin/work 0e8aff6 88e71e7 main A3
origin/work 88e71e7 049a227 main A2
origin/work 049a227 45124c6 main A1
```

Three of the four are `main`'s own commits. **Every one of them has a parent**,
and the walk ends against `45124c6`, which the base *does* reach - so it is a
clean stop by `PL-MGNC`'s rule and `unbounded` stays empty. An id leading any of
those subjects is reported in flight and withheld from `bin/docket next` under
"do not start these again".

## Why it is not being fixed in the same pass, and what needs deciding

The signature the existing guard uses - a parentless commit in the walk - is
absent here by construction, and no *sound* replacement is available inside a
truncated checkout. The decisive question is whether an emitted commit is one the
base reaches in the **full** history, and the commits that would answer it are
exactly the ones the clone does not hold. Three dispositions, and the choice is a
trade rather than a bug fix:

1. **Name a ref unread whenever the base is truncated.** Sound and far too
   blunt: an agent session's container is normally shallow, so `flight` would
   report nothing at all in the common case and the collision guard it exists to
   be would be gone.
2. **Fetch to deepen before walking.** Answers it exactly and breaks the rule
   that `docket check` runs from a bare tree with no network.
3. **Accept the limit and document it**, which is what the code does today, with
   this reproduction recorded so the limit is demonstrated rather than inferred.

A date-based narrowing - distrust an emitted commit older than the base's newest
graft - would cover this case cheaply, but it rests on commit dates, which a
rebase or a skewed clock moves, so it trades an exact guard for a heuristic one
in the direction that withholds work.

Moved to `needs-decision` because the item's own **Done when.** offers only
"the guard covers it" or "the topology cannot be produced here", and the
reproduction above rules out the second while the first cannot be had soundly.
Which of the three to take is the project owner's call, and it is cheap now: the
recipe is written down and the failing walk is one clone away.

**Decision needed.** Which of the three dispositions above to take: name a ref
unread whenever the base is truncated (sound, and it silences `flight` in every
shallow container), deepen by fetching before the walk (exact, and it breaks the
bare-tree/no-network rule), or keep today's behavior with the limit documented and
this reproduction standing as the evidence. A fourth, distrusting an emitted
commit older than the base's newest graft, is cheap and covers this case but rests
on commit dates a rebase moves.

**Where the test goes, if the decision is to cover it.**
`subprojects/docket/tests/test_cli.py`'s `_shallow_pair` already builds this in
real git for `PL-MGNC`'s *caught* case: the default branch fetched to a depth that
leaves it grafted, and a branch fetched past that graft. The uncaught shape is one
change to it - `main` needs a **second, shorter path** to the root, so that the
depth truncates the long path while the short one reaches bottom, and the walk
then terminates against a commit the base still reaches instead of against a
parentless one. So the fixture is nine-tenths built, and the `-k horizon` selector
this item's `verify:` names has somewhere to live.

## Decided and closed 2026-09-13: the limit is accepted, documented and pinned

**Project owner's answer to the three dispositions above: keep today's behavior,
with the limit documented.** So this closes on its **Done when.**'s first branch in
substance rather than its letter - the guard does not cover the shape and
deliberately will not, and what covers it instead is a test that asserts the wrong
answer on purpose plus two documents that say why.

**What the reproduction turned out to be worth.** Built as a real-git fixture,
`_unevenly_truncated_pair` in `subprojects/docket/tests/test_cli.py`, sibling to
the `_shallow_pair` the *caught* case uses. The difference between them is one
commit's worth of topology - `main` reaching the root down a second, shorter path -
and that is enough to remove the parentless commit `PL-MGNC`'s guard keys on. Run
end to end through `bin/docket flight`, it is worse than this item predicted:
**three** of the default branch's own commits are reported as work a branch is
carrying (`PL-M1QJ`, `PL-M2KT`, `PL-M3NW`), with `unbounded` empty and no ref named
unread.

**Where the limit is now written down.** `_unmerged_commits`' docstring, which
previously implied the converse - "a walk that ends soundly ends against a commit
`base` excluded" - and now states that the signature catches its shape and is not a
proof of completeness; `subprojects/docket/README.md`'s walk-guard section, same
correction; and the test itself, whose docstring carries the decision and says that
a later change making it pass differently is progress rather than regression, so
long as it is a decision.

**Why not each alternative**, recorded so this is not re-litigated. Naming a ref
unread whenever the base is grafted is sound and silences the read in every agent
container, which is the common case. Fetching to deepen answers exactly and breaks
the rule that these commands run from a bare tree with no network. Distrusting a
commit older than the base's newest graft covers this case cheaply and rests on
commit dates, which a rebase or a skewed clock moves - an exact guard traded for a
heuristic one, in the direction that withholds work.

**The `verify:` was corrected while closing.** It was `pytest ... -k horizon`, which
selects nothing and exits 5 - the shape `.claude/skills/docket/SKILL.md` warns reads
as a command correctly failing when it is really a command specifying nothing. It is
now the prescribed pair: the file's whole suite, which proves the suite healthy, and
a `grep` for the test the work adds, which exits 1 until that test exists. Both
halves were run - the grep against `origin/main`'s copy returns 1, and the pair
returns 0 here.

**Found while building it:** `_shallow_pair`'s own commits carry `PL-M01`-style
subjects, which `ID_PATTERN` does not match, so the sibling test's
`assert "PL-M01" not in out` cannot fail. Filed as `PL-CY8B`; that test's other
assertions are sound, so the guard is still covered.
