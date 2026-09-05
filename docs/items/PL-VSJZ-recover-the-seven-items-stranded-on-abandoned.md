---
id: PL-VSJZ
title: Recover the seven items stranded on abandoned branches, including two the score-architecture drops created
priority: P2
effort: S
status: done
closed: 2026-09-05
classes: defect
feature: docket-store
touches: docs/items, docs/WORKING_NOTES.md
added: 2026-09-05
verify: bin/docket check && ! bin/docket stranded | grep -qE "^PL-(39B7|4RBD|6580|C4PH|JDX0|KBFN|Y5WR) "
---

**Problem.** Seven items existed only on `origin/claude/sampling-frequency-review-ju1knf`,
`origin/claude/capture-cleanup-tk6a1v` and `origin/claude/next-item-75htc6` —
invisible to `bin/docket next`, `list`, `status` and the session digest, and
therefore to every session choosing what to work on. No live session held any
of those branches (checked against the harness session list, 2026-09-05).

**Why it matters.** Two of the seven are findings *about work this project
just did*, and losing them would have been the expensive kind of loss:

- **`PL-Y5WR`** — the 30-day scenario cap is enforced nowhere as an explicit
  halt, and dropping `PL-011` removed the only item that required it. That is
  a gap the 2026-09-05 score-architecture drops created, caught by another
  session and stranded before anyone could act on it.
- **`PL-C4PH`** — record the history sampling cadence as a decision of its
  own, separate from the integration step. The same root cause the
  2026-09-05 design round reached independently, filed first and never seen
  by it. It is v0.5.0 scoping input.

`PL-JDX0` (state the coupled system's modal time constants in `docs/MODEL.md`)
is the third that bears on the coming milestone.

**A defect in the recovery path itself, found by following it.** `bin/docket
stranded` printed a recover line for `docs/WORKING_NOTES.md`, and running it
verbatim **reverted `main`**: the branch predates `PL-LLWN`'s merge, so the
per-file `git checkout` overwrote 93 lines of settled content with the
branch's older copy while adding 38. A recover line is safe for a file that
exists *only* on the branch and unsafe for one `main` has since changed, and
the command does not distinguish them.

That is direct evidence for `PL-39B7` (make `docket stranded` distinguish a
merged-and-deleted branch from an abandoned one, and say when its `main` is
stale), which this item recovered — it is now recovered *and* has a worked
example. Recorded here rather than acted on: the fix is that item's.

**Worked.** The seven item files were recovered as-is. `docs/WORKING_NOTES.md`
was merged rather than checked out: `main`'s copy restored, and only the
branch's new "Decided: no numpy" section appended, with a dated correction
noting that two of its three measurements describe `select_indices` and
`RunHistory.record`, which `PL-2FM6` and `PL-8LXM` delete, while its
conclusion survives on independent ground. Net effect on that file is 52
additions and 0 deletions. No recovered item's content was edited, and none of
their work was started.

**`PL-KBFN` arrives already closed, and that is why this branch's pull
request title names it.** Its record was `status: dropped, closed: 2026-09-05`
on the branch it was stranded on — another session did that work and its
closure never reached `main`. Carrying the file therefore closes it from
`main`'s point of view, so `tools/pr_title_check.py` requires the title to
lead with `PL-KBFN, PL-VSJZ`; `docket check` recovers a closed item's pull
request from that subject, and an id that never leads one is attributed to
its own capture commit instead (`PL-GW37`). Its `verify:` was re-run here and
passes: `PL-XLQ5` is on `main`, so the recovery item it stood for is
legitimately dropped. No work of its was done by this item.

**Done when.** All seven items are in the checkout, `bin/docket stranded`
no longer names them, `docs/WORKING_NOTES.md` retains every section `main`
held, and `make check` is green.
