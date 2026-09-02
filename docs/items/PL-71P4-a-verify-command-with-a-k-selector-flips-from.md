---
id: PL-71P4
title: "A verify: command with a -k selector flips from correctly failing to falsely passing when unrelated work adds a matching test name, so the already-passes set grows on its own"
priority: P2
effort: S
status: done
closed: 2026-09-02
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, docket.toml, subprojects/docket/tests/test_checks.py
added: 2026-09-02
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_an_item_whose_work_has_landed_is_an_error' subprojects/docket/tests/test_checks.py
---

**Problem.** `PL-L9JS` records eight open items whose `verify:` command passes
on a tree without their work, and scopes itself to repairing those eight. The
set is not static. On 2026-09-02 `bin/docket check` named **nine**, and the new
one arrived without anybody touching it:

- `PL-6P9Y` carries `uv run pytest subprojects/docket/tests/test_roadmap.py -k
  out_of_scope`. On 2026-09-01 it was one of the twenty items `PL-5QKT`
  recorded as *selecting no test* - exit 5, reading as a command that correctly
  fails.
- `PL-Q2BJ` (rank the digest's Top line against the plan, #144, merged
  2026-09-01) added `test_the_digest_names_the_milestone_when_only_out_of_scope_work_is_ready`
  to that same file. Unrelated work; it was not about `PL-6P9Y` at all.
- `-k out_of_scope` now matches that test, the command exits 0, and `PL-6P9Y`
  moved from the "selects nothing" advisory to the "already passes" one. Its
  own work - reading a milestone's *Explicitly out of scope* list - has not
  been started.

Verified by `git log -S` on the test name against `test_roadmap.py`.

**Why it matters.** Two consequences, and the second is the one that changes a
decision.

1. **The flip is silent and in the wrong direction.** A command that selects
   nothing exits 5, so `docket verify` rejects the branch: the worst case is a
   round trip. A command that passes exits 0, so `docket verify` returns
   `ACCEPT` on a branch that did none of the work. The transition above turns
   the safe failure mode into the unsafe one, with no commit, no review and no
   advisory at the moment it happens.
2. **`PL-L9JS`'s scope does not converge.** It is written as "eight small edits
   to item files", to be made as each item is started. That is right for the
   eight, but it is a repair with no prevention behind it: every remaining
   `-k`-shaped command is a latent member of the set, converting whenever some
   future test name happens to match. `bin/docket check` counted 14 open items
   selecting nothing on 2026-09-02, down from `PL-5QKT`'s 20. So the arithmetic
   is 14 latent conversions against a repair pass that clears 9 - the set can
   be worked to zero and be non-zero again the following week, from work that
   did nothing wrong.

**Why the existing decision does not already cover this.** `PL-5QKT` left the
selects-nothing case an *advisory rather than an error*, deliberately: the exit
code cannot separate `-k` naming a test the work will add (correct, and the
shape the skill recommends) from `-k` naming a test nobody will ever write
(broken), and only the item's author can. That reasoning is sound and specific
to `-k`. It does not transfer to the already-passes case, because there is no
benign reading of it: the skill's own definition is that a `ready` item's
command fails on a tree without its work and passes with it, so exit 0 at
`status: ready` is unambiguously wrong whoever wrote it. The exit code *does*
separate the cases here, which is exactly what `PL-5QKT` said it could not do
there.

**Where.** `subprojects/docket/src/docket/checks.py` (`_check_landed`, which
already computes the fact), `docket.toml`, `subprojects/docket/tests/test_checks.py`.
`PL-L9JS` carries the repair half and should cross-reference this; `PL-5QKT`
carries the reasoning this item distinguishes itself from.

**Candidate mechanism, not yet decided.** The store already has the pattern:
`verify_required_from = 2026-08-30` grandfathers a closed set of items and
makes the rule binding for everything after it, so the rule started working
immediately without turning the store red on the day it landed. The analogue
would be a dated cutoff past which an item at `status: ready` whose command
exits 0 is an **error** rather than an advisory. The nine existing ones stay
advisory and burn down as their items are started, per `PL-L9JS`; nothing new
can enter the set, including by the silent flip above, because the run that
first sees exit 0 fails `make check` and CI.

