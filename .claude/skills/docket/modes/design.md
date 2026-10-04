# docket: design round

Read this when an item is at `needs-decision`, or its brief asks for a
decision, before any code is written for it: the order a design round runs in,
from the claim to the yield that lets its pull request arm.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

## Mode: a design round on an item

**An item at `needs-decision`, or a planning item whose brief asks for a
decision, gets a design round before any code**, and the round takes every
open decision in the item at once rather than one per sitting (project owner,
2026-09-25, ratified, over coding straight from a brief with an open question,
`PL-NZC0` § "Stress-test additions"; generalised from the three heads it was
written for to every such item in the Projects trial's instructions by
2026-10-03, kind unrecorded, `PL-PDVF`). The round is item files only: it
writes recommendations and answers into the item, changes no code, and its
pull request carries nothing else. The thread that builds the item afterwards
claims it afresh and sets its status as its first write, per
`.claude/skills/docket/modes/start.md`.

The procedure, in the order it runs:

1. **Restart the branch on `origin/main` and claim the item**, as the start
   mode has it - `bin/docket claim <id>` accepts a `needs-decision` item - so
   the round is visible to every other session, and its pull request opens as
   a draft at the claim's push. `bin/docket arm` answers `hold` while the
   claim is open; leave it unarmed.
2. **Read what the design must not contradict before writing a word of it**:
   the items this one builds on - its `blocked-by`, the heads it is a member
   of, the closed items of its `feature:` - and the roadmap section that
   places it, which `bin/docket show` names on its `plan:` line, so that no
   later design contradicts an earlier one without saying so. For a Workspace,
   Area or View item that is `ROADMAP.md` planned-milestone item 34 and
   `docs/interface-provenance.md`, whose § "What a later design thread owes
   this study" binds the round (project owner, 2026-09-27, in the v0.6.0
   Projects trial's instructions).
3. **Write a marked recommendation beside each open question, in the item
   file.** `.claude/skills/docket/modes/triage.md` § "Mode: triage" carries the
   form - `**Recommendation:**` or the word under emphasis where a
   skimming reader lands, or a marked statement that none is owed and why -
   and `bin/docket check` advises where a `needs-decision` brief marks
   neither. The reply dies with its session; the item is the carrier the
   owner's answer will land beside (`PL-KQHN`).
4. **Decide the obvious calls in the round, and put to the owner only what is
   theirs.** Where one option is clearly correct - a measurement, a check or a
   rule this repository already states settles it - take it, record why in the
   item, move the status in the same commit, and tell the owner in one line
   what you did; closing an item whose own measurements show the work is not
   worth doing is one of these (project owner, 2026-09-27). Offer a choice
   only where it is genuinely close, changes the goal, or cannot be undone, and
   then lead with the recommendation. `.claude/rules/instruction-writing.md`
   rule 14 carries the test, and triage.md's paragraph opening "And
   `needs-decision` says the next step is a decision, never whose" the sort:
   the owner's are the consequential questions, and resting on what the
   project wants does not by itself make a question theirs. A round whose every question is an obvious
   call closes or readies its items in the round and arms its pull request
   without waiting (`#1298`).
5. **Push item files only, and stop for the answer.** A question put to the
   owner leaves the status where it stands until the answer. The reply opens
   with the questions and the recommendations, one line each (rule 10), and
   its closing block asks for them in the order they will be decided
   (rule 14).
6. **On the answer, record it beneath the question and leave the question
   standing**, dated and with its kind - `(project owner, DATE, ratified)` and
   what it was chosen over, or the plain form where the owner specified it
   (`CLAUDE.md` § "Working with the project owner") - mark every passage above
   it the answer ended with `[superseded DATE: ...]`, and **move the status in
   the same commit**: `bin/docket check` refuses an answer left beneath a
   `needs-decision` front matter (`PL-JNWS`), and a `ready` item carries a
   `verify:` in an admitted shape and the Done-when in the decided form.
   triage.md carries each of those in full; this step is the order.
7. **Then `bin/docket yield <id>`**, with the same `--trailer` lines as the
   claim, and push with the command it prints where it exits 4 (`PL-1X56`).
   The yield releases the claim, so `bin/docket arm` can answer: `behind N`
   brings `origin/main` in once and asks again; `arm` marks the pull request
   ready and arms it. The build that follows claims the item again.

**What the round is not.** It is not the design round `.claude/skills/docket/modes/ideas.md`
runs on a new idea, which proposes items that do not exist yet; this one
answers questions an existing item already holds. Nor is it the thread that
builds the item: a round that starts writing code has become a build with an
unrecorded decision in it, which is the shape the round exists to prevent.
