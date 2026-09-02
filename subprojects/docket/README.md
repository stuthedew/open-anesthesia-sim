# docket

A backlog for projects worked by sessions that start with no memory of the
last one.

Ordinary issue trackers assume the people using them remember things between
visits. When the work is done in bounded sessions — an AI coding session, or
a human with an hour between meetings — that assumption fails in two specific
ways, and `docket` is built around both.

**Nobody remembers why an item exists.** So every item carries a brief
written for a stranger: the problem, why it matters, where in the code, and
the condition that closes it. An item that cannot be started cold is a bug in
the item.

**Two sessions may be running at once.** So the store is one file per item.
Adding work adds a file, which cannot conflict with another branch's file,
and ids are random rather than sequential, so nothing has to be allocated
from shared state. There is no lock, because there is nothing to lock.

## What it does

```bash
docket new "The induction curve looks wrong" "Colour-blind palette check"
docket next --effort S       # what to work on, and why
docket wave                  # which beat of the plan's cadence is due
docket list                  # the queue, one line per item
docket triage                # what is untriaged, and the rules the answers must satisfy
docket concurrent PL-K7QX    # what can be worked alongside it
docket feature halted-step   # progress on one feature
docket gate --feature x      # the open debt a milestone has to clear
docket release v0.3.0        # verify, bump the version, write the notes
docket delegable             # what a cheaper model may work, and what proves it
docket verify PL-K7QX        # prove one item's work stayed in its commission
docket branch                # where this branch stands against the default one
docket flight                # which items a branch is already carrying
docket stranded              # items that exist only on a branch
docket check                 # validate the store; exits non-zero on errors
```

### Capture costs nothing

`docket new` takes a title and nothing else. No priority, no estimate, no
band — those are triage, and demanding them at the moment an idea occurs is
how ideas stop being written down. Several titles in one call, because
interruptions rarely carry exactly one thought.

### Capture is only unloseable if a lost branch is noticed

An item is committed on whatever branch the capturing session was on. If that
branch never merges, the item exists only there — and since every session
reads the store in its own checkout, nothing will ever mention it again. The
thought is lost as silently as if it had stayed in the conversation, which is
the one failure the store exists to rule out.

`docket stranded` reads it back off the branches: every item id present on
some ref and absent from both the default branch and this checkout, with the
`git checkout` line that brings each file back. The session digest carries the
same finding as one line, and only when there is one, because a session that
must be told its queue is incomplete cannot find that out by reading the queue.

**The comparison is by id and content, never by commit counts**, and that is
the design rather than an implementation note. A squash-merged branch contains
none of the commits it merged, so a containment test calls it unmerged forever
and reports everything on it as lost; a renamed item file was added twice and
deleted once, so a test over added paths reports the old name as lost. Reading
what the trees hold answers both: an id on the default branch is not stranded,
however its commits got there. It also means the check works in a shallow
clone, where every commit-graph question is unreliable — which is what an
agent session's container is.

The answer is bounded by the refs the checkout holds, so the count of refs read
is part of the output, and a checkout that can read none declines rather than
reporting a clean store. Read the other way, the report answers whether a
branch is safe to delete: a branch named nowhere in it carries no item the
default branch lacks. That claim is about items only. It says nothing about
code on the branch, which is not what it read.

### The branch's position is a question, not a session-start fact

`docket branch` reports where the working branch stands against the default
branch, names the command that repairs it, and lists the items that landed
while the branch sat.

It was fifty lines of bash in the session-start hook, and that was the whole
problem: a hook runs once, at session start, and the condition it guards
against develops *during* a session. A session opened to discuss the next piece
of work, while another session finishes something, is told its base is current
- and by the time the discussion becomes implementation, the other session has
merged. Nothing looks again, so the staleness surfaces at push time as a merge
conflict, which is the rework cycle the check exists to prevent.

So the decision lives in `vcs.py`, where a command can ask it at any moment and
a test can hold it to an answer, and the hook keeps only the half that has to
happen outside: the network.

**It prints; it does not act.** `git checkout -B` discards commits, so a check
that fired unattended would be a worse failure than the staleness it cures. Two
commands and no third: a branch behind with nothing of its own is restarted, a
branch behind with work of its own merges the base in. Rebase is deliberately
not offered - telling "only capture commits" from any other commits means
guessing, and a rebase of a pushed branch needs a force-push, which this
project's squash-merge path exists to avoid.

**The fork point is proven before the counts.** `git rev-list --left-right
--count A...B` does not fail on refs sharing no history: it prints the size of
each side, which reads exactly like a position. That state is reachable - a
`--depth` fetch re-truncates `origin/main`, and `.git/shallow` records it, so a
later ordinary fetch does not undo it - and a fabricated "98 ahead" argues
against merging in the very case the line exists to catch. So a clone that
cannot see the fork point is told to deepen instead of being given a number.

