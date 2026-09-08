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
docket next workflow         # ...confined to one half of the project, for a second session
docket wave                  # which beat of the plan's cadence is due
docket list                  # the queue, one line per item
docket triage                # what is untriaged, and the rules the answers must satisfy
docket concurrent PL-K7QX    # what can be worked alongside it, and what a live branch is already changing
docket feature halted-step   # progress on one feature
docket gate --feature x      # the open debt a milestone has to clear
docket release v0.3.0        # verify, bump the version, write the notes
docket delegable             # what a cheaper model may work, and what proves it
docket verify PL-K7QX        # prove one item's work stayed in its commission
docket branch                # where this branch stands against the default one
docket flight                # which items a branch is already carrying
docket stranded              # work that exists only on a branch
docket record                # write every pull request number the base is owed
docket check                 # validate the store; exits non-zero on errors
docket check --verify        # ...and replay every open item's `verify:` command
docket check --verify --verify-base origin/main   # ...only the ones this branch changed
```

### Capture costs nothing

`docket new` takes a title and nothing else. No priority, no estimate, no
band — those are triage, and demanding them at the moment an idea occurs is
how ideas stop being written down. Several titles in one call, because
interruptions rarely carry exactly one thought.

**It writes one line into the body and no headings to fill in:** the title,
under a `**Problem.**` of its own. A brief appended below it composes — the
title is the terse problem statement the fuller sections elaborate — and
appending is what sessions do. Capture used to write the other three headings
empty, which is a form rather than a statement, and a session holding the
brief wrote it *below* the form instead of over it. That leaves a dead stub
above a real brief; the first matching heading is the one judged, so the stub
is the one read, and an item with a two-page brief reports as having nothing
under two required sections. Eighteen of the thirty-two items at one triage
pass carried it.

`docket check` and `docket triage` name that shape wherever it survives — an
empty required heading with a `**Problem.**` starting again below it — and
they do so on an untriaged item too, where the brief requirements deliberately
do not reach. The exemption is not weakened by it: the rule demands nothing
capture chose to leave out, and writing less can never trigger it. Only
writing a brief and leaving a template above it can.

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

**The command refreshes the default branch before it compares, and says so
when it did not.** Every finding is a claim about what the base does *not*
hold, so a base nobody refreshed reports whatever merged since the last fetch
as lost — and the recovery the finding hands over is a `git checkout` that
overwrites the merged copy with the older one. On 2026-09-05 that is what
happened: `PL-XLQ5` merged as `#325` at 01:13, a checkout whose `origin/main`
was from 01:05 reported it stranded at 01:16, and the recovery restored its
pre-triage copy over the triaged one the merge had just landed. Confirming the
branch was gone from the remote read as corroboration and was not — a merge
deletes the branch too, so the two histories are indistinguishable from the
ref's absence. `--no-fetch` is for a caller that already refreshed and for a
checkout with no network; the report then carries a line saying what it rests
on. The library function never fetches, so the read still works from a bare
checkout.

The answer is bounded by the refs the checkout holds, so the count of refs read
is part of the output, and a checkout that can read none declines rather than
reporting a clean store. Read the other way, the report answers whether a
branch is safe to delete: a branch named nowhere in it carries no item the
default branch lacks. That claim is about items only — what a branch carries
outside the store is the next section's question, and `docket stranded` prints
both answers together.

### The loss that is not an item: a commit pushed after the merge

A pull request merges the head it was opened against. A commit pushed to the
same branch afterwards is merged by nothing: no conflict, no red check, no
advisory, and a default branch missing work everyone believes landed. Observed
2026-09-04 on `#284`, whose follow-up `#286` says it plainly — "that pull
request merged at its first commit, so the behavior change pushed to the same
branch afterwards never landed". The commit carried a rule the project owner
had asked for in that session, so `CLAUDE.md`'s "a behavior change takes effect
in the session that asks for it" was quietly void.

It surfaced only because that session happened to check the merge file by file.
`stranded` would have reported the item on the branch; nothing at all watched
the skill edit beside it, which was the actual behavior change.

`docket stranded` reports it now. **The rule has three parts**: a branch whose
introduced content is partly on the base and partly not, *and* which carries a
commit none of whose paths reached the base at all, *and* one of whose commits
the base took whole. The first selects candidates — a branch nobody merged has
landed nothing and is ordinary work in flight, and a branch merged whole never
reaches the read. The second tells a commit nothing took from a commit the
merge took and *merged*. The third tells a merge from a coincidence.

The second part was learned from the check's own first live firing. A branch
carrying the v0.3.8 release commit was squash-merged as `#312` while `#311` was
landing edits to the same `ROADMAP.md` prose; the merge wrote the combined text,
so three of that commit's ten paths matched nothing the base had ever held and
the branch was reported as carrying lost work — while `main` was *ahead* of it.
Ten paths touched and seven landed is the signature of a merge that happened,
and no comparison of the outstanding three can see that. Only counting them
against the rest of the same commit can.

The third was learned the same way, from `#372`, and it is the sharper of the
two because the finding was destructive rather than merely noisy. That branch
was reported as having "already taken the rest of its work" while its pull
request was open and none of its triage had landed anywhere. What matched was
`docket record`: eight of its first commit's twelve files changed only by a
`pr:` line, and the sessions behind `#366` and `#369` had written the same
line — the command writes a value the tool dictates rather than one a session
chooses, so both sides wrote identical bytes. Agreement is not evidence of a
merge, and no comparison of those blobs will ever say otherwise, because there
is nothing to tell apart. What differs is the *unit*: a squash merge takes
whole commits, so a merged branch has a commit every path of which the base
holds, and convergence scatters files inside commits and leaves no whole one.
The prescribed recovery for this section deletes the branch ref and restarts it
on `main`, so believing it about a live branch throws away the work an open
pull request was raised against.

The report names the commits nothing took, the paths under each, and the
`git checkout` line that recovers them.

**The branch ref is the only evidence, and that is worth stating because the
obvious alternative does not work.** GitHub freezes `refs/pull/<n>/head` when
the pull request closes, so the commit pushed after the merge appears in no
pull-request ref and no merge-time check could see it. Measured against this
repository: all 311 pull refs survive their branches being deleted, and
comparing each merged head against the commit that landed it found no
discrepancy in any of the 204 then merged — the loss is invisible from that
side. What does survive is the branch, precisely because the push recreates it.