Open design question, and the reason this is not written as settled: an item at
`in-progress` on a branch may legitimately start passing partway through its
own work, so the error must be scoped to `ready` at minimum, and possibly to
what `docket next` is about to offer - the scoping `PL-JWXF` already applied to
the sibling advisory.

**Done when.** A `verify:` command that passes on a tree without its work
cannot be newly recorded or silently acquired without something failing at the
moment it happens, and the reasoning for treating this differently from
`PL-5QKT`'s selects-nothing case is written down where the next session
reading either advisory will find it.

**Triaged 2026-09-02.** P2, `defect`/`infra`, `dev-tooling`, `S`. Worked
together with `PL-L9JS` (repair the nine open items whose `verify:` command
already passes) as one session, after the v0.4.0 gate rather than interrupting
it - the project owner's call on 2026-09-02. `PL-L9JS` is the repair half and
this is the preventive half; neither is in the frozen gate list, so both are
debt for the gate after it.

**Sequencing note for the implementing session, deliberately not decided here.**
Doing `PL-L9JS` *first* may remove this item's need for a dated cutoff
altogether. The cutoff exists only to grandfather the nine items that pass
today; repair them first and the store is already clean, so the rule can be a
plain error with no `verify_must_fail_from` setting, no grandfather set, and no
second dated policy sitting beside `verify_required_from` for a reader to
distinguish. That is the cheaper mechanism if the ordering holds. It does not
survive the two items being split across sessions, or a tenth conversion
arriving in between - which is the failure this item exists to describe - so
confirm the advisory names zero items before choosing it, and fall back to the
cutoff if it does not.

**Why the `verify:` command is the paired shape and not `bin/docket check`.**
The natural proof - that `docket check` errors on an item whose command passes
- cannot be written as a `verify:` command, because `docket check` runs every
open item's `verify:` command and would recurse without bound (`PL-20CQ`).
`PL-L9JS` records the same constraint in its `not-delegable:`. This item escapes
it because its work is code plus a test, so a pytest run proves it without
re-entering the checker. The command was run before being written down, per
the `docket` skill: the pytest half exits 0 (85 tests, 0.19s) and the `grep`
half exits 1 for the test the work has yet to add, so the pair exits 1 - an
ordinary failure, not the 5 an empty `-k` selection returns.

**Closed 2026-09-02. The cheaper mechanism held.** The sequencing note above
left the choice to the implementing session: repair first and the rule needs
no dated cutoff. `PL-L9JS` was done first in the same session, `bin/docket
check` then named zero items, and the rule went in as a plain error - no
`verify_must_fail_from`, no grandfathered set, and no second dated policy
beside `verify_required_from` for a reader to tell apart.

**What landed.** `_check_landed` in `subprojects/docket/src/docket/checks.py`
appends to `report.errors` rather than `report.advisories`, and its message
names both readings and both repairs: close the item if the work landed, or
rewrite a command that does not discriminate. It also names the consequence
that makes it an error rather than advice - `docket verify` returning ACCEPT on
a branch that did none of the work.

**Left as an advisory beside it, deliberately.** `_check_selects_nothing` is
unchanged. A selector matching no test is the *recommended* shape for an item
whose work has yet to write the test, so the finding cannot say which repair it
wants and only the item's author can. That distinction is now the difference
between the two sections rather than a paragraph asking a reader to hold both.

**The transient case, and why it does not need handling.** A session that runs
`make check` after landing work and before setting `status: done` will see this
error. That window closes in the commit the close-out procedure already
requires - status and work travel together - and when it fires the named repair
is the one that was about to happen anyway.

**This item's own `verify:` was retargeted on closing.** It named
`test_a_ready_item_whose_command_passes_is_an_error_after_the_cutoff`, a test
belonging to the cutoff design this item explicitly left open and which the
ordering made unnecessary. It now names
`test_an_item_whose_work_has_landed_is_an_error`, which the chosen design
produced. Recorded rather than quietly swapped, because a `verify:` rewritten
to match what was built is the exact shape `PL-L9JS` exists to catch - the
difference here is that the command was run and seen to fail before the work
and to pass after it.

