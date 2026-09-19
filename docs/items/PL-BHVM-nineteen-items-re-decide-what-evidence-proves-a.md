---
id: PL-BHVM
title: Nineteen items re-decide what evidence proves a ref is done, seventeen of them in vcs.py: one design round rather than nineteen heuristic patches
priority: P2
effort: M
status: needs-decision
classes: defect, refactor
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-12
root-cause-of: PL-KSCW, PL-LF2C, PL-MBTZ, PL-Q9Z1, PL-R808, PL-SH9Q, PL-SY1J, PL-WNQT
---

**Problem.** Nineteen items re-decide what evidence proves a ref is done, seventeen of them in vcs.py: one design round rather than nineteen heuristic patches

**Why it matters.** This is the largest single cluster in the workflow lane and
the only one whose self-generation rate has been measured against a real
baseline: items declaring `subprojects/docket/src/docket/vcs.py` number 53, 38
are closed, and those 38 spawned 40 further items - `r_vcs = 1.05` against a
whole-lane 0.69 (`PL-CSHL`, which fixes the prediction in advance). The cluster
generates more work than it closes, and more than any other part of the lane.

The mechanism is the one `PL-6ZQY`'s map named under 47% of the workflow lane:
**the apparatus infers a fact it could have recorded.** Nothing is written down
when a session claims work, so `stranded`, `flight`, `orphaned` and the digest
each reconstruct the claim afterwards by comparing file content against the
base - and content is unchanged by a squash, by a history rewrite, and by two
sessions writing identical `docket record` lines, which is exactly the set of
cases where the answer is wrong. Each inference fails in a new way, each failure
is found singly, and each becomes its own item. Patching one closes an item and
leaves the generator running; deciding once what evidence proves a ref is done
closes the cluster.

`PL-VV4D` is what a decided instance looks like: it settled that the exact test
is a ref comparison against `refs/pull/<n>/head`, and `PL-R808` is the build.
`PL-LF2C` then found that even that premise is not permanent. Nineteen open
items are still each choosing their own answer.

**Decision needed.** What evidence the apparatus treats as proof that a ref is
done - recorded at the moment a session claims or lands work, or inferred
afterwards from content and refs - and whether the nineteen open items are then
closed as one round against that decision or left to be patched individually.
The sub-questions the decision has to settle: whether a claim is recorded in the
store, in the commit trailer, or not at all; what the answer is where the
evidence is unreachable (no network, no permission, no such ref - `PL-LF2C`'s
three decline conditions generalise); and whether `vcs.orphaned`'s content
comparison stays as the portable fallback or is retired once an exact test
exists.

**Done when.** The decision is recorded with its reasoning and its costs, the
nineteen items are re-pointed at it or dropped against it, and `PL-CSHL`'s count
of what the round spawns can be taken.

**The `r_vcs = 1.05` figure above does not survive measurement, 2026-09-17
(`PL-M2SD`).** That number counted *every* item spawned by work on a `vcs.py`
item, including captures about unrelated parts of the tree. Counting only
children that land back in `vcs.py` — which is what "this cluster generates its
own work" claims — gives **r_vcs = 0.71**, below 1.0. The cluster closes more
than it creates. Two attribution bugs fixed in `tools/generator_check.py`
account for the rest of the gap: a multi-title `bin/docket new` commit made
each captured item the others' parent, and a `touches` entry written
`docs/items/` escaped the store exclusion.

On the corrected measure **no cluster in this repository reports at all**, and
`vcs.py` is not the lane's worst: `docs/MODEL.md` carries 40 open items at
0.55, `ROADMAP.md` 32. `vcs.py` has 12 open of 67, and its filings fell 26 to
14 over the two weeks to 09-17.

**What this retracts, and what it does not.** The urgency framing is retracted:
this is not a runaway generator and should not be ranked as one. The design
argument is untouched and is the reason to keep this item — nineteen items each
choosing their own answer to one question is duplication, and it is counted
from the items themselves rather than from any spawn rate. So the case for one
design round still holds; the case for doing it *ahead of everything else* does
not.

