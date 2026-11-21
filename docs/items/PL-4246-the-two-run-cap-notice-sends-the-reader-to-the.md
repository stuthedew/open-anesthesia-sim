---
id: PL-4246
title: The two-run cap notice sends the reader to 'the readouts below', and the readouts are above the chart
status: untriaged
feature: interface-matches-its-spec
added: 2026-11-21
---

**Problem.** The two-run cap notice sends the reader to 'the readouts below', and the readouts are above the chart

**Checked 2026-11-21**, at `2452b9b4e`. Found by `PL-5FMC` (the check of `docs/INTERFACE.md` and the two documents beside it against the code). `COMPARED_CAP_NOTICE_TEMPLATE` in `app/dashboard_frame.py` reads "Two runs are shown, so the chart draws at most {cap} compartments at once. Every compartment's value is in the readouts below, for both runs." The readouts are above the chart. `OFF_SCALE_NOTICE_TEMPLATE` in the same module says "their values are in the readouts above". With two runs shown offscreen, the notice's top was at y = 587 in the window and the readout row ran from y = 119 to y = 295. `git grep "readouts below" -- docs src tests` finds only the constant.

**Why it matters.** The notice tells the learner where the hidden compartments' values are, and it points the wrong way.

**Done when.** The notice says where the readouts are, and a test compares the notice's direction word with the positions of the notice and the readout row.

**Built 2026-11-21.** `READOUTS_PLACE_TEXT` in `app/dashboard_frame.py` holds the phrase "the readouts above", and the two-run cap notice and the off-scale notice both take it from there. `test_the_cap_notice_sends_the_reader_to_readouts_that_are_above_it` compares the phrase's direction word with where the window draws each compartment's readout and the notice, for both runs. The off-scale notice's test makes the same comparison for the clipped compartment.

**Generator check.** One-off. The fact is where the compartment readouts are drawn relative to a notice in a chart's Area. Two notices each spelled it, and one was wrong. Both now read one constant, and a test compares it with the window. Found by `PL-5FMC`, the check of the interface documents that the project owner asked for.
