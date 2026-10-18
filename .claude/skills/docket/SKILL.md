---
name: docket
description: Read, add to, and work this repository's development queue in docs/items/. Use it for every queue workflow - choosing what to work on next or what can run at the same time, including when the owner has time and no plan; recording an idea, bug or finding that this session will not fix; turning an idea into items; starting a named item ("let's do PL-K7QX"); running a design round on a needs-decision item; triaging, reprioritizing or grooming; freezing a debt gate or shipping a release; closing an item out; and filing repository work that no item names, such as a merge, a stale ref or a stranded item.
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

Auto-compaction re-attaches an invoked skill "keeping the first 5,000 tokens
of each" ([skills](https://code.claude.com/docs/en/skills)), so anything past
that is cut off mid-sentence in every session that compacts. This page is sized
to come back whole. Each mode lives in its own file, reached by a read that the
cap does not touch (`PL-2XM2`).


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

**A sweep verdict goes in the swept item's brief, not in the reply.** A sweep
checks many open items against the tree and reaches a verdict on each: it still
reproduces, it was solved another way, or its brief overstates what is left.
Write each verdict on an item that stays open into its brief as a dated
paragraph, `**Checked 2026-10-17:** ...`, in the commit the sweep makes. A
reply is deleted with its session. The 2026-09-19 workflow sweep left ten such
verdicts in a reply, and `PL-6ZQY` had to work all ten out again (`PL-NGLM`).

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
Here `docket next` picks, and the session goes deep. While product focus holds
(`CLAUDE.md` § "What this project is"), a session given no particular work runs
`docket next product` instead, and takes the product entry of the digest's
`By lane` line rather than its `Top:` line, which is the bare `next`
(`PL-2866`).

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
| "What should we work on next", "I have some time", "what's left", "what is next debt", "what have we forgotten"; or planning a batch that can run together | `.claude/skills/docket/modes/picking.md` |
| About to start a named item | `.claude/skills/docket/modes/start.md` |
| An item at `needs-decision`, or a brief that asks for a decision, before any code is written for it | `.claude/skills/docket/modes/design.md` |
| Untriaged items to fold into the queue, your own new capture's fields included; a grooming pass; or writing an item's `verify:` command | `.claude/skills/docket/modes/triage.md` |
| Scoping a milestone's debt gate, or there is finished work to ship | `.claude/skills/docket/modes/release.md` |
| An item's work is done and wants closing out | `.claude/skills/docket/modes/close-out.md` |

`cat .claude/skills/docket/SKILL.md .claude/skills/docket/modes/*.md` is the
whole skill for a session that wants it end to end.
