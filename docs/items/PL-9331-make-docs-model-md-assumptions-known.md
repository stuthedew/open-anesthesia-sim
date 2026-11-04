---
id: PL-9331
title: Make docs/MODEL.md § "Assumptions", § "Known limitations" and § "Release gate" readable for a clinician: move its decision history to the items and rewrite its phrasing
priority: P1
effort: M
status: done
classes: docs
feature: prose-quality
milestone: v0.6.15
touches: docs/MODEL.md, docs/items/PL-J1ZM-sessions-write-prose-that-over-explains-in.md
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

**Owner's review, 2026-11-04.** Five sentences in `docs/MODEL.md` § "Known limitations" and § "Assumptions" now say something different, so pull request #2019 waits for the owner to review them. Four of them correct an error:

1. The humidification table said that with the water-vapour factor (713/760) applied, three of the four published wash-in cohorts fall outside one standard deviation of their published means. It now says all four do, as the table's rows show.
2. The Gas Man note said the cardiac-output note carries Brody's 1945 relation. It now says that note declines to adopt it.
3. The lung-store paragraph said the store does not appear in $`F_A/F_I`$ at all. It now says the store takes up agent in the first minutes of wash-in and barely changes $`F_A/F_I`$ at 30 minutes.
4. The lead-in said "Version v0.1.0 assumes". It now says "This model assumes".

The fifth rewords the arterial-blood bullet. It said arterial blood "is flow-limited and equals alveolar gas". It now says the lung is perfusion limited and arterial blood carries the alveolar partial pressure.
