---
id: PL-RLRG
title: docs/MODEL.md's paragraphs for a clinician carry item ids and decision records such as '(project owner, 2026-09-04, ratified', and nothing refuses them: tools/model_rewrite.py ids lists them and no check or close-out step runs it
priority: P2
effort: M
status: ready
classes: defect, docs
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/MODEL.md, .claude/skills/docket/modes/close-out.md
deferred-from: v0.7.0 - present at the freeze and not on the frozen list; found by the 2026-11-10 audit; it changes how the specification reads and no value in it
added: 2026-11-10
payoff: a clinician reading docs/MODEL.md meets no record of who decided what and when, and a session that adds one fails the build
verify: grep -q 'def test_a_decision_record_in_a_paragraph_for_a_clinician_is_refused' tests/unit/test_doc_check.py
---

**Problem.** docs/MODEL.md's paragraphs for a clinician carry item ids and decision records such as '(project owner, 2026-09-04, ratified', and nothing refuses them: tools/model_rewrite.py ids lists them and no check or close-out step runs it

**Checked 2026-11-10:** `grep -c 'project owner, 20' docs/MODEL.md` prints 20, and one of the matches is "(project owner, 2026-09-04, ratified". `tools/model_rewrite.py` has an `ids` command that lists the item ids a section cites. `grep -rn 'model_rewrite.py ids'` over `Makefile`, `.github`, `.claude` and `tools/` finds no caller.

**Why it matters.** `.claude/rules/plain-writing.md` names the first reader of `docs/MODEL.md` as a clinician who does not know this repository's own names, and says "Decision history goes in the item". A decision record in a clinician's paragraph is text for a later session. `PL-J1ZM` (prose over-explains) has been answered three times with more rule text, and `PL-ZYHX` measured that writing rules with a check had no violations while rules without one recurred.

**The pause on new workflow mechanisms.** The project owner lifted it for this item on 2026-11-10.

**Done when.** `make check` refuses a decision record, the text "(project owner, " followed by a date, in a `docs/MODEL.md` paragraph outside a note that opens "**For developers.**". It starts from a baseline of the 20 present today, and the baseline may only shrink. The count of item ids per section, which `tools/model_rewrite.py ids` already prints, is shown at close-out as an advisory, because the rule allows an id as a pointer. Read `PL-P3GZ` first (decide whether to split `docs/MODEL.md` by reader, on pull request #2088): a split changes which file the check reads, not the rule.

**Generator check.** An instance of `PL-J1ZM`'s fact (what a reader can do without), found while that head is open. The audit's reviewer reported that the head's members also show the opposite defect, private compressed wording (`PL-VGDX`, `PL-2K0K`); `PL-VZ57` carries that lead.
