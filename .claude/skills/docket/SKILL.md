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

**Design first, items second. Do not create anything on first contact.** An
idea arrives half-formed by nature, and the first exchange is where it changes
shape most. Items written then get rewritten, re-scoped and deleted across the
next three replies, which fills the queue's history with churn and buries the
one version that mattered. Worse, "I created PL-A1B2, PL-C3D4" as a first
response reads as a decision already taken, when what the owner wanted was to
think it through.

So the first reply proposes. It creates nothing.

1. **Say what you understand the request to be**, in your own words. A misread
   surfaces here, cheaply, or it surfaces after the work is done.
2. **Ask what genuinely needs deciding** — the questions where different
   answers produce different software. Ask them together so they can be
   answered in one pass, and only the ones you cannot resolve from the code or
   from sensible defaults.
3. **Say how you would build it.** A few sentences of approach, and where it
   touches the existing design. This is the part the owner is here for.
4. **Propose the breakdown** — the items you would create, by title, with a
   size each, and which are decisions rather than code. Proposed, not created.

Then stop and let them react. Expect the shape to change; that is the point of
proposing it. Iterate in conversation, where revising costs a sentence.

**Create the items once the design has settled**, in one call, and say that is
what you did:

```bash
docket new --feature run-scrubbing \
  "Keep the full run in the controller's history buffer" \
  "Add a scrub control to the chart axis" \
  "Decide what the readouts show while scrubbed away from now"
```

Never hand the decomposition back. Working out what the idea breaks into,
naming the feature and writing the briefs is the job being delegated — asking
"which items should this be?" or "what should we call the feature?" returns it.
Propose an answer and invite correction; do not ask an open question.

**Where a thing lands depends on how ready it is, not on how big it is.**

| What the owner said | Where it goes |
| --- | --- |
| "Make this specific change" | A queue item, now. It is actionable already. |
| "I want this feature eventually" | One line of intent in `ROADMAP.md`'s "Planned milestones". No items. |
| "Let's build this" | The design round above, then items once settled. |

The middle row is the one that goes wrong. An aspirational feature filed as an
`L` queue item is work that cannot be worked: it sits at the bottom of the
queue being skipped by every session that reads past it, while looking like
something anyone could pick up. `ROADMAP.md` keeps such items deliberately
unspecified — no goal, no scope, no definition of done — until someone is
ready to scope one, which is exactly the right shape for intent.

## Mode: an idea arrives mid-task

Triggered by the owner raising a new feature while something else is underway.

Ideas arrive faster than they can be built, and the owner has asked to be kept
on task rather than followed down each one. Neither dropping the current work
nor quietly filing the idea is right — the first loses the thread, the second
loses the idea's placement to a decision they never got to make.

> "That fits — I'd put it in Phase 2, next to the settings panel, since it is
> the same consolidation problem. Parking it there unless you want it sooner;
> we are two items from finishing the halted-step decision."

Name where it would go and why, say what it would displace, and go back to
what you were doing. Place it on the roadmap once they agree.

**This is a nudge, not a gate.** If they want to switch, switch — it is their
project, and an idea that will not wait is sometimes the one to follow. The
obligation is to make the trade visible, not to win it.

## Mode: bring the roadmap back into the queue

Triggered by the queue thinning out, by a release shipping with little left
behind it, or by the owner asking what is next when nothing pressing is open.

**Offer this; do not wait for it.** Intent parked on the roadmap is only worth
parking if something brings it back. The digest's plan line says which beat is
due — it does not say that a planned milestone is worth scoping now, which is
the judgment this mode exists for.

> "v0.2.4 is out and what is left is four small items. The next planned
> milestone is the anesthesia-machine abstraction — the interlock baseline
> everything else on the list builds on. Want to scope it? That is a design
> round, and it would come out as items."

Then run the design round: goal, required scope, definition of done, and an
explicit out-of-scope list, written into `ROADMAP.md` per the development
rules there — *then* the items. A milestone is scoped before implementation
begins, not discovered during it.

**The exception is a session that is about to end with the thread open.** A
design still under discussion when the session stops is lost like anything
else, so capture what has been agreed as one untriaged item naming the open
questions, rather than letting a good conversation evaporate.

## Mode: capture

Triggered by the owner raising a passing thought they are not developing, or
by a finding this session makes that it will not fix.

