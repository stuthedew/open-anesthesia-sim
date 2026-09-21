---
id: PL-QRD1
title: A dashboard showing two runs lets either selector switch its own agent, which the shared MAC axis then refuses only after the controller has switched: lock the selectors while two runs are shown, with PL-8PSW
priority: P3
effort: S
status: done
classes: defect, ux
feature: scenario-branching
milestone: v0.5.0
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, ROADMAP.md, tests/integration/test_simulation_view.py, tests/unit/test_dashboard_frame.py
blocked-by: PL-8PSW, PL-VKJW
added: 2026-09-15
closed: 2026-09-20
pr: 784
payoff: no control on a compared dashboard can destroy the case the comparison is of - the agent switch that halted both runs is refused before it reaches the controller
verify: grep -q 'def test_the_trunks_selector_is_locked_while_two_runs_are_shown' tests/integration/test_simulation_view.py
---

**Problem.** A dashboard showing two runs lets either selector switch its own agent, which the shared MAC axis then refuses only after the controller has switched: lock the selectors while two runs are shown, with PL-8PSW

**Found by the Qt-correctness review of `PL-25KS`, 2026-09-15.** `RunView`
keeps its own agent selector, and `SimulationView` admits two runs. Switching
one run's agent goes through `SimulationController.set_agent`, which succeeds
on a trunk, and the refusal comes a moment later from `assemble_chart_frame`
(two agents cannot share one MAC axis) - after the controller has already
switched. `_halt_every_run` then fails both runs. The port made the halt
itself visible (`present_halt` writes each run's status word and banner with
no frame), but the switch should be refused before it reaches the controller:
while two runs are shown the selectors are locked, in the same disabled-and-
hidden form the running-agent chip uses, because a comparison is of one
agent by construction. Only reachable today by constructing a two-trunk
dashboard, which no shipped entry point does; `PL-8PSW` (overlay two branches)
is where two runs first reach a reader, and a branch's `set_agent` already
refuses, so this is that item's to settle - lock, or rely on the branch
refusal and say so.

**Why it matters.** The failure is ordered the wrong way round: the controller
switches first and the refusal arrives afterwards from `assemble_chart_frame`,
so `_halt_every_run` then fails *both* runs over an input to one of them.
`CLAUDE.md`'s expert-review standard asks for interfaces that prevent an error
rather than report it after the fact, and a selector that accepts a choice the
next layer cannot honour is the case that rule names. The port already made the
consequence legible - `present_halt` writes each run's status word and banner
with no frame - which is the right handling of a halt and not a substitute for
not halting.

**Triaged 2026-09-15 as blocked on `PL-8PSW`** rather than ready, per its own
brief: no shipped entry point constructs a two-trunk dashboard, so the defect is
unreachable today, and `PL-8PSW` (overlay two branches) is where two runs first
reach a reader. A branch's `set_agent` already refuses, so whether this needs a
selector lock at all is decided by the shape `PL-8PSW` lands - lock the
selectors while two runs are shown, or rely on the branch refusal and say so
there. Working it before then would design against an interface that does not
exist yet.

## Groomed 2026-09-20 under `PL-JFQ3`: the premise that `PL-8PSW` would settle it was wrong

**What the brief expected.** That `PL-8PSW` (overlay two branches on one time
axis) "is where two runs first reach a reader", so it would settle whether this
needs a selector lock at all — "lock, or rely on the branch refusal and say
so".

**What `PL-8PSW` actually landed.** The drawing, not the route.
`src/anesthesia_sim/app/main.py` constructs `SimulationView((controller,))`
with one controller and mentions no branch, and `dashboard_frame.transport`
still computes `selector_locked=snapshot.is_running` — locked while *running*,
which is the discards-the-case rule, and not while two runs are shown. So
neither disposition was taken: the selectors are not locked on a two-run
dashboard, and nothing says the branch refusal is being relied on instead.

**The defect is therefore still exactly as unreachable as the triage said**,
and for the reason the triage gave: no shipped entry point constructs a
two-trunk dashboard. What was wrong was only *which item* makes one reachable.

**The real blocker, now declared.** `PL-XJ37` (nothing in v0.5.0's scope lets a
learner take a fork or select between runs, and `SimulationView`'s run set is
fixed at construction), `needs-decision`, written into `blocked-by` beside
`PL-8PSW`. The question the brief poses is unchanged and is `PL-XJ37`'s to
settle for the same reason it was `PL-8PSW`'s: working it before then designs
against an interface that does not exist yet.

## Re-pointed 2026-09-20 under `PL-XJ37`: the blocker is `PL-VKJW`, and half the question is answered