**The command fetches; the function does not.** `branch_state` reads only what
the checkout holds, because the rule the rest of `vcs.py` follows is that a
read must work from a bare checkout with no network. A command whose one
question is "has the base moved" would then answer "current" from a ref nobody
refreshed, so `docket branch` refreshes first and `--no-fetch` says not to -
and the line says which happened, rather than letting a stale answer look
fresh.

Where no comparison exists at all - a detached HEAD, no base, or the default
branch with no remote copy of it - `--brief` prints nothing. That is what the
hook passes, and this text is resent on every turn of a session, so a line
saying there is nothing to say is a line worth not printing. Asked directly,
the command says why.

**What asks it is the first edit.** A command nobody runs closes nothing, so a
`PreToolUse` hook on `Edit`/`Write` runs `docket branch --brief --if-stale`
once per session - at the moment a discussion becomes implementation, which is
the moment the answer is wanted. `--if-stale` is why it is bearable: a hook
that speaks unasked has to earn each line, and "your base has not moved" does
not. Two properties of that hook are easy to get silently wrong and are held by
tests: a `PreToolUse` hook's plain stdout reaches the debug log and nothing the
session can read, so the line travels as `additionalContext` in the documented
JSON form; and the JSON must not carry `permissionDecision`, which would
auto-approve the very edit it is attached to.

### In flight is read from the commits, not from the branch name

Two sessions may be running at once, so neither must start an item the other
is already implementing — and nothing records that one has. The fact is in git,
where a branch is already carrying the work: `docket flight` reads it back, and
`docket next` excludes what it finds.

The id is taken from **the front of the commit subjects**, and from the branch
name where it carries one. Reading names alone is what this replaced, and it
went blind in exactly the case it existed for. A session names its own branch
`claude/pl-k7qx-short-slug`, but a branch created for it by a web harness is
named from the opening prompt — `claude/roadmap-release-write-failure-nhsjwo` —
and cannot be renamed afterwards. One such branch sat with 22 commits of item
work on it while the command reported that nothing was in flight.

**Only a leading id counts.** A subject mentioning an item further in is
usually about somebody else's work — a capture, a close-out, a merge — and
counting those would make `docket next` skip an item that is *startable*, which
is a worse failure than the blindness being fixed. Measured over 120 commits of
this project's history: 79 subjects contained an id, 64 led with one, and every
one of the difference was bookkeeping rather than implementation. A subject may
lead with two ids, because one branch may carry two items, and then both count.

**A branch is finished when its content has landed, not when its commits
have.** The squash trap `stranded` describes above reaches this read from the
other side: a squash keeps the branch's content and none of its commits, so
`git branch --merged` calls the branch unmerged for as long as its ref exists
— and a checkout that has not pruned holds that ref indefinitely, reporting
every id at the front of one of its subjects as work somebody is still doing.
The same rule answers it. Each blob a candidate ref adds to the tree it forked
from is looked for in the default branch's history, and a ref whose every blob
has been there carries nothing that has not landed, however its commits got
there — squashed, rebased or cherry-picked.

**The history, not the tip.** Comparing that content against the default
branch as it stands now would un-land the branch the moment anyone edited a
file it had touched, which here is routine: the triage pass that follows a
capture rewrites the very file the capturing branch added, so the branch would
be back in the report one merge later. Asking whether the blob was ever on the
default branch does not decay.

A ref that adds no blob this checkout can read — no commits yet, only
deletions, or a fork point beyond a truncated clone's horizon — stays in the
report. Silence is not evidence of landing, and the two errors are not worth
the same: naming a merged branch is noise the reader can see through, while
dropping a live one hands its item to a second session, which is the collision
the whole read exists to prevent.

**The age is reported, not thresholded.** "Has an unmerged branch" and "is being
worked right now" are different claims and no timeout separates them: a branch
touched an hour ago is a live session, and the same branch three weeks later is
work nobody will merge. So each line carries the date of the branch's last
unmerged commit and the reader decides, the way `stranded` reports rather than
decides.

A ref whose merge-base with the default branch cannot be read is named as
unread rather than passed over silently. In a truncated clone — which is what
an agent session's container is — that means history the checkout does not
have, and walking such a ref would report everything it can see as that
branch's own work.

**A readable merge-base does not make the walk complete**, and that is a
second guard rather than the same one. `^origin/main` excludes only what the
checkout can reach *from* the default branch, and in a truncated clone that
history ends at a grafted commit — so anything below the graft goes
unexcluded. A branch reaching round it, which one merge of the default branch
into the branch is enough to do, then has the default branch's own commits
reported as its work and the ids leading their subjects reported as items
somebody is implementing. On 2026-08-31 that put twenty-seven ids in a
session's digest, under a line telling it not to start them again: eighteen
were closed, and one of the nine open was an entry of the release that same
session had just been asked to finish.