**This is the opposite case to the one above, and the difference is whether a
design conversation is happening.** A thought dropped in passing — "the
induction curve looks wrong at low flows" — is captured immediately, because
the owner has moved on and nothing is lost by recording it. An idea being
worked through with you is not captured yet, because it is still changing. If
unsure, ask yourself whether the next reply is likely to change what the item
says: if it is, propose rather than create.

```bash
docket new "The induction curve looks wrong at low flows"
```

That is the whole procedure. No id to allocate, no band to choose, no file to
edit, nothing to conflict with another branch. Write the brief into the item
if the context is live and worth keeping — it is expensive to reconstruct
later and cheap to write now — but never let a missing brief stop the
capture.

**A finding that completes a frozen or in-progress item is not a new item.**
When work turns up something such an item needs in order to be properly
finished, the two are worked together - one branch, closed together - rather
than filed as sequential items. A freeze closes new behavior and features, not
the completeness of a fix; `ROADMAP.md`'s "The gate is a snapshot, not a moving
target" carries the rule and the reasoning.

Never hold a finding in conversation until the current work lands. The
container is ephemeral; an uncommitted thought is one interruption from gone.
Commit the new item on its own so it survives an abandoned branch.

The digest names an item that exists only on a branch when it finds one, and
`bin/docket stranded` prints it with the `git checkout` line that restores the
file. The command cannot tell live work from an abandoned branch, so that
judgment is the reply's: leave a branch someone is working, and recover from
one nobody will merge - restore the file, commit it on its own, and say in the
reply which branch it came off.

## Mode: housekeeping nobody filed

Triggered by the session being about to *do* repository work that no item
names: resolving a merge, clearing a stale `origin/<branch>` ref, a docs
sweep, a lint fix, recovering a stranded item, backfilling a field the store
wants.

**The rule: file the item first, then start it under its id** — `docket new`,
then Mode: start an item below. This is the cheap half of a problem the project has
already paid for the expensive half of. `flight`, `show`, `next`, `concurrent`
and the digest are all id-matchers, so work carrying no id gets a clean answer
from every one of them, correctly and uselessly. And unlike a race between two
sessions starting the same item, which closes the moment one of them pushes,
this stays invisible after *both* have pushed (`PL-CP74`).

It buys a record as well as visibility. Housekeeping is obvious enough that two
sessions recommend it in the same hour; unfiled, it leaves nothing behind
saying it was already done, so the next session rediscovers it and recommends
it again.

**How small is too small to file is the judgment here, and the line is whether
the work gets a commit of its own.** A rule demanding an item for a one-line
typo fix would convert the queue into a log, which is worse than the collisions
it prevents — so a fix riding inside a commit already led by an item's id is
filed by that id and needs nothing more. File it when it is the reason this
session exists, or when it will take a branch of its own.

`tools/branch_id_check.py` catches the case where none of this happened: `make
check` and CI fail a branch ahead of `main` that carries no id in its name and
leads no commit subject with one. It decides visibility only, never whether the
work deserved an item — that judgment is the paragraph above and stays here.


## Mode: recommend what to work on

Triggered by "what should we work on next", "I have some time", "what's left".

```bash
docket wave            # which beat of the plan is due - read this first
docket status          # features first - lead with this
docket next            # the specific next item, with its reason and its lane
docket next product    # ...the simulator only
docket next workflow   # ...the apparatus only
```

**Start above the queue.** `docket wave` says where the project stands on the
roadmap's cadence: the version, the step of the release train, the frozen debt
gate and how much of it is closed, and whether that leaves a gate to clear, a
release to cut, a milestone to implement or the next one to scope. The queue
cannot answer that, so a session that opens with `docket status` is answering
a narrower question than the one it was asked. Where the beat and the top of
the queue disagree, say so rather than following the queue: the beat is what
the plan says, and only the project owner rolls the wave forward.

`docket wave` computes and decides nothing. It will not tell you whether a
gate should open early, whether the prose beside a step is still true, or
whether a scoped milestone is scoped well. Those are the reply's judgment to
add, and they are why it prints the counts rather than a verdict.

**Open with the recommendation, then say where the release stands.** Rule 10
of `.claude/rules/instruction-writing.md` opens a reply that asks the owner to
decide with the question and the recommendation, one line each, and nothing
before them — and that file decides the shape of a reply here, per `CLAUDE.md`.
So the answer leads: "I'd take `PL-K7QX` (decide what the interface shows
after a halted step)." The release paragraph is the first thing under it, not
the opening.

