---
id: PL-QBQX
title: A run that halts on a mark still shows the status word "Paused", the same word as the learner's own Pause, and the only sign that a mark stopped it, the "Branch here: …, stopped on your mark" label, is withdrawn while two runs are compared, so a halt during a comparison, or a second halt on a MAC target whose row already reads "reached", looks like a pause nobody made
priority: P2
effort: M
status: done
classes: ux, defect
feature: replay-findings
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/controller.py, docs/MODEL.md, tests/unit/test_dashboard_frame.py, tests/integration/test_simulation_view.py
added: 2026-10-25
closed: 2026-10-31
pr: 1895
payoff: a learner comparing two runs can tell that a mark stopped one, instead of seeing a pause nobody made
verify: grep -q 'def test_a_halt_on_a_mark_is_told_apart_from_a_pause_during_a_comparison' tests/integration/test_simulation_view.py
---

**Problem.** `status_word` returns "Paused" for any stopped run that has not failed or reached the run-length limit (`src/anesthesia_sim/app/dashboard_frame.py`). It does not read `SimulationSnapshot.bookmark_halt`. Since `PL-TYWQ`, the trunk's fork button reads "Branch here: …, stopped on your mark" after a halt (`dashboard_frame.py`). That is now the only cue. `fork_offer` withdraws the button while two runs are shown (`dashboard_frame.py`), and nothing replaces it. A MAC target halts on every crossing. On the second crossing its row already reads "reached", so the row does not change either.

**Why it matters.** During a comparison, a run that stops on a mark looks exactly like a run the learner paused. The learner cannot tell that a mark stopped it, which is the hidden mode `docs/MODEL.md` § "Halting on a marked crossing" says the every-crossing rule avoids. The fork label's wording and its choice not to name the mark are the owner's ratified decision (2026-09-21). So a fix that names the mark, or that changes the status word, is put to the owner first. Showing the existing cue during a comparison may not need that.

**Done when.** A run halted on a mark is told apart from one the learner paused while two runs are compared, as it is with one run shown. Any change to the status word or a label that names the mark is put to the owner first. `tests/integration/test_simulation_view.py` has `test_a_halt_on_a_mark_is_told_apart_from_a_pause_during_a_comparison`.

**Found by.** `PL-TBQS` reviewer replay on #775, findings 775 r01 F2, r02 F4, r03 F3, r05 F2 and r06 F3, and the second `PL-ZWXD` addendum entry, checked against main on 2026-10-25 by reading the code. The halt-not-drawn half of these reports was fixed by `PL-T995`.

**Decided, 2026-10-31 (session decision; the words are a placeholder).** The status word carries the cue. A paused run whose snapshot holds a `bookmark_halt` reads "Paused — stopped on your mark" (`STATUS_MARK_HALT_TEXT`). It starts with "Paused" because the run is paused and Start resumes it. It reuses the fork label's ratified "stopped on your mark", which names no mark and no instant, so the ratified fork label is unchanged. The brief asked for a change to the status word to be put to the owner first. The project owner's later rule of 2026-10-18 makes look, wording and placement placeholders for a session to decide while the interface is built (`PL-KBBJ`). So this was decided here rather than put to the owner. A failure and the supported run length still outrank the word. `RunView.present_halt` passes `stopped_on_mark=False`, because every halt it shows has failed the run or stopped it at the supported run length. A branch at its fork carries the halt record of the parent's step that reached the fork (`PL-3K9B`), but no step of its own stopped it. Both blind review passes found that the first version showed the word on such a branch. So the word reads `SimulationSnapshot.stopped_on_mark`, which is true only when the run has a halt record and stands past `began_at_s`. `test_a_branch_opened_on_a_mark_crossing_is_not_said_to_be_stopped_by_it` pins it. `docs/MODEL.md` gains a hazard-table row and a sentence in § "Halting on a marked crossing".
