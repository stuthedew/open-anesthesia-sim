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

## Mode: turn an idea into work

Triggered by the owner describing something they want — a feature, a problem,
a direction. **They describe the outcome; decomposing it is yours.**

Never hand the decomposition back. Asking "which items should this be?" or
"what should we call the feature?" or "which ones go in this release?" is
asking them to do the job they are delegating. They should be able to say
"the chart should let you scrub back through a run" and then hear nothing
until there is a plan to react to.

So: work out what the idea breaks into, name the feature, write each item with
a brief a stranger could act on, and create them in one call.

```bash
docket new --feature run-scrubbing \
  "Keep the full run in the controller's history buffer" \
  "Add a scrub control to the chart axis" \
  "Decide what the readouts show while scrubbed away from now"
```

Then report the approach *and* the shape, in that order:

> "The scrub control needs the run kept in memory, so the first item widens
> the history buffer and the second hangs a control off the chart axis. The
> third is a question rather than code — what the numeric readouts should say
> when you are scrubbed away from now, since showing live values beside a past
> chart is exactly the stale-context error the safety standard warns about.
>
> Created PL-A1B2, PL-C3D4, PL-E5F6 — two small, one needing a decision."

A few sentences of *how* come first, because the owner wants to understand the
design, not merely receive it. Item ids belong in the reply as references,
never as something they have to supply, and never as a substitute for saying
what the work actually is.

If the idea is one thing rather than several, it is one item; do not inflate
it. If it is genuinely a milestone — its own goal, scope and definition of
done — say so and scope it in `ROADMAP.md` instead.

## Mode: capture

Triggered by the owner raising a passing thought, or by a finding this session
makes that it will not fix.

```bash
docket new "The induction curve looks wrong at low flows"
```

That is the whole procedure. No id to allocate, no band to choose, no file to
edit, nothing to conflict with another branch. Write the brief into the item
if the context is live and worth keeping — it is expensive to reconstruct
later and cheap to write now — but never let a missing brief stop the
capture.

Never hold a finding in conversation until the current work lands. The
container is ephemeral; an uncommitted thought is one interruption from gone.
Commit the new item on its own so it survives an abandoned branch.

## Mode: recommend what to work on

Triggered by "what should we work on next", "I have some time", "what's left".

```bash
docket status          # features first - lead with this
docket next            # the specific next item, with its reason
```

**Answer at feature altitude first.** "We could finish chart-readout — two
items left, both small — or start vaporizer-controls, which is four. Outside
those, PL-026 is safety-tagged and wants doing regardless." Nobody chooses
what to do next by reading twenty item titles, and a list of ids is a list of
homework. Drop to specific items once a direction is picked, or when
something individually urgent outranks the grouping.

`docket next` gives the ranking and the reason, already honoring `P0` first, then work
that finishes a feature already underway, then priority — and it excludes
what is in flight on a branch. Lead the reply with its answer. Add judgment
the tool cannot have: whether the item is still real, and how it fits what
the owner said they were trying to do.

`docket next` states which model the work warrants. That is not a suggestion
to weigh: safety- or science-classed work, and any item whose next step is an
unresolved decision, wants the strongest available model at high effort, for
both the change and the review of it. Say so before work starts — a model
switch mid-session costs a cold cache.

Recommend a **fresh session** when this one is long or was about something
else. Give the exact line to paste, on its own:

```text
PL-K7QX Decide what the interface shows after a halted step
```

That message sets the next session's name and branch, so it must carry the id
and title verbatim.

## Mode: work several items at once

Triggered by "can we do these together", or by planning a batch.

```bash
docket concurrent            # a batch that can run together
docket concurrent PL-K7QX    # what can run alongside this one
```

**Report what it rules out, never what it certifies.** Declared overlap
proves contention; absence of overlap proves only that nobody foresaw a
collision. Say that plainly rather than presenting a clean result as a
guarantee, and treat an item with no `touches` as unanalysed rather than
safe — fill its `touches` in instead.

## Mode: start an item

Decide where the work happens and act on it — do not ask. Continue here when
this session's context is an asset (short, already about this item, just
diagnosed it). Start fresh when it is a liability (already completed
something else, long, or the item wants a model this session is not running).

Then name the work after the item, because a session list is unsearchable
otherwise:

- **Session name** — rename immediately to lead with the id. On a remote
  session, `set_session_title` via the `claude-code-remote` MCP server.
- **Commit subjects and PR title** — always carry the id. These outlive the
  branch.
- **Branch** — `claude/pl-k7qx-short-slug` where the session creates it. A
  branch generated before the session started cannot be renamed; that is
  expected, and the commits carry the id instead. Say so in the reply.

Set the item's `status` and `feature` as work begins, and add `touches` if it
is missing — that is what makes the next concurrency answer correct.

## Mode: triage

Triggered by the digest reporting untriaged items, or by a grooming pass.

Read each untriaged item and fill in what capture deliberately skipped:
`priority`, `effort`, `classes`, `touches`, and `feature` when it belongs
with related work. Safety-critical work starts at `P0` or `P1`; the checker
enforces that. Process work — work on how the project is built rather than on
the product — does not enter the top band when it would outnumber the product
work already there.

An item that should not be done becomes `status: dropped` with a `reason`.
Never delete the file: the reason is what stops the finding being re-raised.

## Mode: ship a release

**Offer this; do not wait to be asked.** The session-start digest says when
there is enough finished work to be worth raising, and the release itself
takes no arguments — the store already knows what has shipped and what has
not. There is nothing for the owner to look up, so asking them to is pure
friction.

Raise it the way a colleague would: what got done, what it completes, what the
version would be, and a question.

> "PL-010 and PL-011 landed, so chart-readout is finished — four items. That
> makes a natural v0.2.3. Want me to cut it?"

```bash
docket status               # includes what is releasable
docket release --dry-run    # the notes and the bump, without writing
docket release              # infers the version; --version to override
```

The version is inferred: a minor bump when `feature`-classed work went out, a
patch otherwise. A major bump is never inferred, because breaking a published
interface is a decision rather than a fact about labels — raise that one.

`release` stops before tagging on purpose: review the bump and the generated
notes, then commit and tag.

## Mode: close out an item

1. Set `status: done`, record the `commit`, and set `closed`.
2. **Sweep the docs.** `make doc-check` decides the package-map,
   provenance-table, and dangling-citation questions outright, and
   `python3 tools/doc_check.py candidates --base <ref>` prints the
   documentation lines mentioning anything the diff touched.

   Spend the judgment on what neither can decide: whether each statement is
   still *true*. Stale documentation is a safety issue here — a reader who
   trusts a wrong statement about which agent is running or what a value
   means can reach a wrong clinical conclusion from a correct number. Say in
   the reply which files were checked.
3. Capture anything found but not fixed as its own item.
4. Re-run `make check`.

## Always

`make docket` after editing the store — it gates `make check` and CI, and its
errors mean an item is about to be silently wrong. Commit item changes with
the work they describe. An uncommitted queue is a lost queue.
