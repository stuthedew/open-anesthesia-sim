---
id: PL-VYSP
title: A design round's whole output is item files, so the in-flight mark can never fire for one: bin/docket show called PL-BHVM startable while a live session held it with three PL-BHVM commits pushed
priority: P2
effort: M
status: done
classes: defect
feature: parallel-sessions
milestone: v0.4.28
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-19
closed: 2026-09-19
pr: 686
verify: uv run pytest subprojects/docket/tests/test_vcs.py -q && grep -q 'def test_a_design_round_on_a_needs_decision_item_is_in_flight' subprojects/docket/tests/test_vcs.py
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

**Why it matters.** The suppression is not a window that closes as a session
proceeds. For an item whose deliverable is a decision it holds for the whole
life of the work, and it lands on exactly the items a recorded generator ranks
above every band but `P0` - so the guard reads "startable" precisely where a
second session costs most. Measured live at 04:40 on 2026-09-19, after
fetching every branch: five design rounds were running on the five generator
heads, and `bin/docket flight` named one of them (`PL-4FBP`, whose round had
touched a file outside the queue) while `show` called `PL-HWW1` and `PL-6TP8`
startable with live sessions on both.

**Done when.** `bin/docket show` and `bin/docket next` mark an item at
`needs-decision` in flight from a queue-only commit that leads with its id and
writes its own file, while a stale capture branch of such an item is not a
claim; `precedence` orders two such rounds on one item; and `flight`'s
empty-report sentence says only what was checked.

**Decided against the candidate above, on a count (2026-09-19).** The rule
adopted reads the item's *status* off the default branch, the way `PL-7790`
reads its `touches`: a queue-only commit that leads with an id and changes that
id's own file is a claim where the base holds the item at `needs-decision`, and
annotation everywhere else. The candidate rule fails `PL-X3WZ`'s test as soon
as it is counted, and so does the obvious repair to it. Over the 1,006 commits
on `origin/main` at the time:

| Rule | (commit, id) pairs it would have marked | What they were |
| --- | --- | --- |
| Candidate: queue-only, leads with the id, changes its own file | 316 | 81 captures and recoveries creating the file; the rest below |
| ...and the parent commit already holds the file | 235 | 120 triage passes out of `untriaged`, 51 on `ready` items (24 of them pure notes), 36 `docket record` writes, 23 on `needs-decision` items |
| ...and the item was at `needs-decision` | 23 | 21 the item's own decision work - the answer, a measurement for it, or its disposition; 2 notes written into `PL-2XTF` on 2026-09-02 |

What would have changed the answer: a material share of the 23 being notes by
sessions not working the item, which is the false mark `PL-X3WZ` removed. Two
of twenty-three, both on one item in the project's first week, against the
current rule's miss rate of every design round ever run.

The conjunction - the subject must *lead* with the id whose file it writes -
is not decoration. A design round re-points its cluster, so one commit edits a
dozen other items' files, some of them at `needs-decision` and being worked by
other sessions; `PL-BHVM`'s `#676` edited fourteen. Promoting on the file edit
alone would have marked those items "do not start again" against the sessions
holding them.

The same commits now reach `precedence`, so two rounds on one item get the
yield verdict the skill tells a session to read rather than reason out - the
step that failed for the two `PL-BHVM` sessions.

**Where it sits relative to `PL-BHVM`, and why it is not folded in.** The
paragraph above asked for this to join that item's `root-cause-of:` once its
branch landed. It landed (`#676`, `#677`) with a ratified decision that splits
the cluster into four questions and removes "has a session claimed this work?"
from it as Q4 - not a question about what proves a ref *done* - moving
`PL-HX5C` and `PL-99YZ` out on that ground. This item is Q4's third instance
and belongs beside those two, so `PL-BHVM`'s eight ids are left as ratified.

**Two findings from running the rule live before closing (2026-09-19 ~04:45).**

1. **The status test alone produced three false marks, so the fix carries a
   second test.** With every remote branch fetched, `bin/docket flight` gained
   `PL-4ZK8` and `PL-NJ9M` on `origin/claude/gate-items-zyfl0o` and `PL-V67Q` on
   `origin/claude/graph-y-scale-mac-percent-v-6ohg70`, all eleven days old:
   captures whose items merged by another route and were triaged to
   `needs-decision` on `main`, leaving a stale branch that leads with the id and
   changes its own file too - the "branch nobody merges, forever" false mark
   `PL-X3WZ` removed. The commit's own parent tells them from a round: a
   capture creates the file, a round writes into one that exists. So
   `_modified_by` asks `git rev-parse <commit>^:<path>` for the ids the status
   test passes, in both readers, and the fake runner and tests cover the stale
   capture and the rename that changes two paths. With it, `flight` named
   eight items, every one on a branch a live session was working.

2. **Two of the five live design rounds stay invisible for a different reason,
   filed as `PL-2BZY`.** `PL-4FBP` is now marked; `PL-HWW1` and `PL-6TP8` are
   not, because `origin/claude/clever-fermat-qp7s60` carries the commit `#675`
   squash-merged, the walk keeps one ref per id and that ref sorts first, and
   `_taken_on_base` then correctly finds *its* claim spent and deletes the id -
   discarding keen-cannon's and eager-brown's live claims with it. Not this
   item's mechanism: those two claims pass the annotation rule on their own.
