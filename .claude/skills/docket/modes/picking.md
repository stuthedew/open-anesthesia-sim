# docket: picking

Read this when the question is what to work on next, or when planning a batch
of items that can run at the same time.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

## Mode: recommend what to work on

Triggered by "what should we work on next", "I have some time", "what's left",
"what is next debt", "what have we forgotten".

```bash
docket wave            # which beat of the plan is due - read this first
docket status          # features first - lead with this
docket next            # the specific next item, with its reason and its lane
docket next product    # ...the simulator only
docket next workflow   # ...the apparatus only
docket next --oldest   # owed work longest-waiting first - "what is next debt"
```

**Start above the queue.** `docket wave` says where the project stands on the
roadmap's cadence: the version, the versions ahead of it the roadmap has
already given out, the step of the release train, the frozen debt gate and how
much of it is closed, and whether that leaves a gate to clear, a release to
cut, a milestone to implement or the next one to scope. The queue
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
then a recorded *generator*, then what the roadmap's current step places, then
work in a feature already underway — the one nearest finishing first — then
priority, and it excludes what is in flight on a branch. A generator is an item
carrying `root-cause-of:`, naming three or more items it causes.

**Recording one and ranking one are two separate writes** (project owner,
2026-09-21, ratified). The count is what records it; a second field,
`generator:`, is what decides whether it ranks — `live - <why the store is
still handing this mechanism members>` puts it above every other band, a
`safety`-classed `P1` included, and `spent - <why it can no longer produce
one>` keeps the record for the audit and leaves it on its own band. Recording
alone ranks nothing, and `docket check` asks any open generator that has not
answered. So a three-item cluster you judge finished is now written down
rather than withheld to keep the ranking honest, which is the trade the split
removed. A third field, `misread:`, states in one line the fact the members
misread, so later captures and other heads can be compared with it. It ranks
nothing, and `docket check` asks it of every head, open or closed (`PL-5MYR`). `CLAUDE.md` § "A root cause of more than two items is pulled, not
queued" is what a session does on finding a *ranking* one;
`tools/generator_check.py` prints the clusters worth looking at and decides
none of them.

**"Are the generators dealt with?" is `bin/docket generators`, and the heads'
own statuses do not answer it.** Fixing a generator closes the head and leaves
its members owed, so every head this project has recorded reads `done` over a
cluster that is mostly open. The command prints each cluster's open count, how
far it has drained since its head closed, and which clusters are finished,
with each head's `misread:` line and the heads whose clusters overlap; with
an id it lists one cluster's members, and a member's id resolves to the head
above it. Answering from the item files instead is the read this was built to
replace — it had been done twice in two days by a throwaway script (`PL-XF5V`).

**That tier has a second entrance, and finding one is not a filing.** A
defect in the machinery that *finds and ranks* generators ranks at the same
priority as a generator (project owner, 2026-09-19): while identification is
broken a generator is never recorded, and an unrecorded generator is ranked by
nothing, so nothing in the store would ever say one went unfound. Record it as
`impairs-generators:` — prose, never `yes`, naming which function broke — and
the item's `touches` must reach a path in `generator_paths`, which is what
`docket check` holds it to. `bin/docket set <id> --impairs-generators "..."`
writes it. The judgment is yours and nothing infers it; the path list can only
refute a claim, never make one, since 36 of this store's open items touch those
files for unrelated reasons.

**Then take one of the generator's own two endings** — fix it in this session,
or end the reply with a ready-to-paste prompt starting a fresh one. Recording
the field and carrying on is not a third (project owner, 2026-09-19, against
the recommendation to confine the obligation to a measured cluster; `PL-4MPJ`).
So this is a `docket new` only on the way to one of those two, never instead of
one — which is the same shape `CLAUDE.md` gives a generator, and the reason a
triage pass meeting such an item escalates it rather than banding it. A suggestion the step has not reached stays in the list, marked with
the milestone that places it, because hiding it would be a verdict the tool
cannot support. Placement is read from the frozen list a milestone records and
from the `(queue item …)` slot its `Required scope` entries declare in, never
from a mention elsewhere in the section, so an id an entry cites in passing is
placed by nobody and one the anchor's own exclusion heading names is reported
as ruled out. Lead the reply with its answer. Add judgment the tool cannot
have: whether the item is still real, whether the marking is right about a
milestone whose prose it cannot read, and how it fits what the owner said
they were trying to do.

**"What is next debt" and "what have we forgotten" are `docket next
--oldest`** (`PL-Q89J`). The plan's order favours what is newer, more urgent or
more central, so owed work that is none of those - the `docs`, `infra` and
`test` items no gate will hold - waits for good. `--oldest` hands out owed work
longest-waiting first with `P0` on top, lists `needs-decision` items apart,
and composes with a lane and `--effort`. Its picks are usually off-gate, and
the placement sentence under each one says so; offer them under the off-gate
rule below, and name the plan's own pick, which its last line prints. Age is a
reason to look, not evidence the item is still real: an old brief can describe
code that has since moved, so read it against the tree before starting it.

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

**Every item you offer carries its relation to the gate, and this rule is not
confined to this mode** (project owner, 2026-09-13). It applies wherever a next
item is named: a `next` answer, the closing line of a design round, the last
paragraph of a session that just finished something else. That last one is
where it was missed — `PL-FZ6T` was offered as "the natural continuation" of
the item that had just unblocked it, with nothing said about the gate, which
reads as *what the project should do next* while sitting outside what the
project said it was doing (`PL-J790`).

There are four relations, and `docket next` prints all but the last in its
reason line under each item:

- **On the gate** — "On the debt gate recorded under v0.5.0; v0.4.x — the code
  is the model clears it."
- **Outside what the anchor names** — the id sits in a later milestone's
  section, which the current step has not reached.
