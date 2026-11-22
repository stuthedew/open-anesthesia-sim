---
id: PL-1WFW
title: A dial preview held across an agent change still reads the earlier agent in its delivered line, and one held across a Reset that drops the branch still reads Run 1 preview, on main as on the PL-RF2S branch
priority: P1
effort: S
status: done
classes: defect, safety
feature: every-view-in-run-state-tests
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/simulation_view
added: 2026-11-11
closed: 2026-11-22
pr: 2214
payoff: A preview never names an agent or a run that is no longer on screen, so a learner cannot read a dotted trajectory as belonging to the wrong agent.
tests: tests/integration/simulation_view/test_simulation_view_views.py::test_a_preview_held_across_an_agent_change_ends_rather_than_name_the_earlier_agent, tests/integration/simulation_view/test_simulation_view_views.py::test_a_preview_held_while_a_branch_is_opened_ends_rather_than_go_unnamed
---

**Problem.** A dial preview held across an agent change still reads the earlier agent in its delivered line, and one held across a Reset that drops the branch still reads Run 1 preview, on main as on the PL-RF2S branch

**Found on 2026-11-11 by a review of `PL-RF2S`'s second pull request, and not
fixed there.** The reviewer drove the interface through random sequences of
actions and compared the screen with the runs the dashboard held. Two
sequences left a preview that named the wrong thing, and both behaved the same
on `main` at `35294da61` and on the branch at `70dbdc525`:

1. A dial thumb is held, so the delivered line shows a preview. The agent is
   then changed from sevoflurane to desflurane while the thumb is still held.
   The line still reads "Delivered sevoflurane 3.00%".
2. A dial thumb is held on the trunk while a branch is open. The trunk's Reset
   then drops the branch. The preview still reads "Run 1 preview", though the
   dashboard holds one run and names none.

Both need an action taken while a thumb is held, which a pointer cannot do
alone. A keyboard shortcut or a second input device can. The reviewer's script
was `repro4_previews.py`, cases C and D, in that session's scratchpad, which
does not outlive the session.

**Where it may belong.** `PL-RF2S`'s third pull request makes a run's name
travel with its values. A preview's line is built from the run's name and
agent at the moment the thumb is pressed, so it is the same fault: a value
shown without the state it was built from.

**Checked 2026-11-22**, at `d4e8200c`. The code that builds the label is unchanged in kind. `RunView.request_preview` in `app/run_view.py` builds the preview's label once, from `self.controller.settings().agent_display_name` and `self._run_name` at that moment, and stores it in `self._preview`. `self._preview` is written only there and in `end_preview`, so neither an agent change nor `set_run_name` rebuilds it while the thumb stays still. The preview did not exist at the freeze; it came in with `PL-5B1N` (the preview a held control draws).

**Why it matters.** The preview's label is the words that say what the dotted trajectory would be. After an agent change it names an agent that is no longer running, such as "Delivered sevoflurane 3.00%" on a desflurane run. After a Reset that drops the branch it names "Run 1", though the screen holds one run and names none. A learner reading the label is told the wrong agent or the wrong run for the curve beside it. Reaching it needs an action taken while the thumb is held, such as a key press or a second input device.

**Done when.** While a dial's thumb is held, a change of agent or a Reset that changes the run set leaves the preview's label naming the agent and run that are shown, or ends the preview. A test drives both sequences and reads the label.

**Generator check.** An instance of the fact that `PL-RF2S` states, "Which widgets state a run's current state, and that each is restated on every path that changes it": the label is a value shown without the state it was built from. `PL-RF2S` is still open, so this is a member of that head rather than a re-entry.

**Done 2026-11-22.** A preview held across a start-over, a branch opening or an agent change now ends, by clearing the held preview in `_announce_the_start_over` and in `set_run_name` when the name changes, so the preview label never names a run or agent that is no longer drawn. Docs checked: `docs/INTERFACE.md` § "A preview of an unapplied setting" (updated), `docs/ARCHITECTURE.md` (its preview passages say how a preview is computed, not when it ends, so unchanged) and `README.md` (no mention of a preview, by `grep -n -i "preview"`).
