---
id: PL-DBRB
title: A build session that finds an item needs the owner's decision sets it aside for the next batched design round and goes on with the rest, as the owner asked on 2026-10-12, where the docket skill says only that a design round stops for the answer
priority: P2
effort: S
status: untriaged
classes: docs
touches: .claude/skills/docket/modes/design.md, .claude/skills/docket/modes/start.md
added: 2026-10-12
payoff: a build session that meets a question for the owner keeps building the rest of its batch, and the owner answers the lane's questions in one sitting
---

**Problem.** A build session that finds an item needs the owner's decision sets it aside for the next batched design round and goes on with the rest, as the owner asked on 2026-10-12, where the docket skill says only that a design round stops for the answer

**Why it matters.** The owner asked on 2026-10-12, in the v0.6.0 Project's
chat: "I'm wanting workflow fixes to be fairly automated so can we batch all
needs my input items as able so we limit it halting waiting for my input?" The
repository's two stop rules are narrower than a build session reads them.
`CLAUDE.md` § "Working with the project owner" stops a session that would
substitute a deliverable, and already says to do the parts that are the same
under either answer meanwhile; `.claude/skills/docket/modes/design.md` step 5
stops the design round's own thread for the answer. Neither says what a
session holding several items does when one of them turns out to need the
owner, so a session reads "stop for the answer" as stopping the batch, and the
owner is asked one question at a time, each halting a build. The Project's
instructions carried his rule alone until now; `docs/maintainer.md` § "Rules
for sessions live in the repository" says a rule he gives there is written
into the repository in the same sitting, which this item is.

**The rule** (project owner, 2026-10-12; the set-aside mechanics and the one
round per lane are the coordinator's reading of his words). A session holding
several items that finds one of them needs the owner's answer writes the
question and a marked recommendation into that item, sets it `needs-decision`,
yields its claim, and goes on with the rest. It neither stops the batch for
the answer nor settles the question itself. The questions are then put to the
owner together, as one design round over every open `needs-decision` item in
the lane, each worked as the design mode says, so he answers in one sitting
and no build thread waits on him. `CLAUDE.md`'s ask-gate is unchanged: the
parts of the work that are the same under either answer are still done, and
the parts that depend on it are not.

**Checked for conflict, 2026-10-12.** None. `CLAUDE.md`'s "Then stop, and
wait for the answer" binds the deliverable in hand, not the other items on the
branch, and its own next bullet keeps the independent work going. The design
mode's step 5 binds the round's thread, which still stops. The start mode's
batching paragraph already keeps an item out of a pull request where "a claim
likely to stall" would hold the rest, which is the same instinct one step
short of the rule. So the rule lands in the design mode, whose trigger is a
decision, with one sentence in the start mode's batching paragraph pointing
at it; nothing resident changes. The pause on new workflow mechanisms does
not hold a rule the owner asked for: his request lifts it for that request
(`PL-6Q9L`).

**Done when.** `.claude/skills/docket/modes/design.md` carries the rule under
a heading of its own, dated and attributed, and
`.claude/skills/docket/modes/start.md`'s batching paragraph points at it.
