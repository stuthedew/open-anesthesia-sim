# docket: triage

Read this when folding untriaged captures into the queue, on a grooming pass,
or when writing an item's `verify:` command.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

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

**A second and weaker line fires where that mark cannot reach at all.** A
triage pass writes nothing outside `docs/items/`, which is exactly the diff
shape the in-flight mark refuses to read as work — so two passes on one item
were invisible to each other however carefully each one fetched, and on
2026-09-06 the merge discarded one of two identical answers (`PL-N1JK`). `Its
file is already edited on <branch>` is that case: not work in flight, so
`bin/docket next` still offers the item and nobody has claimed it, but a second
answer here is still a second resolution of the same file. Skip it the same
way, and say in the reply which branch you left it to.

**The mark now means the edit is genuinely unmerged, which it did not before.**
It used to be computed from the item files a branch's commits touched, without
asking whether the base already held them — and a squash merge keeps none of a
branch's commits, so the branch stayed ahead forever and kept reporting edits
that had landed. One pass was told to skip four of its five items and all four
were byte-identical to `origin/main`'s copies (`PL-8MJ3`). It is now checked
against the base's own tip, so a skip is worth obeying.

What it still cannot promise is that the ref it names is the *only* one. In that
same pass one of the four was a real collision, answered an hour later on a
different branch than the one the mark named. So read the mark as "somebody may
be in this file" rather than as the identity of who: skipping is still right, and
the branch named is where to look first rather than the whole answer.

Fill in what capture deliberately skipped:
`priority`, `effort`, `classes`, `touches`, and `feature` when it belongs
with related work. Safety-critical work starts at `P0` or `P1`; the checker
enforces that. Process work — work on how the project is built rather than on
the product — does not enter the top band when it would outnumber the product
work already there.

**Write the answers with `bin/docket set`, not into the file.** `bin/docket set
<id> --priority P2 --effort S --classes defect --touches a.py --status ready
--verify '...' --payoff '...'` writes the named fields in canonical order, keeps the file's
name, and refuses a value the item already records (`--overwrite` replaces
one; `status` needs no flag, since moving it is what triage does) and any
write `docket check` would then fail, in the checker's own words. The brief is
prose and stays a hand edit; write it first, because `--status ready` is
refused until the sections it owes exist (`PL-L4YG`).

An item that should not be done becomes `status: dropped` with a `reason` —
`bin/docket set <id> --status dropped --reason "..." --closed DATE`. Never
delete the file: the reason is what stops the finding being re-raised.

**Dropping an item closes it.** `dropped` is one of `CLOSED_STATUSES` beside
`done` in `subprojects/docket/src/docket/model.py`, so a triage pass pushed
onto an open pull request owes that title the dropped id exactly as a close-out
does. Retitle before pushing, per **Mode: close out an item** step 1 in
`.claude/skills/docket/modes/close-out.md` (`PL-X1S4`).

**An item whose next step is a decision is triaged to `needs-decision`, not
answered.** Triage sets fields; it does not resolve the question an item poses.
Answering one means reading the code around it, weighing the alternatives and
recording a conclusion - a work session's shape, spent on one item out of the
queue this pass exists to describe. `needs-decision` is what the store has for
it, and `bin/docket gate` counts it, so the question reaches the owner through
the queue rather than through the reply.

**Except where the decision is a milestone being scoped, which is `blocked-by:
<version>`.** The two look alike and want opposite statuses. A question this
project can answer is `needs-decision`, and `bin/docket gate` counting it as
debt is right - somebody can go and resolve it. A milestone not yet scoped is
`status: blocked` with `blocked-by: v0.6.0`, and is not debt: only a scoping
round resolves it, and working the item cannot bring one forward. `docket
check` promotes it once that section carries its four subsections, and errors
on a version the roadmap names nowhere. `PL-B9PY` is what the wrong one cost -
parked at `needs-decision`, counted into Gate 1 as resolvable, then two days
hidden from `bin/docket next` after v0.5.0 was scoped. A patch track
(`v0.5.x`) is not a version anything can wait on: it freezes no gate and takes
no section, so nothing resolves it.