`PL-XJ37` was a decision item and the project owner answered it on 2026-09-20:
forking is what v0.5.0 is, and the run selector is deferred. The
implementation that answer names is `PL-VKJW` (a learner takes a fork from the
dashboard), which is what `blocked-by` now carries in `PL-XJ37`'s place -
`PL-8PSW` is kept beside it for the same reason the last pass kept it, that the
sequence is the record.

**The branch half is answered, and neither of the two dispositions this brief
offered is what was chosen.** The triage left "lock the selectors while two
runs are shown, or rely on the branch refusal and say so". The answer is
neither: **a branch's `RunView` shows the running-agent chip in place of the
agent dropdown**, in the same `setDisabled(locked)`-beside-`setHidden(locked)`
form `RunView._write_transport` already writes, with
`dashboard_frame.transport` gaining a branch test beside
`selector_locked=snapshot.is_running`. A control that always refuses is not
locked and not relied on - it is not shown. `PL-VKJW`'s brief carries it.

**The trunk half is what is left, and it is this item's title.** `set_agent`
refuses a branch and *succeeds* on a trunk, so the disposition above removes
the control that cannot work and leaves the one that works destructively:
with a branch displayed and the trunk paused, the trunk's dropdown is live,
`RunView._confirm_new_case` asks about the control changes it would discard
and says nothing about the branch, and after the switch
`assemble_chart_frame` refuses the frame over the shared MAC axis and
`_halt_every_run` fails both runs. That is the ordering this item was filed
about, reached through a trunk and a branch rather than through two trunks.

**It also stops being unreachable the moment `PL-VKJW` lands**, which is the
change since the 2026-09-15 triage: no shipped entry point built a two-run
dashboard then, and `PL-VKJW` is the entry point. So this is not deferrable
past it. `PL-VKJW`'s brief puts the choice - lock the trunk's selector too, or
keep it live and grow the confirmation dialog a clause about the branches it
orphans - to the project owner, and recommends locking. Under that answer this
item closes against `PL-VKJW`; under the other it stays open and wants a place
in v0.5.0's scope.

**The two-*trunk* case in the title is untouched either way.** `PL-VKJW` builds
a trunk-and-branch dashboard only, so a dashboard of two trunks stays
unreachable and stays the stronger statement of the guard.

## Closed 2026-09-20 under `PL-VKJW`: **prevent** was taken, over **warn**

**Both halves are answered, and the second is the one this item's title is
about.** `PL-VKJW` made the defect reachable for the first time - it is the
entry point that builds a two-run dashboard - so this closed against it rather
than after it, which is the disposition its brief named under the answer taken.

- **The branch half**, as `PL-VKJW`'s brief settled it: a branch's `RunView`
  shows the agent chip in place of the selector, `setDisabled(locked)` beside
  `setHidden(locked)`, because `set_agent` refuses a branch outright and a
  control that refuses every input it accepts is one presenting itself as
  working.
- **The trunk half**, which is this item: the trunk's selector is locked while
  two runs are shown, and Reset is the way back to one run (project owner,
  2026-09-20, ratified, over keeping the selector live and growing
  `RunView._confirm_new_case`'s dialog a clause about the branches it would
  orphan). On `CLAUDE.md`'s expert-review standard - an interface that
  prevents the error over one that reports it afterwards - and because it adds
  no mode: the same gesture already refuses a second fork, so the rule on
  screen is simply that nothing about the case may be changed while a
  comparison is shown.

  **Ratified rather than specified**, which is the bar to reopen it. The case
  put to the owner was a session's own recommendation wearing their signature,
  so ordinary evidence puts it back to them: a learner who wants to change
  agent mid-comparison, a measurement, or a cost the case did not carry. "It
  is what the owner decided" does not defend it.

**`dashboard_frame.transport` carries all three locks rather than the widget
choosing between them**, and names the longest-lasting one that holds: a
branch's never returns, a comparison's returns on Reset, a running run's
returns on Pause. A chip naming the shortest lock that happened to hold would
send a reader to Pause for something Pause cannot lift.

**The two-*trunk* case in the title is untouched**, as the last pass said it
would be: `PL-VKJW` builds a trunk-and-branch dashboard only, and `comparing`
is read from the run count rather than from either run's kind, so a dashboard
of two trunks is covered by the same lock without anything having been written
for it.

**Reversing it is small and local**, which is why it was implemented rather
than asked about: `dashboard_frame.transport`'s `comparing` branch and the one
line in `SimulationView._rename_runs` that writes it are the whole of it.
