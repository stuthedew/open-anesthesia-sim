---
id: PL-9331
title: Make docs/MODEL.md § "Assumptions", § "Known limitations" and § "Release gate" readable for a clinician: move its decision history to the items and rewrite its phrasing
priority: P1
effort: M
status: done
classes: docs
feature: prose-quality
touches: docs/MODEL.md
added: 2026-11-02
closed: 2026-11-04
pr: 2019
payoff: a clinician reading this part of the model specification finds the equations, units and limitations without reading past decision history and padding
verify: uv run python tools/model_rewrite.py ids "Assumptions" "Known limitations" "Release gate"
not-delegable: `docs/MODEL.md` is a `protected_paths` entry, so no delegated diff may touch it. Readability is judged by a person: no command separates plain prose from padded prose.
---

**Problem.** The prose of docs/MODEL.md § "Assumptions", § "Known limitations" and § "Release gate" still carries decision history and the
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

**Blocked** (project owner, 2026-11-04). This rewrite waits for the writing rule and the copy editor that `PL-J1ZM`'s design builds through `PL-W8FL`, `PL-43GT`, `PL-22T5` and `PL-JP8X`. Done before them, it would be written under the rules that made the section verbose, and then rewritten again.

**Ready, 2026-11-04.** All four have closed, so the rewrite is written now, and the copy editor edits it at close-out step 8.

**Owner's review, 2026-11-04.** Five sentences changed what they say, so the pull request waits for the owner to read them. Four correct an error: the humidification table now says all four cohorts fall outside one standard deviation with the factor, the Gas Man note says the cardiac-output note declines Brody's relation, the lung-store paragraph says the store takes up agent early in wash-in, and the lead-in says "This model assumes". The fifth rewords the arterial-blood bullet to say the lung is perfusion limited and arterial blood carries the alveolar partial pressure.