That 204 is a sample rather than a proof, and the next merge after it produced
a shape the sample did not contain. The population a measurement covered is
part of what it measured.

Both directions of error are still possible and the trade is deliberate. Two
shapes go unreported, and both are silence, which is the expensive direction: a
commit pushed after the merge that happens to leave one file in a state the base
has held, and a post-merge push to a branch whose every pre-merge commit was
re-merged against a base that had moved under it, since neither side then has a
whole commit. Both are accepted only because the alternative — the content
split on its own — fired in every session's digest, which `CLAUDE.md` calls a
defect in the check rather than coverage.

### The other loss: a merge that deletes an item nothing deleted

`stranded` answers for a branch that never merged. The opposite case is a
branch that *did* merge and whose item did not come with it: a conflict
resolution removes the file in the merge's own tree, and since a merge is not
diffed against either parent, `git log --diff-filter=D` over the store returns
nothing. Nobody reviewing the merge sees a deletion, because there is not one
to see. `PL-Q8QX` was lost exactly this way and survived only because one
container still held a stale ref.

`docket check` now walks the objects instead: every blob path reachable from
the ref, against the ids its tree currently holds. Anything the history held
and the tree does not is an **error**, with the `git cat-file -p <blob>` line
that recovers the file as it last stood. It is an error rather than an
advisory because this is the capture rule itself failing, and the id
comparison keeps a renamed file from reading as a loss.

**It has to run on the branch, and that is not a preference.** After a squash
merge the branch's commits are ancestors of nothing, so the objects proving
what it carried are unreachable — `PL-Q8QX`'s blob is reachable from no commit
`main` holds. Asked on the default branch the walk answers "clean" and is
wrong to; asked on a pull request, before the squash, the evidence is intact.
CI runs it there at `fetch-depth: 0`. A clean answer from a truncated clone
says so rather than claiming the history it could not read.

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
commands for the ordinary cases and no third: a branch behind with nothing of
its own is restarted, a branch behind with work of its own merges the base in.
Rebase is deliberately not offered - telling "only capture commits" from any
other commits means guessing, and a rebase of a pushed branch needs a
force-push, which this project's squash-merge path exists to avoid.

**A rewritten history is not divergence, and no count can tell them apart.**
`filter-repo`, `filter-branch` and a force-pushed rebase of the default branch
rebuild every commit on it. A branch still sitting on the old history is then
counted as hundreds behind *and* hundreds ahead, which reads exactly like a
branch carrying a great deal of work - and both commands above lose whatever it
pushed into the rewrite's window, one by replaying the base's own history
against itself and one by discarding the branch outright. `PL-YGF3` is the
incident: two commits survived only because the session that wrote them still
had them in a live working tree, and nothing anywhere reported them missing.

So the divergence is read rather than counted. A rewrite preserves author date
and subject while changing every hash, so the two sides of the symmetric
difference hold the same commits twice; the rule is that the **oldest** commit
unique to this side has a counterpart on the base, which means the divergence
*begins* in duplicated history - what a rewrite leaves and what forking and
then committing cannot produce. An ordinary fork matches nothing there and is
left alone, and so is a branch that cherry-picked from the base after its own
first commit. What is left unmatched is named commit by commit, because that is
the work held nowhere else, and the recovery carries it onto the new history
instead of discarding it. The tags line goes with it: `git fetch` will not move
a tag that already exists, so a clone keeps the old history reachable through
its release tags until something forces them across.

Matched on author date and subject rather than on patch id - what `git cherry`
uses - for two reasons that both bit the incident. The rewrite stripped a file
out of history, so the patch of every commit that had ever touched it changed;
and `git cherry` drops merge commits entirely, while one of the two commits
actually lost was a merge.

**The fork point guards the counts, and the rewrite test runs in front of it.**
`git rev-list --left-right --count A...B` does not fail on refs sharing no
history: it prints the size of each side, which reads exactly like a position.
That state is reachable - a `--depth` fetch re-truncates `origin/main`, and
`.git/shallow` records it, so a later ordinary fetch does not undo it - and a
fabricated "98 ahead" argues against merging in the very case the line exists
to catch. So a clone that cannot see the fork point is told to deepen instead
of being given a number.

But a rewrite is *also* a pair of histories with no fork point, and usually is:
rebuilding every commit shares no root with the original, measured against a
real `filter-branch` rewrite on 2026-09-06. Deepening does nothing for it. So
the duplicated-history test is asked first, and where it answers, the counts
mean something and are reported; the deepen-me decline is what is left for the
truncated clone it was written for.

**The session-start hook deepens it first, so that line is a fallback rather
than the normal case** (`PL-K2ZK`). Every environment this runs in clones
shallow, so the decline above used to fire in every session for the life of a
container - and the answer it declined to give is one a single fetch makes
available: 3.4 s to take this repository from 52 commits to 542, measured
2026-09-02, after which `branches_in_flight` answers instead of declining.
`.claude/hooks/docket-digest.sh` therefore runs `git fetch --unshallow origin`
once, before anything reads a ref, guarded on the checkout actually being
shallow and bounded by `timeout` where that exists. It is allowed to fail: no
network leaves the checkout as truncated as it was, and the deepen-me line is
then what a person is given. The library still does not fetch - this is the
hook, which has a network and runs once, and `vcs.py`'s rule that a read must
work from a bare offline tree is untouched.

**The command fetches; the function does not.** `branch_state` reads only what
the checkout holds, because the rule the rest of `vcs.py` follows is that a
read must work from a bare checkout with no network. A command whose one
question is "has the base moved" would then answer "current" from a ref nobody
refreshed, so `docket branch` refreshes first and `--no-fetch` says not to -
and the line says which happened, rather than letting a stale answer look
fresh. `docket stranded` is the second command on this pattern and the same
three parts: it refreshes, it takes `--no-fetch`, and its report carries which
happened.

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

