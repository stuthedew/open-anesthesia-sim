---
id: PL-QL0X
title: Make docs/MODEL.md § "Runtime controls" up to § "Supported input ranges" readable for a clinician: move its decision history to the items and rewrite its phrasing
priority: P2
effort: M
status: done
classes: docs
feature: prose-quality
touches: docs/MODEL.md
blocked-by: PL-ZT47
added: 2026-11-02
closed: 2026-11-02
pr: 1953
payoff: a clinician reading this part of the model specification finds the equations, units and limitations without reading past decision history and padding
verify: uv run python tools/model_rewrite.py ids "Halting on a marked crossing" "The control-input record"
not-delegable: `docs/MODEL.md` is a `protected_paths` entry, so no delegated diff may touch it. Readability is judged by a person: no command separates plain prose from padded prose.
---

**Problem.** The prose of docs/MODEL.md § "Runtime controls" up to § "Supported input ranges" still carries decision history and the
phrasing patterns that `PL-ZT47` names. The history is item ids, re-measurement narratives, notes
on who supplied a source, ratification records and accounts of how a choice was
reached. The phrasing patterns are tautological asides, contrasts nobody
claimed, narration about the document, defensive scope statements, and table
cells or paragraphs that have grown into essays. The project owner judged the
document to read "like the worst kind of AI slop" on 2026-11-02, and decided
that it should be a document clinicians can read (project owner, 2026-11-02).

**Why it matters.** `docs/MODEL.md` is the document a clinician opens to decide
whether to trust a displayed number. History and padding bury the equation, the
unit and the limitation the reader came for.

**How.** `PL-ZT47` § "How each section part is done" is the procedure: take the
history out to the items first, in its own commit, then rewrite the phrasing,
and account for every line `tools/model_rewrite.py lost` prints. No equation,
unit, value, assumption, limitation, citation, marker, named test or
declared-none form may be lost. `PL-ZT47` built the rule and the tools this
uses.

**Generator check.** Work the owner asked for: one section part of `PL-ZT47`'s
decided split. The mechanism that let the history and padding accumulate,
`docs/MODEL.md` prose that no close-out review read, is `PL-ZT47`'s to fix.

**Done when.** `uv run python tools/model_rewrite.py ids` prints nothing for this part's sections, which its
`verify:` runs. The pull request body accounts for every line
`tools/model_rewrite.py lost` prints. The owner reads it only where
`PL-ZTZF`'s rule sends it: a changed value, equation, code span or citation,
or a sentence whose meaning needs their judgment.

**Three sentences changed meaning on purpose (2026-11-02).** The paragraph on
how a branch's drawn range is clipped quoted the line
`first_s = max(start_s, self._run_definition.opened_at_s)` from
`app/controller.py`, with its comment "a branch opens at its fork". That line
is gone: `drawn_window` now clips at `self.began_at_s`. The paragraph now quotes
the line the code holds. The same paragraph and § "The canonical evaluation
rule"'s bookmark-fork paragraph said that only a bookmark fork opens its
definition at an earlier keyframe and carries the fork instant. Since `PL-ZR49`
every fork reads its provenance from `RunDefinition.reaching_segment_at`, which
at a keyframe returns the stretch before it, so a control-event fork opens at
an earlier keyframe too. Both now say "every fork". The second blind review
found this.

**Handoff (2026-11-03 02:45Z).** The thread that did this part stopped for
length, past its spend budget, after the owner's pause on `PL-H76S` lifted.
The rewrite is closed and pushed on #1953, which is a draft and unarmed:
history pass `012a50e1`, phrasing pass `a920241a`, prose review and both blind
reviews `66b01ab7`, `verify --self` ACCEPT at `66b01ab7`, and main merged in
after #1962. What is left:

1. Re-run the close-out prose review on this branch under the rules #1956 to
   #1962 added to `.claude/rules/plain-writing.md` (each paragraph's reader,
   decided point, and no rewrite longer than the paragraph it replaces). The
   review applied in `66b01ab7` ran under the earlier rule.
2. Apply what it returns, then run `bin/docket verify --self PL-QL0X` again.
3. Publish `/mnt/project-files/v0.7.0/pl-zt47/pr1953-body-draft.md` as the
   pull request body, with its verify line filled and its review counts
   updated, and rename the pull request to "PL-QL0X: rewrite docs/MODEL.md's
   runtime controls, halting and control-input record in plain English, with
   their history moved to the items".
4. Ask `bin/docket arm`. Under `PL-ZTZF` this rewrite merges on green: no
   stored value changed, and `tools/model_rewrite.py lost` drops only history
   and one stale code quotation, which the note above accounts for.
