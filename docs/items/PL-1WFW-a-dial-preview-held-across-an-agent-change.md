---
id: PL-1WFW
title: A dial preview held across an agent change still reads the earlier agent in its delivered line, and one held across a Reset that drops the branch still reads Run 1 preview, on main as on the PL-RF2S branch
status: untriaged
feature: every-view-in-run-state-tests
added: 2026-11-11
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