**And `needs-decision` says the next step is a decision, never whose.** That is
the third case, and it is the one taken by mistake, because the status looks
like an invitation and `bin/docket next` ranks it. The owner's are the
*consequential* questions - whether a feature enters `ROADMAP.md`, the order
features come in, which of two defensible products this is, anything a learner
would see or the safety-critical standard reaches. `CLAUDE.md` divides it in
one sentence: "The division of labour is theirs to set direction and yours to
make it real."

**Resting on what the project wants does not by itself make a question
theirs** (project owner, 2026-09-19). How a milestone records a fact about
itself, which of two defensible phrasings a section carries, where a note
lands - each turns on what the project wants and is still a session's, because
its consequence is one document's wording. `PL-C4RS` is the worked example: two
ids sat in v0.5.0's `Required scope` under a gate heading saying another track
had cleared them, and "what does `Required scope` mean for work done elsewhere"
was put to the owner as a decision when it was a session's to take. Rule 14 of
`.claude/rules/instruction-writing.md` carries the test in full and is
resident, so it applies here without being read from this file. Where one
specific point genuinely needs them, ask that point rather than handing over
the decision around it.

**Sort by what the answer rests on, not by how hard the item looks.** An item
answerable by reading the code, running a measurement, or applying a rule this
repository already states is a session's, however long it takes to reach:
`PL-74R0` and `PL-79YX` were both settled by measurement against briefs that
expected argument. An item whose answer rests on what the project is for is the
owner's, however obvious the answer seems from inside the session.

**Most such items are both, and the halves are worked differently.** Do the
half that does not depend on the answer, say that is what you did, then put the
direction half in the reply with a recommendation and leave the item open. A
session that closes it on its own reasoning has taken a decision the owner
would have made differently often enough to matter: `PL-8GV5` was closed as
"do not model anaesthesia's effect on cardiac output, and carry no roadmap
line", the measured half of it correct and the disposition not, and the owner's
answer was "not now, and keep it on the roadmap as an option" - which is a
different project, and a better one, because an option can state its own
uncertainty where a default cannot (`PL-4T90`).

**And record the recommendation in the item, not only in the reply.** The
reply is where the recommendation naturally goes, and it is the one carrier
that does not survive: a reply dies with its session while the item waits.
So the longer an item sits at `needs-decision` - which is what the status is
*for* - the likelier the recommendation is gone by the time the owner answers.
`PL-KQHN` is what that costs. Its brief carried a `**Decision needed.**`
naming both answers and marking neither; by the time the owner said "agree
with the recommendation", the recommending session's branch had been deleted
with its pull request, and the only surviving carrier was a harness-written
summary line naming two options and marking neither. A decision of record
about the release train was settled by reconstructing another model's
compressed prose.

Write it into the brief as you write the question, in your own words, and
**mark it** - `**Recommended.**`, `**Recommendation:**`, or the word under
emphasis somewhere a reader skimming will land on it. Marking is the half
that is easy to skip and the half that failed here: a recommendation in the
ninth paragraph of a long brief is present and unfindable, which buys the
owner nothing. `bin/docket check` advises where a `needs-decision` brief
marks neither a recommendation nor a reason there is none.

**Where none is owed, say that and why, in the brief.** Declining is a real
answer - `PL-PFK1` declines because the deciding number cannot be measured
retroactively, and `PL-JW9J` because the answer follows from a count nobody
has taken yet. Both are better records than a brief that simply says nothing,
because silence cannot be told apart from an omission. Marking the
declination also satisfies the check, which is deliberate: the advisory is
asking the brief to be explicit, not to hold an opinion.

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
unstarted one. `docket check --verify` runs every open item's command and
raises an advisory for the ones that pass, so this is caught — but CI is what
passes that flag, so it is caught after the item is written *and* after it is
pushed. The fix is still to see the command fail first.

