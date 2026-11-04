---
id: PL-ZTZF
title: A docs/MODEL.md rewrite that changes no value, equation, code span or citation still waits on the owner's read, because the read rule calls any change to what MODEL.md says high-risk and PL-ZT47's section parts each wait on the owner
priority: P2
effort: S
status: done
classes: infra, docs
feature: review-hold
milestone: v0.6.15
touches: tools/model_rewrite.py, tests/unit/test_model_rewrite.py, subprojects/docket/src/docket/arming.py, .claude/skills/pull-request/SKILL.md, docs/maintainer.md, .claude/skills/docket/modes/coordinator.md, docs/apparatus.md, docs/items/PL-9331-make-docs-model-md-assumptions-known.md, docs/items/PL-J37P-make-docs-model-md-displayed-precision-readable.md, docs/items/PL-PS5H-make-docs-model-md-minimum-displayed-outputs-up.md, docs/items/PL-QHR2-make-docs-model-md-supported-input-ranges-and.md, docs/items/PL-QL0X-make-docs-model-md-runtime-controls-up-to.md, docs/items/PL-WBR3-make-docs-model-md-s-published-wash-in-and.md, docs/items/PL-XBJ3-make-docs-model-md-the-chart-s-hover-readout.md, docs/items/PL-XT53-make-docs-model-md-the-control-input-timeline.md, docs/items/PL-YVL0-make-docs-model-md-reset-behavior-through.md, docs/items/PL-ZT47-docs-model-md-still-reads-as-machine-written.md
added: 2026-11-02
closed: 2026-11-02
pr: 1951
payoff: a docs/MODEL.md rewrite whose values, equations, code spans and citations are unchanged merges on green, and the owner reads only the sentences whose meaning needs a clinician
verify: grep -q 'def test_lost_lists_a_fact_the_rewrite_added' tests/unit/test_model_rewrite.py && grep -qF 'tools/model_rewrite.py lost' .claude/skills/pull-request/SKILL.md && grep -qF 'A docs/MODEL.md rewrite is not needed when' subprojects/docket/src/docket/arming.py
---

**Problem.** A rewrite of `docs/MODEL.md` that keeps every value, equation,
code span and citation still waits on the owner's read. `bin/docket arm` holds
any change to `docs/MODEL.md` until a session records `Owner-read: needed` or
`not needed`. The text `arm` prints for that judgment (`JUDGE_ASK` in
`subprojects/docket/src/docket/arming.py`) calls a change to "what
docs/MODEL.md says one means" high-risk, so sessions record `needed` for a
plain-English rewrite. `PL-ZT47`'s procedure step 6 also says each section
part waits on the owner's read, and its thirteen section-part briefs end with
"the project owner has read the rewrite". Four of those parts had pull requests
open on 2026-11-02 (`#1945`, `#1947`, `#1949`, `#1950`).

**The owner's decision** (project owner, 2026-11-02, ratified, over the
current rule that every section part waits on the owner's read). The
coordinator proposed that a `docs/MODEL.md` rewrite merge on green when every
check passes and no value, equation or code span changed, and that only an ask
needing a clinician's or the owner's judgment, such as what a hazard row
promises, go to the owner. The owner answered "yes" at 19:40Z.

**Why it matters.** Each held section part costs the owner a read of prose
whose facts a tool has already shown unchanged, and fourteen such reads were
planned. The owner's attention should go to the sentences whose meaning a
clinician has to judge.

**Fix.**

1. `tools/model_rewrite.py lost` also lists each equation, code span,
   citation and number that the working tree holds more often than the fork,
   so a value added or restated in a new place is shown, not only one that
   was dropped. Its summary line says how many lines need accounting.
2. `JUDGE_ASK` says that a `docs/MODEL.md` change is not needed when every
   line `lost` prints is accounted for as history or a kept duplicate, it adds
   no value, equation, code span or citation, and no sentence changes what a
   value means or what a hazard row or limitation promises. Otherwise it is
   needed, and the ask quotes the sentences that need judgment.
3. The `pull-request` skill, `docs/maintainer.md` § "What comes to you before
   it merges" and the coordinator mode say the same.
4. `PL-ZT47`'s step 6 gets a dated revision, and the section-part briefs not
   held on another branch drop "the project owner has read the rewrite".

**Generator check.** Work the owner asked for. The mechanism that held these
pull requests is the read rule itself, and this item changes it. No other open
item traces to it. The pause on new workflow mechanisms is lifted for this
request, because the owner asked for it.

**Done when.** `lost` lists added facts, a test pins it, and `JUDGE_ASK`, the
skill, the maintainer guide and `PL-ZT47` state the rule.