- **Ruled out** — the anchor's own `Explicitly out of scope` heading names it,
  so the roadmap has taken a decision rather than not reached one. It sorts
  below out-of-scope work (`PL-6P9Y`).
- **Placed nowhere** — neither preferred nor excluded. It ranks on its band
  alone, and nothing prints it.

The last is the one that goes wrong, and in two ways. Nothing states it, so
silence is indistinguishable from not having looked; and it means *no milestone
section places it*, which is narrower than it sounds. `Scope` reads three
structures — a section's frozen list, the `(queue item …)` slots its `Required
scope` entries declare in, and the anchor's own exclusion heading — so a
milestone recording scope in a sentence that declares nothing records it
invisibly, and a **timeline row** places nothing at all. A row that *bears* a section places through it,
numbered or not - the Qt port's `—` row anchors the beat while its scope is
open (`PL-FWJF`) - but the `v0.4.x` row bears none. `PL-FZ6T` is the worked
example: `docket next` gives it no gate sentence, while `ROADMAP.md`'s
`v0.4.x` row names it outright. So
"placed nowhere" is a fact about those structures and never a claim that the
roadmap is silent — read the row for the step before saying either.

`bin/docket show` prints the item's placement on its `plan:` line (`PL-J790`),
so an item reached by name — the way the owner usually starts one — carries
its relation to the plan without a lookup, and "placed nowhere" there is the
same fact about the same structures. Placement is not gate membership:
`bin/docket wave` prints the gate's open entries by id and is still what
settles membership.

**Say what the work buys, in consequence terms, before naming what it does**
(project owner, 2026-09-19). An item's title is written for the session that
will implement it, so it names a mechanism - "reconcile the jobs reporting a
status check against the branch-protection required list". Offered to the
project owner unchanged, that is a string they cannot weigh: *"I don't know why
it's selected ... 'links predicate xyz predicate to runner 267' or whatever."*

So each item you offer leads with what closing it changes for them - it gets
faster, fewer bugs reach `main`, a check stops lying, a release stops needing a
person to remember a step - and names the mechanism second. One clause each,
not a paragraph:

> `PL-XZD0` (nothing reconciles CI's checks against the required list) - stops
> a renamed CI job silently leaving pull requests waiting forever on a check
> that can never arrive. It has happened twice. P2, not on the gate.

The rule is strictest where the item is **workflow-lane**, because that is the
offer the owner has no other way to judge: a simulator item's title describes
something they already have an opinion about, and an apparatus item's does not.
`bin/docket next` prints each lane pick's band and gate relation, which is the
decidable half.

**The sentence itself is now a field, so write it once into the item rather
than into the reply** (`PL-WYKF`). `payoff:` holds it - one line, required at
`ready` from 2026-09-20 - and `bin/docket show`, `next` and the digest print it
wherever they name an item. Composing it is still judgment and still yours;
what has changed is that composing it again next session is not. So when you
meet an item that has none, write it as you start the item - the advisory
`bin/docket check` raises names exactly the ones `next` is about to offer - and
when an item has one, offer it rather than paraphrasing it:

```bash
bin/docket set PL-XZD0 --payoff "stops a renamed CI job leaving pull requests \
  waiting forever on a check that can never arrive"
```

Presence is all `docket check` can hold it to: whether the line states a
consequence or restates the title is the judgment this project refuses to
script. So a payoff that says "faster" passes the checker and fails its reader,
and the reader is the project owner.

**Never let "it is what `docket next` returned" stand as the reason.** The
ranking is a sort over bands, placement and feature progress - it is not an
argument that this work is worth doing now, and reporting the sort as though it
were is what makes a queue feel arbitrary from outside. If you cannot say what
an item buys, that is a finding about the item rather than a licence to offer it
unexplained: say so, and offer the next one.

**Recommending off-gate work is allowed, and is never silent about being
off-gate.** Say what the gate says, then say why this goes first anyway. The
grounds are the ones this project already states, not a new list: a `P0`, which
precedes feature work by its own rule in
`.claude/skills/docket/modes/start.md`; `ROADMAP.md`'s own exception for a
finding that is `safety` or `science`, or whose problem predates the freeze;
and `CLAUDE.md`'s three compounding-friction tests — a check passing while the
guarantee it stands for is void, an advisory being routed around, something
sitting upstream of every other command. Being the obvious next step of the
conversation is **not** one of them, and neither is wanting to do it. Where
none of the grounds hold, the item is still worth naming — say plainly that it
is off-gate and let the owner weigh it, rather than dressing it as what the
step calls for.

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

**Where this session holds a claim on the item, the line carries the takeover
too**, because the fresh session's `bin/docket claim` would otherwise exit 3
behind this branch's claim for up to seven days. The owner pasting it is the
owner's word that `--over` needs, and the fresh branch then holds the item where
this one stood:

```text
PL-K7QX Decide what the interface shows after a halted step. Claim it with: bin/docket claim PL-K7QX --over claude/this-branch-name --reason "handed off by the session that held it"
```

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

**Read the tier, not merely the presence of a conflict.** Only "Cannot run
alongside" — a `blocked-by` edge — refuses the work. "Shares a file" and "Same
area only" are sequencing notes: both items are startable, and the smaller
change lands first. Treating a shared file as a refusal is what `PL-VRMK`
fixed, and it had already cost a real answer — Gate 1's science half all
declares `docs/MODEL.md`, so the whole of it read as unstartable at once.

The `<id>` form adds what the branches in flight have **already changed**,
read from the branches rather than from anybody's `touches`. That section is
the stronger evidence of the two — it fires only where work is underway, and it
names the file to open. Report the two separately for that reason, and do not
present a clean observed section as a clean answer: it means no branch has
touched these files *yet*.