**A leading id is a claim only where the commit reached past the queue.**
Bookkeeping leads with ids too, and has to: capturing a finding, triaging an
item, recovering a stranded one and recording a merged pull request number all
carry the id of the item they concern and none of them is work in progress.
Measured on the parent project 2026-09-04: of nine items reported in flight,
eight were marked by commits whose entire diff was inside the queue directory
and one branch was actually implementing something — and three of the eight
were open, startable, and hidden from every session for it. So the paths are
read alongside the subject, from the same `git log` rather than a `git show`
per commit, and a commit that only wrote to the queue stakes no claim.

It fails toward keeping the mark. A merge prints no paths under `--name-only`,
and a path git quoted does not match the prefix; neither is evidence of
bookkeeping, so both keep their claim. What it cannot see is a session that
*starts* an item by pushing only a `touches` fill — annotation by the diff and
a claim in fact. A branch named for its item still carries the claim in its
name, which is read whatever the diff says.

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
handed an item is not obliged to run any command at all. `triage` carries the
same mark now, for a collision it went on to hit itself — below.

**A triage pass raises no mark at all, so a second and weaker one reads the
paths.** The rule above is that a commit whose whole diff sits in `docs/items/`
is a capture, a triage pass or a note rather than work — which is right, and
which leaves a triage pass with no way to be seen at all: it never commits
outside the queue, so no amount of fetching, `show` or `flight` could show one
pass to another. Two sessions triaged one pair of items on 2026-09-06, each
having checked, and the merge discarded one of the two answers (`PL-N1JK`).

So `FlightReport.editing` names, per item, a ref that has changed that item's
own file. It is a measurement of paths rather than a judgment about subjects,
which is what makes it exact: the file is what conflicts, whatever either
commit was for. It ranks nothing — `next`, `list` and `status` read `ids`
alone, so an annotated item stays startable and `PL-X3WZ` is intact — and it
prints only where it changes a decision: `triage`, which is about to write to
that file, and `show`, which is about to start the item. It is deliberately
absent from `flight`, where capture being mandatory would put a row under
nearly every live branch and change no answer to the question that command
asks.

**Detection stops at "somebody is on it"; `precedence` says which one
continues.** Everything above answers whether an item is being worked, and
nothing said which of two sessions discovering each other was the one to stop.
Two sessions reasoning in prose from the same evidence can reach the same
answer as each other or the opposite one, with no way to tell which happened
until the merge — and the expensive outcome is not both continuing, which is
merely the state before any of this, but both standing down, after which the
item is unstarted and each session believes the other has it.

So it is an order rather than a judgment: the earliest commit naming the item
holds it, and a tie breaks on that commit's hash. Both halves carry weight. The
*earliest* commit, so a session that pushes again does not overtake one that
started before it; a commit rather than a push time, because git records no
push time and a commit's date is the same fact in both checkouts. Two sessions
can still both continue, when one has pushed nothing the other can see; what
cannot happen is both yielding, since that needs each to be ahead of the other
in one order. `docket show` prints the order whenever more than one branch is
carrying the item.

**A claim is identified by the commit that staked it, never by the ref that
reached it.** `git log --source` credits a commit two refs reach to one of
them, and not reliably the one named first — so a branch a single merge ahead
of its own tracking ref has its claim reported under `origin/...`, and a check
on branch names then reads a session's own work as somebody else's and tells it
to stand down. Asking whether `HEAD` *contains* the staking commit answers it
for the local branch, its tracking ref, and a branch pushed under a third name
alike.

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

It names, per item, whether a branch already carries that id — and which refs
it could not read to answer that. Triage is the more exposed of the two entry
points rather than the less: `show` guards the path where a session has
already *chosen* an item, while triage is what a session runs straight off a
digest that reports the untriaged count and nothing about who is holding those
items. Two sessions answered the same pair of items on one afternoon and the
merge discarded most of one answer, the reasoning behind it included. The mark
names the branch rather than the fact of one, so a session can tell another
session's work from its own; and it advises rather than refuses, because the
answer is bounded by what has been pushed and a lock built on that would
sooner or later block the session whose own branch is the one holding the
item.

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

### Two sessions, one queue: the lanes

`docket next product` and `docket next workflow` answer the same question
confined to one half of the project — the thing being built, or the apparatus
building it — so a session on each can rank at the same moment and never be
handed the same item. `docket next` with no lane is unchanged and remains the
default: the split is a way of running two sessions at once, not a new way of
reading the queue.

The side an item falls on is read from its `touches`, against the
`workflow_paths` a project declares. Every declared path inside them is
workflow; none inside them is product. The alternative — deriving it from
`classes`, which already has a `process_classes` list — was measured against
this repository's own store on 2026-09-04 and put 33 of 145 open items on the
wrong side, eighteen of them workflow defects that a simulator session would
then have been offered. `classes` says what *kind* of work an item is, and a
defect in the tooling carries the same label as a defect in the product;
`touches` says where it lands, which is the question a lane is asking.

Two answers are not a side, and both are printed rather than filtered away. An
item reaching *both* halves is set aside from each lane, because no session
confined to one of them can make the change whole; an item declaring no
`touches` is set aside because nothing has been said about it. `next` names
both sets under the ranking, with the count and the ids, and the unfiltered
ranking still offers them. A lane is a filter, and a filter that silently
drops a fifth of a queue is how work goes missing for months.

An undeclared `workflow_paths` refuses the lane arguments outright rather than
answering from the whole queue. A lane that quietly degrades to *everything*
is the exact failure the split exists to prevent, wearing the flag that was
supposed to prevent it.

The lane filters and never reorders. `P0`, the roadmap's phase and the
finish-a-feature preference all apply inside a lane exactly as they do across
the queue, and how near a feature is to done is still counted from the whole
store — that is a fact about the feature, not about which session is asking,
and counting only the lane's share would make the same feature report a
different completion in each.

The digest names each lane's pick beside its `Top:` line, because the digest
is what a session reads *first* — before it would think to ask for a lane, and
before anything has been said that could tell it which half it is. Naming both
is what lets the hook avoid guessing:

    By lane, for a second session: product PL-F52R, workflow PL-Y0RZ; 15 in neither lane.

It costs one line in every digest, single-session ones included, which is why
it reads as an offer rather than an instruction, and why it is omitted entirely
where no boundary is declared or neither lane has anything startable. The
spanning count rides the same line: two picks read as the whole queue without
it.

### The one command that looks backwards: `docket trend`

