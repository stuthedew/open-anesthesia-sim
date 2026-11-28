---
id: PL-PJWT
title: While the user previews zero alveolar ventilation, the F_A/F_I plot's preview region is empty and nothing says why
priority: P3
effort: S
status: done
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/views.py
deferred-from: v0.7.0 - new: PL-49D5's rule for zero ventilation, merged 2026-11-27, left the preview empty; not safety or science, and no user sees a wrong value from it, since the plot draws no ratio rather than a wrong one (triage 2026-11-28)
added: 2026-11-27
closed: 2026-11-28
pr: 2365
filed-pr: 2329
payoff: a user previewing zero ventilation is told why the F_A/F_I plot draws no preview, rather than seeing an empty region that looks like a drawing that failed
tests: tests/unit/test_chart_frame.py::test_the_f_a_f_i_plot_says_why_it_draws_no_ratio_for_a_preview_at_zero_ventilation, tests/unit/test_chart_frame.py::test_the_line_on_an_empty_f_a_f_i_preview_is_on_the_compared_run_that_draws_it, tests/integration/simulation_view/test_simulation_view_views.py::test_a_held_thumb_at_zero_ventilation_says_above_the_f_a_f_i_plot_why_it_draws_no_ratio
---

**Problem.** While the user holds the alveolar ventilation slider at zero, the preview of the F_A/F_I plot draws nothing past the run's reach. Rule 3 of `src/anesthesia_sim/app/wash_in.py` (`PL-49D5`) leaves every predicted state without a ratio, because a step at zero ventilation reached it. The compartment chart still draws its preview, so the two plots show the same future, but the F_A/F_I plot's preview region is blank and its caption speaks only of the run's own state. A user cannot tell a blank preview from a preview that failed to draw.

**Why it matters.** While a user drags the slider to judge what a setting would do, an empty preview region with no word of explanation looks like a drawing that failed, or like a ratio of zero. `docs/INTERFACE.md` § "A preview of an unapplied setting" lists the four cues that mark a preview as a prediction (position, label, width and timing), and none of them says why a preview draws nothing. The compartment chart draws its preview at the same time, so the user sees one plot predict and the other stay blank.

**Found by** the domain review pass of `PL-49D5`'s close-out on 2026-11-27 (`s2_preview_coarse.py`, second block), as an optional finding. `PL-49D5` draws the one-point stretch at the reach as a dot, which shows where the run stands, and leaves the empty region.

**What to decide.** Whether the preview region of the F_A/F_I plot should say, while a zero-ventilation setting is previewed, that the ratio is not a wash-in fraction at zero ventilation, and where that text goes. `docs/INTERFACE.md` § "A preview of an unapplied setting" names the four cues a preview carries.

**Reproduced 2026-11-28, from the code.** `src/anesthesia_sim/app/wash_in.py` returns `WashInReading(WashInDomain.VENTILATION_STOPPED, None)` for a state reached by a step at zero alveolar ventilation (rule 3), so a preview at zero ventilation has no ratio to draw. The caption beside the plot, `wash_in_state_lines` in `src/anesthesia_sim/app/dashboard_frame.py`, is written from the run's own state.

**Done when.** A test that previews zero alveolar ventilation finds text, inside the preview region or in the caption beside the F_A/F_I plot, saying that the plot draws no ratio for the previewed stretch because the ratio is not a wash-in fraction while ventilation is zero. Where the text goes and how it reads are decided from a cited source by the session that builds it, and recorded here.

**Generator check.** A one-off. `PL-49D5`'s rule 3 withholds the ratio, and its caption explains that for the run's own stretch. The preview, drawn from the same rule, was left without an explanation of its own. No head's `misread:` names what a preview must say when it draws nothing.

