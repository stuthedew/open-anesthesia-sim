---
id: PL-5867
title: Three MAC target refusals in app/bookmarks.py name a compartment by its code value, such as 'vessel_rich', and one quotes a repr; they reach the mark editor's notice verbatim through refused_setting_notice
status: untriaged
feature: replay-findings
touches: src/anesthesia_sim/app/bookmarks.py
added: 2026-11-23
filed-pr: 2291
---

**Problem.** Three MAC target refusals in app/bookmarks.py name a compartment by its code value, such as 'vessel_rich', and one quotes a repr; they reach the mark editor's notice verbatim through refused_setting_notice

**Found 2026-11-23** while closing `PL-8QFW` (the refused-setting banner named a setting by its field in the code). The mark editor shows a refused mark through `refused_setting_notice` (`SimulationView._apply_to_every_run`, `_remove_mark` and the add path), word for word. Three messages in `app/bookmarks.py` name a compartment by `RecordedQuantity.value`, which is a code value such as `vessel_rich` or `mixed_venous`: `MacTarget.__post_init__` ("given 'vessel_rich', which is not one of ..."), `BookmarkSet.without_mac_target` ("no MAC target stands at 0.8 ×MAC on the vessel_rich compartment, so there is none to remove") and `_require_readings` ("the before reading names no vessel_rich compartment"). The removal refusal is reached only when the Remove rows disagree with the run's marks, which the dashboard halts on first (`_marks_now`), so a learner should rarely or never see it.

**Why it matters.** It is the same fault as `PL-8QFW` in a second notice: a learner reads a code name where the screen labels the compartment in words.

**Done when.** Each refusal that can reach the mark editor names the compartment as the chart's legend names it, read from the one place that label is held, and a test pins the notice the editor shows. The approved-wording list records any changed string.