**Then reproduce the fault, because the command cannot.** Watching the
`verify:` fail proves the *fix* is absent. It does not prove the *fault* is
present, and those are different claims - a command tests for the presence of
the fix, never for the presence of the fault (`PL-LKGL`). So run the one
command that shows the defect itself, and write what it showed into the brief
with its date. Measured 2026-09-19 across all 166 open workflow-lane items:
five rested on a premise already false when they were filed, and **three of
those five carried a `verify:` that was run and failed correctly** while the
premise was false - `PL-RZPX` asked for a report that had shipped in docket's
first commit the day before, `PL-T86P` said an item carried no
`**Decision needed.**` section when it had one from creation. One `grep` would
have caught each. It costs one command per triaged item for about one catch in
thirty-three; the alternative is the sweep that found them, which read 145,000
tokens of briefs across twelve agents (`PL-JB3Z`, project owner, 2026-09-19,
ratified, over leaving it to a periodic sweep). Capture is untouched: this is
triage's obligation, not the capture rule's, which stays unconditional.

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
| `grep -q 'def test_no_such' <file>` | 1 | an ordinary failure |

So write the `grep` for the test the work adds, and nothing ahead of it. That
exits 1, the code a failing test gives, so no reader has to know a special
case, and the `grep` names the exact test the work owes. The file's suite is
not the command's to prove: `docket verify` runs `make check` as a line of its
own report, `docs/worker.md`'s loop runs it after the command, and CI runs it
ahead of the replay - so a `pytest` clause ahead of the `grep` proved nothing
twice, and it was what made a failure unreadable and 99.7% of the replay's
serial cost (project owner, 2026-09-19, ratified, chosen over keeping the
paired shape; `PL-6TP8` has the measurements).

`docket verify` says so on the check line where a command selects nothing, and
`docket check` reports it — separately from the commands that already pass —
for the items `next` is about to offer, which is the first moment there is
anybody to act on it. Reading one about your own item means: replace the
selector with a `grep` for the test the work adds. The sentence carries how many open items across
the store are in the same state, which is context rather than a backlog to
clear in one pass — a command written away from its work is how every wrong one
here came to exist, so each is repaired as its item is started.

**From 2026-09-23 a `-k` is refused rather than remembered.** `docket check`
errors on, and `docket set` will not write, a command captured from that date
whose `&&` chain narrows a `pytest` run over `tests/` or
`subprojects/docket/tests/` with `-k` - wherever the clause stands, since ahead
of the `grep` it answers 5 and behind it it re-proves `make check` (`PL-Q8RQ`).
A run piped into another command, one carrying `--cov`, and one over any other
tree are left alone. The five open commands of the shape on 2026-09-22 are
grandfathered, and lose it as their items are started.

**What the exit status is read to mean once the command is recorded** is one
contract - `subprojects/docket/README.md` § "What a `verify:` exit status
proves, and to whom" - and two of its consequences fall on the author. Exit 0
says the assertion holds, so the replay reports an open item whose command
passes as an error whichever way that happened. A non-zero exit says only that
the assertion did not hold *or was never evaluated*: the tools separate a kill
at the limit, a command the shell cannot find and pytest's "selected nothing",
and read nothing from any other failure, since a red prerequisite clause and an
unstarted item both exit 1. So, first: a `grep` for a test name pins the
*name*. On an item whose work may already exist under another `def`, check the
code before writing it - the command fails identically whether the behaviour
is absent or present under a different name, and no reading of the exit will
ever say which (`PL-6TN8`, `PL-0M32`). Second: the discriminating clause goes
green only for *this* item's work and reads a path the item's `touches`
declares (`PL-3DXV`, `PL-LBW5`); a neighbour's work satisfying it turns the
replay red against the wrong item.

Copy one of these shapes rather than inventing one:

| The item is | The command |
| --- | --- |
| Covering a module's untested paths | `uv run pytest --cov=anesthesia_sim.core.tissue --cov-fail-under=100` |
| A string, label, or single behavior | `grep -q 'def test_halted' tests/unit/test_simulation_view.py` |
| Documentation only | `grep -qF 'the sentence the item adds' docs/MODEL.md` |

The last two are the same shape, and it is the one to reach for: a `grep` for
what the work adds, alone. It fails until the work exists and nothing else can
make it fail, which is what keeps its exit readable. Do not put a health check
ahead of it - `doc_check.py check`, `bin/docket check`, the file's `pytest`
run - and do not record one on its own: `doc_check.py check` passes whenever
the docs are internally consistent, which they are before the item is started
too, and five open items once shared exactly that command with none of them
proving anything. The commands recorded before 2026-09-20 still carry such a
clause; each loses it as its item is started, never in a pass.

