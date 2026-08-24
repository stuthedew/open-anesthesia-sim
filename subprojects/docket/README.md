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
docket list                  # the queue, one line per item
docket concurrent PL-K7QX    # what can be worked alongside it
docket feature halted-step   # progress on one feature
docket release v0.3.0        # verify, bump the version, write the notes
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

### Releases are mechanical

A milestone is a version and the items in it. `docket release` refuses to
ship one whose work is unfinished, then bumps the single version string,
writes the notes from the items themselves, and stops short of tagging.
Generated notes cannot claim something the items do not, and nothing shipped
goes unmentioned because whoever wrote them forgot it.

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

`status` runs `untriaged` → `ready` / `needs-decision` / `blocked` → `done` /
`dropped`. Requirements scale with it: an untriaged capture needs only a
title and a body, while anything past that is a commitment to do work and is
held to the standard that lets someone else pick it up cold. Closed items
keep their files — `done` records the commit, `dropped` records the reason,
because a finding dropped without one gets raised again by the next person
who notices it.

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
minor_classes = ["feature"]
version_file = "pyproject.toml"
```

## Requirements

Python 3.11 or newer, and nothing else. Standard library only, so a
session-start hook can run it in a bare checkout with no virtualenv and no
install step.
