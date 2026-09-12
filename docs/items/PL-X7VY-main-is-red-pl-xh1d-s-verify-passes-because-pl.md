---
id: PL-X7VY
title: main is red: PL-XH1D's verify: passes because PL-78JQ created the CONTRIBUTING.md it tests for, so docket check --verify errors on every run
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.13
touches: docs/items/PL-XH1D-state-how-the-project-is-developed-and-what.md
added: 2026-09-08
closed: 2026-09-10
pr: 493
verify: bin/docket check && grep -qF "grep -qiF 'co-authored-by' CONTRIBUTING.md" docs/items/PL-XH1D-state-how-the-project-is-developed-and-what.md
---

**Problem.** main is red: PL-XH1D's verify: passes because PL-78JQ created the CONTRIBUTING.md it tests for, so docket check --verify errors on every run

**Found 2026-09-08** by `PL-55DH`, checking whether the base was green before
opening a pull request onto it. `origin/main` has been red since `cf6f71f`
(#488) and `4a4a4831` (#487) - runs 1691 and 1689 - on the `checks` job, and
the failure is one line:

> `PL-XH1D` is open but its `verify:` command already passes (1 of 111
> checked).

**Why it started.** `PL-XH1D`'s command is
`test -f CONTRIBUTING.md && python3 tools/doc_check.py check`. `PL-78JQ`
created `CONTRIBUTING.md` in #487, so the first half now passes and the second
half passes whenever the documentation is internally consistent - which it is
before the item is started too. The command was invalidated by another item's
work, and it did not stop discriminating: it never did.

**`PL-XH1D` is genuinely open**, so closing it is the wrong resolution.
`PL-78JQ`'s own brief says so in terms: "Deliberately not covered there: how
the project is developed and what each attribution trailer means. That is
`PL-XH1D`, still open, and saying it twice is how two documents come to
disagree." The item still owes the attribution disclosure in `README.md`, the
trailer scheme in `CONTRIBUTING.md`, and the owner's approval of any statement
made about him.

**Why it matters, and why nothing on a branch can see it: that is the sharper half.**
`make check` runs `bin/docket check` without `--verify`, so no local gate
reaches an open item's command. A *pull request* runs
`bin/docket check --verify --verify-base origin/<base>`, scoped by `PL-P3B6`
and `PL-L17Q` to the items the branch itself edited - correctly, since a branch
cannot have changed whether some other item's work merged. The whole-store
sweep runs only on a push to the default branch.

So the failure is invisible everywhere a session could act on it and visible
only after the merge, on a run nobody is watching and no pull request shows.
Measured 2026-09-08: `#490` is green on exactly the tree whose `main` run is
red. Every merge from here re-reds `main` until this is fixed, and each one
looks like a fresh break rather than the same one.

That is two of `CLAUDE.md`'s three compounding-friction tests at once - it
gives a wrong answer silently to every branch, and the advisory that would
carry it is one nobody is positioned to read - which is why this is worth
raising rather than filing and moving on.

**Corrected on closing, 2026-09-10.** "Invisible everywhere a session could act
on it" overstates it by one mechanism, and the overstatement is worth removing
so that a later reader does not build reporting this project already has.
`PL-0ZGK` shipped `tools/main_ci_status.py` in v0.4.9, and the session-start
digest now names main's last run: this session opened on `main's quality run
#1699 on 7e0ff5bb concluded failure - main is red and no pull request will show
it`, which is how it learned the failure was real before running anything. So
the failure *is* reported, once per session, to whoever starts one. What
remains true is the half that matters here: no check a branch can run reaches
it, because the whole-store sweep runs only on a push to the default branch -
so the branch that will re-red `main` is green when it merges.

**And a second correction, on the same reading.** The paragraph below infers
from `PL-XH1D` being `not-delegable` that its `verify:` "is worth a moment of
[the owner's] attention rather than a passing edit". That does not follow.
`Item.delegability` in `subprojects/docket/src/docket/model.py` states what the
field means in its first line - "Why this item may *not* be handed to a cheaper
model" - and `not-delegable:` is the one writable control that withholds an
item from `bin/docket delegable`. It says nothing about who else may work the
item: a session at full strength takes a withheld item like any other, which is
what happened here.

What is true is narrower, and it belongs to `PL-XH1D` rather than to this
field: that item's **Done when** requires the project owner to approve the
wording of any statement made about him, because that wording is the item's
deliverable. Its `verify:` line is not that wording, and repairing it was this
item's job. The first half of the paragraph below stands unaltered - the
fix-now door's second test genuinely did refuse `PL-55DH` the edit, since
`PL-XH1D`'s file sat outside its `touches`. Only the inference drawn after it
is withdrawn.

Recorded because the misreading is repeatable: a `not-delegable` reason that
names a close condition, as `PL-XH1D`'s does, reads as an instruction about who
must act. It is a reason for withholding the item from a cheaper model, and
nothing more.

**The fix is one line**, and it is the shape the `docket` skill prescribes -
something that runs and passes today, paired with a `grep` for what this item's
own work adds:

```
verify: python3 tools/doc_check.py check && grep -qF 'Co-authored-by' CONTRIBUTING.md
```

Run against the tree as it stands: `doc_check` passes, and the `grep` exits 1
because `CONTRIBUTING.md` does not mention the trailer scheme. Any phrase only
`PL-XH1D`'s work puts in the file would do; the trailer name is the one the
brief guarantees will be there.

**Not fixed by the session that found it**, deliberately. `CLAUDE.md`'s
fix-now door requires the change to touch no file outside the current item's
`touches`, and `docs/items/PL-XH1D-*.md` is outside `PL-55DH`'s. `PL-XH1D` is
also `not-delegable` on the ground that its wording states publicly what the
project owner did and did not write - so its `verify:` is worth a moment of
his attention rather than a passing edit.

**A second instance, found the same day, says this is a class rather than one
stale line.** `PL-X9T3`'s command was `grep -q 'PL-X9T3' docs/WORKING_NOTES.md`,
and `PL-55DH` wrote a section whose heading cites that id - correctly, since
that section is where the spike's measurements live. The grep passed while none
of `PL-X9T3`'s work had been done. Different route to the same place: in both
cases *another item's work* satisfied the command, and in both cases nothing
local reports it.

The shared lesson is the `docket` skill's own rule, which both commands broke:
a `verify:` must name something **only this item's work** creates. A file
another item creates is not that; an id that any note may cite is not that
either. `PL-X9T3`'s is repaired in place - it greps for a phrase its own
recorded measurement must carry, and the item's brief now states that phrase so
the command is a specification rather than a bet on a name. `PL-XH1D`'s is the
one still outstanding, and it is the one holding `main` red.

**Worth considering when this is fixed**, though not required by it: whether
`docket check` should advise on the *shape* rather than only on the outcome -
a command whose whole discriminating half is a `grep` for an id, or for a file
some other item is known to create, is suspect before it starts passing. That
is a judgment about a command's wording, so it may be past what a script can
decide; the outcome check that caught both of these already exists and works.

**Done when** `bin/docket check --verify` reports zero errors on `origin/main`,
and `PL-XH1D`'s command fails against a tree that has not done its work.