Every other command describes the project as it stands. `docket trend` asks
how the balance between the two halves has *moved*, which is a question the
store answers and nothing was reading:

    docket trend            # 7-day periods
    docket trend --by day

It reports three measures side by side, and the reason it does not reduce them
to one is that each is wrong in a way the others are not.

**Closed items** is the obvious count and the most misleading of the three.
Apparatus work arrives in many small pieces; measured against this repository's
own store, workflow items average well under the size of product ones, so
counting them overstates the apparatus by roughly half. **Effort-weighted
closures** correct for that, at the price of leaning on a size ladder — `S=1,
M=3, L=8` — that is a convention rather than a measurement, which is why the
ladder is printed under the column that uses it. **Churn**, lines added plus
deleted, is the only measure read from what actually changed rather than from
what an item declared, so it is the one that still answers where `touches` is
missing or wrong.

The lane columns use exactly the boundary `docket next product` uses, so the
two commands cannot drift apart, and `crossing` and `unplaced` keep their own
columns here for the same reason `next` names them: neither is a side, and
folding either into one would be a verdict the data does not support.

Churn splits finer than the lanes do, because two of its categories would
otherwise say the wrong thing. The **queue store** is inside `workflow_paths`
and belongs there — editing it is apparatus work — but it is also written by
every session that captures a finding while doing something else, so counting
it makes a product session read as a workflow one; it is reported and left out
of the share. The **roadmap** is deliberately *outside* `workflow_paths`,
since product direction is product work, but a period spent rewriting it is
not a period spent building anything, so it is separated from `code`. What
counts as code is `code_paths`, which defaults to `src` and `tests`.

Periods are anchored at the first day the report has anything to say about,
never counted back from today: two runs a day apart have to agree about what
happened in August. A period with nothing in it is dropped rather than printed
as a row of zeroes, and a period where neither side moved shows a dash rather
than `0%`, which would read as a period of pure product work.

Like `docket wave`, it computes and decides nothing. Whether the balance it
prints is the right one is a judgment about the project, and a tool that
answered it would re-open the same question every run without being able to
see what the run was for.

### The digest and the ranking cannot disagree

The session digest's `Top:` line is that same answer, from the same ranking
against the same plan, because the two lines a session reads first have to
agree. The lane line above goes through `recommend` for that reason too — two
lines in one block ranked by different rules contradict each other where a
reader can see both at once. It was a sort of the store by priority alone, which opened every
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
those as a conflict graph and reports what stands between two items being
worked at the same time.

It reports in one direction only. Declared overlap proves two items will
contend. *Absence* of declared overlap proves only that nobody foresaw a
collision — the work may still wander into a shared file. So the command
rules pairs out and never certifies a pair as safe, and items declaring no
paths at all are reported as unanalysable rather than assumed harmless.

**Contending is not the same as being refused, and the three tiers say
which.** Only a `blocked-by` edge means the work cannot be done yet. Two
items naming the same file is ordinary — the second branch to merge resolves
against the first, and the practice is to land the smaller change first — and
an overlap that exists only because one item declared a *directory* covering
the other's file is weaker still, since it has not claimed that file at all.
Reporting all three as "cannot run alongside" made the graph refuse work that
was startable: 27 of Gate 1's 112 open entries declared `docs/MODEL.md`, so
the gate's most expensive half excluded itself from every batch, and a session
asked for three concurrent gate items withheld the strongest one it had
(`PL-VRMK`, 2026-09-06). A batch therefore stays the independent set when
unlimited, and fills out with same-file work — annotated with what it shares
and with which item — when `--limit` asks for a batch of a given size.

**`docket concurrent <id>` also reports what the branches in flight have
already changed**, which is the other half of the question and the one that
fires on work actually underway. `touches` is a prediction written before the
work; a branch diff is a measurement taken during it, so the two fail in
opposite directions — the first is complete about intent and silent about
drift, the second exact about what has happened and silent about what comes
next. Observed 2026-09-02: two sessions passed every declared check, both
edited `vcs.py`, and found out at merge. They are printed as separate sections
rather than merged into one verdict, because a reader deciding whether to start
needs to know which kind fired: only the second says the collision has already
happened.

The observed half is read per unmerged ref with `git diff --name-only
base...ref`, and it inherits every limit of the in-flight read it is built on.
A ref whose commits that read could not compare is not diffed either — the
merge-base a three-dot diff needs is the one that already failed to resolve.
An empty diff on a ref that holds commits the base does not is named as unread
rather than reported as a branch that changed nothing, because `_run_git`
answers a failure with the same empty string a clean branch gives. And the
answer is bounded by what has been *pushed*, like everything else here.

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

**A release is the one change no in-flight guard can see.** Every guard here
matches a `PL-` id — `flight`, `show`, `next`, `concurrent`, the digest,
`branch_id_check` — and a release cut carries none by design. So the change
that rewrites the version file, the lock file, the roadmap and a new notes
file, which is the most collision-prone in the repository, is the only one
nothing watches. Two sessions cut v0.3.7 within an hour that way, and the
second one's whole release was discarded at the merge (`PL-66FP`).

`release.already_released` closes the half of that which is *certain*.
`vcs.released_on_base` reads the default branch's own version file and its
`docs/releases/` listing — the ref, never the working tree, which is this
session's cut in progress and would answer about itself — and a version
either of them already names is refused rather than reported. That refusal is
what separates it from every other parallel-session read here: a notes file
on the base is a fact about a merge that has happened, not an inference from
a ref that may have moved since it was fetched.

**The base is not enough on its own, and this is the part that had to be
measured rather than assumed.** Both collisions this closes were between two
*unmerged* cuts: the session that lost the v0.3.7 race cut from a checkout
that did not yet hold an item merged eight minutes before the winning release
landed, so its `origin/main` read the old version whenever it looked. A
base-only check would have passed it, and would have passed the second race
the same day.

So `vcs.cuts_in_flight` reads the other half from the refs. It reuses
`_unlanded_refs`, which is what makes it survive a squash merge, and
subtracts the notes the base already holds - without that subtraction the
branch whose v0.3.9 release had merged twenty minutes earlier was still
listed, and a guard that fires on every release after the first is one nobody
reads. A ref `HEAD` contains is marked `mine` rather than reported, for the
reason `Carrier.mine` gives.

