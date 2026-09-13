---
id: PL-1MKQ
title: bin/docket release stamps its items one file at a time, so an interrupted cut leaves a milestone stamped on items no release notes name, and the re-run's notes silently cover only the remainder
priority: P2
effort: M
status: done
classes: defect
feature: release-process
touches: subprojects/docket/src/docket/release.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_cli.py
added: 2026-09-13
closed: 2026-09-13
pr: 513
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_a_cut_interrupted_inside_the_stamp_loop_is_resumed_whole' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket release stamps its items one file at a time, so an interrupted cut leaves a milestone stamped on items no release notes name, and the re-run's notes silently cover only the remainder

**Observed cutting v0.4.15, 2026-09-13.** A `make release VERSION=0.4.15` was
interrupted partway through `cmd_release`'s stamp loop. The loop had written
`milestone: v0.4.15` into 26 item files; `bump.write()` and the notes write,
which both follow the loop, had not run. The tree was therefore: 26 items
claiming to have shipped in a release that did not exist, `pyproject.toml`
still reading `0.4.14`, and no `docs/releases/v0.4.15.md`.

**The re-run is the part that is dangerous, because it succeeds.** `readiness`
treats a stamped item as already shipped, so the second run saw only the 7
remaining unstamped items. It printed `7 finished item(s) since 0.4.14`,
rendered a notes file naming those 7, bumped the version and exited 0. Nothing
in that output distinguishes it from a correct cut of a 7-item release. The
resulting `docs/releases/v0.4.15.md` would have been the permanent record of a
33-item release, listing 7 of them, with the other 26 carrying a `milestone:`
that no notes file names.

**It was caught by reading the two numbers side by side** - the dry run had
said 33 and the cut said 7 - and not by any check. The repair was to revert
the stamps (`git checkout -- docs/items pyproject.toml uv.lock`, plus removing
the untracked notes file and the one item the run had renamed) and cut once,
uninterrupted, which produced the correct 33.

**Why it matters.** `cmd_release`'s own comment states the guarantee this
breaks: "a release records all of itself or none of it". That guarantee was
written for the failure it does hold against - `prepare_bump` is called before
the loop so a rejected bump cannot strand a stamp - and it does not hold for an
interruption inside the loop, which is the likelier event. The release notes
are the only record of what a range of work was for, and the failure mode
produces a short one that looks complete. `CLAUDE.md`'s first
compounding-friction test is a check passing while the guarantee it stands for
is void; this is that, on the one command whose output is permanent.

**Two repairs, and they are independent.**

1. *Make the detection deterministic, which is the cheap half.* Nothing
   reconciles a release's notes file against the items stamped with that
   milestone, and the comparison is decidable: for every `milestone: vX.Y.Z` in
   the store there should be a `docs/releases/vX.Y.Z.md` naming exactly those
   ids. As a `docket check` error it would have caught this state the moment it
   existed, and it costs nothing on a healthy store. This is the half worth
   doing even if the second is declined.
2. *Make the write atomic, which is the real fix and the larger one.* Options
   worth weighing rather than a decision: write the notes and the bump first
   and the stamps last, so an interruption leaves the store unstamped and the
   re-run repeats cleanly; or stage every item write and rename them into place
   at the end; or record an in-progress marker the next run reads. The first is
   probably the smallest change that inverts the failure into a safe one.

**Done when.** A cut interrupted anywhere in `cmd_release` leaves a state that
either re-runs correctly or is reported as inconsistent by `docket check`, with
a test that interrupts the stamp loop and asserts the outcome.

**Built: the reclaim, not the reorder.** Both repairs landed, and the second
one is not the option this item leaned towards. Reordering the writes - notes
and bump first, stamps last - closes only the interruption that lands *between*
the two halves. Interrupted inside the stamp loop, which is the likelier event
and the observed one, the re-run still sees a short set; and under that
ordering it overwrites the correct notes with the short ones, so the residual
case is worse than the one it replaces rather than equal to it.

What holds at every interruption point is making the cut of a named version
**idempotent**: `release.unreleased` takes a `resuming` argument, and items
already stamped with the version being cut are folded back in beside the
unstamped ones. A re-run then re-stamps the same set, re-renders the same
notes and re-writes the same version. Three supporting pieces:

- `release.unrecorded_milestones` is the one rule for "an interrupted cut":
  a milestone stamped in the store with no notes file. `cmd_release` resumes
  what it names and `checks` reports it, so the command and the check cannot
  drift into two definitions.
- Its floor is the lower of the oldest version with a notes file and the
  current version. The first exempts v0.2.2, which shipped eleven items before
  `docs/releases/` existed; the second covers a project's *first* release,
  where the interrupted cut has written no notes file to take a floor from.
- The untagged guard is skipped for the version being resumed. A cut
  interrupted after its bump leaves `current` reading the release being
  finished, and the guard would otherwise refuse the only run that can write
  its notes. A run asked for a *different* version while a cut is unfinished is
  refused outright, which is what stops one interrupted release becoming two.

**On the detection half's premise.** `_check_milestones` did already error on
the observed tree, because the stamps named a version above the one
`pyproject.toml` read. The silence is one step later: once the re-run bumped,
the stamps and the version agreed and only the notes disagreed, which nothing
compared. That is the window `_check_release_notes` closes, in both directions.

**Measured before it became an error**, per `.claude/rules/expert-review.md`:
across 37 releases, 36 agree exactly between their notes and their stamps and
the 37th is v0.2.2, below the floor. The first attempt read every id in a notes
file and made 20 of the 37 look inconsistent - item titles quote other ids -
so the pattern is anchored to the bullet's leading id, which is the only place
the notes actually claim an item.
