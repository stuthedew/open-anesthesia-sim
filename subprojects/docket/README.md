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
docket check                 # validate the store; exits non-zero on errors
```

### Capture costs nothing

`docket new` takes a title and nothing else. No priority, no estimate, no
band — those are triage, and demanding them at the moment an idea occurs is
how ideas stop being written down. Several titles in one call, because
interruptions rarely carry exactly one thought.

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
that finishes a feature already underway, because a shipped feature is worth
more than equal progress spread across several. Work already in flight on a
branch is excluded rather than ranked low.

The step's scope is preferred *absolutely* rather than as a tie-breaker inside
a band, because the priority field cannot express the phase: `docket check`
pins `safety` and `science` items to `P1`, so the top band is product work by
construction and a tie-breaker there would never fire in the case the rule
exists for. `P0` sits above it: a hotfix outranks the phase.

### What a milestone names, and what it does not

The scope above is read from one fact and no others: an item id printed in a
milestone's own section of the roadmap. An id named in the milestone the
current beat is about is work the step includes; an id named only in a later
milestone's section is marked with that milestone (`scoped to v0.4.0, not this
step`) and ranked below it; an id named in no section at all is neither: it
carries no mark, and sits between the two in the ranking. That silence is deliberate — most of a queue is placed
nowhere, and reading it as exclusion would be a verdict rather than a fact.

Out-of-scope work is marked, never hidden, for the same reason. Whether an
item is *really* out of scope is a judgment about the prose around its id, and
the command reads ids rather than sentences.

Three things follow, and they are limitations in the same way the concurrency
answer below is:

- A milestone that excludes something in prose alone excludes it invisibly
  here. No id, no marking.
- An id named in a later section for *any* reason reads as that milestone's
  scope — including a sentence deferring the item *out* of it.
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

Tags are outside that check, and inside the project's own. A shallow or
tag-less clone is a normal checkout, so nothing about tags may be concluded
from a repository that cannot answer — `vcs.tags` collapses every such failure
to an empty set, and a checker reading it says nothing rather than reporting
every release as untagged. What it does say, when git can answer, is which
completed releases carry no tag and which tags name no release. `docket
release` still enforces the tag at the one moment tags are certainly to hand:
it refuses to cut the next release while the current one is untagged.

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

Two further fields govern whether the work may be handed to a cheaper model:
`verify`, a single-line command that proves the item done, and `not-delegable`,
holding the reason an otherwise-qualifying item is withheld. See *Delegation is
derived, never granted* below.

An item at `ready` must carry one of them: the command that would prove it
done, or a recorded reason why no command can. The gate sits at `ready` rather
than at capture deliberately — demanding a command at the moment an idea occurs
is the same tax as demanding a priority, and `ready` is the first point at
which the question is answerable at all. `verify_required_from` is the date a
project adopts the rule; items captured before it are counted in one grooming
advisory rather than turned into an error each, so adopting the rule does not
mean rewriting the whole store on the same day. Leaving that setting unset
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

`pr` names the pull request, as a bare number written without the `#`. The
number is allocated before the merge, so it can be recorded in the same commit
as the closure rather than after it; it is unaffected by rebasing, squashing
or amending; and GitHub writes it into the subject of whatever reaches the
default branch — `Merge pull request #71 from owner/branch` for a merge commit,
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

So `done` requires `pr`, and `commit` is optional beside it. The requirement
carries no cutover date, because there is nothing to cut over from: the store
this grew in had every one of its 66 closed items backfilled in a single pass,
each number derived from the commit on the default branch that first contained
the recorded hash. A dated exemption is a leak that has to be remembered
forever; a backfill is one commit.

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
blocker that is not an item, a missing brief section, a safety-classed item
sitting in a band it is not allowed to sit in, a `done` item recording a pull
request the default branch has never seen. These are errors and they exit non-zero.

Everything requiring judgment is left alone. The tool will tell you the top
band has grown past what anyone can choose between at a glance, or that most
of it is blocked on decisions nobody has made — but it will not tell you what
to work on instead, and it does not try to decide whether an item is still
worth doing. A tool that guessed at that would produce output that looks
authoritative and is not.

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
