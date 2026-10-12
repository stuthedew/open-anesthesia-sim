---
id: PL-08SS
title: SimulationView._handle_fork and _handle_halt_fork keep the branch in the case before add_run reads its snapshot, so a fork taken on a run whose snapshot refuses raises out of the slot and leaves a branch kept but never displayed, which Reset neither drops nor rebuilds (found at PL-V2HC's review)
status: untriaged
feature: every-control-restates-the-halt
added: 2026-10-12
---

**Problem.** SimulationView._handle_fork and _handle_halt_fork keep the branch in the case before add_run reads its snapshot, so a fork taken on a run whose snapshot refuses raises out of the slot and leaves a branch kept but never displayed, which Reset neither drops nor rebuilds (found at PL-V2HC's review)

**Why it matters.** `BranchedCase.fork_at` (or `fork_at_halt`) builds the
branch from keyframes and keeps it in `BranchedCase.branches` before `add_run`
reads the branch's `snapshot()` to draw it. On a run whose snapshot refuses a
value (`PL-7DJK`), that read raises out of the slot, which the toolkit prints
and swallows: `_fork_refusal` stays None, nothing on screen answers, and the
branch is kept but never displayed. `_handle_case_restarted` returns early with
one displayed run, so Reset neither drops it nor rebuilds the case; a second
press keeps a second branch, and a fork taken after Reset leaves branches of a
run that no longer exists. Reproduced 2026-10-12 by the adversarial review of
`PL-V2HC`, with the snapshot made to refuse as
`tests/integration/test_simulation_view.py`'s `_read_the_alveolar_quotient_as`
does: one displayed run and `case.branches` at 1, then 2, then 3 after a Reset
and a further fork. No supported setting reaches a refusing snapshot
(`core/concentration.py`), so this is reachable only through a future write
that skips every checked path, as `PL-544D`'s was.

**What a fix probably wants.** Read the trunk's snapshot through the halt gate
before the case keeps anything - `RunView._snapshot_for_a_control` on the
reference run, or a view-level counterpart that halts every run - and return
when it refuses, so the halt is restated and no branch is kept; or keep the
branch only once `add_run` has drawn it. A test that makes the snapshot
refuse, presses Fork, and asserts the branch count and the displayed runs
agree.

**Done when.** A fork taken on a run whose snapshot refuses ends in the halt on
screen with `case.branches` unchanged, shown by an integration test.