So the walk is checked as well as the merge-base. It has to stop against a
commit the default branch accounted for, never because the checkout ran out of
history, and a commit with no parents in this checkout is the signature of the
second — a grafted boundary, or a root the default branch should have
excluded. A ref whose walk ends that way is named as unread rather than
believed, on the same reasoning as everything else here: the ids it produced
would be *removed* from `docket next`, so believing a walk that cannot be
checked hides startable work, while naming the ref costs a line of output.

**And the naming reaches wherever the queue is read**, not only `docket
flight`. The seven answers that rank or mark against in-flight work — `next`,
`list`, `status`, `concurrent`, `delegable`, `show` and the session digest —
took the ids alone, and a `set[str]` cannot carry "and one ref went unread": the same
checkout that told `flight` it could not read a ref told `next` that the queue
was fully known. So they take the whole `FlightReport` and read `ids` off it,
which keeps the gap in the caller's hands and puts one sentence under every
answer:

```
1 ref could not be compared with origin/main on the history this checkout
holds, so any item its commits carry is missing here; `bin/docket flight`
names it.
```

`show` is the newest of the seven and arrived last for a reason worth
recording: the exclusion itself lives in `plan.recommend`, so it reached a
session only through `next`. An item named by the project owner skips `next`,
and `triage`, `check` and reading the file directly all said nothing — so the
guard against two sessions doing one item was applied only on the path where a
person had *not* chosen the work. Marking it in `show` is the smaller half of
that repair; the larger half is prose, in the `docket` skill, because a session
handed an item is not obliged to run any command at all.

Neither half reaches the network. Only `docket branch` calls `fetch_remote`, so
`flight` and `show` answer from the refs this checkout already holds — which is
what lets them answer in a bare or offline tree, and what makes a fetch the
caller's business before the question is worth asking.

It still reports rather than refuses, for the reason the rest of this read
does: a ref past a truncated clone's horizon is the ordinary state of an agent
session's container, not an error in it.

**What went unread is the ref's commits, and its name is read either way.**
The two reads need different evidence and only one of them needs history:
`^origin/main` can exclude the default branch's own work only where the
checkout holds it, while `claude/pl-k7qx-short-slug` names its item in a
checkout holding nothing at all. So an unread ref still contributes the id its
name proves, and still appears in the block above for the ids its commits
might have added — one ref, in both halves of the answer, neither line
claiming what the other says.

That cuts against the direction of the two guards, deliberately, and the
difference is what is being believed. A guard refuses an id *inferred* from a
walk the history could not support, where being wrong withholds a startable
item under the digest line telling a session not to start it again. A branch
name proves its id outright,
and what stays open is only whether the branch has landed — the cheaper
uncertainty, because an item whose work landed is closed and never offered
anyway, while dropping the id offers an item a live session is holding.

### Triage is a worklist, not a verdict

`docket triage` prints every untriaged item with its body, the fields still
unset, the brief sections still missing, and the rules the answers have to
satisfy — which classes force the top band, how full that band already is,
which paths make an item undelegable, what a `ready` item must carry. Those
are read from the settings and the checker, so they cannot drift from what
`docket check` will say a moment later.

What an item is worth, how big it is and what it belongs with are not computed
and never will be. Triage is the judgment; what the command removes is having
to recall the rules from memory and find out afterwards whether the recall was
right.

### Choosing is answered, not browsed

`docket next` ranks the work and says why it picked it. `P0` first, then what
the roadmap's current step includes, then — *within* a priority band — work
in a feature already underway, the one nearest finishing first, because a
shipped feature is worth more than equal progress spread across several. Work already in flight on a
branch is excluded rather than ranked low.

The step's scope is preferred *absolutely* rather than as a tie-breaker inside
a band, because the priority field cannot express the phase: `docket check`
pins `safety` and `science` items to `P1`, so the top band is product work by
construction and a tie-breaker there would never fire in the case the rule
exists for. `P0` sits above it: a hotfix outranks the phase.

The session digest's `Top:` line is that same answer, from the same ranking
against the same plan, because the two lines a session reads first have to
agree. It was a sort of the store by priority alone, which opened every
session with v0.4.0 science work two lines above a beat saying clear v0.2.8's
gate, and left the reader to work out which of them knew about the plan.
Deriving it from the plan the digest already carries is what makes that
disagreement unrepresentable rather than merely fixed.

### What a milestone places, and what it only mentions

The scope above is read from two structures of a milestone's own section and
nothing else: the entries of the frozen list it records, and its `Required
scope`. An id one of those places, in the milestone the current beat is about,
is work the step includes; an id only a *later* milestone places is marked
with that milestone (`scoped to v0.4.0, not this step`) and ranked below it;
an id neither places is neither: it carries no mark, and sits between the two
in the ranking. That silence is deliberate — most of a queue is placed
nowhere, and reading it as exclusion would be a verdict rather than a fact.