`cmd_release` refuses on *any* unmerged cut, not only one of the version being
written: two concurrent releases under different numbers is the worse case,
since both stamp `milestone:` onto an overlapping set of items and whichever
merges second claims work the first already shipped. It reports the date the
notes were written, because that is the only thing separating a live session
from a branch nobody will merge, and leaves that judgment to the reader the
way `flight` and `stranded` do.

**And it fetches first**, which is the step without which neither question is
worth asking. This is the rarest command here and the most expensive to get
wrong, which is what makes one network read proportionate where the digest's
would not be; `--no-fetch` is there for a caller that has already refreshed or
cannot. The digest carries the same answer on its `Releasable:` line, computed
only where a release is actually being offered, because the offer is where a
duplicate release starts - refusing at `release` alone leaves the second
session having already raised it and been approved.

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

The command must not name `docket verify`. That subcommand runs an item's own
`verify` field, so an item recording one re-enters it once per level, and each
level takes a fresh timeout rather than a share of one — the recursion ends at
the process table rather than at an answer. `check` refuses such an item by
name, and `verify` itself reports the re-entry as a failed check where it is
reached on a store nobody has validated yet. `check` is deliberately not
refused the same way: it replays a `verify` only under `--verify`, and a nested
run is told not to ask, so `docket check && grep -q ...` — a command that
passes today paired with a grep for what the work adds — is bounded at one
level and is the shape to reach for.

What `check` does say about that command is an advisory, and only for the one
shape that can pass without meaning anything: a `docket check` whose *output*
is piped or captured, rather than whose exit status is read. A nested run is
told not to replay the open items' commands, so it never prints the landed
advisory - a `grep` for that answer matches nothing whether the work is done or
not, and an inverted one passes on the strength of it. An advisory rather than
an error because "reads the output" is a judgment about a shell line, and hard
failure is reserved for exact rules.

### A closed item's command is a record, and it is not rewritten

Once the item is `done`, `verify` stops being a command and becomes the record
of an experiment that was performed: this command ran, it failed before the
work and passed after. That is a fact about a tree which no longer exists, not
a claim about the default branch today, and reading it as the second is what
makes the field look broken when it is working.

It stops resolving as a matter of course. Measured over the store this grew
in, 14 of the 179 closed items carrying a command no longer resolve against
the tree, and not one of the 14 is a defect — each is later work correctly
consuming the state its predecessor established. Four are
`grep '^blocked-by: PL-…'` against an item file, which pass exactly while the
blocker is unresolved and were written in the expectation of stopping. A field
whose commands are designed to become false cannot be read as a standing
claim, so nothing here runs a closed item's command and nothing warns that one
has gone stale: a check firing on all 14 would change no decision on any of
them, which is the shape of check this project retires rather than adds.

The hazard is the repair. A session meeting a dead command re-points it at
whatever covers the ground now, and the item then names a command that never
ran against the work it claims to prove — a false provenance where there was a
true one, which is worse than an absent one because it looks authoritative.

So `check` errors where a branch changes the `verify` of an item that already
reads `done` on the default base, and where it adds one to an item closed
without a command, which after the merge has nothing left to run against it.
An error rather than an advisory because the rule is exact: the field either
differs from the base's or it does not. The reading is one-sided — the two
diffs behind it return nothing where no merge base resolves, so a truncated
checkout under-reports and no branch is ever accused of an edit it did not
make. Reopening the item is the way out and needs no flag, because an item
whose status admits the work is unfinished is no longer claiming the recorded
command proved it.

Which tree the command was true of is already recorded, and by `pr` rather
than by a second field. The pull request outlives the squash-merge that
discards the branch commit, which is why `commit` was retired; 246 of the 248
closed items in the store carry one, and the merge behind it is what a reader
follows back to the tree the command last passed on.

`status` runs `untriaged` → `ready` / `needs-decision` / `blocked` → `done` /
`dropped`. Requirements scale with it: an untriaged capture needs only a
title and a body, while anything past that is a commitment to do work and is
held to the standard that lets someone else pick it up cold. Closed items
keep their files — `done` records where the work landed, `dropped` records the
reason, because a finding dropped without one gets raised again by the next
person who notices it.

### `blocked` means "not first", and that is the whole of it

`blocked-by` names what must settle before this one starts, and `status:
blocked` takes it out of `docket next` until it does. The two are checked
together: a blocker must exist, an item may not block itself, and a `blocked`
item may not outrank its own blocker — nothing can start before the thing
gating it, so a `P1` waiting on a `P2` is an error rather than a priority. When
the last blocker clears, `docket check` says so.

**The field takes two kinds of entry, on one line: an item id, and a milestone
version.**

```yaml
blocked-by: PL-K7QX, v0.5.0
```

An id names work in this queue and clears when that item closes. A version
names a milestone in `ROADMAP.md` and clears when that milestone is **scoped** —
when its section carries the four subsections the roadmap's development rules
require of one — or when it has shipped, which is the same thing recorded
differently. Scoped rather than released, because what an item waits on there
is the *decision* the scoping round makes, not the release: `PL-B9PY` could not
be designed until v0.5.0 settled what a side-by-side comparison renders, and
could be the moment it did, several releases before v0.5.0 goes out.

The milestone need only be *placed* to be named — a row on the timeline is
enough, and having a section of its own is not required. That is deliberate,
because the interval a milestone blocker exists to cover is exactly the one
between a milestone being planned and being scoped. A version the roadmap
places nowhere is an error rather than a block: a typo would otherwise be
indistinguishable from a live dependency and would never fire.

**Why one field rather than two.** An item whose real dependency is a milestone
being scoped previously had no honest state. `blocked` with the field emptied
is a store error; `blocked` naming an item that has since closed is false, and
raises "every blocker has closed" in every session from then on — an advisory
nobody can act on, which is the failure mode that trains a reader to skim the
output where a real one also appears; and `ready` invites a session to start a
refactor against a target shape nobody has decided. `needs-decision` was the
workaround, and it is debt by the `debt_classes` rule, so every item parked
that way was counted into the next gate as though somebody could resolve it. A
`blocked-on-milestone:` field beside the existing one was considered and
rejected: it keeps id parsing simple at the cost of two fields meaning one
thing and every reader of `blocked-by` having to know about the second
(`PL-W8XP`).

