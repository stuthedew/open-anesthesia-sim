---
id: PL-NGLM
title: A sweep verdict left in a session's reply is not recorded: the 2026-09-19 workflow sweep's what-landed notes for ten items died with the archived session and PL-6ZQY had to re-derive all ten from the tree
priority: P2
effort: S
status: ready
classes: infra
touches: .claude/skills/docket/SKILL.md
added: 2026-09-19
payoff: stops the next sweep re-deriving at full context the verdicts an earlier sweep already reached and lost with its session
verify: grep -qF 'sweep verdict' .claude/skills/docket/SKILL.md
---

**Problem.** A sweep verdict left in a session's reply is not recorded: the 2026-09-19 workflow sweep's what-landed notes for ten items died with the archived session and PL-6ZQY had to re-derive all ten from the tree

**Why it matters.** A sweep is the most expensive read this project performs
and the one whose output is least recoverable. `PL-LKGL`'s pass over the
workflow lane read 134 items to find 12 dead and 31 overtaken; `PL-4YJK`
records what one costs, and `PL-JB3Z` measured a later sweep at 145,000 tokens
across twelve agents. What a sweep produces is a per-item verdict - this one
still reproduces, this one was solved another way, this one's brief overstates
what is left - and a verdict is a *fact about the tree at a date*, which is
exactly the kind of thing the store exists to hold.

Left in a reply it is held by the session, and a session is deleted. The
2026-09-19 workflow sweep's what-landed notes for ten items died with its
archived session, and `PL-6ZQY` re-derived all ten from the tree. That is the
same work twice at full context, and the second pass could not know it was
repeating the first.

It is also the failure rule 14 of `.claude/rules/instruction-writing.md`
already names for the closing block - "a line that could reasonably outlive
this sitting is `bin/docket new` as well" - arriving on a different carrier. The
block rule covers *requests*; nothing covers a *verdict about an item that
stays open*, which has no action attached and so never reaches the closing
block at all.

**What the fix might be**, not settled here and roughly in order of cost: a
sweep verdict appended to the swept item's own brief with its date, which needs
no mechanism and is what a session can do today; a front-matter field recording
the date an item was last checked against the tree, which `bin/docket next`
could surface so a stale verdict is visible; or a `docs/WORKING_NOTES.md`
thread per sweep, which is the existing home for reasoning spanning more than
one item. The first is probably all of it - the store already holds prose per
item, and the thing missing is the instruction to write there rather than in
the reply.

**Done when.** A sweep's per-item verdict lands somewhere a later session reads
without being told it exists, and the rule saying so is where a session
performing a sweep will meet it - or the item records why the reply is the
right place after all.
