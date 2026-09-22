---
id: PL-X4RX
title: PL-SYG4's brief says it is left at needs-decision while its front matter reads ready, and nothing checks a brief's prose against its own status field
priority: P3
effort: S
status: ready
classes: docs
feature: brief-state-agreement
touches: docs/items/PL-SYG4-the-digest-s-reserved-verdict-suppresses-the.md
added: 2026-09-22
payoff: PL-SYG4's brief stops telling a session it waits on a decision that its own front matter and later paragraphs say was taken
verify: ! grep -q '^Left at .needs-decision. rather than triaged' docs/items/PL-SYG4-*.md
---

**Problem.** PL-SYG4's brief says it is left at needs-decision while its front matter reads ready, and nothing checks a brief's prose against its own status field

**Reproduced 2026-09-22 (`PL-14QR`, triage).** `PL-SYG4` reads `status: ready`. Its brief's
paragraph at line 199 opens "Left at `needs-decision` rather than triaged to
`ready` because the owner ratified the `PL-KQHN` recommendation, not this one",
with no date, and a later paragraph records the decision being taken and
committed. Across the store, three briefs say "Left at `needs-decision`" under a
different status:

- `PL-55JM`, which is done;
- `PL-LT77`, which is ready but dated ("**Triage note, 2026-09-07.**"), so it
  reads as history;
- `PL-SYG4`, the only one that reads as current.

**Why it matters.** A session reads the brief to decide whether it may start an
item. Prose saying the item waits on a decision, under front matter saying it
can start, leaves the reader to work out which is true. The cheap reading stops
at the prose and turns a ready item back into a question nobody is asking. This
is the failure `PL-RWJD` names: a superseded statement left undated, where the
convention would have kept it standing with the answer dated beneath it.

**Done when.** `PL-SYG4`'s paragraph is dated and marked as superseded by the
decision further down its brief. **Triage's call: no check is owed on this
count.** One live instance across the store is not a recurring failure, and
telling current prose from dated history is the judgment half that a check
would have to guess at. Reopen that call if a second undated instance turns
up.

**Reopened 2026-09-22 (`PL-8YXJ`).** The call above - no check owed on one
live instance - is reopened on its own condition: a second undated instance
exists. `PL-Z34C` says "It is left `needs-decision`" under an undated heading
while its status is `blocked`, and `PL-Z3V5` says "deliberately left at
`blocked`" while it is `ready`; the search for the literal "Left at
`needs-decision`" found neither, and `PL-7G5M` (closed 2026-09-15) was the
identical failure a week earlier. `PL-8YXJ` holds the mechanism and the check.
This item's own Done-when is unchanged, and is cheapest done in that session,
with the superseded marker it settles.
