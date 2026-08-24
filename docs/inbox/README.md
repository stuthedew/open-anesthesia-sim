# Inbox

The capture channel for a thought that arrives while something else is in
flight.

`docs/PUNCH_LIST.md` is the queue. This directory is the doorstep: one file
per captured thought, dropped here the moment it is raised, triaged into a
punch-list entry later. Nothing is ever meant to *live* here.

## Why the queue is not written to directly

A punch-list entry is a bad thing to write from a session that is in the
middle of something else, for two reasons that have nothing to do with how
good the entry is:

- **Every entry lands in one file, at a position chosen by priority.** Two
  branches adding entries in the same band produce a textual merge conflict
  in `docs/PUNCH_LIST.md`, and resolving one by hand is exactly the moment an
  item gets silently dropped.
- **Ids are allocated as "one past the highest in the file".** Two branches
  that allocate concurrently both pick the same number, and neither notices
  until they meet. `python3 tools/punch_list.py check` catches the duplicate
  after the merge, which is later than it should be caught.

A note here has neither property. It is a new file, so it cannot conflict
with a note another branch added, and it carries no `PL-` id, so there is
nothing to race for. That is the whole design: **capture is unconditional and
immediate; only triage is serialized.**

The alternative — holding the thought in conversation until the current work
lands — is the one option that is actually unsafe. A session's container is
ephemeral, so an uncommitted thought is a lost thought, and `CLAUDE.md`'s
capture rule exists precisely because that has happened.

## Format

One file per note, named `YYYY-MM-DD-short-slug.md`, where the date is the
day it was captured. The date leads the name so that notes sort by age and
so that age survives a re-clone, which an mtime does not.

```markdown
# Short imperative title

`P2` · `S` · `ux`

**Problem.** What is wrong or missing, concretely.
**Why it matters.** The consequence of leaving it. Name the safety or
scientific-correctness implication when there is one.
**Where.** The files or modules involved, if known.
**First step.** The specific action that starts the work.
**Done when.** The observable condition that closes it.
```

Only the title and a body are required. The metadata line is a *proposed*
band, recorded because the capturing session had the context and the triaging
session will not; triage decides the real one, and may demote something else
in the process. Omit the line entirely rather than guessing.

A half-formed thought is still worth capturing. Write it as a note that says
what was actually observed and what is not yet known, rather than inventing a
brief around it — an entry that reads as actionable when it is not costs a
later session more than a note that admits it is a lead.

`python3 tools/punch_list.py check` validates the title, the body, and the
filename's date, lists what is pending, and raises a grooming advisory once a
note has sat here for more than two weeks.

## Triage

The punch-list skill's "Mode: triage the inbox" covers it: allocate the id,
place the entry in its real band, delete the note in the same commit. A note
that has become an entry and a note that was decided against both leave this
directory — the second one leaves a line in the punch list's `Archive` with
the reason, because an idea dropped without a recorded reason gets raised
again.
