---
id: PL-JTHW
title: tools/main_ci_status.py passes over a cancelled main run in silence, so after PL-SMN4 a commit with no whole-store verdict is indistinguishable from one nobody asked about
priority: P3
effort: S
status: ready
classes: defect, infra
feature: ci-cost
touches: tools/main_ci_status.py, tests/unit/test_main_ci_status.py
added: 2026-09-16
verify: grep -q 'def test_a_cancelled_main_run_is_reported' tests/unit/test_main_ci_status.py && uv run pytest tests/unit/test_main_ci_status.py
---

**Problem.** tools/main_ci_status.py passes over a cancelled main run in silence, so after PL-SMN4 a commit with no whole-store verdict is indistinguishable from one nobody asked about

`VERDICTS` in `tools/main_ci_status.py` lists the conclusions that judged the
tree - `success`, `failure`, `timed_out`, `startup_failure`, `action_required` -
and `pick_run` walks past everything else to the newest run that reached one.
`cancelled` is excluded deliberately and the module docstring says why.

**That was right while a cancelled `main` run meant nothing, and `PL-SMN4`
changed what it means.** Under the shared concurrency group, a `main` run was
routinely evicted from the single pending slot by the next merge: 31 of the 257
completed `main` push runs between 2026-09-05 and 2026-09-16 - 12.1% - ended
`cancelled` having started no job. Reporting each of those would have been a
line on one session in eight about a run that was superseded seconds after it
was created, which is the advisory-nobody-reads failure `CLAUDE.md` names.

A per-commit group removed the eviction, so a `cancelled` run on `main` now
means a hand cancellation, a lost runner, or GitHub cancelling for its own
reasons. In every one of those the commit got no whole-store `bin/docket check
--verify`, and this tool still says nothing - it reports the *previous*
commit's verdict as "the most recent real answer about `main`", which is true
of that commit and silent about the one that lost its run.

**Why it was not fixed in `PL-SMN4`.** It is a behavior change with a new
output line and therefore owes a test, which closes `CLAUDE.md`'s fix-now door
on test 1. The prevention `PL-SMN4` shipped is what the item's **Done when.**
asked for; this is the reporting half it names as its second candidate shape,
scoped down to what is left once the common case is gone. `PL-SMN4` corrected
the docstring to say what now holds and to point here, so nothing in the tree
currently claims otherwise.

**Done when.** A `main` commit whose quality run was cancelled is visible to a
session - through the session-start digest or by running the tool by hand -
rather than being passed over in silence. The rule that a green `main` prints
nothing is not up for revision: whatever this reports has to be something a
reader can act on, and the rate to beat is the one above without the eviction
in it.

**Worth measuring before designing it.** How many `cancelled` `main` runs
remain once eviction is gone is not known - every instance in the window above
has that cause. If the honest answer is a handful a year, the cheapest shape
may be a line in `advisory` rather than any new state.

**Why it matters.** A commit that got no whole-store check and a commit nobody
asked about are different facts, and the tool now reports them identically: it
names the *previous* commit's verdict as "the most recent real answer about
`main`", which is true of that commit and silent about the one that lost its
run. A check reporting confidently about a question it did not answer is the
silent-wrong-answer shape `CLAUDE.md` names, and it reaches the session-start
digest, which is where a session forms its first view of whether `main` is
sound.

**Handoff, 2026-10-01 (CI and tooling tweaks thread).** Claimed on
`claude/ci-tooling-tweaks-53wk39` with `PL-7K2C`, `PL-CR36` and `PL-NWSK`, all
three closed there with `pr: 1259`. The thread stopped for length before
starting this item, so nothing below is done yet:

1. Re-confirm the brief against `tools/main_ci_status.py` (`VERDICTS`,
   `pick_run`, the docstring that points here); `show` asks for it, since this
   was filed more than 14 days ago.
2. Measure first, as the brief says: count `quality.yml` runs on `main` with
   event `push` and conclusion `cancelled` since `PL-SMN4` merged
   (`actions_list`, `list_workflow_runs`, resource `quality.yml`, branch
   `main`). Every one in the brief's window was an eviction.
3. Choose the shape on that count and record why here. A green `main` still
   prints nothing; a cancelled run on a commit newer than the verdict reported
   is a line a session can act on (re-run it).
4. `def test_a_cancelled_main_run_is_reported` in
   `tests/unit/test_main_ci_status.py`, failing before the change, which is what
   this item's `verify:` greps for.
5. Close it with `bin/docket set PL-JTHW --status done --closed DATE` and
   `bin/docket record 1259`, in one commit with the work, retitling `#1259` to
   lead with all four ids first.
6. For the whole pull request: sweep the docs (`make doc-check`, and
   `python3 tools/doc_check.py candidates --base origin/main`), run
   `bin/docket verify --self PL-7K2C PL-CR36 PL-NWSK PL-JTHW` to `ACCEPT`,
   write the body, mark it ready and leave it unarmed: it changes `tests/`, so
   it waits on the project owner's read, with the review summary the project
   instructions describe.