The two kinds cannot collide — an id is `PL-`-prefixed, a version is
`v`-prefixed — and are partitioned fail-closed: a milestone is matched
positively and *everything else* is treated as an item entry, so an entry of
neither shape is refused by name rather than falling out of both halves and
being silently ignored.

Without a readable `ROADMAP.md` the milestone half declines rather than
guessing, and `docket check` names the items it could not judge. A bare
checkout must not fail for the roadmap's absence, and must not report the store
as fully checked either.

**A sequencing dependency is a legitimate use of it, not an abuse.** The word
invites a narrower reading — that the work is impossible, or waiting on
something outside the queue — and under that reading a project would leave
ordering in prose and let the ranking contradict it. That is the failure this
field exists to prevent, so the broader reading is the intended one: `blocked`
says *this is not the one to start*, whatever the reason. Being startable-but-
second qualifies.

The cost of reading it narrowly is silent and falls on whoever picks the work
up: `next` ranks on front matter and never reads a body, so a prerequisite
written only in prose is invisible to it, and the ranking then states a sound
reason for an order the briefs contradict. The cost of reading it broadly is a
word doing slightly more work than it looks like. Prefer the word.

Say which it is in the body — `**Blocked on X (date, who decided).**
Sequencing only`, and why — so a reader can tell an ordering constraint from a
genuine impossibility without inferring it from the field alone.

**`docket check` raises a grooming advisory for the half of that which is
decidable.** Declaring an edge is a one-off edit; noticing an undeclared one
was the recurring cost, and it fell entirely on whoever happened to read the
brief. So where an open item's body names another *open* item in an explicit
dependency sentence — `depends on`, `blocked on`, `blocked by`, `waits on`,
`requires` — and `blocked-by` does not carry it, the advisory names the item,
the blocker and the sentence. Either answer clears it: declare the edge, or
reword a sentence that was not claiming one. Closed blockers never fire, since
most in-body mentions name work that has since landed.

It is an advisory rather than an error because only half of this is decidable:
whether the id is declared is a fact, whether the sentence states a
prerequisite is judgment. And it is deliberately narrow. `before X` and
`follows X` name the edge *backwards*, so they are not cues; `after X` points
the right way but reads the same in a prerequisite ("do this after `X`") and in
a narration ("amended after `X` merged"), and the store held more of the second
than the first. A clean run therefore means the explicit declarations agree
with the front matter — never that the dependency graph is complete. The
dependency that cost the most to find, `PL-011` → `PL-W3DD`, is named in
neither brief, and nothing mechanical reaches it.

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

`commit` named the branch commit, and is **retired**. Do not write it into a
new closure. It was exact and it stopped being resolvable the moment a project
squash-merged: the squash puts a *new* commit on the default branch, and
deleting the head branch makes the one the item names unreachable. Measured
over the 83 items carrying the field on 2026-08-31: 21 hashes resolved from
the default branch, 21 were present but reachable from nothing, and 41 sat
below a shallow clone's horizon and could not be judged — so roughly half of
what could be checked pointed nowhere, and the proportion grew with every
squash-merged item.

The values already recorded are left where they are, as a historical record
rather than a pointer to follow. Nothing validates them, because there is no
longer a field to hold to a standard; a reader who wants the change reads `pr`.
Recording the *landing* commit instead was considered and rejected: it is
durable but unknowable until after the merge, so it could not be written by
the closing commit and would need a second pass over every item forever, to
produce a second pointer to what `pr` already reaches (`PL-T63T`).

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

So a *landed* `done` requires `pr`, and carries no second pointer. The
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

**Recency is not enough, so the answer is confirmed before it is believed.**
Leading a subject proves a commit is *about* an item, never that it *closed*
it, and several kinds of commit are about a closed one: the merge that writes
its `pr` back, a follow-up fix, the triage that filed it. Measured 2026-09-04
over the 122 closed items on this project's `main` that a leading-id subject
names, the unconfirmed scan answered 21 with a number that is not their
closure. So each hit is put to the test the file reading already uses — the
commit must read `status: done` in its own tree and not in its parent's — and
an unconfirmed hit falls through to that reading instead. Over the same
history the confirmation agreed with the file reading wherever both could
answer and disagreed nowhere, and across every closed item carrying a `pr` the
recovery went from 101 correct and 25 wrong to 114 correct and 12 wrong
(`PL-GW37`).

Two shapes made up most of what was left. The first is fixed: an item whose
file was renamed after it closed used to recover the renaming commit, because
the fallback walked `git log` without rename detection and the parent does not
hold the new path at all. The walk now follows renames *and* reads each commit
at the name the file carried there — the second half being the one that does
the work, since `--follow` on its own still leaves every commit older than the
rename reading as "not done" (`PL-S5LB`). The second shape is open: an item
whose work landed in one pull request but whose `status: done` was written in
a later one recovers the later number, which carries the closure and none of
the work (`PL-YDL6`) — the shape `PL-D2GW` closed by requiring the closure to
travel in the same commit as the work, so it exists only in the three items
predating that rule.

- **The number is recoverable** → an advisory naming it, and the command that
  writes it. Nothing is lost; the way back exists in git, and the field is a
  transcription still owed so the item file carries it too. This should be a
  rare sight rather than a routine one — see below.
- **The commit that would name it has no parent in this checkout** → a decline,
  like the truncated case below. Finding a commit that names a number was once
  taken as proof it was the closure, at any depth. It is not: the closure is
  told from every later commit touching the same file *only* by its parent's
  tree, and at a graft boundary git reports every file as added, so the oldest
  commit a shallow clone holds reads as the closure of every item in it.
  `record` wrote `#401` onto five items that way, of which four had merged in
  `#399`, `#400` and `#402`, and `check` then reported no error at all — the
  field was present and well formed, and the one check that could have
  contradicted it is the shallow decline two paragraphs up (`PL-KX9N`).
  `closed_by` had refused this since it was written; the two readings here had
  not, and `_parent_in_reach` is shared by all three now.

  The refusal is per closure rather than per checkout, which `is_shallow`
  cannot express: it is equally true of `--depth 1` and of the `--depth 200`
  that recovered the four wrong numbers. Measured against real git on a
  12-commit history fetched to depth 4, the three closures whose commit and
  parent are both held resolve and the nine at or below the boundary decline.
  So a bounded fetch buys back exactly what it reaches.
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

