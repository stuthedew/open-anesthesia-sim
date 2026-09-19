---
id: PL-VYSP
title: A design round's whole output is item files, so the in-flight mark can never fire for one: bin/docket show called PL-BHVM startable while a live session held it with three PL-BHVM commits pushed
status: untriaged
feature: parallel-sessions
added: 2026-09-19
---

**Problem.** A design round's whole output is item files, so the in-flight mark can never fire for one: bin/docket show called PL-BHVM startable while a live session held it with three PL-BHVM commits pushed

**Observed, 2026-09-19 ~04:25.** `origin/claude/happy-planck-ar6dak` carried
three commits, every subject led by `PL-BHVM`, the newest nine minutes old, and
`session_01LMH7APjVf5RWSEEjifJScv` was live on it at 254k tokens under the title
`PL-BHVM Nineteen items re-decide what evidence proves a ref is done`. That
session did everything the skill asks: it renamed, it led every subject with the
id, and it pushed early. Yet after `git fetch origin`:

- `bin/docket show PL-BHVM` printed **`Not work in flight - PL-BHVM is
  startable`**, with only the weaker `Its file is already edited on
  origin/claude/happy-planck-ar6dak` above it.
- `bin/docket flight` named the branch as carrying `PL-99YZ` — an item whose
  file the branch happened to touch — and never named `PL-BHVM`, whose id leads
  all three subjects.
- The session-start digest therefore ranked `PL-BHVM` **first**, as the whole
  queue's top pick, while a session held it.

**Why the existing covers do not reach it.** All fourteen files the branch
changed are under `docs/items/`, and `PL-X3WZ` made the mark refuse a commit
whose whole diff is in the queue — correctly, for the capture and annotation
commits it was aimed at. `PL-7790`'s exception rescues an item whose own
`touches` never leave `docs/items/`, and `PL-BHVM` declares
`subprojects/docket/src/docket/vcs.py`, so it gets no cover. `PL-N1JK` added
the weaker "file is already edited" line for triage passes, and that is what
fired here — it says somebody is in the file, not that anybody has claimed the
item, which is the sentence `docket next` reads.

**Why this case is worse than the two it descends from.** A triage pass or an
annotation is minutes of work; a design round is the whole item. A generator
head's deliverable *is* item files — the decision, the cluster membership, the
brief — and on this project a design round may never produce a diff outside
`docs/items/` at all, because implementing the decision is separate work. So
the suppression is not a window that closes as the session proceeds: it holds
for the entire life of the work. And it lands precisely on the highest-ranked
items in the store, since a generator outranks every band but `P0`.

It has already been paid once, before this observation: the archived
`session_01MLCbBSb3MbZ1UicvjuW83H` is titled `Yielded PL-BHVM to
claude/happy-planck-ar6dak - awaiting redirect`, so two sessions reached
`PL-BHVM` and one was spent getting far enough to discover the other.

**Where it belongs.** This is an instance of `PL-BHVM`'s own mechanism — what
evidence proves a ref is doing an item — and would sit in its
`root-cause-of:` list. It is deliberately not added there: that file is being
edited on `origin/claude/happy-planck-ar6dak` right now, and a second edit
collides at merge. Fold it in when that branch lands.

**Candidate fix, for triage rather than decided here.** A commit whose subject
leads with an id and whose diff includes *that id's own file* is a claim
regardless of where the rest of the diff sits — which separates a design round
on its own item from a capture commit writing somebody else's, and needs no new
field. Weigh it against `PL-X3WZ`'s reason for the current rule before adopting.

**Confirmed by the state changing, 2026-09-19 ~04:28.** `#676` merged and the
branch pushed two more commits, one of which edits `ROADMAP.md`. `bin/docket
flight` then named `PL-BHVM` where minutes earlier it had named `PL-99YZ`, and
nothing about the session's claim on the item had changed in between. Two
things follow, and they are the mechanism rather than an inference:

- `PL-99YZ` was named first because it declares `touches: docs/items`, so
  `PL-7790`'s exception covered its queue-only edit. `PL-BHVM` declares
  `vcs.py` and got no cover from the identical commits.
- The mark appeared only once a non-queue path — `ROADMAP.md`, edited to record
  a gate disposition — happened to enter the diff. That edit is incidental to
  the design round; had the decision needed no roadmap line, the branch would
  still be reading as unclaimed now.

So the visibility of a design round currently depends on whether its reasoning
happens to touch a file outside the queue.

**Third observation, 2026-09-19 ~04:31, and the cleanest one.** After `#676`
merged, `origin/claude/happy-planck-ar6dak` was force-updated — restarted on the
merged base, per the skill's restart procedure — and now carries exactly one
commit, `PL-BHVM: record the ratification and close the design round`, whose
whole diff is one file: `docs/items/PL-BHVM-…​.md`, the item's own. The session
is still live on it. `bin/docket flight` prints:

    No branch carries an item id, in its name or at the front of a commit.

That sentence is false as printed. The branch carries the id at the front of its
only commit, which is the condition the sentence denies. The suppression is a
deliberate rule about the *diff*, but the message reports it as a fact about
*subjects*, so a reader cannot tell a store with no claimed work from one whose
only claim was filtered. Whatever is decided about the mark itself, the wording
here should not outrun what was checked.

It is also the cleanest case for the candidate fix above: one commit, one file,
and that file is the item's own. A capture commit writes somebody else's item;
this writes its own, which is exactly the distinction available for free.
