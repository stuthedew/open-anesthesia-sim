---
name: docket
description: Read, add to, and work this repository's development queue in docs/items/. Use when the project owner asks what to work on next, what is left, what the priorities are, or whether to start the next milestone; when they have usage time available and no particular plan; when they flag a bug, cleanup, optimization, or idea to track for later; when a session's own work turns up a finding that will not be fixed in that session; when they name an item to start ("let's do PL-K7QX"); when they ask what can be worked on at the same time; and when asked to triage, reprioritize, groom, or ship a release.
---

# docket

The queue lives in `docs/items/`, one file per item. `subprojects/docket/README.md`
documents the format and the commands; this skill covers when to reach for
which, and the few judgments the tool deliberately does not make.

Run everything through `bin/docket <command>`, which needs no virtualenv and
no install step. `make docket` is the same validation, wired into `make check`.

**Do not read the store to answer a question a command answers.** `next`,
`list`, `check`, and `concurrent` exist so a session spends tokens on the
work rather than on the queue. Read an item's file when implementing it.

## Always

Kept at the top deliberately, and that reason now shapes the whole page.
Auto-compaction re-attaches an invoked skill "keeping the first 5,000 tokens
of each" ([skills](https://code.claude.com/docs/en/skills)), so anything past
that is cut off mid-sentence in every session that compacts. The modes used to
sit past it: this file ran 93,454 characters, about 23,400 tokens, and four
fifths of it - `start an item`, `triage`, `ship a release` and `close out`
among them - could not survive a compaction. They are separate files now,
reached by a read the cap does not touch, and what is left here is sized to
come back whole.


**Check repository state; never recall it.** Rule 14 of
`.claude/rules/instruction-writing.md` requires anything asserted about
external state to be re-verified before it is repeated. Here that is one
command each, against the remote rather than the local checkout: `bin/docket
show <id>` for an item's status, `git log origin/main` for what has merged,
`git fetch --tags` for what is tagged, the pull request's own state for
whether it is open. Say what the check showed when it changes the answer.

`make docket` after editing the store — it gates `make check` and CI, and its
errors mean an item is about to be silently wrong. Commit item changes with
the work they describe. An uncommitted queue is a lost queue.

## The two modes this queue serves

The project owner works in two distinct modes, and they have opposite cost
profiles. Recognize which one is happening and behave accordingly.

**Ideation.** Ideas, plans, direction, "what if we". This must stay cheap,
because it often happens when usage is nearly exhausted, and because losing a
thought to a rate limit is the worst outcome available. Capture with `docket
new`, take no detours, read nothing you were not already reading. Several
ideas arrive at once — `docket new` takes several titles in one call, so
capture them in one command rather than one per turn.

**Implementation.** Usage is available and the point is to burn it on work.
Here `docket next` picks, and the session goes deep.

Do not silently convert the first into the second. An idea raised mid-session
gets captured and the session continues; it does not become an implementation
detour unless the owner says so.

## Which file the mode is in

**Read the file for the mode you are in before acting. This table is a
dispatch, not a summary.** Each file carries the judgments, worked examples and
refusals that one row cannot hold, so a session acting from this page alone
gets the common case right and every edge wrong. The read is one call, and the
compaction cap does not reach it.

| When | Read |
| --- | --- |
| The owner describes something they want; an idea arrives mid-task; or the queue has thinned and a planned milestone is worth scoping | `.claude/skills/docket/modes/ideas.md` |
| A passing thought to record, or a finding this session will not fix; or repository work no item names - a merge, a stale ref, a docs sweep, a stranded item | `.claude/skills/docket/modes/capture.md` |
| "What should we work on next", "I have some time", "what's left"; or planning a batch that can run together | `.claude/skills/docket/modes/picking.md` |
| About to start a named item | `.claude/skills/docket/modes/start.md` |
| Untriaged items to fold into the queue, your own new capture's fields included; a grooming pass; or writing an item's `verify:` command | `.claude/skills/docket/modes/triage.md` |
| Scoping a milestone's debt gate, or there is finished work to ship | `.claude/skills/docket/modes/release.md` |
| An item's work is done and wants closing out | `.claude/skills/docket/modes/close-out.md` |

Nothing was cut in the move: each file holds its modes verbatim, and
`cat .claude/skills/docket/SKILL.md .claude/skills/docket/modes/*.md` is the
whole skill for a session that wants it end to end.