**The `pytest` half of that is now refused rather than remembered.** `docket
set` will not write, and `docket check` errors on, a command captured from
2026-09-20 that runs `pytest` over `tests/` or `subprojects/docket/tests/`
while another clause stands beside it - the shape 82 open commands carry and
`PL-FZ58` costed at 59% of a whole-store replay. So this paragraph now only
has to be remembered for the clauses a check cannot judge: `doc_check.py
check` and `bin/docket check`, where which clause discriminates depends on
what the item's work is (`PL-09G9`).

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

**Once the item is closed the command is a record, and it is not rewritten.** A
closed `verify:` says what was run — it failed before the work and passed after,
on a tree that no longer exists — rather than what still runs today. It stops
resolving as a matter of course: 14 of the 179 closed items carrying one no
longer do, and each of the 14 is later work correctly consuming what its
predecessor established, four of them `grep '^blocked-by: PL-…'` commands
written in the expectation of stopping. So a dead command on a closed item is
not a defect and there is nothing to repair. Re-pointing one replaces the
command that proved the work with one that never ran it, which is why `docket
check` errors on the attempt and on backfilling a command onto an item closed
without one. Where an item is genuinely not done, reopen it and the field is
writable again; which tree the command passed on is recoverable from the item's
`pr` (`PL-JZ1D`).

### `falsifies:`, and why triage is the only pass that can write it

**Skip this unless the item's brief already quotes a string its work will
delete.** The field is rare by construction, and the closing paragraph says how
rare; nothing is owed on an ordinary item. It is here at all because the
instruction to write it used to live in
`.claude/skills/docket/modes/close-out.md` alone, which is read at close-out -
the one moment it is certainly too late (`PL-YZJD`).

**What it is for.** Where an item's deliverable *is* a changed output string,
the test pinning the old string has to change, and the old string is then simply
gone. Nothing in the diff separates the commissioned rewrite from an
expectation quietly dropped, so the close-out's `no existing assertion removed`
check refuses - correctly, and every time. `falsifies:` holds enough of the one
assertion the work makes untrue for that removal to be folded and printed
rather than counted.

**Why this pass and no other.** `docket verify` reads the declaration from **the
base's copy of the item**, never from the branch, because the whole worth of
the field is that a reviewer wrote it before the work. So the line counts only
once it has *merged*: a session that triages an item and works it in the same
session declares on its branch alone, folds nothing, and is told the
declaration is its own word for it. The window shuts at the working branch's
first commit, and triage is the last pass inside it - which is also why a
session meeting that refusal has nothing to do about it, and the advisory now
says so.

**Write it only from what the brief already quotes**, as `PL-FCM3`'s title did -
then `bin/docket set <id> --falsifies '<the quoted string>'`, twelve characters
or more, one subject rather than a list. Do not go looking for the string, and
do not guess at it: a declaration naming an assertion the work turns out not to
remove is reported as the item describing work the branch did not do, which is
a worse record than no declaration at all. Where the brief does not quote it,
there is nothing to write.

**How rare, stated so nobody re-opens this expecting a win.** Over 502 single-id
close-outs, 57 would refuse this check and 20 are the changed-output-string
shape; the brief quotes the string in 3 of the 20. Of 80 recent `done` items,
53 had their file on the base before the commit that closed them, so roughly
two thirds of that 3 sit inside the window - about **2 folds in 502
close-outs**, against 0 of 1,503 items carrying the field on 2026-09-22. The
field is worth writing when the case lands in front of you and is worth no
search at all, and that is the whole reason the check stayed as it is rather
than being moved to read the branch point (`PL-YZJD`, project owner decision
recorded there).

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
per **Mode: recommend what to work on** in
`.claude/skills/docket/modes/picking.md`. Not a diagnosis, not a patch, not
a branch. A pass where nothing pressing surfaced ends without this section;
reaching for something because the reply feels thin is how the summary turns
back into a to-do list.
