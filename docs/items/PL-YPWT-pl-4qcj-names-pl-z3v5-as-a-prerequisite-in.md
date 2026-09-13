---
id: PL-YPWT
title: PL-4QCJ names PL-Z3V5 as a prerequisite in prose without declaring the edge in blocked-by, so docket next offers it as startable work whose first step is another item
priority: P2
effort: S
status: done
classes: infra
feature: queue-hygiene
touches: docs/items
added: 2026-09-13
closed: 2026-09-13
verify: bin/docket check && grep -q '^blocked-by: PL-Z3V5' docs/items/PL-4QCJ-the-yasuda-methods-reading-has-no-extraction.md
---

**Problem.** PL-4QCJ names PL-Z3V5 as a prerequisite in prose without declaring the edge in blocked-by, so docket next offers it as startable work whose first step is another item

**Where it came from.** Surfaced by the first `bin/docket check` after `PL-ZGK2`
recovered `PL-Z3V5` from an abandoned branch. The advisory could not fire while
`PL-Z3V5` existed on no ref the checker reads, so an open item had been sitting
blocked on something the store did not contain, with nothing saying so.

**The decision, which is why this is an item rather than a fix.** The advisory
names two remedies and they are not interchangeable. Either `PL-4QCJ` really is
blocked - in which case it takes `blocked-by: PL-Z3V5` and `status: blocked`,
which is the half `bin/docket next` reads, and it leaves the startable queue
until `PL-Z3V5` closes - or the sentence overstates the relationship and should
be reworded, in which case the item stays startable. The prose reads "`PL-Z3V5`,
which decides what an extraction note contains and", so the dependency is on a
*format decision* rather than on work; whether that blocks a reading is the
question.

**Why it matters.** An undeclared edge is invisible to every command that ranks
work. `bin/docket next` offers `PL-4QCJ` as startable, and the session that
takes it discovers the prerequisite by reading the brief - which is the cost
`blocked-by` exists to remove, and the same failure `PL-B9PY` and `PL-L09X`
have each cost once before.

**Where.** `docs/items/PL-4QCJ-the-yasuda-methods-reading-has-no-extraction.md`,
front matter and the `**Blocked on.**` paragraph.
**Done when.** Closed in the triage pass of 2026-09-13, which is where the
question belonged: the remedy either way was a front-matter field, and setting
those is what triage does.

**Which remedy, and why.** The first. `PL-4QCJ` now carries `blocked-by:
PL-Z3V5` with `status: blocked`, so it leaves the startable queue until
`PL-Z3V5` (decide what a `docs/references/` extraction note contains) closes.
The sentence was not an overstatement: `docs/references/README.md` says "What a
note contains, and the first worked example, are `PL-Z3V5`'s and are
deliberately not fixed here", and `PL-4QCJ`'s own brief adds "Do not invent the
format here." A prerequisite the repository forbids working around is a blocker.
`bin/docket check`'s advisory recommended the same disposition.

**One thing corrected in the same edit.** `PL-4QCJ` said `PL-Z3V5` existed only
on `origin/claude/vibrant-curie-0x11e4` and needed recovering. `PL-ZGK2`
recovered it; `bin/docket check` now reports it ready to promote. The stale
sentence is replaced rather than left standing under a note.
