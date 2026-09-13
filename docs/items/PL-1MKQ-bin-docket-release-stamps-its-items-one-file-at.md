---
id: PL-1MKQ
title: bin/docket release stamps its items one file at a time, so an interrupted cut leaves a milestone stamped on items no release notes name, and the re-run's notes silently cover only the remainder
status: untriaged
added: 2026-09-13
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
