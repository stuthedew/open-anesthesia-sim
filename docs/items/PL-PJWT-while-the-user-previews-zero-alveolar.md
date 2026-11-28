---
id: PL-PJWT
title: While the user previews zero alveolar ventilation, the F_A/F_I plot's preview region is empty and nothing says why
priority: P3
effort: S
status: ready
classes: defect
feature: interface-design-review
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/wash_in.py
deferred-from: v0.7.0 - new: PL-49D5's rule for zero ventilation, merged 2026-11-27, left the preview empty; not safety or science, and no user sees a wrong value from it, since the plot draws no ratio rather than a wrong one (triage 2026-11-28)
added: 2026-11-27
filed-pr: 2329
payoff: a user previewing zero ventilation is told why the F_A/F_I plot draws no preview, rather than seeing an empty region that looks like a drawing that failed
---

**Problem.** While the user holds the alveolar ventilation slider at zero, the preview of the F_A/F_I plot draws nothing past the run's reach. Rule 3 of `src/anesthesia_sim/app/wash_in.py` (`PL-49D5`) leaves every predicted state without a ratio, because a step at zero ventilation reached it. The compartment chart still draws its preview, so the two plots show the same future, but the F_A/F_I plot's preview region is blank and its caption speaks only of the run's own state. A user cannot tell a blank preview from a preview that failed to draw.

**Why it matters.** While a user drags the slider to judge what a setting would do, an empty preview region with no word of explanation looks like a drawing that failed, or like a ratio of zero. `docs/INTERFACE.md` § "A preview of an unapplied setting" lists the four cues that mark a preview as a prediction (position, label, width and timing), and none of them says why a preview draws nothing. The compartment chart draws its preview at the same time, so the user sees one plot predict and the other stay blank.

**Found by** the domain review pass of `PL-49D5`'s close-out on 2026-11-27 (`s2_preview_coarse.py`, second block), as an optional finding. `PL-49D5` draws the one-point stretch at the reach as a dot, which shows where the run stands, and leaves the empty region.

**What to decide.** Whether the preview region of the F_A/F_I plot should say, while a zero-ventilation setting is previewed, that the ratio is not a wash-in fraction at zero ventilation, and where that text goes. `docs/INTERFACE.md` § "A preview of an unapplied setting" names the four cues a preview carries.

**Reproduced 2026-11-28, from the code.** `src/anesthesia_sim/app/wash_in.py` returns `WashInReading(WashInDomain.VENTILATION_STOPPED, None)` for a state reached by a step at zero alveolar ventilation (rule 3), so a preview at zero ventilation has no ratio to draw. The caption beside the plot, `wash_in_state_lines` in `src/anesthesia_sim/app/dashboard_frame.py`, is written from the run's own state.

**Done when.** A test that previews zero alveolar ventilation finds text, inside the preview region or in the caption beside the F_A/F_I plot, saying that the plot draws no ratio for the previewed stretch because the ratio is not a wash-in fraction while ventilation is zero. Where the text goes and how it reads are decided from a cited source by the session that builds it, and recorded here.

**Generator check.** A one-off. `PL-49D5`'s rule 3 withholds the ratio, and its caption explains that for the run's own stretch. The preview, drawn from the same rule, was left without an explanation of its own. No head's `misread:` names what a preview must say when it draws nothing.
