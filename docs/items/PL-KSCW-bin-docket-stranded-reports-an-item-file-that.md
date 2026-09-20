---
id: PL-KSCW
title: bin/docket stranded reports an item file that exists only on a branch but says nothing about a section appended to an item main already holds, which is how PL-879R's fourth-instance evidence and five other item edits sat unreported on claude/focused-dijkstra-outqzu
priority: P2
effort: M
status: ready
classes: defect
feature: stranded-ahead-or-behind
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-17
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_an_unmerged_edit_to_an_item_the_base_already_holds_is_named' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket stranded reports an item file that exists only on a branch but says nothing about a section appended to an item main already holds, which is how PL-879R's fourth-instance evidence and five other item edits sat unreported on claude/focused-dijkstra-outqzu

**Found working `PL-879R`** (dropped 2026-09-17). Its brief on `main` was
missing a whole section — a fourth `verify:` failure shape, and a count of the
population it implied — written by the `PL-32Z9` session onto
`origin/claude/focused-dijkstra-outqzu`. That branch has no pull request open,
and its session is idle on a question `#643` and `#646` have since answered. The
section is the evidence `PL-879R`'s decision turned on, and nothing reported it:
`bin/docket show` said only `Its file is already edited on <branch>`, which is a
concurrency warning rather than a recovery.

**Why `stranded` cannot see it.** It answers "which items exist *only* on a
branch", so it is keyed on the item file's existence. `PL-879R` exists on `main`,
so the item is not stranded; only 68 lines of its brief are. The same branch
carries edits to four more items `main` already holds — `PL-7SVX`, `PL-C4RS`,
`PL-D1RT` and `PL-MQH0` — none of them reported by anything.

**It is the same evidence loss `stranded` was built for.** The skill's own
framing — "a diagnosis nobody receives is a session spent for nothing" — applies
identically to a brief nobody merges. And the shape is more likely, not less: an
item's file is created once, while its brief is appended to by every session that
learns something about it.

**The decidable half.** For each unmerged ref, the item files it changed that
`main` also holds, and whether the branch's copy is ahead of `main`'s. That is
one `git diff --name-only` per ref plus a comparison, which is the shape
`stranded` already runs. The judgment it must not make is the same one
`stranded` already leaves to the reader: whether the branch is live work or
abandoned.

**One design question to settle first.** `stranded`'s recovery line is a `git
checkout <ref> -- <path>`, which overwrites `main`'s copy wholesale. That is
right for a file `main` does not have and wrong for one it does — `PL-KBFN` and
`PL-39B7` record it costing `PL-XLQ5` when a merged item was overwritten with an
older copy. So this case wants a diff to read, not a checkout to run.

**Done when** a branch carrying an unmerged edit to an item `main` already holds
is named by a `docket` command, with the diff to read rather than a checkout to
run, and the live-versus-abandoned judgment left to the reader.

**Immediately actionable regardless**: `origin/claude/focused-dijkstra-outqzu`'s
four remaining item edits are unreviewed. `PL-32Z9` and `PL-D1RT` both closed on
`main` under `#645`/`#646` with different content, so those two are likely
superseded; `PL-7SVX`, `PL-C4RS` and `PL-MQH0` are not.

**Why it matters.** `bin/docket stranded` exists because a diagnosis nobody
receives is a session spent for nothing, and it catches the rarer half of that.
An item file is created once; its brief is appended to by every session that
learns something about it, so the unmerged *section* is the common case and
nothing reports it. `PL-879R`'s decision turned on evidence that sat unreported
on a branch with no pull request open, and five more item edits are still there.
The only signal a session gets today is `Its file is already edited on <branch>`,
which is a concurrency warning - it says somebody may be in this file, never that
something is in it that `main` will never get.

**Done when** a `docket` command names, for each unmerged ref, the items the ref
edits that the base already holds and is ahead on, and prints the **diff to
read** rather than a `git checkout` to run - the distinction `PL-KBFN` and
`PL-39B7` record `PL-XLQ5` paying for - with the live-versus-abandoned judgment
left to the reader, as `stranded` already leaves it.

**Re-pointed by `PL-BHVM`'s design round, 2026-09-19.** Question 3 — is the
ref's copy ahead of the base's. `PL-SH9Q`, `PL-KSCW` and `PL-MBTZ` are one
build, not three: `stranded` keys on whether an item *id* is on the base, and
the predicate it wants is per item file and three-valued — the ref's copy is
**ahead** (report it, with a diff to read), **behind** (never report, never
print a checkout line) or **equal** (silent). Ahead-not-equal is `PL-SH9Q` and
`PL-KSCW`; behind is `PL-MBTZ`. Do them together.

**Grouped as `feature: stranded-ahead-or-behind`** (`PL-JKML`'s duplicate sweep,
2026-09-20). `PL-BHVM`'s design round settled on 2026-09-19 that `PL-SH9Q`,
`PL-KSCW` and `PL-MBTZ` are one build rather than three - one three-valued
per-item-file predicate, where the ref's copy is **ahead** (report it, with a
diff to read), **behind** (never report, never print a checkout line) or
**equal** (silent). That conclusion was written into two of the three briefs as
prose and into the store's only grouping field nowhere, so `bin/docket status`,
`bin/docket feature` and `recommend`'s finish-a-feature preference all read the
three as unrelated work, and they sat in two different features
(`parallel-sessions` and `stranded-item-edits`). They are ranked together by
`PL-BHVM`'s `root-cause-of:` and now grouped together as well; the group closes
when `stranded` makes that comparison.

**`PL-SH9Q` is this same finding and is dropped in its favour** (`PL-JKML`'s
duplicate sweep, 2026-09-20, confirmed on independent refutation against the
source). `vcs.stranded` builds `known = {store ids} | set(on_base)` and then
`continue`s per ref on `if identifier in known` - one branch, keyed on the id
being on the base and discarding content entirely. That single `continue` is
what both briefs indict, a day apart, each from the angle that bit it:
`PL-SH9Q` from `PL-PX7V`'s 60-line closure on
`origin/claude/wizardly-maxwell-dyzpjt`, this item from `PL-879R`'s appended
section plus five more edits on `origin/claude/focused-dijkstra-outqzu`.

**The one route to their being complementary was checked and is closed.**
`PL-SH9Q` floated a deliberately narrower rule - report only a modification
that *closes* an item, `status` moving into `done` or `dropped`. Built that
way, `PL-SH9Q`'s own done-when and its `wizardly-maxwell-dyzpjt` test would
both be satisfied while `PL-879R`'s append to a still-`ready` item went
unreported, leaving this item fully standing. That one-directional gap would
have made them halves. `PL-BHVM`'s 2026-09-19 design round retired the
closures-only option in favour of the three-valued per-item-file predicate, so
under the settled shape one predicate satisfies both done-whens and neither
fix leaves the other standing.

**`PL-SH9Q`'s surviving contribution, carried here.** Reporting *every*
branch-only modification would fire on every live branch editing its own item -
the check `CLAUDE.md` retires for firing each run without changing a decision.
So the ahead/behind/equal predicate is not only a correctness improvement over
the id test; it is what keeps the report quiet enough to be read at all.