**Ranked as a generator after all - on the other definition (2026-09-17,
`PL-VX5H`).** What the paragraph above retracts is a *ratio*, and the ratio was
never the definition. `CLAUDE.md` now makes a mechanism causing three or more
items a generator and ranks it above everything but `P0`, and the count this
item argues from - items each choosing their own answer to one question - is
that definition exactly. Both readings stand: on the spawn rate this is not
runaway, and on the recorded definition it is a generator, so the
`root-cause-of:` line in the front matter is the claim and `docket next` now
offers this ahead of every band but `P0`.

The ten ids it names are the open items still re-deciding what evidence proves
a claim on a ref is done - the `stranded`/`flight`/`show` content comparisons
(`PL-SH9Q`, `PL-WNQT`, `PL-MBTZ`, `PL-KSCW`, `PL-SY1J`, `PL-Q9Z1`), the exact
ref test and the premise it rests on (`PL-R808`, `PL-LF2C`), and the two
records of guards passing while two sessions duplicated work anyway
(`PL-HX5C`, `PL-99YZ`). Ten rather than the title's nineteen because nine
closed as one round on 2026-09-13, which `PL-CSHL` records and measures.

Deliberately not named: items that merely declare `vcs.py`. `PL-GVC0` (the
hard-coded `PL-` id prefix), `PL-3LLZ` (four test fakes teaching the same git
question) and `PL-7XNX` (one `git diff` per ref rather than per file, which its
own brief calls "not a correctness question") are in the same file and are not
this decision.

---

## The design round, 2026-09-19 — recommended, not yet ratified

**The round's first finding is that this item's own framing is wrong, and it is
refused by the file it is about.** The brief's decision line offers two options:
evidence "recorded at the moment a session claims or lands work, or inferred
afterwards from content and refs". `vcs.py`'s module docstring already decided
that, in its opening paragraphs, and against recording:

> Storing that in the item file instead would mean a session has to remember to
> write it when it starts and to clear it when it stops — and a session that
> crashes, or that is simply abandoned, leaves the item marked in-progress
> forever with nobody able to tell whether that is true. So it is derived,
> never stored.

That reasoning still holds, and this project has since paid for it twice in the
other direction: `PL-HX5C`'s duplicate implementation and `PL-99YZ`'s three pull
requests are both **sessions failing to write a record they were asked to
write**, which is the failure mode storing it would make permanent rather than
transient. Nothing in the nineteen items is new evidence against the docstring's
argument, so the recorded decision stands and the "record it" half of this
item's decision line is closed — not re-opened, closed, because re-opening a
settled question needs a carrier and this round did not find one.

Worse for the framing: for two of the four questions below, **the session cannot
record the fact at all.** "Did this ref's work land" is authored by the merge,
which happens on GitHub after the session is gone. The only party that can
record it already does — `refs/pull/<n>/head` plus the merge commit — which is
`PL-VV4D`'s decision and `PL-R808`'s build, both of which predate this item.

### The generator is one level down, and it is measured

The nineteen items do share a mechanism, and it is not inference. It is that
**the evidence layer collapses "git failed" and "git answered nothing" into the
same value**, so every reader re-decides what the silence means — and they
disagree.

`_run_git` returns `""` for a non-zero exit, a missing git and a timeout alike.
Its callers then adjudicate that silence one at a time: the module carries eight
`known()` properties, 54 references to `declined`, and about forty docstring
passages each settling what an absent answer means for one read. Two calls
**inside `branches_in_flight`** settle it in opposite directions.

Measured against this repository on 2026-09-19, by substituting a runner that
fails one subcommand and answers everything else truthfully:

| Evidence failure | `editing` marks | `unreadable` |
| --- | --- | --- |
| none — git answering normally | 13 | 0 |
| one `diff --numstat` fails | **0** | **0** |
| one `diff --raw` fails | 24 (over-reports — safe) | 0 |

So a single failed `git diff --numstat` silently deletes **every** in-flight
edit warning the session-start digest has, and the report's own `unreadable`
field stays empty, so nothing says anything went unread. Under a total git
failure the same split appears across the module's public reads: `stranded`,
`lost`, `orphaned` and `merged_pull_requests` decline correctly, while
`branches_in_flight`, `precedence`, `branch_state` and `default_base` each
return a confident clean answer.