**Then say where the release stands, in two or three sentences, before any
other item.** `docket wave` prints the facts; state them as prose, because a
row of counts is not an answer to "where are we". Name the release being built
and what it is for, what is left of it, and what closing it unblocks. For
example: "v0.3.0 is the foundation release — no new capability, just Gate 0's
inherited backlog. Eight of its twenty entries are open: four core-correctness
items wanting the strongest model, and the four `core-boundaries` refactors.
Closing it opens v0.4.0, the teachable case."

That is the paragraph the owner is actually asking for, and it costs one
`wave` call. Gloss every id at every mention, per rule 7 of
`.claude/rules/instruction-writing.md`. Then drop to the queue.

**Answer at feature altitude first.** "We could finish chart-readout — two
items left, both small — or start vaporizer-controls, which is four. Outside
those, PL-026 is safety-tagged and wants doing regardless." Nobody chooses
what to do next by reading twenty item titles, and a list of ids is a list of
homework. Drop to specific items once a direction is picked, or when
something individually urgent outranks the grouping.

`docket next` gives the ranking and the reason, already honoring `P0` first,
then what the roadmap's current step places, then work in a feature already
underway — the one nearest finishing first — then priority, and it excludes
what is in flight on a branch. A suggestion the step has not reached stays in the list, marked with
the milestone that places it, because hiding it would be a verdict the tool
cannot support. Placement is read from the frozen list a milestone records and
its `Required scope`, never from a mention elsewhere in the section, so an id
a section names only to exclude it is placed by nobody. Lead the reply with its answer. Add judgment the tool cannot
have: whether the item is still real, whether the marking is right about a
milestone whose prose it cannot read, and how it fits what the owner said
they were trying to do.