### The write belongs to the merge, not to a later session

Everything above describes how a missing `pr` is *detected*, and for a while
that detection was also the mechanism: `check` named the number and a session
retyped it. That is the wrong division of labour, and it showed.

The transcription cost a commit and usually a pull request of its own after
every merge that closed anything. It is also the most deterministic work in the
queue — the tool names the item and states the exact line — so two sessions
reading the same advisory computed the same answer and opened two pull requests
for one identical insertion. And it could fail outright: a squash subject that
names no id leaves nothing to recover from, so the advisory became an error and
the number had to be read off a web page by hand.

`docket record` is the other half, and bare is its normal form: it asks the
same question `check` asks — which landed closures owe a number, and which
number does the base name for each — and writes the answer instead of printing
it. There is one reading, so the two cannot disagree, which is why the fix for
the graft-boundary case above went into the reading rather than into this
command: a `record` that declined while `check` went on printing `#401` as
recoverable would have left the wrong number on screen and the instruction to
write it pointing at that. Where the checkout is shallow and some landed
closure went unnamed, it names `git fetch --unshallow origin` — the one thing a
session can do about it, and cheaper than sending it to `check` for an answer
it already has. Crucially it takes no
merge, because a session may be owed numbers from several, and because taking
them from the base is what lets the write ride whatever commit the session was
about to make. That is the cost being removed: not the typing, but the commit
the typing needed.

`docket record <number> --merge <commit>` is the explicit form, for the number
the base cannot name — a squash subject that led with no id. It takes the
number rather than deriving it, and `closed_by` supplies what that merge closed
by comparing its tree against its parent's: `status: done` here and not there,
compared by id so a title edit renaming the file cannot be read as a closure. A
revision whose parent the checkout does not hold declines rather than
answering, because "no parent" would otherwise read as "everything done here
was closed here" and stamp one number across the whole store.

Neither form runs in CI, and one was tried. `PL-WTQR` put the write in a job
fired by the merge, which is exact — the number comes from the event, with no
subject to parse. It cannot land: a push made with `GITHUB_TOKEN` starts no
workflow, so a default branch that requires status checks can never see them
report on the commit such a job pushes, and every configuration that would
accept the push weakens that gate instead. `PL-N5WZ` records the measurement
and the decision.

An item already carrying a *different* number is refused, never overwritten.
Two numbers for one closure means one is wrong, and nothing here can know
which; a confident wrong provenance is worse than the missing one this exists
to supply.

Both halves are kept, and they answer to different failures. The write is the
mechanism; the detection is what notices the mechanism did not run.

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

So `check --verify` runs each open item's own `verify:` command instead — the
item's own statement of what would prove it done — and reports the ones that
pass. Scoped to `ready` and `needs-decision`, and behind a flag: it is the only
check here that *executes* the project rather than reading it. `next` and the
digest are asked on every session start, and a bare `check` is a pre-commit
gate, which is the wrong moment for this — the finding is about work that has
already *merged*, so a `make check` on a feature branch was spending about half
its wall clock asking about a state its own commit could not have changed.
Measured 2026-09-05 on four cores, `make check` went 60.0 s → 29.5 s. CI passes
the flag and answers on the same events it always did (`PL-P3B6`).

**`--verify-base REF` narrows the replay to the items this branch changed
against `REF`**, which is the same argument one step on (`PL-SDHR`). A pull
request cannot have changed whether some *other* item's work merged, any more
than a pre-commit gate can, and the sweep was measured at 74.6 s of a 102-command
run against 5.5 s scoped. So CI scopes on `pull_request` and sweeps on `push` to
the default branch, where the answer is a fact about that branch. The scope is
read from the diff — the item files the branch touched, not their declared
`touches`, which is a claim made before the work. **A scoped run always says so**,
on the cost line and even when the scope held nothing to run: a narrowed run
reporting nothing must never read as a whole store with nothing to report.

**It reports two findings rather than a verdict**, because a passing command is
consistent with two states no exit status can separate:

- the work landed and nobody set `status: done`; or
- the command does not discriminate — it would have passed before the work
  too, so it proves nothing and the item's commission is unprovable.

Both want a person, and both close: the first by closing the item, the second
by giving it a command that fails until its work exists. Run against this store
on 2026-09-01 the second reading was every one of the eight it named, which is
why the wording leads with the possibility rather than the conclusion.

**An error rather than an advisory since `PL-71P4`.** Not knowing which of the
two states holds does not make either one tolerable: the second leaves `docket
verify` returning `ACCEPT` on a branch that did none of the work, which is the
delegation gate open, and the first is an item that should have closed. The
message names both repairs, and reporting an ambiguity is not the same as
reporting something optional.

The severity was affordable only because of an ordering. `PL-L9JS` repaired the
seven items that passed on a clean tree *first*, so the rule needed no cutover
date, no grandfathered set, and no second dated policy sitting beside
`verify_required_from` for a reader to tell apart. Had the repair not gone
first, the rule would have had to grandfather them and carry that exemption
forever.

The transient case — a session that ran the work before editing its item —
resolves in the commit the close-out procedure already requires, since `status:
done` travels with the work. `_check_selects_nothing` stays an *advisory* beside
it, deliberately: a selector matching no test is the recommended shape for an
item whose work has yet to write the test, so only the item's author can say
which repair it wants.

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
- **Nothing ran to completion.** Every command returning "not found" is what a
  bare checkout with no virtualenv looks like from here; every one killed at
  the time limit is what a box too loaded to finish anything looks like. Either
  is indistinguishable from a clean store unless it is reported as a refusal,
  and the two want different repairs, so the sentence says which happened.

**Where only some commands could not answer, the run still reports and names
them** — among the not-checked lines, beside the runs that declined whole.
This is the same refusal made per item rather than for the whole run, and it
is what keeps the `N of M checked` in the findings above honest: a command
that was killed, or that the shell could not find, produced no evidence about
its item and is left out of that M rather than counted in it.

It has to be said rather than merely subtracted, and a status of its own is
what makes saying it possible. A killed command used to come back as exit 1 —
which is what a failing test returns — so it fell out of every finding while
still counting as checked, and the report stayed clean (`PL-T940`).