**This is not a new policy question.** `.claude/rules/apparatus-standard.md`'s
floor already decides it — "What this apparatus tells a session must be true, or
must say what it could not read" — and cites `FlightReport.unreadable` as an
instance of the code already holding to it. The measurement above is that same
field, empty, on the read the floor names. The four reads are in breach of a
written standard, which makes this a defect with a known fix rather than a
decision anybody needs to take.

**`test_vcs.py:467` pins the breach.** `test_no_git_means_no_claims_about_branches`
drives a total git failure and asserts `branches == ()`, one file away from
`test_no_git_declines_rather_than_reporting_a_clean_store`, which asserts the
opposite for `stranded`. That test changes under this decision.

### The ten items are four questions, not one

Treating them as one question is what produced a decision line with an answer
that was already refused. Separated by what evidence each one needs:

1. **What does silence mean?** — `PL-Q9Z1`, `PL-SY1J`. Substrate under the rest.
2. **Did this ref's work land?** — `PL-WNQT`, `PL-R808`, `PL-LF2C`.
3. **Is this ref's copy ahead of the base's?** — `PL-SH9Q`, `PL-KSCW`, `PL-MBTZ`.
4. **Has a session claimed this work?** — `PL-HX5C`, `PL-99YZ`. **Not this
   question**, and leaving them in is what made the cluster look uniform: they
   are about a claim that does not exist yet, not about a ref being done.

### The answers

**Q1 — every read declines rather than answering clean, and a test enforces it.**
The rule is the apparatus floor, already written. What is missing is that
`_run_git` gives its callers no way to obey it, so the build is a failure
channel plus a **fault-injection test that fails the Nth git call and asserts
each public read either declines or keeps the mark**. Prose cannot enforce this:
`_superseded`'s docstring states the correct direction in three cases and the
code inverts two of them. Cost: `FlightReport` and `Precedence` gain a declined
signal, and `test_vcs.py:467` is rewritten. `PL-Q9Z1` is the build and should go
first — it is the one item here whose defect silently voids the guarantee every
other read is trusted for.

**Q2 — the merger's record is the evidence; the content comparison is permanent.**
Already decided by `PL-VV4D` (2026-09-12) and amended by `PL-LF2C`: the exact
ref test is exact where the ref resolves, `vcs.orphaned` answers everywhere
else, and because `refs/pull/<n>/head` is deletable on request the exact test is
**not a superset** of the portable one even in principle. `orphaned` is
therefore never retired — which answers the third sub-question in this item's
decision line. `PL-R808`'s open question — what to print when the two disagree —
is answered by the same ordering: the exact test wins, and the disagreement is
printed rather than resolved silently.

**Q3 — one directional predicate replaces id-presence, and it closes all three.**
`stranded` keys on whether an item *id* is on the base. The predicate it wants
is per item file, three-valued: the ref's copy is **ahead** of the base's
(report it, with a diff to read), **behind** (never report, never print a
checkout line), or **equal** (silent). That single change is what `PL-SH9Q`
asks for (content, not filename), what `PL-KSCW` asks for (a diff to read, not a
checkout to run) and what `PL-MBTZ` asks for (compare before offering). They are
one build, not three.

**Q4 — `PL-HX5C` and `PL-99YZ` leave this cluster**, and `root-cause-of:` drops
from ten ids to eight. Still a recorded generator by `CLAUDE.md`'s definition,
which needs three.

### What this round retracts, and what it costs

Retracted: the decision line's "recorded … or inferred" framing, refused above;
and the implication that one round closes ten items. It closes **one question
across eight items in three builds**, and two items go elsewhere.

`PL-Q9Z1`'s own reachability argument is corrected rather than retracted. Its
brief rests on `_run_git`'s 10-second timeout; measured on 2026-09-19 the real
`diff --numstat` calls run in **4.5 ms**, three orders of magnitude clear, so a
timeout is not the trigger. The trigger is a **non-zero exit**, and the likely
one in this repository is a ref that vanishes between the `for-each-ref` that
lists it and the `diff` that reads it — another session's branch deleted, or a
merged branch cleaned up, while the digest is running. Verified: git answers
`fatal: bad revision` and `_run_git` returns `""`, so every path in that call
reads as superseded.

Costs accepted: a failure channel touches the seam every test fake uses, so the
Q1 build is larger than its item suggests; and the fault-injection test is a
standing cost on every new public read, which is the point of it.