**The digest already names both lanes' picks.** Its `By lane, for a second
session:` line carries each half's top item and how many span both, so the
choice needs no command: read the lane matching this session and start there.
Where that line is absent, no boundary is declared and there are no lanes.

**A prompt that names a lane has already asked for it.** "Next workflow item",
"what's next on the simulator", "workflow lane" — that is `docket next
workflow` or `docket next product`, run as the first command, and the session
stays in that lane. It does not wait on establishing that a second session
exists: naming the lane *is* the instruction, and the owner does not restate
why they want it. `PL-0D4X` is what the older reading cost — a session prompted
"Next workflow item" ran the bare command, was handed the product lane's pick,
and started it.

`docket next` now names the lane of its own answer and the other lane's pick,
so a bare call in a lane-named session says so in its own output. Read that
line before the item.

**Otherwise ask for a lane only when another session is genuinely running.**
The owner runs two sessions at once precisely so one can take the simulator
while the other takes the apparatus, and a bare `docket next` in both hands
them the same item. Told nothing at all, ask for neither: a lane narrows the
queue, and narrowing it for a session that is the only one running is how the
next piece of work is worse than the one the whole queue would have offered.

Two lanes and no more, because two sessions can hold a repository between them
and four cannot. `product` is what `CLAUDE.md` holds to the specialist standard
— the simulator and the documentation a reader of it needs. `workflow` is the
apparatus that exists so sessions can be productive. The boundary is
`docket.toml`'s `workflow_paths`, read against each item's `touches`, and it is
a fact in the files rather than a judgment to re-make per item.

**Say what the lane set aside, and never treat it as absent.** `next` prints
the work no lane could claim: items reaching *both* halves, which need a
session that can hold the whole change, and items declaring no `touches`, which
nobody can place. Both stay in the queue and the unfiltered `docket next` still
offers them. When the reply offers a lane's answer, say the set-aside count in
the same breath — "PL-K7QX is the workflow lane's pick; three items span both
halves and are waiting for a session that can take the lot." An item invisible
in both lanes and mentioned in neither is how work goes missing for months.

**Work the roadmap places nowhere ranks on its band alone.** `docket next`
sorts in-scope work above unplaced work above out-of-scope work, so an item no
milestone section names is neither preferred nor excluded — it sits between the
two. Say so when you offer one, rather than presenting it as what the step
calls for.

Do not promote process work into P1 to move it up that order. `docket check`
pins `safety`- and `science`-classed items to P1, so the band means "a
clinician could be misled", and it stops meaning that the moment it also means
"the release script is annoying".

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

The `<id>` form adds what the branches in flight have **already changed**,
read from the branches rather than from anybody's `touches`. That section is
the stronger evidence of the two — it fires only where work is underway, and it
names the file to open. Report the two separately for that reason, and do not
present a clean observed section as a clean answer: it means no branch has
touched these files *yet*.

## Mode: start an item

**First, ask whether anybody else is already on it: `git fetch origin` and
then `bin/docket show <id>`, which marks it `IN FLIGHT` and names the refs it
could not read.** This is the one step with no other guard. `docket next`
excludes in-flight work, so a session that got here through `next` is already
covered — but an item named by the project owner skips `next` entirely, and
`triage`, `check` and reading the file with `cat` all say nothing. That is
backwards: naming an item is the higher-confidence path and was the one with
no check.

**The fetch is not optional, and it is the half that was missed.** Only
`docket branch` refreshes; `flight` and `show` read the refs this checkout
already holds, deliberately, so that they answer in a bare or offline
checkout. Without a fetch the answer is as old as the clone. Observed
2026-09-01: a session checked, was told nothing was in flight, and a branch
carrying the item was pushed four minutes later — the owner caught it, not the
tooling. Even fetched, the answer is bounded to what has been *pushed*, so
read a clean result as "nothing visible", never "nothing".

**Then push the first commit as soon as there is one.** The reading side
above is as hard as it can get - a fetched `show` still answers only for what
has been *pushed* - so the other half is not leaving the next session to find
out the slow way. Push the first real commit rather than batching to the end:
the `verify:` command an older item owes, a `touches` fill, the first failing
test. There is usually something within minutes; where there is not, push as
soon as there is. It costs nothing here - `.github/workflows/quality.yml`
triggers on `pull_request` and on `push` to `main`, so a push to a branch with
no pull request open runs no CI at all.

The cost is that an abandoned branch and a live session look alike in `flight`,
which says so and separates them by age; `bin/docket stranded` recovers what
one strands. That trade is worth taking - a session picking a different item
because one looked busy costs almost nothing against a queue this size, while
two sessions on one item costs a session and a merge conflict (`PL-PRHN`).

This shrinks the window rather than closing it: two sessions starting in the
same minute still race, because both answers come from refs.

**So read the session list too, which sees what no ref can.** `list_sessions`
from the `claude-code-remote` MCP server (`mine: true`) returns every session's
title and its branch, including a session that has committed nothing at all —
the window the two rules above leave open. Scan the live ones for the id
(`session_status` `RUNNING` or `IDLE`; archived and completed ones are finished
work), in the title and in `external_metadata.current_branches` both, because
either can carry it and neither reliably does.

**It adds a warning and never a clean bill of health.** It rests on the rename
rule below, which is followed about three times in four: measured 2026-09-02
over a twenty-session window, nine titles carried an id and at least three
sessions demonstrably working one item had never been renamed. A session
working an item under a generic title is indistinguishable from one working no
item at all — so unlike `show`, which names the refs it could not compare, this
read cannot name its own gaps. Finding nothing here means nothing; finding
something is decisive. It is also this harness only: `docket` knows nothing
about it and must not (`PL-SK88` records why).

**Then ask the other question: *is another session in these files?*** Every
step above answers "is another session on this item?", and that is not what
collides. Two sessions on different items are the normal case and neither
should yield — but they meet at merge if both edit the same file, which is
what `bin/docket concurrent <id>` exists to say. Run it. It needs no argument
the session does not already have.

It answers in two parts, and they are different kinds of evidence:

- **Declared overlap** — other items whose `touches` name a path this one
  names. A prediction written before either was started, so it fires on work
  nobody has begun and goes stale the moment a branch wanders outside its
  declaration.
- **Already changed on a branch in flight** — the files a live branch has
  *actually* changed, read from the branch itself. This one means the
  collision has already happened.

**Usually the answer is "proceed, and expect to resolve", not "pick something
else".** Two unrelated items legitimately touch one file; the point is that
the second to merge resolves deliberately instead of discovering it. Yield only
where the overlap is the same logic rather than the same file — and then it is
`PL-YHD3`'s question, not this one's. What a non-empty answer always changes is
sequencing: land the smaller change first, and say in the reply which branch
you expect to resolve against.

Read a clean result the way `concurrent` states it: it rules work out and never
certifies it. Silence means no branch has touched these files *yet*, and says
nothing at all about a file this item touches without having declared it —
which is why filling `touches` in as work begins, below, is what makes the next
session's answer true.

Then decide where the work happens and act on it — do not ask. Continue here when
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
  expected, and the commits carry the id instead. Say so in the reply. Leading
  every commit subject with the id is what keeps such a branch visible:
  `docket flight` reads the subjects, and an id buried mid-sentence does not
  count.

**A `P0` is a hotfix.** Before feature work, on its own branch, with a patch
version bump and a regression test. It joins no milestone list.

**Never start an `L` item straight from a queue entry.** An `L` is aspirational
scope that reached the queue rather than `ROADMAP.md`. Promote it into a scoped
milestone first, per the development rules there, and start the items that
milestone produces.

Set the item's `status` and `feature` as work begins, and add `touches` if it
is missing — that is what makes the next concurrency answer correct.

## Mode: triage

Triggered by the digest reporting untriaged items, or by a grooming pass.

```bash
bin/docket triage
```

That prints each untriaged item's body, the fields still unset, the brief
sections still missing, and the rules the answers must satisfy — read from
`docket.toml` and the checker, so they are what `docket check` will hold you
to rather than what this file remembers. Do not read the store for this, and
do not re-derive the rules from here.

**An item marked `IN FLIGHT` is one a branch already carries — skip it.** A
second answer here is a second resolution of the same file, and the merge keeps
one of them. The mark names the branch, so another session's work is
distinguishable from this one's. It is bounded by what has been pushed, so an
*unmarked* item means "no ref proved it" rather than "no branch has it" — which
is why the output also names the refs it could not read.

Fill in what capture deliberately skipped:
`priority`, `effort`, `classes`, `touches`, and `feature` when it belongs
with related work. Safety-critical work starts at `P0` or `P1`; the checker
enforces that. Process work — work on how the project is built rather than on
the product — does not enter the top band when it would outnumber the product
work already there.

An item that should not be done becomes `status: dropped` with a `reason`.
Never delete the file: the reason is what stops the finding being re-raised.

**An item whose next step is a decision is triaged to `needs-decision`, not
answered.** Triage sets fields; it does not resolve the question an item poses.
Answering one means reading the code around it, weighing the alternatives and
recording a conclusion - a work session's shape, spent on one item out of the
queue this pass exists to describe. `needs-decision` is what the store has for
it, and `bin/docket gate` counts it, so the question reaches the owner through
the queue rather than through the reply.

### The `verify:` command, and running it before writing it down

Triaging an item to `ready` means naming the command that proves it done.
`docket check` requires one at that status, because a `ready` item is a
commitment to do work and "what would prove this?" is the first thing that
becomes answerable.

**Run the command before you write it into the item.** All six commands that
ever existed here were wrong in the same two ways and none had been executed:
`--cov=` was given a file path where `pytest-cov` expects a dotted module, and
the run was scoped to one test file, which makes lines covered by the rest of
the suite read as uncovered and puts `--cov-fail-under=100` out of reach. An
unrun command fails after a worker has done the work, which costs a round trip
and the owner's attention.

**Run it and watch it fail, not merely run it.** A command that passes on a
tree without the work proves nothing: `docket verify` accepts a delegated
branch that did none of it, and nothing distinguishes a finished item from an
unstarted one. `docket check` now runs every open item's command and raises an
advisory for the ones that pass, so this is caught — but it is caught after the
item is written, and the fix is still to see it fail first.

**Watch it fail for the right reason, and never a bare `-k`.** `pytest -k
<name>` where no test yet carries that name does not fail; it *selects
nothing*, collects nothing and exits 5. Non-zero, so it looks like the command
failing as intended, and it goes on looking that way after the work too unless
the test the work adds happens to match. It also specifies only that some test
somewhere comes to be called `<name>` — not that any behavior holds. Measured
against a scratch file, which is why these are the codes and not a memory:

| Written as | Before the work | Reads as |
| --- | --- | --- |
| `pytest <file> -k no_such_name` | 5 | a command that correctly fails |
| `pytest <file>::test_no_such` | 4 | a usage error, same as a typo'd path |
| `pytest <file>` | 0 | already passing, proves nothing |
| `pytest <file> && grep -q 'def test_no_such' <file>` | 1 | an ordinary failure |

So pair the file's whole suite with a `grep` for the test the work adds. That
exits 1, the code a failing test gives, so no reader has to know a special
case; the pytest half proves the file's suite healthy, which `-k` never did;
and the `grep` names the exact test the work owes, which makes the command a
specification rather than a bet on a name.

`docket verify` says so on the check line where a command selects nothing, and
`docket check` reports it — separately from the commands that already pass —
for the items `next` is about to offer, which is the first moment there is
anybody to act on it. Reading one about your own item means: replace the
selector with the paired shape. The sentence carries how many open items across
the store are in the same state, which is context rather than a backlog to
clear in one pass — a command written away from its work is how every wrong one
here came to exist, so each is repaired as its item is started.

Copy one of these shapes rather than inventing one:

| The item is | The command |
| --- | --- |
| Covering a module's untested paths | `uv run pytest --cov=anesthesia_sim.core.tissue --cov-fail-under=100` |
| A string, label, or single behavior | `uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_halted' tests/unit/test_simulation_view.py` |
| Documentation only | `python3 tools/doc_check.py check && grep -qF 'the sentence the item adds' docs/MODEL.md` |

