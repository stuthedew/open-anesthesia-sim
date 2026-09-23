---
id: PL-8L9S
title: Say in CLAUDE.md that the generator pause holds apparatus work unrelated to the generators, not work on them or on the machinery that finds and ranks them (project owner, 2026-09-23)
priority: P2
effort: S
status: ready
classes: docs
feature: generator-identification
touches: CLAUDE.md, docs/items
added: 2026-09-23
payoff: Sessions stop treating work on the generators, or on the machinery that finds them, as new apparatus needing the owner to lift the pause
verify: grep -q 'machinery that finds and ranks generators' CLAUDE.md
---

**Problem.** Say in CLAUDE.md that the generator pause holds apparatus work unrelated to the generators, not work on them or on the machinery that finds and ranks them (project owner, 2026-09-23)

**The owner's words, 2026-09-23:** "The pause is on apparatus work unrelated
to fixing these generators (new features, housekeeping). 5MYR is exactly the
type of thing that should be in the pause." Asked to choose between two
readings, the owner confirmed the first: work on the generators, including the
machinery that finds them, is what the pause is for.

**Why it matters.** `CLAUDE.md`'s pause paragraph said "A new command, check,
field or rule ... is captured and not built", with only "fixing a live
generator, or a defect in what exists" exempt. Read literally, that blocked
`PL-5MYR`, a defect in generator identification whose fix adds a field.
`PL-T7Y1`'s session asked the owner to lift the pause for it, and the owner
had to correct the reading. Every later session would have made the same
mistake from the same sentence.

**Done when.** The pause paragraph states its scope in the owner's words and
names the machinery that finds and ranks generators as work the pause exists
for. The sentence it replaces is gone, so the paragraph does not say it twice.
