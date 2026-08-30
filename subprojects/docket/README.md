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
docket concurrent PL-K7QX    # what can be worked alongside it
docket feature halted-step   # progress on one feature
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

### Choosing is answered, not browsed

`docket next` ranks the work and says why it picked it. `P0` first, then —
*within* a priority band — work that finishes a feature already underway,
because a shipped feature is worth more than equal progress spread across
several. Work already in flight on a branch is excluded rather than ranked
low.

### Concurrency is computed, and honestly qualified

Each item declares the paths it expects to touch. `docket concurrent` reads
those as a conflict graph and reports what cannot run alongside what.

It reports in one direction only. Declared overlap proves two items will
contend. *Absence* of declared overlap proves only that nobody foresaw a
collision — the work may still wander into a shared file. So the command
rules pairs out and never certifies a pair as safe, and items declaring no
paths at all are reported as unanalysable rather than assumed harmless.

### The plan reports its own position

A queue answers "which item next". It cannot answer "what is the project
*doing* next", because that is settled by the roadmap and the roadmap is
prose. `docket wave` reads the parts of it that are not — the release train,
the milestone sections, and the debt list each one records when it is scoped —
and reports the version, the step, the gate's size and how much of it is
closed, and which beat of the cadence that leaves due.

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

Tags are deliberately outside that check. A shallow or tag-less clone is a
normal checkout, and a documentation check that fails on how somebody fetched
the repository is a check that gets switched off. `docket release` enforces
the tag instead, at the one moment tags are certainly to hand.

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
keep their files — `done` records the commit, `dropped` records the reason,
because a finding dropped without one gets raised again by the next person
who notices it.

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

`docket verify <id> --base <ref>` answers a narrower question than "do the
tests pass": did the work that claims to close this item stay inside what the
item declared? It runs the item's `verify` command and the project's own
check, and it reads the diff for the ways a green build can be reached
without doing the work — a file outside `touches`, a protected path, an edit
to the gate itself, an added suppression, a deleted assertion, a rewritten
front matter.

Several ids may be given at once — `docket verify PL-K7QX PL-B2B2 --base main`
— because that is the shape delegated work comes back in: one branch, one
commit per item. Each item's own command still runs per item, since that is
what makes one acceptable and the next rejectable, while the project's own
check runs once for the batch. It proves a property of the tree, and proving
the same property six times turns a two-second command into a two-minute one,
which is how a reviewer learns to skip it.

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
sitting in a band it is not allowed to sit in, a `done` item with no commit
recorded. These are errors and they exit non-zero.

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