The last two are the same shape, and it is the one to reach for: something
that runs and passes today, paired with a `grep` for what the work adds. Each
half is doing a different job — the first proves the tree is healthy, the
second is what fails until the work exists — and neither alone is a
specification. `doc_check.py check` on its own passes whenever the docs are
internally consistent, which they are before the item is started too; five
open items shared exactly that command and none of them proved anything.

The first is the one that goes wrong loudly. `--cov=` takes the **dotted module**
(`anesthesia_sim.core.tissue`), never the path, and the run is the **whole
suite** — no test file argument — because coverage of a module is the union of
everything that exercises it.

Some work has no command that can run beforehand: proving a release-time fix
means cutting a release. Record that in `not-delegable:` rather than inventing
a command to satisfy the checker. An item saying why it cannot be proven is
better specified than one carrying a command nobody ran.

**Items older than the rule are asked for one when they come up, not before.**
A closed set of items reached `ready` before `verify_required_from`, and they
carry no command. `docket check` raises an advisory for them only as `docket
next` is about to offer them, naming those and the number still outstanding.
So the answer on meeting one is to write its command — having run it — as part
of starting it, which is the first moment there is any work to run it against.
Do not treat the advisory as a backlog to clear in one pass: that would mean
writing commands away from the work, which is how all six of the wrong ones
above came to exist.