*Where* an id is written decides this, never the fact that it is written. A
section names ids for at least four reasons — an entry of its frozen list,
scope the milestone clears itself, commentary on an entry ("blocked by
`PL-ZQ9C` above"), and an exclusion set out at length ("`PL-68XK` … is *not*
admitted by this rule") — and only the first two are membership. Counting
every mention read those exclusions as the opposite of what they said, so each
structure is read by its own grammar instead:

- the frozen list, by its entries' heads — an entry is one bullet per problem,
  and an id later in the sentence is prose about another item;
- `Required scope`, in full — a milestone names what it covers in whatever
  grammar the sentence wanted, `(queue item PL-DHV7)` mid-bullet or a
  paragraph, and the heading has already said that everything under it is
  scope.

Out-of-scope work is marked, never hidden. Whether an item is *really* out of
scope is a judgment about the prose around its id, and the command reads
structure rather than sentences.

Three things follow, and they are limitations in the same way the concurrency
answer below is:

- Scope recorded *only* in a section's prose is placed nowhere. Printing the
  id inside `Required scope` is what places it.
- An exclusion is invisible rather than reported, a milestone's own
  `Explicitly out of scope` list included. Silence is the honest answer to a
  sentence the command cannot read, and the safe one: an unread mention makes
  no claim, where an over-read one told a session that work a milestone
  excludes was the work that milestone was waiting on.
- A released milestone's section places nothing. Its narrative records where a
  problem was raised, not what is current work.

### Concurrency is computed, and honestly qualified

Each item declares the paths it expects to touch. `docket concurrent` reads
those as a conflict graph and reports what cannot run alongside what.

It reports in one direction only. Declared overlap proves two items will
contend. *Absence* of declared overlap proves only that nobody foresaw a
collision — the work may still wander into a shared file. So the command
rules pairs out and never certifies a pair as safe, and items declaring no
paths at all are reported as unanalysable rather than assumed harmless.

### A debt gate is computed, not transcribed

A project that clears recorded debt before starting a milestone has to produce
the list of what is owed, and doing that by hand means reading every open
item's classes and status, applying the rule, and splitting the result by
whether the milestone clears the item itself. `docket gate --feature <name>`
does that pass: open debt on one side, the items carrying that feature on the
other, with effort totals for each.

Debt is an open item classed `defect`, `safety`, `science`, `refactor` or
`perf` — `debt_classes`, configurable — or one at `needs-decision`, since a
decision left open stops being one anybody can make. It writes nothing and
reaches no verdict: whether an item is really debt and whether the gate should
open are judgments, and freezing the list stays the deliberate act it is meant
to be.

### The plan reports its own position

A queue answers "which item next". It cannot answer "what is the project
*doing* next", because that is settled by the roadmap and the roadmap is
prose. `docket wave` reads the parts of it that are not — the release train,
the milestone sections, and the debt list each one records when it is scoped —
and reports the version, the step, the gate's size and how much of it is
closed, and which beat of the cadence that leaves due.

The beat and the step also ride in `docket digest`, as one line. A command
nobody runs unprompted does not change where "what next" gets answered from,
and the queue nags every session while a roadmap nags none. One line is the
whole budget: the digest is resent on every turn of a session, and a plan
that cannot be read at a glance is one more thing to scroll past. An
unreadable roadmap produces no line at all rather than a guessed step.

It computes; it decides nothing. Whether the prose beside a timeline row is
still true, whether a gate should open early, whether a scoped milestone is
scoped *well*: none of that is on the page in a form a parser can read, so
none of it is attempted.

### Releases are mechanical

A milestone is a version and the items in it. `docket release` refuses to
ship one whose work is unfinished, then bumps the single version string,
writes the notes from the items themselves, and stops short of tagging.
Generated notes cannot claim something the items do not, and nothing shipped
goes unmentioned because whoever wrote them forgot it.

**A release writes all of itself or none of it.** Two things reach disk — the
`milestone:` stamp on every item going out, and the version — and neither
order is safe while the bump can still fail on the file it is about to
rewrite. Stamping first left the store recording a release that never
happened, with nothing saying which stamps to unpick; the next run then
reported nothing to release, because the work it would have shipped claimed to
have shipped already. So `prepare_bump` settles everything the bump can reject
— an absent version file, one carrying no version field — before the first
stamp is written, and hands back the text to put there. What a rejected file
costs is then an exit code and a message naming it, rather than a half-written
store.

**The offer a session reads is reconciled with the plan before it is
printed.** `readiness` reads the store and only the store, which is what
makes it honest about what is finished and blind to what a number *means*:
the version it arrives at is arithmetic on the last one, and a project that
plans in versions has usually spent that number already. Cutting it then is
not a smaller release than the plan's — it is the plan's milestone going out
under its own name with most of it missing, which a tag makes permanent. So
`release.release_offer` puts the suggestion beside `wave`'s current step:
where the step already holds that version and is unfinished, the digest
withholds the offer and names the step holding it; where the plan is itself
asking for a release, the digest offers the version the roadmap named rather
than the one a class label inferred. The digest's release line and its plan
line can no longer recommend opposite actions.

**What a release deliberately does not write is the roadmap.** A project that
keeps a version table in a hand-maintained plan will find it left behind by
every release — twice here, the second time one release after the first was
repaired. The fix is a check that refuses, not a command that writes: the
milestone column is editorial, so a generated row would either be thin or
would overwrite something considered, while a refusal costs one hand-written
row per release and cannot corrupt the file. `roadmap.parse_version_table` and
`roadmap.baseline_heading` read the grammar; the project's own checker asks
the three questions that follow from it — one row per released version,
exactly one marked current, and a "Current baseline:" heading naming that same
version, which is the version the version file holds.

Not writing it is not the same as not mentioning it. Refusing later is only
useful if somebody knows what is owed now, so `release` ends by reading the
roadmap through those same two parsers and printing the statements the cut has
just made stale, each with its line number
(`release.outstanding_roadmap_edits`). A command that stops mid-sequence
without saying where it stopped leaves the next one — the project's own check —
to report the omission as a failure nobody caused, which is how a red check
comes to look like the normal end of a release.

Tags are outside that check, and inside the project's own. A tag-less clone is
a normal checkout, so nothing about tags may be concluded from a repository
that cannot answer — `vcs.tags` collapses no git, no repository and no tags
alike to an empty set, and a checker reading it says nothing rather than
reporting every release as untagged.

A **shallow** clone was assumed to collapse the same way and does not: it holds
the tags reachable within its depth and omits the rest, so every release older
than that depth reads as never tagged (`PL-J295`). `vcs.is_shallow` tells the
two apart. The rule built on it is deliberately narrower than "decline in a
shallow clone" — every environment this runs in clones shallow, the session
container and `actions/checkout` alike, and one that has since run `git fetch
--tags` can answer exactly. So the findings are computed first and withheld
only when there is one *and* truncation could account for it. A tag being
**present** is never in doubt, so the conclusions drawn from that stand either
way.

What the check does say, when it can, is which completed releases carry no tag
and which tags name no release. `docket release` still enforces the tag at the
one moment tags are certainly to hand: it refuses to cut the next release while
the current one is untagged.

## The item format

One file per item, markdown with a small front-matter block. Front matter is
what the tool reads; the body is what a person reads. Keeping both in one
file means the machine-readable state and the human-readable brief cannot
drift apart, and both arrive in a diff for review.

```markdown
---
id: PL-K7QX
title: Decide what the interface shows after a halted step
priority: P1
effort: S
status: needs-decision
classes: safety, ux
feature: halted-step
touches: src/app/simulation_view.py
added: 2026-08-24
---

**Problem.** What is wrong or missing, concretely.
**Why it matters.** The consequence of leaving it.
**Where.** The files or modules involved.
**Decision needed.** The question blocking the work.
**Done when.** The observable condition that closes it.
```

`**Problem.**`, `**Why it matters.**` and `**Done when.**` are required once
an item leaves `untriaged`; the others are conventions. A heading is matched
by the words it opens with and may continue past them — `**Why it matters, and
why it is not new.**` is the same section, and a check that made an author
flatten a better heading would be editing prose rather than checking it. What
it does require is text under the heading: a required section with nothing
below it is an error, because presence of a heading is not what makes an item
startable by a stranger.

Two further fields govern whether the work may be handed to a cheaper model:
`verify`, a single-line command that proves the item done, and `not-delegable`,
holding the reason an otherwise-qualifying item is withheld. See *Delegation is
derived, never granted* below.

An item at `ready` must carry one of them: the command that would prove it
done, or a recorded reason why no command can. The gate sits at `ready` rather
than at capture deliberately — demanding a command at the moment an idea occurs
is the same tax as demanding a priority, and `ready` is the first point at
which the question is answerable at all. `verify_required_from` is the date a
project adopts the rule; items captured before it raise a grooming advisory
rather than an error each, so adopting the rule does not mean rewriting the
whole store on the same day. The advisory names only the ones `next` is about
to offer, and carries the number still outstanding: naming the whole backlog
made it an advisory that could not reach zero, and the cost of one of those is
not the items it names but the next advisory, which is then read the same way.
It also puts the command where it can be run before it is written, since the
moment an item is offered is the first moment there is anything to run. Leaving that setting unset
leaves the requirement off, which is right for a project that does not delegate
and therefore has nothing riding on the field.

Write the command only after running it. Every one of the six that existed in
the project this grew in was wrong and none had been executed — a check nobody
ran is a specification nobody tested, and it fails after a worker has done the
work rather than before.

`status` runs `untriaged` → `ready` / `needs-decision` / `blocked` → `done` /
`dropped`. Requirements scale with it: an untriaged capture needs only a
title and a body, while anything past that is a commitment to do work and is
held to the standard that lets someone else pick it up cold. Closed items
keep their files — `done` records where the work landed, `dropped` records the
reason, because a finding dropped without one gets raised again by the next
person who notices it.

### `milestone:` records where work went out, never where it is planned

`docket release` stamps `milestone:` onto the items it ships, and that is the
whole of what the field means. Nothing else writes it. An item carrying one
before its release is cut claims to have shipped in a release that has not
happened — and worse, silently: `release.unreleased` selects finished work
with **no** milestone, so a stamped item is invisible to the release that
would actually ship it and is left out of that release's generated notes. Ten
items in the project this grew in were in exactly that state, hand-stamped for
a release still being assembled, every one of them scoped to the release its
own notes would have omitted it from.

The other thing the field is tempting to record — *this item is scoped to the
next release* — has a home already: the gate subsection of that milestone's
section in the roadmap, which `docket wave` parses and which is the only thing
deciding membership. One field cannot carry both meanings, because they demand
opposite timing. Shipped-in must be absent until the release is cut;
scoped-to must be present from the moment the list is frozen.

So `docket check` refuses both shapes of the wrong one: a `milestone:` on an
item that is not `done`, and a `milestone:` naming a version above the
project's current one. Where either side is not `major.minor.patch` — a
project versioning by date, a release named `v1.0-rc1` — the comparison is not
made rather than guessed at.

### Provenance survives the merge strategy

A closed item's whole traceability is the pointer from it to the work: it is
how a reader gets from "the interface rounds to two decimals" to the reasoning
that chose two. Two fields carry it, and they fail in different ways.

`commit` names the branch commit. It is exact, and it stops being resolvable
the moment a project squash-merges: the squash puts a *new* commit on the
default branch and deleting the head branch makes the one the item names
unreachable. It also cannot be recorded by amending the commit it names,
because amending changes the hash — so it is written after the fact, which is
how a hash that resolves nowhere gets in.

`pr` names the pull request, as a bare number written without the `#`. It is
unaffected by rebasing, squashing or amending, and GitHub writes it into the
subject of whatever reaches the default branch — `Merge pull request #71 from owner/branch` for a merge commit,
`Title (#71)` for a squash — so the link back is free either way.

So `check` holds a recorded pull request to one the default branch has
actually seen, and two cases are deliberately passed over rather than
reported:

- **A number above the highest one on the default branch.** An item is closed
  on the branch that carries it, so at the moment `check` first reads the
  number, that pull request has not merged. Numbers past the high-water mark
  are not-yet-merged rather than wrong.
- **Anything at all, in a shallow clone.** `git log` in a truncated history
  answers confidently and wrongly, and the commits it is missing are the
  oldest ones — so the best-established provenance in the store is what would
  be reported as broken. This matters more than it looks: the container an
  agent session runs in is normally shallow.

A shallow checkout is a worse condition than a bare one, and the difference
shapes how it is reported. In a bare checkout git cannot answer and every read
in `vcs.py` already collapses to silence. In a shallow one git answers, so
`merged_pull_requests` returns a `PullRequestHistory` that carries *why* it
declined instead of a set that cannot be distinguished from "this project uses
no pull requests". `check` then prints a third section beside the errors and
the advisories:

```
docket: 71 open (…), 0 errors, 1 advisory, 1 not checked

Not checked (this checkout cannot answer; nothing is claimed):
  recorded pull requests: the checkout is a shallow clone, so the commits it
  is missing are the oldest ones and the longest-settled provenance would
  read as broken
```

The count is on the headline because the headline is what a reader takes
away, and "0 errors" from a run where a check never ran says the store is
sound when nobody looked. Deepening the checkout is deliberately *not* the
fix: `check` runs from a bare tree with no network, and fetching here would
trade that away to answer a question the caller can simply skip.

What is left is the case worth failing on — a number inside the range the
default branch covers that no commit there names, which is a typo or an
invention.

So a *landed* `done` requires `pr`, and `commit` is optional beside it. The
requirement carries no cutover date, because there is nothing to cut over
from: the store this grew in had every one of its 66 closed items backfilled
in a single pass, each number derived from the commit on the default branch
that first contained the recorded hash. A dated exemption is a leak that has
to be remembered forever; a backfill is one commit.

### When the `pr` is owed

"Landed" is load-bearing, and it was learned the hard way. The number does not
exist until the pull request is open, so an item cannot be closed in the same
commit as the work it closes *and* carry it. Requiring it unconditionally
forced the closure into a second push, and a merge arriving inside that window
took the work and left the closure on the branch: the default branch had the
fix while the store still called the item open and a debt gate still counted
it. The window was 100 seconds wide the once it was measured, and it was open
on every item.

`closures_on_base` reads whether each closure in question already stands on
the default base, and `check` owes a `pr` only for those. A closure that is
`done` only in the working tree is still in flight, which is the expected
shape rather than an error — so the closure travels in the same commit as its
work and there is nothing left for a merge to strand.

Whether a closure *landed* does **not** decline in a shallow clone, unlike
`merged_pull_requests`. That reader needs history, which a truncated one
answers confidently and wrongly; this needs a single tree read, and `git show
<ref>:<path>` is correct however little history stands behind the ref. Since an
agent session normally runs shallow, a reader that declined there would decline
in exactly the case the rule exists for. It declines only when no default
branch resolves at all.

Which pull request landed it is the other kind of question, and the depth does
bear on it — see below.

What is left over is not a gap. An item reaching the default branch with an
empty `pr` is the *normal* shape of a successful merge, not an exception:
the closure travels with its work, and the number does not exist when that
commit is written. So `check` asks a second question before deciding what it
has found — does any commit on the base name a number for this item?

`closures_on_base` answers it from the subject a squash merge writes,
`PL-JWXF Scope the selects-no-test advisory ... (#148)`, using the two
parsers already here: the run of ids a subject opens with, and the number in
trailing parentheses. One history read for the whole set, taken only when
something landed, and the newest such commit wins — an id also leads the
capture that filed it.

- **The number is recoverable** → an advisory naming it and the line to
  write. Nothing is lost; the way back exists in git, and the field is a
  transcription still owed so the item file carries it too. True at any
  depth: finding the commit is proof it was there to find.
- **No commit names one, in a checkout that says it is complete** → the error
  it always was. That is provenance genuinely lost.
- **No commit names one, in a truncated checkout** → a decline naming the
  ids. The commit may simply be out of reach, and at `fetch-depth: 1` that is
  true of every closure but the newest, so absence proves nothing. `is_shallow`
  answering neither way is treated the same, per the rule `PL-J295` set for
  `tags`.

Erroring on the first case meant `main` went red on the completion of every
item, which trains a reader to treat a red store check as routine — the
opposite of what the loudest signal here is for. Erroring on the third meant
it went red one merge *later* instead, which is worse: nothing about the
provenance had changed between the green run and the red one, only what the
clone could see, so the failure pointed at an item that was not at fault
(`PL-99Y4`). The check therefore runs for real only where the history is
whole, which is what `fetch-depth: 0` in a CI checkout is for.

### An open item whose own command already passes

Closing an item is a hand edit, so work that merges without `status` being set
leaves the item `ready` for good. Nothing notices: it keeps its place in
`next`, `wave` and `gate` count it open, and the next session picks it up and
re-derives what is already on `main` before finding out. Four instances are
known — `PL-XCYB`, `PL-ZQ9C`, `PL-1TPM` and `PL-0RS6`, the last two squashed in
one pull request — and every one was caught by a person rather than by a check.

The obvious signal is an item id at the head of a commit subject on the default
branch, and it was measured and rejected: of the thirteen open items whose id
led such a subject, eleven were capture or triage commits ("PL-8HJ2 Capture
that make release always ends in a red test") and two were implementations. An
advisory wrong five times in six is one every session learns to skim past.

So `check` runs each open item's own `verify:` command instead — the item's own
statement of what would prove it done — and reports the ones that pass. Scoped
to `ready` and `needs-decision`, and to `check` alone: it is the only check
here that *executes* the project rather than reading it, and `next` and the
digest are asked on every session start.

**It names candidates, never a verdict**, because a passing command is
consistent with two findings no exit status can separate:

- the work landed and nobody set `status: done`; or
- the command does not discriminate — it would have passed before the work
  too, so it proves nothing and the item's commission is unprovable.

Both want a person, and both close: the first by closing the item, the second
by giving it a command that fails until its work exists. Run against this store
on 2026-09-01 the second reading was every one of the eight it named, which is
why the wording leads with the possibility rather than the conclusion.

One part of that *is* decidable. A command recorded against more than one open
item cannot be proving any single one of them done, whatever it returns, so
those are named separately and with certainty — five of the eight shared
`python3 tools/doc_check.py check`, which passes whenever the docs are
internally consistent and says nothing about any particular item.

Two conditions decline rather than answer, for the reason
`merged_pull_requests` declines on a shallow clone — an empty result meaning
"could not look" must never render as "looked, found nothing":

- **A nested run.** Two open items record commands ending in `bin/docket
  check`. Unguarded, the outer run would re-enter itself once per candidate and
  each re-entry would do it again, so children are given `DOCKET_SKIP_LANDED`
  and skip this one question while still validating the store.
- **Nothing could be executed.** Every command returning "not found" is what a
  bare checkout with no virtualenv looks like from here, and is indistinguish-
  able from a clean store unless it is reported as a refusal.

It costs what the commands cost: 29 candidates, about 17 seconds, on the store
as it stood on 2026-09-01. Each command is capped at two minutes so one wedged
run cannot hang `make check`.

### Delegation is derived, never granted

Work that a cheaper model can finish should go to one; work whose correctness
rests on judgment should not. `docket` decides which is which from the item
itself rather than from a label somebody applied.

An item is delegable when all of: its `status` is `ready`; `model_guidance` is
silent, which excludes safety- and science-classed work and open decisions by
the rule that already governs model choice; it names a `verify` command; its
`touches` is declared and lies wholly outside `protected_paths`; and its effort
is `S` or `M`.

There is no `delegable: yes`. The only writable control is `not-delegable`,
which withholds an item that would otherwise qualify, so delegability can be
taken away by hand and never granted by hand — a worker editing its own front
matter can at worst refuse itself work. That asymmetry is the safeguard; a
boolean flag would be a thing that could be set wrong, and set wrong in the
permissive direction.

`protected_paths` is the list a delegated item may never modify, whatever its
check proves. A delegated item may add tests *about* those paths and may never
edit them. The partition is absolute rather than overridable by a sufficiently
good check, because "good enough" would be relitigated per item and the items
where it would be relitigated are the consequential ones. It defaults to empty,
and that default disables delegation entirely rather than permitting it
everywhere: a project that has not said which of its files matter has not
earned an unguarded lane.

A `verify` command bounds what "done" means; it does not prove the work is
right. It can be satisfied by the wrong route — a weakened assertion, an added
suppression, an edit to the check itself. What makes the pair trustworthy is
the check *plus* the declared scope, which is why an item naming a `verify`
command and no `touches` is a validation error rather than a delegable item.

### Verification is scoped, not just green

`docket verify <id>` answers a narrower question than "do the tests pass":
did the work that claims to close this item stay inside what the item
declared? It runs the item's `verify` command and the project's own
check, and it reads the diff for the ways a green build can be reached
without doing the work — a file outside `touches`, a protected path, an edit
to the gate itself, an added suppression, a deleted assertion, a rewritten
front matter.

Several ids may be given at once — `docket verify PL-K7QX PL-B2B2` — because
that is the shape delegated work comes back in: one branch, one
commit per item. Each item's own command still runs per item, since that is
what makes one acceptable and the next rejectable, while the project's own
check runs once for the batch. It proves a property of the tree, and proving
the same property six times turns a two-second command into a two-minute one,
which is how a reviewer learns to skip it.

The base defaults to the first of `origin/main`, `origin/master`, `main` or
`master` that resolves, and the remote refs come first deliberately. A session
that starts from a fresh clone holds a local `main` frozen at whatever it was
cloned at, so a diff taken against it reports every file merged in the
meantime as this branch's own work: one real run named 20 paths outside the
item's commission where the true answer was 4. `--base <ref>` overrides it,
and a base behind its own remote is said so at the top of the report rather
than left to be read as clean.

The diff is scoped to the commits whose subject names the item, which is what
one-commit-per-item buys: a batch branch carries several items' work, and each
is judged on its own. Uncommitted changes are attributed to whatever is being
verified rather than excused, and a base with nothing between it and `HEAD` is
a failure rather than a vacuous pass.

What it does not decide is whether the work is *right*. A new test can
exercise the intended line and assert the wrong value, and nothing here can
tell. The report says so on every run, because a tool that implied otherwise
would be worse than no tool.

## What is checked, and what is left alone

Everything mechanically decidable is decided by code: a duplicate id, a
blocker that is not an item, a brief section that is missing or that has
nothing written under its heading, a safety-classed item
sitting in a band it is not allowed to sit in, a `done` item recording a pull
request the default branch has never seen. These are errors and they exit non-zero.

Everything requiring judgment is left alone. The tool will tell you the top
band has grown past what anyone can choose between at a glance, that most of
it is blocked on decisions nobody has made, or that an open item's own
`verify:` command already passes — but it will not tell you what to work on
instead, it does not close the item whose command passed, and it does not try
to decide whether an item is still worth doing. A tool that guessed at that
would produce output that looks authoritative and is not.

## Configuration

Everything has a working default; a project needs no config file. To change
the defaults, add `docket.toml` at the project root:

```toml
[docket]
items_dir = "docs/items"
safety_classes = ["safety", "science"]
process_classes = ["session-cost", "docs", "infra"]
debt_classes = ["defect", "safety", "science", "refactor", "perf"]
top_band_limit = 5
untriaged_stale_days = 14
verify_required_from = 2026-08-30   # omit to leave the `verify:` rule off
minor_classes = ["feature"]
protected_paths = []
version_file = "pyproject.toml"
roadmap_file = "ROADMAP.md"
```

## Requirements

Python 3.11 or newer, and nothing else. Standard library only, so a
session-start hook can run it in a bare checkout with no virtualenv and no
install step.
