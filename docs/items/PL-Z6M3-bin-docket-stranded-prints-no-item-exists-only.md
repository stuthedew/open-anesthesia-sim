---
id: PL-Z6M3
title: bin/docket stranded prints 'No item exists only on a branch' while an item sits on two branches and not on main, because the predicate is 'neither the store nor the default branch' and the rendered sentence drops the store half
priority: P2
effort: S
status: done
classes: defect
feature: rendered-claim-accuracy
touches: subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-09-19
closed: 2026-09-26
verify: grep -q 'def test_stranded_states_both_halves_of_its_predicate' subprojects/docket/tests/test_cli.py
recurrences: 2026-09-25 PL-LFNK, 2026-09-26 PL-PV6H
---

**Problem.** bin/docket stranded prints 'No item exists only on a branch' while an item sits on two branches and not on main, because the predicate is 'neither the store nor the default branch' and the rendered sentence drops the store half

**Found doing it.** This session recovered `PL-6T44` from
`origin/claude/optimistic-brahmagupta-63pa72` and pushed it to
`origin/claude/pl-swp3-x5j7w1` under `#674`. The next `bin/docket stranded`
printed:

```
No item exists only on a branch, across the 26 branch refs this checkout holds.
```

At that moment `PL-6T44` was on exactly two branches and **not** on
`origin/main`. Checked directly: `git cat-file -e
origin/main:docs/items/PL-6T44-*.md` → absent; the file present on
`origin/claude/optimistic-brahmagupta-63pa72` and
`origin/claude/pl-swp3-x5j7w1` and nowhere else.

**The behaviour is right and the sentence is wrong.** `vcs.stranded`'s docstring
states the predicate exactly - "items that exist on some branch and in neither
the store nor the default branch" - and gives the reason `known_ids` includes
the calling session's own working tree: "an item captured on this branch a
moment ago is not reported back to the session that captured it." That is
correct and worth keeping. What is wrong is only the rendered line at
`subprojects/docket/src/docket/render.py:484`, which reports the two-part
predicate as a one-part claim. The digest's own wording gets it right - "Only on
a branch, not in this checkout" - so the accurate phrasing already exists in the
tree.

**Why it matters, and why it is not cosmetic.** The silence is self-inflicted and arrives at the
worst moment. A session that recovers a stranded item is, by construction, the
session whose checkout now holds it - so from that moment the command tells that
session the hole is closed while the item is still absent from `main`. If the
recovering pull request is never merged and the container is reclaimed, the item
is stranded again and now sits on *two* unmerged branches instead of one, with
nothing in between having reported it. The recovery procedure in
`.claude/skills/docket/SKILL.md` ends at "restore the file, commit it on its
own" and has no step that re-checks against `main`, so nothing else catches it
either.

It also reads wrong to any session on a branch that captured items and has not
merged: its own captures are in its store, so a clean line means "clean for
you", not "clean".

**This is the apparatus floor rather than a nicety.**
`.claude/rules/apparatus-standard.md`: "What this apparatus tells a session must
be true, or must say what it could not read." The line already carries one bound
- "A branch not fetched here was not read" - and simply omits the other.

**Smallest fix.** Say what the predicate is, in both the finding and the
no-finding case: *"No item exists only on a branch and outside this checkout's
store"*, or name the count it suppressed - *"...; N carried by a branch are
already in this checkout's store"* - which would have printed `PL-6T44` here and
is the more useful of the two, since the suppressed set is exactly what an
unmerged recovery looks like.

**Where.** `subprojects/docket/src/docket/render.py:484`, and the finding-case
heading above it. No change to `vcs.stranded`.

**Done when.** `bin/docket stranded` states both halves of its predicate in the
no-finding case as well as the finding case - naming the count it suppressed
because this checkout's own store holds those items, or saying in the sentence
that the claim is bounded by the store as well as by what was fetched - and a
test under `subprojects/docket/tests/test_cli.py` drives an item present on a
branch and in the store but absent from the default branch.

**Worked.** Took the brief's first route, stating the predicate, rather than
naming the suppressed count: `StrandedReport` carries no such count, and adding
one means changing `vcs.stranded`, which the brief rules out and `touches` does
not reach. The empty case now reads "No item exists only on a branch and
outside this checkout's store", which keeps the prefix
`test_stranded_reports_nothing_when_every_branch_has_landed` pins, so no
existing assertion changed; its second line names the store bound beside the
fetch bound. The finding case's heading carries the same two halves, and so
does its closing line, "Every other branch read carries no item the default
branch lacks", which made the same one-part claim and is fixed here too, with
the docstring sentence that repeated it. One test,
`test_stranded_states_both_halves_of_its_predicate`, drives both cases from
`_branched_repo` with `--no-fetch`: checked out on `abandoned` the store holds
`PL-K7QX` and `main` does not (read from `git ls-tree`, not assumed), and
checked out on `main` the item is reported under the two-part heading.