**Closing one is where the exemption ends, and that is an error rather than an
advisory.** `verify_required_at_close_from` holds any item *closed* on or after
its date to the same rule, whatever its capture date, so a grandfathered item
cannot be finished while still saying nothing about what proved it. The
advisory above asks; this refuses. Nothing about it needs judgment — whether
the field is present is decidable, and only what it should say is not — which
is why it is a hard failure and why the advisory was not simply made louder
(`PL-J49T`).

There is no new burden in it if the command is written where the rule above
already says to write it: at the moment the item is started, having been run.
Reaching a close with nothing to record means the command was never run, and
`not-delegable:` is the honest answer where none can be. Items closed before
the cutover are untouched, deliberately — backfilling one onto merged work
means writing a command with nothing left to run it against.

### What the reply says, and what it must not

**Triage is a queue pass, not a work session, and its reply is a summary rather
than a to-do list** (project owner, 2026-09-04). Two things, then it stops:

1. **What was triaged** - each item by id and glossed title, the fields it
   landed on, one line of why. A dropped item says what its `reason` was; one
   left `needs-decision` says what the open question is.
2. **Where the queue stands as a result** - `bin/docket status`, at feature
   altitude, which is the altitude that makes a queue legible. Counts are not a
   summary on their own; say what shape they describe.

**Nothing else.** No ranking of what to work on, no release offer, no "and
while I was in there". `bin/docket next` answers "what next" in the session that
asks it, and this is not that session. Rule 14 of
`.claude/rules/instruction-writing.md` is met here by its own escape clause -
when nothing genuinely needs the owner, say so in one line rather than inventing
items to fill the block. On a normal pass that is the expected ending, not a
failure to find anything.

**Do not work the finding.** Committing and pushing the triage edits is routine,
not something to recommend. What must not happen is the pass becoming the fix: a
branch opened for an item it just triaged, a design question resolved, a pull
request shepherded through review. The pull is strongest where the finding is
most interesting, and interesting is not the test.

