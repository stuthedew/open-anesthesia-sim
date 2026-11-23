---
id: PL-RXR8
title: In a Workspace pinned to one run, the Branch View offers Branch here with nothing saying the comparison will not be drawn there, so a learner finds out only after the one comparison slot is filled
priority: P3
effort: S
status: done
classes: ux
feature: interface-design-review
milestone: v0.6.22
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/qt_widgets.py, docs/INTERFACE.md, tests/integration/test_workspace_tabs.py, tests/unit/test_dashboard_frame.py
added: 2026-11-22
closed: 2026-11-22
pr: 2259
payoff: a learner in a pinned Workspace learns before branching that the comparison will not be drawn there
tests: tests/integration/test_workspace_tabs.py::test_a_pinned_workspace_says_before_a_branch_that_it_will_not_draw_it, tests/integration/test_workspace_tabs.py::test_a_workspace_pinned_to_a_run_that_is_not_open_says_so_before_a_branch, tests/unit/test_dashboard_frame.py::test_fork_offer_names_the_pin_only_beside_a_branch_that_can_be_taken
---

**Problem.** `PL-YQ5J` made the Branch View say, after the press, that a
pinned Workspace does not draw the comparison and how to unpin it. Before the
press, the same Workspace offers "Branch here" and the run selector with no
hint that the result will not be drawn there. A branch cannot be undone short
of starting the case over: the branch's Reset returns it only to its fork
point, and the trunk's Reset restarts the case. So a learner in a pinned
Workspace learns where the branch went only after it has filled the one
comparison slot.

**Where it came from.** Pass 1 of the blind review of pull request #2239, on
2026-11-22, marked it optional. It is a design addition beyond `PL-YQ5J`'s
fix, so it is filed rather than built there.

**Why it matters.** A learner who branches in a pinned Workspace spends the
case's one comparison slot and sees nothing change on the chart. Getting the
comparison back on screen then needs an unpin, and getting the slot back needs
the trunk's Reset, which starts the case over.

**What to do.** Show a short conditional line beside "Branch here" while the
Workspace is pinned, saying the comparison will open in an unpinned Workspace.
Read the pin the same way `SimulationView._compared_runs` does, so the two
sentences cannot disagree. `.claude/rules/expert-review.md` prefers an
interface that prevents an error to one that reports it.

**Generator check.** One instance. The cause is that `PL-YQ5J` fixed the
report after the press and not the offer before it.

**Done when.** A test pins a Workspace, opens its Branch View before any
branch, and finds the line; and finds it gone once the Workspace is unpinned.

**Built, 2026-11-22.** While one run is open and a branch is offered, the
Branch View says above its control: "This Workspace is pinned to Run 1, so it
will not draw a branch taken here beside it. Unpin it from the Workspace's tab
to compare the two runs here." Both buttons stay offered, and the sentence is
a muted caption like the lock's, not a warning. `SimulationView._pinned_to`
reads the pin once for both this sentence and the caption after a branch.
Research read on 2026-11-22: Vermeulen, Luyten, van den Hoven and Coninx,
"Crossing the Bridge over Norman's Gulf of Execution: Revealing Feedforward's
True Identity", CHI 2013 (doi:10.1145/2470654.2466255), read in full text to
about 70%: "Feedforward occurs before the user's action and tells users what
the result of their action will be." Nielsen Norman Group, "Preventing User
Errors: Avoiding Conscious Mistakes"
(https://www.nngroup.com/articles/user-mistakes/): "Wherever possible, offer a
preview state that users can examine to make sure that they will get what
they want", and a warning against confirmation dialogs that "interrupt users'
workflow". So the press is not blocked or confirmed, and the consequence is
stated beside the control. The wording is a placeholder.

**Docs swept:** `docs/INTERFACE.md` § "Naming the run in a comparison"
(the pinned-Workspace paragraphs), `docs/MODEL.md` (no mention of pins).

**Regression test run before the fix.** With `src/` stashed,
`uv run pytest -q "tests/integration/test_workspace_tabs.py::test_a_case_view_s_header_never_names_the_open_run_a_workspace_is_pinned_to"`
failed: the pinned Workspace's Branch View read the same words as the
unpinned one, with no sentence naming the pin. The two new tests need the
panel's new caption, so this changed test is the variant run before the fix.
