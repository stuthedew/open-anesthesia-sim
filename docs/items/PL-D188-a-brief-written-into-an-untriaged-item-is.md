---
id: PL-D188
title: A brief written into an untriaged item is appended below docket new's template rather than replacing it, so the dead stub survives to triage
priority: P2
effort: S
status: done
classes: defect, infra
feature: planning-cadence
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-05
closed: 2026-09-07
pr: 428
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -rq 'def test_a_brief_written_into_a_captured_item_leaves_no_template_above_it' subprojects/docket/tests
---

**Problem.** `docket new` writes a capture template - `**Problem.** <title>`
followed by empty `**Why it matters.**`, `**Where.**` and `**Done when.**`
headings. A session that later writes the real brief appends it *below* that
template instead of replacing it, so the item carries a dead stub above a
complete brief. `checks.py`'s `_section_text` judges the first matching
heading, deliberately - "the stub this check was written for" is its own words
- so the item reads as having nothing under two required headings however good
the brief beneath it is.

**Observed at triage on 2026-09-05.** Eighteen of the thirty-two untriaged
items carried the stub; fifteen of those had a full, careful brief immediately
under it. Repairing them was most of the pass: for eleven the stub could be cut
whole, and for four the real content had no `**Problem.**` of its own, so the
stub's restated title had to be kept and the empty headings removed around it.

**Why it matters.** It costs the triage pass rather than the capture, which is
what makes it invisible where it happens: capture is exempt from the brief
check by design, so nothing says anything until somebody is triaging thirty-two
items at once. It also produces exactly the wrong reading - `docket triage`
reports "brief has nothing under **Why it matters.**" for an item whose brief
is two pages - and a reader who learns that the line can be wrong stops reading
it.

**Where.** `subprojects/docket/src/docket/cli.py` (`cmd_new`, and the template
it writes), `subprojects/docket/README.md` and `.claude/skills/docket/SKILL.md`
for the instruction half. The decidable part is small: a body holding an empty
required heading *and* a later `**Problem.**` is a stub left above a brief, and
that is a yes/no.

**Done when.** Writing a brief into a captured item leaves no template above
it - because the template is not there to append to, because the write replaces
it, or because a check names the shape when it happens.