**Escalate only a `P0` or a compounding-friction finding** - `CLAUDE.md`'s three
tests: a check passing while its guarantee is void, an advisory being routed
around, something upstream of every other command. Name it in a sentence or two
and hand over the means to act on it *elsewhere* - `bin/docket next` where the
queue already holds the work, or the exact line to paste into a fresh session,
per **Mode: recommend what to work on** above. Not a diagnosis, not a patch, not
a branch. A pass where nothing pressing surfaced ends without this section;
reaching for something because the reply feels thin is how the summary turns
back into a to-do list.

## Mode: freeze a milestone's debt gate

Triggered by scoping a milestone — scoping is the act that freezes the list.

```bash
bin/docket gate --feature teachable-case
```

That is the whole pass: the open debt, split into what the milestone clears
itself (the items carrying its feature) and what clears before it begins, with
effort totals for each. Recording Gate 0 by hand meant reading 48 items and
applying the rule to each; do not repeat that.

**Recorded debt is cleared before a new milestone begins.** `ROADMAP.md`'s
"The debt gate" is the rule: open items classed `defect`, `safety`, `science`,
`refactor` or `perf`, and anything at `needs-decision`, reach `done` — or
`dropped` with a reason — before milestone work starts. `feature` and
`planning` items are not debt. Process work is debt once its mechanism is live
and unreliable, not while it is still being built; that case is classed
`defect` like any other, so the class carries the rule.

The command computes and decides nothing. Whether an item is *really* debt,
whether the gate should open, and what goes into `ROADMAP.md` are yours —
transcribe the two lists into the milestone's own section with the date they
were frozen, per `ROADMAP.md`'s "Recording it". The list is frozen at that
moment; a finding made afterwards goes to the next gate unless the problem it
describes predates the freeze, or is `P0`, `safety` or `science`.

## Mode: ship a release

**Offer this; do not wait to be asked — when the session is about what to do
next.** The session-start digest says when there is enough finished work to be
worth raising, and the release itself takes no arguments: the store already
knows what has shipped and what has not, so there is nothing for the owner to
look up and asking them to is pure friction.

Where the digest says `No release to offer` instead, the version a bump would
arrive at is one `ROADMAP.md` has already given to a step it has not finished,
and the line names that step. There is nothing to raise then: the beat printed
under it is the work, and cutting the version anyway would ship a milestone
under its own name with most of it missing.

But the digest says it in *every* session, including the ones where it is
beside the point. Offer it when the owner is choosing what to work on or has
just finished something. Not in a design round, a triage pass, a
question about one mechanism, or a review of one change — there it is noise appended to a reply
that was about something else, and it quietly converts ideation into
implementation, which the two modes above say not to do.

Raise it the way a colleague would: what got done, what it completes, what the
version would be, and a question.

> "PL-010 and PL-011 landed, so chart-readout is finished — four items. That
> makes a natural v0.2.4. Want me to cut it?"

```bash
docket status                    # includes what is releasable
bin/docket release --dry-run     # the notes and the bump, without writing
make release VERSION=0.3.0       # cut it
```