**Fixed 2026-11-28.** While the user holds a slider and the F_A/F_I plot's preview region is empty because alveolar ventilation would be zero, a line in the rows above the plot reads "Preview: alveolar ventilation would be zero, so the predicted ratio would not be a wash-in fraction." `RunPreview.ventilation_stopped` in `app/chart_frame.py` decides when. `_ventilation_empties_the_preview` reads each predicted state after the reach by the three rules of `app/wash_in.py`, in their order (`read_wash_in_with_ventilation`), and the flag is true when no predicted state has a ratio and at least one has none by rule 3 alone. `wash_in_preview_lines` in `app/dashboard_frame.py` writes one entry per run, named by `compared_run_line` while runs are compared, and `WashInView.preview_notes` in `app/views.py` shows them under the plot's state lines. The preview's label inside the plot is unchanged, and so is each plot's description for a screen reader, which leaves out the rows above the plot because a screen reader reads them as text. `docs/INTERFACE.md` says so in § "F_A/F_I as a displayed ratio", with a pointer from § "A preview of an unapplied setting". The new line is on the approved wording list, through a new recorded point, "zero ventilation previewed", in `tests/integration/test_interface_wording.py`.

**Where the text goes and how it reads, from a source.** Nielsen Norman Group's guidance on empty states (Kaplan, "Designing Empty States in Complex Applications: 3 Guidelines", 2021, https://www.nngroup.com/articles/empty-state-interface-design/, read in full 2026-11-28) says that "totally empty states cause confusion about how and whether the system is working", and gives as its fix "a brief system message within the content area" that says why nothing is shown. The line goes in the View's rows above the plot. Those rows already hold the plot's own state line, which says why the run's trace stops, and the concentration chart's rows already name a preview whose traces leave the axis (`PL-5B1N`). The line opens with "Preview", the word that opens the preview's label, so it is read as part of the preview. It has the construction of the state lines: the condition, then "so", then the verdict, which their comment ties to NUREG-0700 Rev. 3, guideline 2.7.1-2. It mirrors the run's own zero-ventilation line, "Alveolar ventilation was zero over the last simulated second, so the ratio is not a wash-in fraction.", in the conditional. The rows above the plot grow while the line shows, so the plot is shorter by that much during the hold. The concentration chart's off-scale preview notice does the same.

**First version, replaced after the blind review.** The first version added two lines to the preview's label inside the plot. Both review passes found that the label is opaque and hangs from the top of the axis. The plot has room for one line above the equilibrium line, so a three-line label covered the equilibrium line and a compared run's curve near equilibrium, and at the plot's least height its last line could be clipped, as the hover box was before `PL-HXSD`. That is why the line moved out of the plot.

**Blind review.** Two general passes on the first version (commit `4641202a`).

1. Pass 1, F1, and pass 2, F1 and F2 (should-fix): the three-line label covered the equilibrium line and a compared run's curve, and could clip at the least height. Fixed by moving the reason out of the plot, as above.
2. Pass 1, F2 (should-fix): no recorded point held a slider, so the sentence was never on the approved wording list, and a later rewording would pass unread. Fixed: the "zero ventilation previewed" point records the line and both plots' descriptions during the hold.
3. Pass 1, F3, and pass 2, F3 (optional): the flag tested rule 3 alone, so a preview whose inspired concentration is too low to divide by would have blamed the ventilation, while rule 1 comes first. Fixed: the flag reads each predicted state by all three rules, and the unit test's "no inspired agent" case covers it.
4. A third general pass, on the reworked version (commit `01ee9ecb`), found nothing.

**Regression check.** With `app/chart_frame.py`, `app/dashboard_frame.py` and `app/views.py` restored to their state before this item, `pytest tests/integration/test_interface_wording.py -k approved_list` fails with "zero ventilation previewed, gone: 'Preview: alveolar ventilation would be zero, so the predicted ratio would not be a wash-in fraction.'". The unit and integration tests need `wash_in_preview_lines` and `WashInView.preview_notes`, which the fix added, so the wording test is their variant on the code before. With `_ventilation_empties_the_preview` given the first version's rule, that no step after the reach is ventilated, the unit test fails on its "no inspired agent" case, which then gets the line.

**Docs checked.** `docs/INTERFACE.md`: one paragraph added in § "F_A/F_I as a displayed ratio" and one sentence in § "A preview of an unapplied setting". `docs/VERIFICATION.md`: the hazard row on reading a preview as part of the run still holds. `docs/MODEL.md`, `docs/PARAMETERS.md`, `README.md` and `docs/ARCHITECTURE.md` say nothing of the F_A/F_I preview's text.