The commands run concurrently, at twice the core count and capped at eight,
which changes no answer — each still runs in the working tree against the
current state — and only the wall clock (`PL-LXR3`).

**So `check` reports what the run cost, on the line under its headline:**

```
docket: 141 open (…), 0 errors, 3 advisories
  verify: 82 commands in 31.1s (181.4s serially); slowest PL-GS5X 26.4s against a 120s limit
```

Four figures, and the reason each is there. The count and the wall clock are
what a session pays. The **serial total** beside them is the one that carries
the news: concurrency holds the wall clock roughly flat while the store grows,
so it is the number that hides the growth, while the serial total climbs with
every item triaged to `ready`. And the costliest command is given against the
per-command limit, because that margin is the question the limit is set to
answer — how much room is left before a real command starts being killed and
the check declines instead of answering.

It is a fact rather than a finding, and it sits outside the errors and the
advisories for that reason: nobody is asked to act on it, and a *change* in it
is the signal. That is what it is for. The same figures used to be written by
hand into two comments and this file, and all three went stale inside a
fortnight while the queue doubled underneath them — which nobody caught,
because a healthy store printed no cost at all and there was nothing to notice
moving (`PL-9NKK`). The dated measurements live in `PL-LXR3` and `PL-9NKK`,
where a number keeps its date and stays true; this line is the same reading
taken now.

The wall clock is set by the slowest single command as much as by the number of
them, which is worth knowing before writing a `verify:` — a full-suite `pytest
--cov` run is tens of seconds on its own, and once one is in the pool a second
costs a fraction of that. Each command is capped at two minutes so one wedged
run cannot hang the check.

**So a command far enough above the typical one is named, with what it cost.**
The person who writes a heavy `verify:` is the only one placed to reconsider
it, and was the one person told nothing — the cost arrived in one step and was
then paid by every later run. The advisory closes either way: narrow the
command, or accept a cost you have now seen. It is CI that pays it now rather
than each session, which lowers the stakes without removing them: the pool is
still bounded by the size of the queue, and that bound still only ever grows.

**And it says what narrowing would leave, rather than that the command sets the
floor.** Those are different statements and the second was wrong. A pool cannot
finish before its slowest member — true, but only the *binding* constraint
while the rest of the work fits underneath it, and this store outgrew that.
With 49 commands totalling 34 s across eight workers, about 4 s of aggregate
work sat behind a 6.9 s slowest member and the slowest member really was the
floor. At 78 commands totalling 175 s the aggregate is ~22 s against a 27 s
slowest member, and removing the named command measured **28.6 s → 23.7 s** — a
sixth of what "sets the floor for every `make check`" invites a reader to
expect (`PL-FRGP`).

So the bound is computed rather than asserted, from the serial total and the
pool's width:

```
PL-GS5X (29s) is the costliest `verify:` command this check runs: against a
0.7s median and 33s for the whole run. Narrowing it cannot take the run below
about 21s: the other 81 commands are 164s of work across 8 workers, so the
pool is bounded by the size of the queue as well as by its slowest member —
narrow the command if it can be narrowed, or accept the cost knowing what it is
```

It is a **lower bound rather than a prediction**: a pool never packs perfectly,
so the real run lands above it. That is the honest shape — this can say what
narrowing cannot buy, and must not promise what it will. Both regimes fall out
of the one arithmetic: where the queue is small the bound is near zero and
narrowing genuinely collapses the run; where the queue is large the bound is
most of the elapsed time, and the reader learns that before spending an
afternoon on it. Where the run recorded no width, or the named commands are the
whole of it, the sentence stops early rather than dividing by a number nobody
measured.

The line is a ratio against the median command rather than a number of
seconds, so it needs no re-tuning as the suite grows: measured on this store
2026-09-02, a healthy store's slowest command was 14x its median, and adding
one full-suite `--cov` put a command at 88x in the same pool. It sits at 30x,
with a one-second floor under it so that a store of trivial commands cannot
turn process-startup jitter into a finding. Durations are measured under the
pool's own contention, because the wall clock a session waits through is the
question.

### Delegation is derived, never granted

Work that a cheaper model can finish should go to one; work whose correctness
rests on judgment should not. `docket` decides which is which from the item
itself rather than from a label somebody applied.

An item is delegable when all of: its `status` is `ready`; `model_guidance` is
silent, which excludes safety- and science-classed work and open decisions by
the rule that already governs model choice; it names a `verify` command; its
`touches` is declared and lies wholly outside `protected_paths` *and*
`gate_paths`; and its effort is `S` or `M`.

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

`gate_paths` is the second list, and it refuses for a different reason: these
are the files that *measure* the work rather than the ones that produce a
consequential value, so a diff editing one has changed the instrument. `docket
verify` has always failed such a diff outright; delegability reads the same
list so that the two commands agree, because a lane that offers work its own
acceptance audit is certain to REJECT is untrustworthy in exactly the case it
exists for. The reasons stay distinguishable in the output — `touches
protected path(s) X` against `touches the checks themselves: X` — and the
protected one is reported first where both apply.

The two lists are read differently when empty, and the asymmetry follows from
which of them has a default. An empty `protected_paths` means a project has
never declared one, and delegation closes. An empty `gate_paths` can only mean
a real default was cleared on purpose — a project that told `verify` to stop
auditing its checks has not asked delegability to start.

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
band has grown past what anyone can choose between at a glance, or that most of
it is blocked on decisions nobody has made — but it will not tell you what to
work on instead, and it does not try to decide whether an item is still worth
doing. A tool that guessed at that would produce output that looks
authoritative and is not. Where it does fail the run — an open item whose own
`verify:` command already passes — it still names the two readings and both
repairs rather than picking one: it does not close the item whose command
passed, and it does not rewrite the command.

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
gate_paths = ["Makefile", "pyproject.toml", ".github", ".claude", "docket.toml"]
code_paths = ["src", "tests"]      # what `docket trend` counts as code
version_file = "pyproject.toml"
roadmap_file = "ROADMAP.md"
```

## Requirements

Python 3.11 or newer, and nothing else. Standard library only, so a
session-start hook can run it in a bare checkout with no virtualenv and no
install step.