**Cut it with `make release`, never `bin/docket release` on its own.** The
tool writes the new version into `pyproject.toml` and stops, but `uv.lock`
records the project's own version too, so the next `make check` fails on `uv
sync --locked` with the tree half-updated and the reason unrelated to the
release. That happened on both releases the command has existed for. `make
release` runs `bin/docket release` and then `uv lock`, which is the whole
mechanical half.

**It stops there, and the last thing it prints is what is left.** `ROADMAP.md`
needs a version-table row, the `current baseline` mark moved onto it, and a
baseline section — release prose that says what the release was *for*, which
nothing generates. `bin/docket release` names each statement that is now
stale, with its line number. Make those edits, then run `make check`: that is
what proves they landed, and running it any earlier fails on edits nobody has
been asked for yet.

This project names its version rather than incrementing it, so `VERSION=` is
required; `bin/docket release --dry-run` prints the mechanical guess for
reference.

`docket.toml` sets `version_policy = "manual"` here, so the version is named
rather than inferred — `ROADMAP.md`'s "Versioning decision" is why: the number
marks the capability boundary a release crosses, which no class label carries.
The dry run still prints the mechanical guess, as a reference point and not an
answer.

`release` stops before tagging on purpose: review the bump and the generated
notes, then commit and tag. It **refuses to cut a release while the previous
one is untagged**, because a release cut without a tag leaves a permanent gap
— `git describe --contains` resolves nothing across its span — and the gap
cannot be repaired with confidence once the history has moved on.

**Never ask the owner to "tag vX.Y.Z". Paste the commands, filled in:**

```bash
git tag -a v0.3.0 <merge commit> -m "v0.3.0"
git push origin v0.3.0
```

Every time, not only the first. Asking for a tag without them makes the owner
reconstruct three commands at the moment they are trying to do something else.

## Mode: close out an item

1. Set `status: done` and `closed`, and commit that **with the work, in one
   commit**, whose subject leads with **every** id it closes, comma-separated -
   the recovery below reads the newest subject naming an id, so a rider closed
   under another item's id alone is attributed to its own capture commit
   (`PL-GW37`). **Do not write `commit:`** - the field is retired (`PL-T63T`),
   because a squash-merge discards the branch commit while the pull request
   number outlives it.

   **Leave `pr` empty; it is written after the merge, by command.** The number
   cannot be known before the pull request is open, and `docket check` owes a
   `pr` only on a closure that already stands on the default base — so an
   unlanded closure carrying none is the expected shape rather than an error.
   **Do not split the closure out to get the number earlier** — pushing the
   work first and adding the `pr` before the merge reopens the very window
   below, and the merge can arrive between the two pushes. Closing in the same
   commit as the work is what removes that
   window: requiring the number up front forced the closure into a second
   push, and a merge inside it took the work and left the closure on the
   branch — `main` had the fix while the queue still called the item open and
   a debt gate still counted it (`PL-D2GW`, then `PL-P5S0`).

   **`bin/docket record` writes it, and `make fix` runs that.** Bare, with no
   number: it writes every `pr` the base is owed and can supply, which is the
   same reading `docket check` prints the advisory from. **Never edit the field
   by hand** — the command refuses to overwrite a different number, and typing
   the line is how the wrong one gets recorded and how two sessions opened
   `#229` and `#230` for one identical insertion (`PL-QTSB`). Let the write
   ride a commit you are already making; do not compose one for it, and do not
   open a pull request for it alone. Where a number exists that the base cannot
   name — a squash subject that led with no id — `bin/docket record <number>
   --merge <merge commit>` is the explicit form.

   No in-flight guard is owed before running it, unlike every other path that
   edits an item someone else may hold. `PL-QTSB`'s harm was two *pull
   requests* for one insertion (`#229`, `#230`), and there is no pull request
   here: two sessions that both run it write the same tool-dictated line and
   git merges them. Asking each to fetch and check first would be friction
   that changes no outcome.

   The advisory is still an *error* where no commit on the base names a number
   at all **and** the checkout says it is complete, which is provenance
   genuinely lost; a truncated checkout declines instead, because the commit
   may be outside it (`PL-99Y4`).
2. **Sweep the docs.** `make doc-check` decides the package-map,
   provenance-table, marked-prose-value, dangling-citation, math-rendering and
   release-train questions outright, and
   `python3 tools/doc_check.py candidates --base <ref>` prints the
   documentation lines mentioning anything the diff touched.

   Spend the judgment on what neither can decide: whether each statement is
   still *true*. Stale documentation is a safety issue here — a reader who
   trusts a wrong statement about which agent is running or what a value
   means can reach a wrong clinical conclusion from a correct number. Say in
   the reply which files were checked.
3. Capture anything found but not fixed as its own item.
4. **Report gate progress if the item is one the gate contains.** Membership is
   decidable rather than a judgment: `bin/docket wave` prints the gate's open
   entries by id and `bin/docket gate` recomputes the split. When the item is
   one of them, close out with where the gate now stands — how many of its
   frozen entries are done, how many remain, and what the remaining ones are,
   glossed and grouped so the shape is visible (what is blocked on the
   strongest model, what is cheap). Say the same for entries the milestone
   clears itself. When the gate does not contain the item — a tooling fix, a
   docs pass, anything captured after the freeze — end without a gate report:
   the remaining entries are all simulator work, and listing them at the end of
   a process session is product work arriving in a discussion that was not
   about it.
5. Re-run `make check`.

## Always

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
