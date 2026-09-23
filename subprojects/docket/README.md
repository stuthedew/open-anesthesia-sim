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
docket next --oldest         # owed work longest-waiting first, so what newer work outranks surfaces
docket wave                  # which beat of the plan's cadence is due
docket list                  # the queue, one line per item
docket triage                # what is untriaged, and the rules the answers must satisfy
docket set PL-K7QX --priority P2 --effort S --classes defect   # write triage's answers; refused where check would fail them
docket withdraw PL-K7QX PL-B2B2 --because PL-34BG   # disown a recorded filing whose match was wrong
docket concurrent PL-K7QX    # what can be worked alongside it, and what a live branch is already changing
docket feature halted-step   # progress on one feature
docket gate --feature x      # every open debt item, split by feature: a freeze's first cut
docket release v0.3.0        # verify, bump the version, write the notes
docket delegable             # what a cheaper model may work, and what proves it
docket verify PL-K7QX        # prove one item's work stayed in its commission
docket verify PL-K7QX --self # ...auditing your own branch, not reviewing a delegated one
docket branch                # where this branch stands against the default one
docket flight                # which items a branch is already carrying
docket stranded              # work that exists only on a branch
docket digest --profile      # what the session-start digest asks git, and the ref set it walked
docket record                # write every pull request number the base is owed,
                             # onto the items and onto the released notes alike
docket check                 # validate the store; exits non-zero on errors
docket check --verify        # ...and replay every open item's `verify:` command
docket check --verify --verify-base origin/main   # ...only the ones this branch could have changed
```

### Capture costs nothing

`docket new` takes a title and nothing else. No priority, no estimate, no
band — those are triage, and demanding them at the moment an idea occurs is
how ideas stop being written down. Several titles in one call, because
interruptions rarely carry exactly one thought.

**It says when the capture may already be in the store, and files it anyway.**
An open item declaring a path this capture reaches, whose title is close to it,
is printed underneath the new id with its status and the shared path. A warning
rather than a refusal: the capture rule is unconditional, and a near-duplicate
that is genuinely a second instance is a legitimate filing. The key is the
declared path, with the title only ordering what the path selected — title
closeness on its own catches none of the known duplicate pairs and finds the
items *meant* to recur, the triage passes and release cuts, instead (`PL-TZ7T`
carries the table; `duplicates.py` carries the floor and what it was measured
against). A capture declaring no path — which is
every capture, since `docket new` writes no `touches` — keys on what the
working tree is changing instead: the branch's own commits and its uncommitted
edits. A capture is made *while* working on the thing that produced it, so that
is the best available guess, and it is the only one, since asking the session
for a path is friction capture may not have. `PL-0KQP` is the miss it closes —
nine of thirteen known duplicate pairs share a declared path and the key finds
them, and all four misses are that one item, filed from a branch whose commits
touched the exact path the four items it duplicated declare. Where git answers
nothing the search has no key, finds nothing, and the command behaves as it did
before any of this existed; it does not fall back to that refuted title-only
key.

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

**The commoner loss is a section, not a file, and it is a second list.** An
item file is created once and appended to by every session that learns
something about it, so an item the default branch holds can still have its
substance on a branch — and the id test above cannot see that at all. A whole
section of `PL-879R`'s brief sat unreported that way. So the command reads one
more question per item file the base also holds: is this ref's copy **ahead**
of the base's, **behind** it, or the same? Ahead is listed, with a `git diff`
naming both blobs; behind and equal are silent.

**That second list is handed a diff and never a `git checkout`**, and the
difference is the whole reason the two print separately. An item in the first
list is one the base does not hold, so restoring the branch's copy overwrites
nothing. An item in the second is one the base *does* hold, so the same
command discards whatever the base has recorded on it since — which is exactly
what `PL-XLQ5` was dealt, and what `PL-THPB` was offered when a branch's
`untriaged` copy was reported against the `done` one the base had closed.

**The direction is decided from content alone** — no date, no commit count, no
ancestry, because this runs against refs a shallow clone holds no history for
and because `closed:` is a field a branch can be holding a stale answer to. The
ref's copy is behind when it adds nothing the base's lacks, and when the base
has closed the item while the ref has not and every field the ref spells
differently is one the base spells too. A copy whose blob the base's history
has held is behind for the plainer reason that the base has been there and
moved on. Everything else is ahead, including two copies that each carry
something the other lacks: the reader is handed a diff either way, and calling
that ahead reports it rather than hiding it.

Two suppressions keep the list to something a reader acts on. A copy whose blob
`HEAD` also holds is one this session can already see, which is the same rule
that keeps a session's own capture out of the first list, applied to content
rather than to ids. And the blob comparisons come first because they are both
cheaper and truer than reading the files: of the 27,009 ref-and-item pairs this
repository held on 2026-09-21, 24,829 carry the same blob on both sides and
2,158 more carry one the base's history has held, leaving 15 files to open —
0.35 s for the whole read, against 13.4 s and 873 false "ahead" readings for a
version that compared the text of every differing pair.

### The loss that is not an item: a commit pushed after the merge

A pull request merges the head it was opened against. A commit pushed to the
same branch afterwards is merged by nothing: no conflict, no red check, no
advisory, and a default branch missing work everyone believes landed. Observed
2026-09-04 on `#284`, whose follow-up `#286` says it plainly — "that pull
request merged at its first commit, so the behavior change pushed to the same
branch afterwards never landed". The commit carried a rule the project owner
had asked for in that session, so `CLAUDE.md` § "a behavior change takes effect
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

The third part has one more shape under it, and closing it is the same argument
one step further. A commit whose *entire* diff is `docket record` output
converges **whole**, so the unit test above convicts it: every path of it agrees
with the base, and the branch reads as merged while its pull request is open. So
a commit that wrote to the queue and nowhere else is not merge evidence either —
the same reading `flight` already applies to the same commits, since a capture, a
triage pass, a recovered item and a `record` write all lead with an id they are
not implementing, and none of them is work a merge took.

**What counts as the branch's outstanding side is decided at its tip, not
across its history.** The content split asks whether the base ever held each
blob the branch introduced, which is right for a squash and wrong for a path
whose content was replaced after the branch introduced it. Two shapes reach it
and neither lost anything: a file the branch itself revised before merging, so
the squash carried only the final version; and a file the base took and then
added to in the same commit, so the base's copy is a strict superset and the
`recover:` line would overwrite the newer half with the older one. Both are
settled by the two-dot diff between the tips — a path the tips agree on is
missing from nowhere, and a path whose diff only *removes* lines is one the base
holds in full. Every silence there leaves the path outstanding, so the report
still errs toward naming a branch.

**A rewritten history is excluded from the verdict and named separately.** This
whole read is content, and a rewrite changes every commit hash while leaving
every byte alone — so a branch left on pre-rewrite history has all the marks of
one whose pull request merged. It is asked last, of a branch the report would
otherwise name, and such a ref is listed apart from the branches: this report's
own recovery copies a file, while the recipe a merged pull request leads a reader
to deletes the ref, and on pre-rewrite history that ref holds the only copy of
its commits.

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

Both directions of error are still possible and the trade is deliberate. Three
shapes go unreported, and all three are silence, which is the expensive
direction: a commit pushed after the merge that happens to leave one file in a
state the base has held; a post-merge push to a branch whose every pre-merge
commit was re-merged against a base that had moved under it, since neither side
then has a whole commit; and a post-merge push to a branch whose only wholly
landed commit wrote to the queue alone. All three are accepted only because the
alternative — the content split on its own — fired in every session's digest,
which `CLAUDE.md` calls a defect in the check rather than coverage. Each of the
three narrowings was bought with an observed false positive, and each false
positive led a reader to a ref deletion rather than to a copy.

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
commands for the ordinary cases: a branch behind with nothing of its own is
restarted, a branch behind with work of its own merges the base in. Rebase is
deliberately not offered - telling "only capture commits" from any other
commits means guessing, and a rebase of a pushed branch needs a force-push,
which this project's squash-merge path exists to avoid.

**Two states replace that advice rather than adding to it, and both do so
because the ordinary commands would destroy something.** The rewritten history
below is one. The other is a branch whose pull request has already merged
(`PL-8M8H`): a squash merge leaves the branch containing none of the commits
that landed its content, so `ahead` counts them all, `restart` - which fires at
`ahead == 0` - is never reached, and the branch reads as "merge the base in".
Nothing merges a merged pull request a second time, so following that advice
pushes a commit that lands nowhere, and `#284`'s follow-up was lost exactly
that way. The verdict is read from the content instead, by `vcs.landed_whole`,
which reuses `orphaned`'s narrowed reading whole rather than re-deriving it -
the whole-commit test and the queue-only exclusion both travel with it. It is
asked only where the counts would otherwise say "merge", so the other four
states pay none of its three git calls, and it is ordered below the rewritten
case, which a content comparison cannot tell it from.

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

### A git that did not answer is not a git that answered nothing

Every read in `vcs.py` goes through one runner, `(args, root) -> str`, and until
`PL-Q9Z1` that runner collapsed a non-zero exit, a missing git and a timeout
alike to the empty string — which is byte-identical to git answering that there
is nothing to say. So each reader adjudicated the silence for itself, and they
disagreed: `_superseded` read a failed `git diff --numstat` as the two tips
agreeing about every path it was handed, and one such call took
`branches_in_flight` from fourteen `editing` marks to none with
`FlightReport.unreadable` empty in both cases.

A failure now comes back as `GitSilence`, a `str` subclass. It still reads as
the `""` every call site has always seen, so the runner's shape is unchanged and
a caller with no use for the distinction needs no edit; a caller that must not
conflate the two asks `answered`. What separates them is git's own exit codes,
measured rather than recalled:

| Call | Exit | Read as |
| --- | --- | --- |
| anything git could answer | 0 | the answer |
| `rev-parse --verify --quiet <no such ref>` | 1 | "no such ref" — an answer |
| `merge-base` on unrelated histories | 1 | "no merge base" — an answer |
| `show <rev>:<path the rev lacks>` | 128 | "not there" — an answer |
| `diff`/`log`/`ls-tree`/`rev-list` on a bad revision | 128 | a silence |
| `diff` outside a repository | 1 | a silence |
| a mistyped option | 129 | a silence |
| git missing, or the ten-second timeout | — | a silence |

The `show` row is one exception and it is forced rather than chosen:
`cat-file --batch`, which the runner serves the same question from when it can,
prints `missing` and exits 0 for an absent path *and* an absent revision alike,
so reading the fatal exit as a failure would make the two paths disagree about
one question.

The `diff` row outside a repository is the other, in the opposite direction.
There git compares two paths on the filesystem under the same name, a form that
implies `--exit-code`, so its 1 means a path it could not read, not git saying
no. Inside a repository a revision diff never exits 1. `changed_items` read
that 1 as a branch that changed no item until `PL-19T3`.

A public read wraps its runner in `_Silences` rather than threading a flag out
of every helper, and reports what went unanswered as `declined`. It over-reports
rather than withholding: an item wrongly marked in flight costs a session one
look, and one wrongly unmarked costs two sessions a merge conflict. On a healthy
checkout eight reads put 174 questions to git and none went unanswered, so the
field is silent in the ordinary case.

`subprojects/docket/tests/test_vcs_silence.py` is what holds this, because prose did not —
`_superseded`'s docstring stated the correct direction in three cases while the
code inverted two of them. It runs every public read against a real repository,
then again with its *n*-th git call silenced, once per call, and holds the
answer to declining or reporting everything the truthful read reported. A read
the fixture gives nothing to find fails rather than passing, and a read added
later that takes a runner fails a registry guard until it says which it is.
Every public read is in it: the last that could not decline, `default_base`,
closed with `PL-73P0`. Each read also runs once from a directory in no
repository, where it must decline. Silencing one call at a time cannot reach a
read whose every call git answers there, which is how `changed_items` came to
answer with no repository at all (`PL-19T3`).

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

**Three exceptions, each read from the item rather than from the commit, and
all three from one shape of commit.** The walk records a queue-only commit that
leads with an id *and* changes that id's own file, and `_own_edit_claims`
promotes it where the item says the queue edit is the work. The conjunction is
what keeps out the other items a pass writes: until 2026-09-22 the first
exception below was read off any edit to an item's file, so `PL-0HPV`'s
`verify:` reorder, led by `PL-0HPV`, claimed four queue-only items it merely
passed through, none of them named by any subject, until its pull request
merged (`PL-3W3P`). `flight` and `precedence` read the same three through the
same helper, so the verdict `show` prints names every carrier the mark does.

**An item whose own work *is* a queue edit is the first.** A release tag item,
a triage pass and a stranded recovery all deliver nothing but a write to
`docs/items/`, so the path test excludes the very work it was built to find.
`_queue_only_work` asks the default branch what the item declares in `touches`
and promotes it where that never leaves the queue; an item the base does not
hold at all is a capture creating its own file, and is not promoted. Measured
against the eight false marks above, not one declares `touches` inside the
queue alone, so the fix costs none of them back. Measured live on 2026-09-14,
`PL-XR8K` was being closed on a branch and appeared in no reading of the report.

**An item at `needs-decision` is the second.** Its next step is a decision,
and a decision is recorded into the item file, so a design round can run its
whole course without a diff outside the queue — and on this project it often
does, because implementing the decision is separate work. Observed 2026-09-19:
`PL-BHVM`, the top of the whole queue, had three commits pushed with every
subject led by the id and a live session on the branch, and `show` called it
startable; the mark appeared only when the round happened to edit
`ROADMAP.md`. So `_deciding_on_base` promotes the shape where the default
branch holds the item at `needs-decision` (`PL-VYSP`). The conjunction is
deliberate: a round re-points its cluster, writing a dozen other items' files,
and those stay file edits rather than becoming claims on items other sessions
may be working. Counted before it was adopted, over the 1,006 commits then on
`origin/main`: the rule the item itself
proposed — any queue-only commit changing the leading id's own file — would
have marked 316 (commit, id) pairs, 81 of them captures creating the file and
120 more triage passes; the status test left 23, of which 21 were the item's
own decision work and two were notes written into one item on consecutive
days. One more read keeps a stale capture out: a capture that merged by another
route and was triaged to `needs-decision` there leaves a branch that also leads
with the id and changes its own file, so the commit's own parent is asked
whether it held the file — a round writes into a file that exists, a capture
creates one. Three such branches, all eleven days old, were promoted the first
time the status test ran live. Two design rounds on one item therefore get a
verdict.

**An item the branch closes while the default branch holds it open is the
third.** A grooming pass disposes of items it never claimed: `#914` dropped
`PL-027`, `PL-043` and `PL-ZBR6` in queue-only commits leading with each id,
and `docket next` went on offering all three, to sessions that would have
started work another had already decided to drop (`PL-8FJK`). The branch's
*tip* is read rather than the commit, so a branch that dropped an item and then
reopened it claims nothing, and a closure the base already records - after the
squash, or by another route - is not open to be closed. The one thing it cannot
see is a closure under a subject that does not lead with the closed id: that
stays a file edit, because reading a closure off any edit is `PL-3W3P` again,
and `CLAUDE.md` already requires a closing commit to lead with every id it
closes.

**A claim on an item the default branch has no copy of is kept, and worded
differently.** This is the opposite direction from the three exceptions above,
and the only one measurement refused outright. A capture commit that also
reaches past the queue claims the ids it merely filed — `CLAUDE.md` requires
the leading id and requires the capture, so the collision comes of keeping the
rules, and it fires on exactly the commits whose purpose is to hand work to a
later session. Withdrawing that claim was measured at three widths against the
913 `(commit, id)` claims in this project's history, and refused at all three.
The rule the item proposed — an id the base does not hold is one this commit is
filing — takes 263, of which 221 create the item at `done`, `dropped`, `ready`,
`needs-decision` or `blocked`: an item filed *and finished* on one branch,
which is the housekeeping rule, the behavior-change rule and the fix-now door
each being kept. Narrowing it to ids the branch still calls `untriaged` takes
22, and 12 of those did the item's own work — `PL-M2SD` shipped
`tools/generator_check.py` beside the file that filed it. No `touches` test
separates them either: the motivating commit carries `vcs.py`, the first path
its captured item declares. What separates a capture from an item filed and
worked is intent, and nothing in the repository records it.

So nothing is withdrawn, and what changed is what the reader is told. An item
the base has no copy of is in no other session's store, so nothing can offer it
and refusing it refuses work that was never on offer — about the very branch
the `stranded` line beneath it names as the place to recover the item from.
`Branch.on_base` carries the fact; the digest sends those ids to `Filed on a
branch, not yet on <base>` and to `bin/docket stranded`, and `docket flight`
marks their rows `filed there` (`PL-3CTW`). `PL-G5ZH` sat in both readings at
once on 2026-09-19, told to be left alone and to be recovered.

**A ref naming nothing at all is the third outcome, and it is reported rather
than dropped.** `unreadable` says the commits could not be read; `unattributed`
says they were read and named no item — no id in the branch name, none at the
front of any subject. Such a ref used to be dropped silently, so the report was
complete about what it could not read and silent about work it could. It is
named in `flight` and in the session digest with nothing suppressing it,
because the steady state is empty: `tools/branch_id_check.py` fails a
`claude/*` branch of one's own that names no id, and on 2026-09-14 none of this
repository's ten unlanded heads was unattributable. A bookkeeping push is not
one of these — a capture, a triage pass and a `docket record` write all name
the item they concern, so they are attributable even though `_annotates_only`
withholds their claim. That distinction is what keeps the line quiet.

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
work nobody will merge. So each line carries how long ago the branch's last
unmerged commit was made and the reader decides, the way `stranded` reports
rather than decides.

**It is elapsed time, told to the minute.** The age used to be the difference of
two calendar dates, which counts midnights rather than time: a branch committed
55 minutes before a read at 00:29 reported "last commit 1 day ago", reading a
live session as abandoned work (`PL-3QM9`). It is now the commit's full
timestamp subtracted from the clock, in minutes under an hour, hours under a
day and days beyond, each rounded down so a branch never reads older than it
is. `--now` fixes the clock for a test; `--today` alone is read as the last
instant of that day, which ages every earlier commit by the whole days it
always did.

**And each line says whether a pull request is open on the branch**, because a
branch outlives its session and an age alone cannot fire in the first hour. PR
`#757` sat green for 25 minutes after its session was archived while its three
items read as somebody's work (`PL-7TVT`). With a pull request open the work is
written and waits on review, whatever became of the session; with none, a
young branch is usually a live session, and one whose session ended reads the
same until its age grows - the report says so in those words rather than
telling the reader what an age means. Nothing a checkout can read closes that
last gap. The session-start digest carries each in-flight item's age too, and
no longer ends "do not start these again", which presumed a session behind
every branch; `show` says the branch already carries the item's work, which is
true of a live session, a pull request and an abandoned branch alike.

**Except for one case the age does not decide.** A branch whose every claimed
item is closed *in its own copy* and which nobody has a pull request open on is
finished work that has stalled: nothing is being implemented there and nothing
is being reviewed, and the report was telling every session to leave it alone.
`claude/hopeful-allen-tetrje` sat that way for three hours with two items at
`status: done` and ten item files existing nowhere else, and surfaced only
because the project owner asked whether the feature had been built (`PL-Q664`).
So `settled_branches` reads both facts and `docket flight` moves those rows
into a section of their own. Either fact alone is ordinary — a branch under
review has closed its items, and a branch with no pull request is usually a
session still working — which is why neither is read on its own.

It changes what a reader is told and never what is in flight. The ids stay
excluded from `docket next`, because the work exists on a branch and offering
it again would have a second session redo what is already written. What moves
is the row: out of the list whose closing lines say what an age and a pull
request can and cannot establish, and into one that says plainly that nothing
there is being worked.

**The package does not ask the forge, and will not learn how.** It answers from
a bare checkout with no network and knows nothing about GitHub; which forge a
project uses is not a fact about its queue. So the caller passes a way to ask —
`open_pull_requests_command` in `docket.toml`, a command printing one branch
name per line, optionally followed by the pull request's number — and the
contract is its exit status: zero means it looked, and
non-zero with nothing on stdout means it could not. The two must never arrive
as the same empty answer, because "could not look" read as "nothing is open"
would announce that finished work has stalled on every branch waiting on
review. `SettledReport.asked` carries the distinction into the wording: "every
item closed, and no pull request is open for it" when the forge answered,
"every item closed" and a line saying the rest went unread when it did not.
A project configuring no command gets the second reading, and `flight
--no-remote` asks for it.

**The forge is asked once per run, wherever a branch carries anything.** It was
asked only where a branch had finished, which kept `docket flight` off the
network on a normal day; the pull-request clause on every live row (`PL-7TVT`)
needs the answer on every run with a row in it, and the settled reading and the
rows share the one request. Measured on this repository 2026-09-22: 1.15 s
median with the lookup configured and 0.65 s with `--no-remote`. A report with
no row asks nothing, and every way the request fails is a row printed without
the clause, under a line saying it could not be read.

Every silence fails toward the live reading. A ref whose commits went unread,
an item whose file the ref does not hold, a `git show` that came back empty:
each leaves the branch in the ordinary list. A live session wrongly called
finished is the expensive mistake; finished work wrongly called live is the one
this repository already had, and it is visible the moment anyone looks at the
branch.


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

**That signature catches the shape it was built for and is not a proof of
completeness**, which is worth stating because the asymmetry is easy to read the
wrong way. A parentless commit means the walk ran off the end; a walk without one
does *not* mean it stopped soundly. Where the default branch reaches the root
down one path and is grafted on another — which a single `--depth` produces,
because depth is counted per path from the tip — a branch forked from a commit
below the graft descends through commits `^origin/main` cannot exclude and then
terminates against the fork point the short path still reaches. Every commit it
emits has a parent, so the guard stays silent and the default branch's own
commits are reported as somebody's work.

The limit is accepted rather than unnoticed (`PL-W1LN`, 2026-09-13). No sound
replacement exists inside a truncated checkout: the question is whether an
emitted commit is one the base reaches in the *full* history, and those commits
are precisely what the clone lacks. Naming a ref unread whenever the base is
grafted is sound and silences this read in every agent container; fetching to
deepen answers exactly and breaks the bare-tree, no-network rule; distrusting a
commit older than the base's newest graft is cheap and rests on dates a rebase
moves. So the behaviour is pinned by a test that asserts the wrong answer on
purpose, which makes changing it a decision rather than an accident.

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

**A third mark on the triage list answers a different question: was this item
already worked when it was filed?** The two above are about other sessions;
this one is about the commit that created the item's own file. `filed_with_work`
reports an untriaged item whose file was *added* by a commit that also changed
something outside the queue and whose subject leads with that item's id — #635
filed `PL-0J9K` and `PL-MMVF` while landing 385 lines of `vcs.py`, and both were
still untriaged on `main` days later, offered to the project owner as live work.
It is the shape `PL-3CBS`'s landed-work advisory cannot reach at all: that one is
keyed on `verify:` and scoped to `ready`, and an item captured and worked in one
commit never passes through `ready` to acquire a command.

**It prints a pointer and never a verdict**, which is a measured limit rather
than caution. `PL-SWP3` counted three keys over this store. Without the subject
clause the shape matches 248 of 319 open items and 10 of the 11 rows a triage
pass reads, because filing findings alongside unrelated work is what `CLAUDE.md`
asks for. With it, 6 — and none of the 6 is an item that should have closed,
because sessions lead a subject with the ids they *captured* as readily as the
ids they *worked*. Replayed over history it fires 22 times at 27% precision, and
the script adjudicating it misjudges in both directions. Whether such a commit
*finished* the item it filed is a relation between the item's intent and the
diff's content, not a property of the diff, so the reader is the only thing that
can decide it. What prints is the commit, the pull request and the paths; the
sentence asks for a read.

It lives on `triage` alone, for the reason the mark above lives on `triage` and
`show`: that is the moment the question is live and a wrong answer reaches the
owner. As a `docket check` advisory it would carry six standing false positives
forever, which is the defect the "a check earns its place every run" rule names.
It costs one `git log` for the store plus one `git show` per item that survives
the subject clause — on the current list, none. A shallow clone declines rather
than reporting nothing filed, since its missing commits are the oldest and an
old item would read as filed by nobody.

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

`docket set` writes the answers. `docket set PL-K7QX --priority P2 --effort S
--classes defect --touches a.py --status ready --verify '...'` sets the named
fields, renders the front matter in the order every tool-written file has, and
keeps the file's name whatever the title now says — a rename arriving as a side
effect of a field write conflicts against whoever else holds the file. That is
the rule for every field write rather than this command's own: `record`'s `pr:`
and a cut's `milestone:` keep the name too, and bringing a drifted one back
into line is its own pass (`PL-LBR6`, `PL-QMC0`). It
refuses three things and adds no rule of its own: a flag it does not know,
since a misspelled field is silently ignored by every reader of it (`--pr` is
refused rather than read as `--priority`, so no abbreviation lands on the wrong
field); a value the item already records with a different one, unless
`--overwrite` says so, because replacing a value nobody looked at is the
duplicate-key hazard arriving through the front door — `status` is exempt,
since moving it is what triage does; and any write after which `docket check`
would report an error it did not report before, printed in the checker's own
words and with nothing written. The brief is prose and stays a hand edit; an
empty value removes a field. Until the command existed every triage answer was
typed into the front matter by hand or by a helper the session wrote and threw
away, and 96 of the 1,189 files in the store this grew in carried a key order
no tool had written (`PL-L4YG`).

**A write that moves a status into `done` or `dropped` names the items that
closure just took the last recorded blocker off.** The reverse of `blocked-by`
is derived rather than stored: a `blocking:` field was considered and refused,
because it duplicates an edge `plan.promotable` already computes and adds a
second place for it to be written wrong (project owner, 2026-09-20, ratified,
over adding the field). The data was never what was missing — `docket check`
has printed the same set all along, and `docket next` names it to a session
choosing work. What was missing is that neither fires at the moment a blocker
closes, so the reading reached only a session running a deliberate grooming
pass: `PL-JFQ3` ran one over nine items, and `PL-8G48` and `PL-CHQY` ran two
more over the same four items four days later, two sessions filing for one
batch on one day (`PL-PQC7`).

It prints what *this* write released rather than the standing backlog, which
is the half no other command can attribute to a cause, and it names without
promoting: 6 of 13 items reached this way across those passes were genuinely
startable, and a recomputed status would have put `PL-WZVZ` — unbuildable —
into `P1` and onto the debt gate (`PL-6T44`). A `blocked-by` write can make an
item promotable the instant it lands; that is a different event with a
different reader and is deliberately left silent.

**A write that moves `status` or `blocked-by` names the passages it leaves
saying the old state.** `docket set --status ready` is a one-line diff that
never shows the paragraph further down reading "Left at `needs-decision`", and
closing an item never shows the briefs that still say they wait on it; nine
such passages stood unreported on 2026-09-22 (`PL-8YXJ`). So the write prints
what `docket check`'s brief reading would newly report - its own brief naming a
status it has left, another brief still waiting on or landing with the item it
just closed, a prerequisite it no longer declares - to the session holding the
context, which repairs each in the same commit: reworded, or opened with
`[superseded YYYY-MM-DD]` where the passage is history worth keeping.

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

`docket next` ranks the work and says why it picked it. `P0` first, then a
recorded generator, then what the roadmap's current step includes, then —
*within* a priority band — work in a feature already underway, the one nearest
finishing first, because a shipped feature is worth more than equal progress
spread across several. Work already in flight on a branch is excluded rather
than ranked low.

The step's scope is preferred *absolutely* rather than as a tie-breaker inside
a band, because the priority field cannot express the phase: `docket check`
pins `safety` and `science` items to `P1`, so the top band is product work by
construction and a tie-breaker there would never fire in the case the rule
exists for. `P0` sits above it: a hotfix outranks the phase.

An item carrying a sound `root-cause-of:` **and** a `generator: live`
verdict sits between the two, above the phase and above every band. Promotion *within* a band was the alternative and
was refused by the project owner on 2026-09-17: *"We constantly add more P1 as
we develop, so these never get done and the bugs pile up."* A band that is
itself growing moves nothing in absolute terms, so the decision is about what
a generator competes with rather than where it sits in a list. The safety floor
is untouched by it — a clinical defect that has to be fixed now is what `P0` is
for, and `P0` still outranks a generator. The reason line says it was ranked as
a generator and names the items it explains, so a `P2` leading a queue with
`P1`s in it reads as the ranking meaning it.

The verdict is the second of two tests and it is the one that moves the rank. A
cluster recorded but marked `generator: spent` ranks on its own band: it is a
generator for the audit, and the tier is for a mechanism still being paid for.

An item carrying a sound `impairs-generators:` sits on that same tier, not
below it — "the same priority as a generator" is what was asked for, so where
both are startable the ordinary terms below settle the order rather than a
sub-order nobody decided. Its reason line quotes the declared prose instead of
naming items, because that prose is the only evidence the claim has.

### What newer work keeps outranking: `docket next --oldest`

Every term `next` ranks on favours work that is newer, more urgent or more
central, so an owed item that is none of those waits while new work keeps
arriving above it. Priority scheduling calls that *starvation*, and its
standard remedy is *aging*: a request's priority rises the longer it waits
(Silberschatz, Galvin and Gagne, *Operating System Concepts*, 10th ed., the
CPU-scheduling chapter's section on priority scheduling). `--oldest` is aging's
extreme form, pure age order, and the simplest to audit. It answers the
question "what have we forgotten" beside the plan rather than changing it: a
bare `docket next` prints exactly what it printed before the flag existed.

- **Order.** Longest-waiting first by `added:`, ties by band and then id, `P0`
  on top whatever its age. Age is `--today` minus `added`, so no git read is
  needed and a bare checkout answers.
- **Population.** What `next` could start, narrowed by a lane and `--effort`
  exactly as `next` narrows it, less *new work*: items classed in
  `new_work_classes` (`feature` and `planning` by default), which are the work
  a gate protects rather than work owed. Everything else is owed, including the
  `docs`, `infra` and `test` work the debt gate never counts, which is the half
  at risk of being forgotten. A debt class or `needs-decision` keeps an item
  owed whatever else it carries, so `docket gate` and this cannot disagree about
  one item.
- **Decisions apart.** Owed work at `needs-decision` is listed on a line of its
  own, oldest first, never ranked: its next step is the project owner's answer,
  and ranked by age the oldest unanswered decision would hold the top for good.
- **Never silent about the plan.** Each pick carries the placement sentence
  `next` writes, so an off-gate pick says so, and the last line names the plan's
  own pick for the same lane and effort, with the command that explains it.

The flag is `--oldest` rather than `--debt` because `docket gate` and the
roadmap already use *debt* for the narrower class list a gate holds, and one
word meaning two sets would make two commands disagree about what debt is.

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

    By lane, for a second session: product PL-F52R (P1, on the debt gate), workflow PL-Y0RZ (P2, not on the gate); 15 in neither lane.

It costs one line in every digest, single-session ones included, which is why
it reads as an offer rather than an instruction, and why it is omitted entirely
where no boundary is declared or neither lane has anything startable. The
spanning count rides the same line: two picks read as the whole queue without
it.

Each pick carries its band and its relation to the gate, and deliberately not
its title. An id alone cannot tell a `P1` sitting on the debt gate from a `P3`
the roadmap places nowhere, so an offer worth waving through and one worth
questioning read identically — which is what `PL-Z27P` fixed, after the two
lines naming the workflow lane to this project's owner turned out to be the
only places it is ever surfaced to them. Titles stay out because this line is
resident in every session's context and the `Top:` line above it already
carries one in full; `placement_clause` is the shared renderer, and it names a
gate only while one is open, since with the gate clear "not on the gate" would
be true of every item in the store.

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

The same holds one line further down, where the counts are. `check`, `digest`
and `next` each print how many grooming advisories the store has, and `analyze`
skips the check behind any input it was not handed - so a command that
assembled its own inputs printed a smaller number with nothing on the line
saying which question it had skipped. The digest never asked for `closures`,
and reported 10 advisories against `check`'s 19 (`PL-VKGJ`). All three now
build their report through `cli._complete_report`, which gathers every input in
one place, so a new one reaches every count-printing command in the commit that
adds it. `landed` is the single exception and stays the caller's argument: the
`verify:` replay is behind `--verify`, and `make docket` - the command the
digest's own line names - does not pass it either. The digest pays 279 ms of
git reads for the agreement, on a 947 ms command, none of them over the
network.

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
- `Required scope`, by the `(queue item …)` slot its entries declare in —
  `(queue item PL-DHV7)` after an entry's bold title, `(queue items PL-1FT6
  and PL-HJPY)` where one entry completes two. Reading that subsection *in
  full* was the same over-read one level down: citing the id that re-briefed
  an entry is how the roadmap records provenance, so every correct maintenance
  edit added a member and the count drifted as the file was kept up to date
  (`PL-HWW1`);
- `Explicitly out of scope`, in full — its heading states the claim, so no id
  under it needs a grammar of its own.

Out-of-scope work is marked, never hidden. Whether an item is *really* out of
scope is a judgment about the prose around its id, and the command reads
structure rather than sentences.

Three things follow, and they are limitations in the same way the concurrency
answer below is:

- Scope written without a declaration is placed nowhere. Declaring the id in
  the slot is what places it — and that cost is no longer paid in silence:
  `tools/doc_check.py` fails an entry declaring none where the section's other
  entries declare, so a milestone cannot quietly be smaller than it reads.
- An exclusion written anywhere but under `Explicitly out of scope` is
  invisible rather than reported. Silence is the honest answer to a sentence
  the command cannot read, and the safe one: an unread mention makes no claim,
  where an over-read one told a session that work a milestone excludes was the
  work that milestone was waiting on. The heading itself *is* read, onto
  `MilestoneSection.excluded_ids` — `tools/doc_check.py` compares it against
  `Required scope` and fails a milestone naming one id under both (`PL-NBCS`),
  and the ranking reports an id under the **anchor's own** exclusion heading as
  ruled out rather than unplaced (`PL-6P9Y`). Another section's exclusions stay
  out of it: one the project has passed says what was true then, and one it has
  not reached is a decision that milestone's own scoping round may revisit.
- A released milestone's section places nothing. Its narrative records where a
  problem was raised, not what is current work. Released is decided by the
  version the project is on, never by position relative to the anchor: an
  unreleased section *below* the anchor - the Qt port, numbered as a patch and
  placed between Gate 1 and v0.5.0 - is work the step has not reached, and its
  ids read as later work mapped to it (`PL-FWJF`).

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

**The same-file tier is reported by path rather than by item, rarest group
first** (`PL-PGZK`). Tiering stopped the false refusals; it left a list whose
entries all read alike, so the whole of it had to be read to find the two lines
that mattered. The distribution is a short head and a long tail — measured
2026-09-13, 237 open items declare 136 distinct paths, the largest of them 32
items, while 72 of the 136 are declared by exactly one open item and so can
never collide at all. One line per path collapses the head into something a
reader can skip deliberately, and ordering by group size puts the rarely
declared paths, where a collision is probably real, at the top. Nothing is
dropped: every item still appears on the line of each path it shares, so this
orders the evidence rather than filtering it.

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
rather than reported as a branch that changed nothing — a corroboration that
predates the failure channel below and is kept, because it also catches the diff
git answered wrongly rather than not at all. And the answer is bounded by what
has been *pushed*, like everything else here.

### A debt gate is computed, not transcribed

A project that clears recorded debt before starting a milestone has to produce
the list of what is owed, and doing that by hand means reading every open
item's classes and status, applying the rule, and splitting the result by
whether the milestone clears the item itself. `docket gate --feature <name>`
does the decidable part of that pass: every open debt item in the store, the
items carrying that feature on one side and the rest on the other, with effort
totals for each. The feature is a first cut and not the rule. Which debt a
milestone clears itself is whether its `Required scope` names the id, the two
differ in both directions, and so the output names its split for the feature
and never for the rule; once a list is frozen, `docket wave` reads it against
the rule (`PL-RFHH`).

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
and reports the version, the versions ahead of it the plan has already given
out, the step, the gate's size and how much of it is closed, and which beat of
the cadence that leaves due. The reserved set is printed rather than only
consulted: the release guard refuses a bump that lands on one of those numbers
and names the milestone holding it, so without the list a reader sees the
verdict on one version and nothing about the rest. It splits the open
entries once more, from the items rather than from the roadmap: an entry whose
`blocked-by` chain leaves the frozen list — a later milestone, or an item the
list does not hold — cannot be closed by clearing this gate in any order, so it
is counted apart and the beat asks for the rest. The entry stays on the list;
the list is frozen, and this is a count of what it can be asked for today.

A second carve-out splits them again, and this one is read from the roadmap:
debt the gated milestone's own `Required scope` names is cleared *by* that
milestone rather than before it, so the gate is open once everything outside
that scope is clear. Membership in `Required scope` is the whole test, because
that is how the rule states it — the group heading a frozen list writes the
same split under is not parsed here. `tools/doc_check.py` holds that heading to
`Required scope` instead, for the current gate, so the two cannot come apart
the way v0.6.0's did, where two entries sat under "Cleared before" after the
scope had named them (`PL-J6HP`). The two carve-outs
are disjoint and `blocked_outside` is computed first: an entry that is
milestone work *and* waits on work off the list is not something the milestone
can simply clear, and the three counts add back up to the open one either way.
Without this the beat kept asking a gate to clear work that implementing the
milestone is what closes, which is a target the roadmap forbids.

Once that gate is clear it counts the milestone's own `Required scope` the same
way, and the split decides the beat: ids still open leave an `implement`, and
all of them closed leaves a `release`. Without it a milestone recording a gate
*and* a scope could never reach `release` at all, whatever the state of that
scope — it was neither of the two arrangements that had one, and the beat stayed
`implement` on a finished milestone while the digest declined the cut. That
count is strict where the gate's is not: a scope id waiting on work outside the
milestone still holds the milestone, because it ships when its scope is done and
not when the remainder is somebody else's fault, and an id the store does not
hold withholds completeness rather than being guessed either way.

It also lists what the gate's section defers: every entry under a `### Declined
...`, `### Deferred ...` or `### Sequenced ...` subsection, with its state read
from the store — an open item's status, the release a shipped one went out in
(its `milestone:`), the date a dropped one closed, and "done, not yet released"
for work no cut has taken yet. A deferral entry is never removed, since the
gate is a snapshot, so this is what separates one still outstanding from one
that shipped. The roadmap used to carry that as a release name written beside
each closed entry, which copied the field and was missing from 36 of 84 closed
entries when it was retired (`PL-B60Q`). The deferral subsections are parsed in
`roadmap.parse_milestones`, beside the frozen list and `Required scope`, and
`tools/doc_check.py`'s disposition rule reads the same parse (`PL-J6HP`): the
entries' leading ids are what this prints, and every id beneath a deferral
heading, prose included, is what that rule counts as disposed.

Every arrangement question in that composition — which row the project stands
on, what comes before what, which section places a blocker — is put to one
object, `roadmap.ReleaseTrain`, resolved once at the top of `wave` from the
timeline's row order. Four consumers used to re-derive the order by comparing
version tuples, and each disagreed with the table somewhere (`PL-2T03`).
Released stays decided by the version the project is on; the train also
carries what the plan and the project disagree on — a milestone row the
version has passed with no release of that number in the version table, and a
section no row bears — and `wave` prints those under their own heading and
exits non-zero, the digest's plan line flags them, and the release hand-off
states a reached-or-passed number beside the table row it already asks for
(`PL-Y1L0`). `wave` adds the two statements the train cannot make because they
need the store: a row the table *does* record as released, whose section's own
`Required scope` still has open ids, which is that same reversal one run later,
after the cut has written the row the hand-off asked for (`PL-LN3T`); and the
same row whose section's frozen list still holds an open entry that no section
ahead places, which is the reversal in the list's own subsection. An entry
deferred to a later gate on `ROADMAP.md` § "The cadence" beat 3's terms is never
that, because the later gate holds it (`PL-SZJ2`). The gate
block splits the entries it cannot clear into those the
plan sequences ahead of the gate, named with the row they wait for, and those
waiting on work placed later or nowhere (`PL-7CSP`).

The milestone the beat is about is read off the timeline row rather than the
`#` column. A `—` row bearing a section with a `Required scope` of its own,
placed between a gate and the milestone that recorded it, comes before that
milestone: once the gate is clear the row's own scope is what the beat counts,
`implement` while it is open and `release` once it has closed, and the gated
milestone returns as the beat when the row's number is cut. The Qt port is that
row — `v0.4.26`, between Gate 1 and v0.5.0 — and anchoring on the next
*numbered* milestone read straight past it: `wave` printed `implement v0.5.0`
for the whole of the port and `next` told every session the port's items were
placed by no section (`PL-FWJF`). What is passed over is stated rather than
guessed at: a row with no section, or one with no `Required scope`, cannot be
counted and leaves the beat on the gated milestone, and a patch-track row bears
no section by grammar, which is what keeps `v0.4.x` the step while the port is
the work.

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

**A release that cannot finish writing itself is resumable, and one that is
not resumed is reported.** Three things reach disk — the `milestone:` stamp on
every item going out, the version, and the notes — and the failures between
them are two different shapes.

The first is a write that is *rejected*, and it is settled by proving the bump
before anything is stamped. Stamping first left the store recording a release
that never happened, with nothing saying which stamps to unpick; the next run
then reported nothing to release, because the work it would have shipped
claimed to have shipped already. So `prepare_bump` settles everything the bump
can reject — an absent version file, one carrying no version field — before
the first stamp is written, and hands back the text to put there. A rejected
file costs an exit code and a message naming it, not a half-written store.

The second is a write that is *interrupted*, which no ordering prevents: the
stamps go in a file at a time, so a lost container leaves some written and the
notes unwritten however the three are ordered. What the ordering decides is
only which half is short, and the re-run was the dangerous part, because it
succeeded — `unreleased` reads a stamped item as already shipped, so the second
run cut the remainder under the same name, wrote notes covering it and exited
0. A 33-item release recorded as 7, caught by a person reading the two printed
counts side by side (`PL-1MKQ`).

So the cut of a named version is idempotent instead. `release.unrecorded_milestones`
defines an interrupted cut once — a milestone stamped in the store that no
notes file records — and both halves of the repair read it: `cmd_release`
folds those items back in and re-cuts the whole release, and
`checks._check_release_notes` reports the state as an error wherever the
re-run has not happened. A run asked for a *different* version while a cut is
unfinished is refused, since two numbers over one unfinished cut make both
sets of notes permanently wrong. Its floor is the lower of the oldest version
with a notes file and the current version: the first exempts releases cut
before the project wrote notes at all, the second covers a first release,
where there is no notes directory to take a floor from.

**A notes file stops claiming partway down, since `PL-P669`.** Below the
`### also inside this tag's span` heading are bullets of the same shape naming
work *another* release stamped - a closing pull request inside this tag's span
that this cut did not name, and the release that does describe it, which
`ROADMAP.md` § "Tags" is the reasoning for. Read as claims they are the exact
shape `_check_release_notes` reports as the notes and the store disagreeing, so
`release.notes_claims` splits the file at that heading and the three readers
take the first half: `notes_by_version`, `unreferenced_by_version`, and
`restate_references`, which puts the second half back byte for byte rather than
appending a second reference to a line already carrying one.
`doc_check.check_tag_span_covers_its_notes` is what fails the next span that
needs a pointer and has none.

**The offer a session reads is reconciled with the plan before it is
printed.** `readiness` reads the store and only the store, which is what
makes it honest about what is finished and blind to what a number *means*:
the version it arrives at is arithmetic on the last one, and a project that
plans in versions has usually spent that number already. Cutting it then is
not a smaller release than the plan's — it is the plan's milestone going out
under its own name with most of it missing, which a tag makes permanent. So
`release.release_offer` puts the suggestion beside what the plan has already
spoken for — every version `ROADMAP.md` names *ahead* of the current one, which
`wave` carries as `reserved`: where one of them is the number the bump arrived
at, the digest withholds the offer and names what holds it; where the plan is
itself asking for a release, the digest offers the version the roadmap named
rather than the one a class label inferred. The digest's release line and its
plan line can no longer recommend opposite actions.

A reading of the plan rather than of the reader's position in it, and that is
the part with a history. The comparison began on one object `wave` binds — the
step the project stands on — and a second was added when that turned out to
hold no number in the live arrangement, where the step is the `v0.4.x` patch
track carrying `(0, 4, -1)`, a track marker rather than a number anything can
be cut at, while the number the bump arrives at belongs to the milestone the
beat is asking to implement. Read off the step alone the reservation was dead
there while looking alive, and the digest printed `Offer 0.5.0 before taking
new work` directly above `Beat: implement v0.5.0 — the case you can branch ...
8 still open` (`PL-6T4L`). Each binding answered the arrangement that had just
bitten and no other, and the same wrong offer arrived four times (`PL-D2GW`,
`PL-KD98`, `PL-6T4L`, `PL-188T`) — the last of them from a row moved between the
project and its milestone, which is an ordinary editorial act rather than an
edge case. A version is spoken for by being *named* ahead of the current one,
and asking the file that question terminates where enumerating bindings does
not (`PL-VFD8`).

Two sources for that set, because a milestone spends months holding only one of
them: a timeline row is written when it is *placed*, a section when it is
*scoped*. Nothing cuttable is suppressed — every version in the set is ahead of
the current one and so unreleased by construction, and a `release` beat is
answered before the comparison is reached. There is no exemption for the
milestone the beat is about, and there was one: `implement` used to be `wave`'s
fall-through when no release arrangement matched, and a gate-only milestone
that had in fact finished, reached from the patch track beneath it, fell
through to it — so withholding an offer would have printed "which is
unfinished" against a milestone that was done. `_release_due` now reads the
release train's row order and releases that shape from whichever row the
project stands on, and `implement` is returned only where the milestone's own
scope counts open work (`PL-J45M`, under `PL-2T03`).

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
that cannot answer — the checker says nothing rather than reporting every
release as untagged.

`vcs.tags` used to reach that outcome by collapsing no git, no repository and
no tags alike to an empty set, which made the silence free for its other
caller: `release.is_untagged` holds a project with no tags to nothing, so a
`git tag --list` that failed skipped the release gate with nothing said
(`PL-ZPDM`). It answers with a `TagSet` now — `names`, and `declined` where git
would not speak. The checker's silence is unchanged and is now a decision it
takes rather than the accident of one empty set; `docket release` refuses the
cut on `declined`, naming the question that went unanswered rather than
asserting an untagged release it has not established.

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
file puts both in one diff for review; it does not keep them in agreement,
because a brief narrates the state its front matter records - "**Blocked on
`PL-XJ5P`**", "Left at `needs-decision`" - and a field write moves only the
front matter. So `docket check` reads an open brief for a closed item it still
waits on or lands with, a status it says it is at other than its own, and a
prerequisite it never declares. A passage that records a state the item has
since left opens with `[superseded YYYY-MM-DD: what replaced it]`, dated for
when it stopped holding, and the check skips it: the history stays, and the
reader meets the marker before the claim (`PL-8YXJ`).

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
payoff: a learner who pauses mid-induction stops seeing numbers that look live
---

**Problem.** What is wrong or missing, concretely.
**Why it matters.** The consequence of leaving it.
**Where.** The files or modules involved.
**Decision needed.** The question blocking the work.
**Done when.** The observable condition that closes it.
```

### What the front matter is, exactly

Deliberately not YAML. A real YAML parser is a dependency this package will not
take, and the subset actually wanted — scalars and comma-separated lists — is a
few lines of parsing that cannot surprise anyone. Four rules, and they are the
whole format:

- **A field is `key: value` at column zero**, and the value runs to the end of
  the line.
- **A list is one comma-separated line.** `classes: safety, ux`. There is no
  second spelling: a list written as an indented YAML block (`- entry` lines
  under an empty field) is *refused by name* at `docket check` rather than
  read, because two spellings of one field is a second thing every reader of
  an item has to know, and the one that parsed to empty put a `safety`-classed
  item in the bottom band with nothing reporting it (`PL-FX0K`).
- **An indented line continues the value above it**, folded on with a single
  space, exactly as YAML folds a plain scalar. Twelve `reason:` fields here are
  hand-wrapped that way. Indentation is what makes a continuation: a line at
  column zero that is not `key: value` belongs to no field and is passed over.
- **A value wrapped in matching quotes parses to the unquoted string.**
  Quoting is the correct instinct everywhere else, so `title: "Untested: every
  test reads the controller"` means what it looks like it means. The pair has
  to close at the last character; a value that merely *opens* with a quote —
  `payoff: 'are the generators dealt with' is answered by ...` — is one nobody
  quoted, and is taken verbatim.

All four are one decision. `_front_matter_pairs` used to keep only the lines
matching `key: value` and skip the rest, and that single skip produced three
separately-briefed defects — a truncated multi-line value that the next field
write then deleted outright (`PL-5B39`), a block-list `touches:` that reached
no lane (`PL-FX0K`), and quote characters landing inside 56 titles and 3
`verify:` commands, where a shell reads the quoted form as one word and exits
127 having run nothing (`PL-V6CR`, `PL-MZH2`). `PL-9HD1` is the cluster.

Where a field cannot be read, it is **reported rather than guessed at** —
`unknown_fields`, `duplicate_fields` and `block_list_fields` on the parsed
item, all three named by `docket check`. Guessing is what turns a validation
failure into a silently wrong queue position.

`**Problem.**`, `**Why it matters.**` and `**Done when.**` are required once
an item leaves `untriaged`; the others are conventions. A heading is matched
by the words it opens with and may continue past them — `**Why it matters, and
why it is not new.**` is the same section, and a check that made an author
flatten a better heading would be editing prose rather than checking it. What
it does require is text under the heading: a required section with nothing
below it is an error, because presence of a heading is not what makes an item
startable by a stranger.

`**Decision needed.**` is required at `needs-decision` and is matched the same
way. It was a bare substring test until `PL-VJ1X`, so the one heading an author
most wants to qualify — who decides, and by when — was the one heading that
could not be, and the checker contradicted the rule stated above it.

**The recommendation is the other half of that status, and the half that does
not survive on its own.** The question is written into the item; the
recommendation that would let the owner answer it in one read is written into
the reply that posed it, and a reply dies with its session while the item
waits. So the longer an item sits at `needs-decision` - which is what the
status is *for* - the likelier the recommendation is gone by the time the
answer arrives. `PL-KQHN` is the instance: its answer was reconstructed from a
harness-written summary line naming two options and marking neither, and a
decision of record about the release train rested on a reading of another
model's compressed prose.

So from `recommendation_required_from`, `check` advises on a `needs-decision`
brief that marks no recommendation. Three things about the rule:

- **The test is the marker, not the word.** A marked recommendation is the
  token under emphasis - `**Recommended.**`, `**This is the
  recommendation.**`, `*Recommendation: not yet.*` - or the labelled
  `Recommendation:`. Presence of the word decides nothing: of the ten open
  `needs-decision` items using it on 2026-09-20, two used it only to say when
  a recommendation should be *formed*. Findability is the property being
  asked for rather than presence, because a recommendation in the ninth
  paragraph of a long brief buys a reader nothing, and the brief is matched
  with its line wrapping flattened - four of the eight carrying a marker wrap
  somewhere inside it.
- **Declining is a marked answer too.** A brief may honestly have no
  recommendation to give, and `**No recommendation**, because the deciding
  number cannot be measured` carries the word under emphasis, so one pattern
  serves both endings. That is what keeps the advisory reachable-to-zero on an
  item that will never carry one.
- **Two populations, reaching two different sessions.** An item captured on or
  after the cutover is one somebody is writing now, and the advisory reaches
  it while the session still holds the reasoning - the only moment anything
  can be *prevented*. One predating the cutover is reached as it is about to
  be offered, which is `verify:`'s and `payoff:`'s narrowing taken for their
  reason: 37 of the 45 open `needs-decision` items marked nothing on
  2026-09-20, and naming all of them every run is an advisory that cannot
  reach zero without a campaign.

An advisory and never an error, because whether a recommendation is *owed* is
not an exact rule - and a check that refuses correct content is one `CLAUDE.md`
retires.

`payoff` is one plain-language line of what closing the item buys, and it is
the only field written for the person choosing rather than for the person
working. A title is written for the session that will implement the item, so it
names a mechanism - "reconcile the jobs reporting a status check against the
branch-protection required list" - and offered unchanged to whoever is deciding
what to fund, that is a string they cannot weigh. The line says what changes
instead: it gets faster, fewer bugs reach the default branch, a check stops
lying, a release stops needing a person to remember a step.

It is stored rather than composed on demand because the alternative is
rebuilding the sentence from the brief, at full context, in every session that
offers the item - the re-derivation a queue exists to move out of the model.
Nothing can infer it. The brief argues the case in the same mechanism
vocabulary as the title, and which consequence a reader cares about is
judgment, so `check` holds this field to **presence** and stops there: a
checker guessing at whether a line states a consequence or restates the title
would be authoritative and wrong, which is worse than no checker. There is no
length floor either - the twelve-character one `falsifies` carries exists
because a short fragment folds assertions it was never meant to, a concrete
harm, where a thin payoff harms only the reader looking straight at it.

The requirement starts at `ready`, from the date `payoff_required_from`
records, and the dated cutover is `verify_required_from`'s pattern taken whole,
for the same reason it was adopted there: a store written before a rule holds
items that predate it, and making every one of them an error at once makes the
checker useless from its first run rather than making the queue better. Items
captured before the date raise a grooming advisory instead, and only as each is
about to be offered - which is also where the sentence is cheapest, since the
session about to work an item already has its brief open. Nothing already
closed is asked for one.

Unlike `verify`, it has no exemption. Some work genuinely has no command that
can run before it; no work has no consequence, and an item nobody can say that
much about is a finding about the item rather than a case for an escape hatch.
There is also no close-time counterpart to `verify_required_at_close_from`:
that rule exists because closing an item is the first moment its command can
be *run*, and a consequence needs no run, so the requirement is answerable in
full at `ready` and has nowhere later to reach.

`show`, `next` and the digest print it wherever they name an item - beside the
band and the item's relation to the debt gate, which are the decidable half of
the same question. `list` and `delegable` deliberately do not: the first is one
line per open item and exists for scanning a whole queue, and the second is a
worker's reading list, which wants the command that proves the work rather than
the reason somebody wanted it.

Two further fields govern whether the work may be handed to a cheaper model:
`verify`, a single-line command that proves the item done, and `not-delegable`,
holding the reason an otherwise-qualifying item is withheld. See *Delegation is
derived, never granted* below.

`falsifies` is read by `docket verify` alone, and is absent from every item
this store holds - 0 of 1,324 on 2026-09-20, having shipped in `v0.4.27`
(`PL-K4R5` counted it, and the bullet below says what the check prints instead).
It holds enough of one assertion to name the single subject this item's work
makes untrue — a substring rather than the whole line, because an exact line breaks on
reformatting and on the commas a real assertion carries, and one subject rather
than a list, because an item falsifying several unrelated assertions is doing
several things. A fragment shorter than twelve characters is an error: `verify`
folds every removed assertion containing it, so `assert` would fold the lot.
Whether the fragment is long enough to name a subject is decidable; whether it
names the *right* one is left to whoever reads the lines `verify` prints. Write
it when the item is triaged, not while working it — a declaration only counts
where the base already holds it. See *Verification is scoped, not just green*.

`root-cause-of` names three or more items this one is the cause of.
`CLAUDE.md` calls such a mechanism a *generator*. `docket check` holds every id
to naming a real item and holds the list to three, because this is the one
place in the store where a typo would buy a promotion; below three, or with an
id that does not resolve, the item ranks on its band exactly as it did before
and the checker says so.

`generator` is the second half, and the two are deliberately on different axes:
**the count decides whether a generator is recorded, and this decides whether
it ranks** (project owner, 2026-09-21, ratified, over keeping the count for
both and accepting that any three-item cluster outranks a `safety`-classed
`P1`). It holds a verdict and a reason — `live - <why the store is still
handing this mechanism members>`, or `spent - <why it can no longer produce
one>`. A `live` one ranks above everything but `P0`, a `safety`-classed `P1`
included, which the project owner was asked about and confirmed: every session
such a mechanism stands through pays it again, which is a claim about future
inflow rather than about the damage the existing three already did. A `spent`
one is recorded all the same, for the audit, and ranks on its own band — so a
cluster judged finished is now written down rather than withheld to keep the
ranking honest.

Recording does not rank. An open generator carrying no verdict ranks on its
band and `docket check` says the field is missing — the fail-safe direction,
because `check` runs separately from `next`, so a store is routinely ranked
before it is validated and the unqualified state has to be the one that cannot
buy a promotion. A **closed** head is asked for nothing: it is startable by
nothing, so its verdict would move no ranking, and demanding one would mean
backfilling every head already closed with a retrospective judgment about a
mechanism that session did not diagnose.

The verdict is a session's judgment written into the store, never inferred.
Reading "still generating" out of an item's prose would be guessing at exactly
the half `CLAUDE.md` refuses to script, while looking authoritative; the
vocabulary is the decidable half a tool may read, and the sentence beside it is
what a later reader needs in order to overturn it.

The edge reads from both ends. `docket show` on an item that some sound claim
names prints the head, its status and how many items it explains, because the
field is written on the head alone: a session reaching a *member* by name -
the way an item is usually started - would otherwise work it as an ordinary
item while the generator above it was still being decided, and that decision
can re-scope or drop the member. An unsound claim prints nothing here, for the
same reason the ranking refuses it.

`docket generators` reports how much of each cluster is still open, and
`docket show` on the head itself carries the same line. Fixing a generator
closes the head and leaves its members owed, so a head's own status is the one
fact that cannot answer "is that dealt with?" for the cluster: every head this
project has recorded is closed while most of what each names is not. Given an
id the command lists that cluster's members the way `docket feature` lists a
feature's, and a member's id resolves to the head above it, since that is the
id a session is usually holding.

The report carries a **trend** as well as the present split, measured against
the head's own `closed:` date, because "unchanged since the cause was fixed" is
the fact that makes the count worth having and no field stores it. The three
buckets are printed apart rather than summed into one "open when the head
closed" figure: `closed:` is a date and not a timestamp, so a member closed on
the head's own date cannot be ordered against it — about a third of this
store's are — and one number would have to pick a reading and print it as
fact. What a sound claim leaves uncounted is named rather than omitted: an
unsound `root-cause-of:`, which nothing ranks and nothing counts, and an
`impairs-generators:` item, which ranks on the same tier while naming no
members to drain - named apart once closed, since a closed item ranks on no
tier whatever its fields say.

Nothing infers it. A ratio over a `touches` path measures how busy a file is,
and citation is not causation — 33 items in this store are cited by more than
two others. `tools/generator_check.py` prints the clusters carrying those
signals so a session can look, and claims none of them is a generator; the
judgment is a session's, and writing the field is how it is recorded.

`impairs-generators` is the same tier's other entrance, and the second field
that changes a queue position. It holds, in prose, which function of the
generator machinery a defect breaks — the `root-cause-of:` field itself, the
predicate deciding a claim is sound, the rank term, or whatever surfaces a
claim to a reader — and it ranks its item at **the same priority as a
generator**, below `P0` and above every band (project owner, 2026-09-19). The
warrant is the generator argument one level up: while identification is broken
a generator is never recorded, and an unrecorded generator is ranked by
nothing, so the cost is unbounded in the same way and invisible in a worse one.
Nothing in a store says a generator went unfound.

Its checkable half is `generator_paths`, the config list naming where that
machinery lives: an item whose `touches` reaches none of it is making a claim
about code it never goes near, and `docket check` refuses it. The list can only
refute. Measured on 2026-09-19, 36 of this project's 322 open items declare one
of those files for unrelated reasons, so promoting on the path alone would
promote all 36 and mean nothing — the objection `generator_check.py` already
records against citation density at 33. The machinery is a few functions inside
shared files, so the claim stays a session's judgment and the path list is the
cheap falsifier. A bare `yes` is rejected for the reason `not-delegable`
rejects one: a field that lifts an item above every band owes its reader the
function that broke.

`recurrences` is the evidence those two fields rest on, arriving without a
session having to notice it — and it is deliberately not a third field that
changes a queue position. Each entry is a date and the id of a capture that
`docket new` matched to this item: the filing happened, so the defect fired
again, and `CLAUDE.md`'s reason for pulling a root cause is that every session
it stands through pays it again. At two distinct recurrences — which is
three filings, the item itself being the first, and so the generator rule's own
number counted in filings rather than in items — `docket next` and the
session-start digest name the item as a promotion candidate and stop there.
Neither names one that is closed or in flight on a branch: the claim a reader
would write moves a queue position and nothing else, so an item `docket next`
will not rank has none left to move. `untriaged` and `blocked` are named,
because those windows have not opened rather than closed — a claim on an
untriaged item ranks the moment triage seats it.
`MIN_RECURRENCES` is derived from `MIN_ROOT_CAUSE_ITEMS` rather than written
down, so the project carries one threshold rather than two; written as a
literal three it would have demanded a *fourth* filing, and the slug-rename
cluster that was recorded as a generator by hand would never have surfaced. A reader opens the briefs and writes `root-cause-of:`
by hand, or does not.

**It surfaces; it never promotes**, and that is the whole restraint of the
design (project owner, 2026-09-20, ratified, over counting repeat filings and
raising the matched item's `priority:`). The count is built from a
title-similarity ranking, and `root-cause-of:` is the one place in this store
where a typo would buy a promotion — so letting the count rank an item would
reintroduce the hazard that field's validation closes, one indirection away.
`priority:` could not have carried it either: `docket check` pins `P1` to
`safety` and `science`, and `CLAUDE.md` forbids promoting process work into
that band to move it up the order, which is every item this counter will ever
fire on.

`docket set` does not write it. The field's worth is that each entry was
recorded by the tool at the moment it matched a filing, so a hand-written one
is a claim about a filing that may never have happened; `docket check` holds
each entry to naming a real item, which is as far as a check can reach.

**A match the tool got wrong is withdrawn rather than deleted** (project owner,
2026-09-21, ratified, over deleting the entry outright as `PL-34BG`'s brief
sketched it). `docket withdraw <item> <capture> --because <item>` annotates the
entry where it stands — `2026-09-20 PL-S8JT withdrawn 2026-09-21 PL-34BG` — so
it stops counting and stays on the record. That argument for keeping the field
out of `set` is about *writing* an entry and does not carry across to
withdrawing one: the hazard of a field nothing can write is a fabricated
filing, and the hazard of one nothing can withdraw is a false filing nobody can
correct, which is the state `PL-34BG` found this store in. Deleting the entry
would leave a file reading as though the match had never been made — a quieter
record than the one that was there before, and it would make the withdrawal the
one event in this mechanism's life that no command will show you. `--because`
names an item rather than a sentence, for the same reason the entry names a
capture: why a match was wrong is a judgment, judgments belong in briefs where
they can run to the length they need, and the field carries the pointer a
reader opens. `check` holds that pointer to a real item exactly as it holds the
capture's id, and a tail it cannot read as `withdrawn DATE PL-XXXX` leaves the
entry counting and says so — a mis-typed withdrawal must not cancel a filing
quietly.

**The write is exempt from the close-out audit and the withdrawal is not.** An
append rides a capture `CLAUDE.md` requires unconditionally, and its value is
dictated rather than chosen, so `verify.sanctioned_queue_edit` forgives a
worker for editing an item it was never commissioned to touch. A withdrawal is
chosen, and what it changes is how much evidence an item carries — so the item
doing it declares the file in its `touches` like any other work, and `withdraw`
says so where it has not. Withdrawing the last recorded entry appends to that
line exactly as a new filing does, which is why the append rule requires what
it gained to start a new entry rather than extend the last one.

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
run is told not to ask, so `docket check && grep -q ...`, the shape the older
commands record, is bounded at one level. Since `PL-6TP8` the `grep` is
written alone, and `docket check` is not put ahead of it.

Two ways of recording a command that proves nothing are refused by a bare
`check`, with no command run at all. **A command that cannot fail** — `true`,
`:`, `exit 0`, and the path spellings of the first — specifies nothing whatever
the tree holds, so `verify` would ACCEPT a branch that did none of the work.
**One command recorded against two or more open items** is the same conclusion
reached by counting rather than by reading: whichever item is worked first makes
the command pass, so from then on it accepts a branch that did none of the
other's. Both are answerable from the store, which is why they are here and not
behind `--verify`: that flag is the expensive tier, it is CI-only in the project
this grew in, and three items triaged with one placeholder command on 2026-09-20
passed every local gate and turned CI red after review had started (`PL-J3WK`).

The rules are exact and stop where the judgment starts. A command whose
*effect* is a no-op — a `grep` for a string that is not in the file it reads,
say — is only answerable by running it, and that question stays with the
replay. Sharing is exact string equality too: collapsing whitespace would be
right for the words of a shell line and wrong inside a quoted argument, where
`grep -q 'a  b'` and `grep -q 'a b'` read different files. An item whose command
cannot fail is told that and is not also told about the sharing, which is a
consequence of the placeholder rather than a second defect.

What `check` does say about that command is an advisory, and only for the one
shape that can pass without meaning anything: a `docket check` whose *output*
is piped or captured, rather than whose exit status is read. A nested run is
told not to replay the open items' commands, so it never prints the landed
advisory - a `grep` for that answer matches nothing whether the work is done or
not, and an inverted one passes on the strength of it. An advisory rather than
an error because "reads the output" is a judgment about a shell line, and hard
failure is reserved for exact rules.

### What a `verify:` exit status proves, and to whom

A `verify:` command is one shell line and its exit status is one number, and
four consumers read that number: the replay (`check --verify`, whole-store on
a push to the default branch and scoped on a pull request), the delegated
audit (`docket verify`), the close-out (`docket verify --self`), and the person
writing the command. Until `PL-6TP8` each read its own meaning out of it, so a
non-zero exit meant all of "not started", "prerequisite broken", "selected
nothing", "timed out" and "finished under another name" at once, and twelve
items each re-decided one facet. This is the one reading. Each consumer in
`verify.py` and `checks.py` names the clause of it that it applies.

**Exit 0 proves that the command's assertion holds on the tree in front of
it** - and nothing about the work being right. It proves the *work landed*
only if the command discriminates, which is to say fails on the tree before
the work, and no exit status can say whether it does. The author establishes
that once, by running the command and watching it fail before writing it down,
and the replay holds the contrapositive forever after: an open item whose
command passes is either finished and unclosed or non-discriminating, and both
are errors (`_check_landed`).

**A non-zero exit proves only that the assertion does not hold *or was never
evaluated***, and the number alone cannot tell the two apart. Three
never-evaluated outcomes are decidable from the run itself, and every consumer
peels them off before reading anything else: killed at the limit
(`TIMED_OUT`, a status no process can return), not found by the shell (127),
and selected no test (pytest's 5, claimed only where the command names
pytest). A fourth is not decidable at all: a prerequisite clause that is red.
`python3 tools/doc_check.py check && grep …` exits 1 whether the `grep` failed
or `doc_check` did, so a command carrying such a clause has made its own
failure unreadable, and the replay accordingly reads nothing from a plain
failure (`PL-T7VS`). A fifth is undecidable by construction: work finished
under a name other than the one the command greps for fails exactly as
unstarted work does, and nothing that reads an exit status will ever separate
them (`PL-0M32`, `PL-6TN8`). That one is the author's to prevent - a
name-pinning `grep` on an item whose work may already exist is checked against
the code, not against the test names - and the close-out's to read, since it
reads the command and the diff together.

**Who may conclude what.**

- **The replay** - `already_passing`, reported by `_check_landed`,
  `_check_selects_nothing` and `_note_cost` - is one-directional. It
  reads exit 0 as its finding, the three never-evaluated statuses as refusals
  (reported per item as not checked, or for the whole run where nothing ran
  to completion), and nothing from any other non-zero exit. It never reads a
  failure as "the item is legitimately open", because it cannot know that. It
  may decline, and a declined run says so; an empty result is never a clean
  one. Where the command reads past the tree its exit 0 is a fact about
  the world rather than about the commit, so the finding is reported as an
  advisory rather than an error (`PL-205P`).
- **The delegated audit and the close-out** - `verify_item` - read exit 0 as
  the commission's assertion holding and every other status as `REJECT`, with
  the reason on the line where the run can name it: re-entered `docket
  verify`, selected no test, killed at the limit. They may not decline. The
  command is the thing being asked about, so "could not run it" rejects the
  work rather than abstaining. What they may not conclude from exit 0 is that
  the work is right; the project's own check and the reviewer's reading of
  the diff carry that, on their own lines of the same report.
- **Delegability** - `Item.delegability` - reads whether a command is
  *recorded*, never whether it would run or discriminate. Both are the
  author's obligations below.
- **`docket check`** reads the command as text: one line, not re-entering
  `docket verify`, not reading `docket check`'s output, `touches` declared
  beside it. It executes the command only under `--verify`, and then as the
  replay above.
- **A closed item's command** is read by nobody as a claim about today's
  tree. It is the record of what ran, and the next section holds it to that.

**What the command owes its item** - three things the author can decide at
the moment of writing and no exit status can decide afterwards:

1. **It discriminates on this item's own work.** Its failure before the work
   is an evaluation - an ordinary exit 1, never pytest's 5 - and it goes green
   only for what *this* item's work creates. A clause a neighbouring item's
   work satisfies makes the replay accuse the wrong item the day the neighbour
   lands (`PL-3DXV`); a bare `-k` is a bet on a name no test may ever carry,
   and `docket check` refuses one at the field (`PL-Q8RQ`, below).
2. **It reads the tree the item touches.** The paths its discriminating clause
   reads are declared in `touches`, so `docket concurrent` and the pull
   request's replay scope both see them (`PL-LBW5`); a `pytest` clause naming
   a suite that cannot exercise the change proves a different tree's health
   and sends a delegated worker to the wrong file (`PL-2M4X`, `PL-6YL1`).
3. **It has been run and watched fail, and the author knows why it failed.**
   `grep` exits 2 for a file it could not read as well as 1 for a line it did
   not find, and `docket` exits 2 for a subcommand it does not have; either
   reads as "not done" forever.

A prerequisite clause - `doc_check`, `bin/docket check`, a file's whole
`pytest` run ahead of the `grep` - is what makes a failure unreadable, and it
proves nothing the consumers do not already prove: every such clause in this
store is a line of `make check`, which `docket verify` runs as a line of its
own report, which `docs/worker.md`'s loop runs after the command, and whose
`doc_check`, `bin/docket check` and whole-suite steps CI runs ahead of the
replay. So the field does not carry one: the command is the discriminator
alone (project owner, 2026-09-19, ratified under `PL-6TP8`, chosen over
keeping the paired shape), and a command recorded before that date loses its
clause as its item is started rather than in one pass, which was chosen over
a mechanical strip of all of them. Measured 2026-09-19: 162 of 177 open
commands carried one, they were 1,879 of the replay's 1,884 serial seconds,
and none of them masked a pass.

**The decidable half of that is a check, and only that half.**
`verify_prerequisite_refused_from` refuses a command that runs `pytest` over a
tree named in `collected_test_paths` while a *separate*, non-pytest clause
stands beside it. The separate clause is what makes it decidable: the author
has already said which clause discriminates, so the `pytest` run is not it,
whatever the item turns out to be about. A command whose only clause is the
`pytest` run says the opposite and is untouched, as is one whose run carries
`-k`, `-m`, `--cov` or a `::` (a `-k` is refused by the rule below instead), and
as is a target outside the declared trees -
that one is running something no other consumer does, which is the condition
that would falsify the rule and the reason the trees are declared rather than
assumed. Measured 2026-09-19: 0 of the 82 open commands of this shape name
such a target.

The other 73 multi-clause commands - `python3 tools/doc_check.py check &&
grep …` and its relatives - are the same contract and are deliberately not
refused. Which clause is the prerequisite there is a question about the item's
work: an item whose work is *making `doc_check` pass* has that clause as its
discriminator, and two of the 73 are two discriminators rather than a
prerequisite and a discriminator at all. A tool guessing at that half would be
worse than no tool, so it stays prose (`PL-09G9`).

The cutover is read against the item's `added` date, so the commands already
recorded are a closed set - nothing can join it - and it drains as each item
is started, which is the repair-as-started policy rather than an exception to
it. It leaks in the same bounded way `verify_required_from` does: an item
captured before the cutover can still have a command written after it. Because
`docket set` refuses any write `docket check` would then fail, the rule is met
at the moment the command is typed rather than at the next run.

**A `-k` is refused on its own account** (`PL-Q8RQ`), which is the contract's
first obligation made mechanical. `verify_k_selector_refused_from` refuses a
command whose `&&` chain narrows a `pytest` run over the collected trees with
`-k`. Every test in those trees passes or `make check` is red, so such a run can
only select tests the check already proves (exit 0) or select none (exit 5, or
4 for a path the work has yet to write), and a substring is satisfied by
whatever test later comes to carry it: `PL-S5YM`'s `-k covered` began passing
when an unrelated merge added one, and three sessions diagnosed the red `main`
that followed (`PL-99YZ`). It is refused wherever the clause stands, since
position decides only which half of the contract it breaks - ahead of a `grep`
its 5 is the command's answer before the work, behind one it re-proves the
tree. Three runs are left alone, each because that reading stops being true:
one whose status a pipe or `||` replaces, one carrying `--cov`, and one over a
tree outside `collected_test_paths`. The date is its own rather than the
prerequisite rule's, because that rule leaves any `-k` alone and `PL-W4XQ` was
captured on its first day carrying one; the five open commands of this shape
on 2026-09-22 are grandfathered and repaired as each item is started.

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

**The pairing runs the other way too: an item at `ready` may not declare an
open item blocker.** `ready` says the work can be started now and the edge says
it cannot, and the ranking reads only the status — `docket next` filters on
`status != "blocked"` and never opens the field — so without this the edge
could be declared, every other check pass, and the item still be offered ahead
of what it waits on, silently (`PL-KBD0`). `needs-decision` is deliberately
exempt: `docket gate` counts that status as debt somebody can resolve, and
forcing it to `blocked` would take a pending decision out of the gate by
renaming it rather than by answering it.

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
would actually ship it and is left out of that release's generated notes. The
one exception is a cut being resumed, which reclaims the items its own
interrupted run stamped and nothing else. Ten
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
rename reading as "not done" (`PL-S5LB`). The second is declined rather than
answered: an item whose work landed in one pull request but whose `status:
done` was written in a later one would recover the later number, which carries
the closure and none of the work, so nothing is recorded and the transcription
stays owed (`PL-YDL6`) — the shape `PL-D2GW` closed by requiring the closure to
travel in the same commit as the work, so it exists only in the three items
predating that rule.

**That decline reads the item's `touches`, not the diff alone** (`PL-YFXG`). A
commit changing nothing outside the queue directory is a closure separated from
its work only where the work was somewhere else to begin with; for a
release-tag item, a triage pass, a stranded recovery or a rename pass it is
what landing correctly looks like. So a queue-only closure is declined only
where the item declares work outside the queue — the same field
`branches_in_flight` reads to draw the same distinction (`PL-7790`). Without
it, `PL-YTDN` closed correctly in `#712` with all twelve changed files under
`docs/items/`, the number was declined, and `check` raised the error rather
than the advisory: `main` failed on every branch cut from it, and nothing
cleared it, because the bare `record` writes only what the base can supply.
Measured across the 927 closed items on this project's `main`, the reading
changes 29 answers and every one matches the `pr` already recorded there.

- **The number is recoverable** → nothing until a cut has shipped the closure,
  then one advisory naming every such closure, its number and its release, and
  the command that writes them. Nothing is lost; the way back exists in git.
  Before the cut, the cut is the writer: it writes each shipping closure's
  number before it renders the notes, so reporting it earlier fired on every
  healthy run for work the cut already does (`PL-XYQW`). After it, the notes
  bullet cites no pull request, which `docket record` restates along with the
  field.
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

Bare, it also puts that number where a reader is actually looking. `pr` exists
so somebody can get from a released item back to the change that made it, and a
release's notes are where they look — so a number written onto the item and not
onto the bullet has been recorded in the half nobody reads. That happened to
128 of this project's 853 released bullets across 22 of 40 releases, because
the cut rendered the notes and this command ran afterwards (`PL-W7WL`, filed
four times from four separate cuts before anything compared the two files on
that axis). The cut now writes the number first, which stops the next one; this
is the only supported route to a bullet that has already shipped, since
re-cutting a released version to regenerate it is refused and should be. The
edit is an append — the id and the title stay exactly as they went out — so a
release never changes what it claims, and a run with nothing to add writes
nothing, which is what lets it sit in `make fix`. `docket check` reports what
is left as an advisory, counting only bullets the store can actually supply a
reference for.

`docket record NUMBER --merge MERGE_COMMIT` is the explicit form, for the number
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

**`--verify-base REF` narrows the replay to the items this branch could have
changed the answer for**, which is the same argument one step on (`PL-SDHR`). A
pull request cannot have changed whether some *other* item's work merged, any
more than a pre-commit gate can, and the sweep was measured at 74.6 s of a
102-command run against 5.5 s scoped. So CI scopes on `pull_request` and sweeps
on `push` to the default branch, where the answer is a fact about that branch.
This project's `make check` runs the scoped form too, against `origin/main`, so
a session sees the finding before it pushes rather than from CI (`PL-0HPV`);
the whole-store sweep stays off it, for the reason above.

**That is two sets, and reading it as one was a defect** (`PL-XMNC`). The first
is the items whose own file the branch edited, read from the diff rather than
from their declared `touches`, which is a claim made before the work. The
second is the open items whose `verify:` command *reads* a file the branch
edited — the command a branch invalidates without ever opening its item, which
every one of the six recorded breaks was, and which the first set replays
never. A command is read clause by clause, split on `&&`, `||` and `;` outside
quotes, and the program a clause runs is not a file it reads: `python3
tools/doc_check.py check` names a path and discriminates on none, so counting
it would drag the 54 open commands carrying that gate behind any edit to it.

Where the reader cannot classify a token it widens rather than narrows, and it
asks the filesystem nothing — a file the branch is *creating* matches, which
`test -f CONTRIBUTING.md` needed. **A scoped run always says so**, on the cost
line and even when the scope held nothing to run: a narrowed run reporting
nothing must never read as a whole store with nothing to report. Where the two
sets both contributed, the line says how many came from each.

**A command that reads past the tree is reported as an advisory, not an error**
(`PL-205P`). Everything above reads exit 0 as a fact about the tree, which
holds only while the command is a function of the tree. A `verify:` that asks
the remote is not one: its answer is a fact about the world at the moment it
ran, so it flips with no commit behind it and the commits the sweep then names
are innocent. `PL-8GQW`'s was `git ls-remote --tags origin v0.4.30` — correct
and failing when `#730` filed it, passing the instant the project owner pushed
the tag, and `main` was then red across six commits by five unrelated sessions
while the repository had not changed. No branch could have shown it, because no
branch changed anything, and scoping was never the reason. Five items have ever
recorded such a command, four of them the same release-tag line, one per
release; there is no hermetic substitute to prefer, because the work is the
owner's and the remote is the only place it is visible.

`verify.reaches_outside_tree` decides it by `shlex`-tokenizing the command and
looking for a network command word — `curl`, `wget`, `gh`, `ssh`, `scp`,
`rsync`, `nc`, or `git` immediately followed by `ls-remote`, `fetch`, `push`,
`pull` or `clone`. Tokenized rather than searched because a hermetic command
may carry one as a *search string*: `PL-K2C8`'s greps `SKILL.md` for the
literal `git push origin --delete` and opens no socket. Unparseable, and
anything unrecognized, reads as hermetic — wrong in the safe direction, so the
finding keeps its severity and only a command the predicate is sure about is
softened. `ROADMAP.md` settled the same question at the other end of the same
window: a release whose tag has not been pushed yet is an advisory "rather than
an error: failing it would turn `make check` red on every release branch".

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
it, deliberately, though no longer because the repair is in doubt. A selector
matching no test was once the recommended shape for an item whose work had yet
to write the test; since `PL-6TP8` the repair is always a `grep` for the test
the work adds, and since `PL-Q8RQ` a `-k` is refused outright on a command
captured from `verify_k_selector_refused_from`. What the advisory still reaches
is that rule's grandfathered set, repaired as each item is started - an error
would force the one-pass repair instead.

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

**An advisory beside it named the outlier, and was retired 2026-09-19.** A
command 30x above the pool's median was named as the one the check waited for,
on the reasoning that the person who writes a heavy `verify:` is the only one
placed to reconsider it and was the one person told nothing (`PL-VG7G`). It was
dropped on a count rather than on taste (`PL-G6J5`), and the numbers are worth
keeping because they say something about the store rather than about the check:

| | 2026-09-02 | 2026-09-19 |
| --- | --- | --- |
| commands in the pool | 46 | **179** |
| median command | 0.65 s | **3.65 s** |
| serial total | 34 s | **1458 s** |
| slowest command | 8.95 s | **67.4 s** |
| the ratio's bar, at 30x | ~20 s | **109.5 s** |

The threshold was calibrated when the typical `verify:` was a `grep`. It is now
`uv run pytest <file>`, so the median rose with the pool and the bar rose with
the median — to 109.5 s against a per-command limit of 120 s, and a command over
that limit is killed and kept out of the median, so **once the median passes
4.0 s the test cannot fire on anything at all.** It was already firing on
nothing: zero of thirteen real branch scopes taken from the last twenty-five
merges, and nothing on the whole store. Widening the denominator to the
*store's* median, which is what the item was filed to propose, measured the
same: zero of thirteen.

**And the silence is the right answer, not a tuning failure.** 1458 s of serial
work across eight workers is a 182 s floor against 204 s elapsed, so no single
command is what the run waits for — the queue is. That is the heaviest of three
whole-store runs taken that day; the container's load moves the totals (serial
1204–1458 s, slowest 48.9–67.4 s, wall 166–204 s) and the conclusion holds at
both ends, since the floor is 150–182 s against 166–204 s elapsed and the
slowest command is far under it in all three. That is `PL-FRGP`'s
correction taken to its conclusion: a pool cannot finish before its slowest
member, but the slowest member is only the *binding* constraint while the rest
of the work fits underneath it, and this store outgrew that. With 49 commands
totalling 34 s, about 4 s of aggregate work sat behind a 6.9 s slowest member
and the slowest member really was the floor; at 78 commands totalling 175 s,
removing the named command measured **28.6 s → 23.7 s**. At 179 commands
totalling 1458 s it would measure nothing at all.

So the cost line above carries the signal alone, and it is built for it:
`serial` is where a store that is uniformly heavy shows up, and the margin
between the costliest command and the limit is where a single command closing
on the timeout does. Neither needs a threshold, which is why neither went stale
the way the ratio did.

Where the cost now is, measured the same day and not addressed by any
per-command test: three test files carry **59% of the 1458 s**, each re-run by
every item whose command names it — `subprojects/docket/tests/test_cli.py` 415 s
across 14 items, `tests/unit/test_doc_check.py` 292 s across 12, and
`subprojects/docket/tests/test_verify.py` 152 s across 4. `PL-FZ58` carries it.

**Two of those three were a setting, not a fixture** (`PL-YRYR`, 2026-09-21).
Both files under `subprojects/docket/tests/` build a scratch repository per
test, and git signed every commit in them because the machine's `~/.gitconfig`
said to - 72.7 ms a commit against 5.1 ms unsigned, which nothing in either
file named or could have named. The repository root's `conftest.py` now points
`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` at `/dev/null`, and the two
commands cost 25.1 s -> 8.6 s and 30.9 s -> 10.0 s measured on 4 cores the same
way. Across the 28 open items whose commands name them, and the 3 naming the
whole tree, that is about 573 s off a whole-store replay - roughly 39% of the
1458 s above, none of it from changing a test. `tests/unit/test_doc_check.py`,
the third file, builds a repository only in the tests that read git rather
than in every test, and was not re-measured. The
`conftest.py` sits at the repository root rather than in this tree, so the
repository's own `tests/` gets the same isolation from the same two lines.

**It changes nothing about `make check`.** That runs pytest under `-n
$(cpu*2) --dist worksteal`, where this cost was subprocess waiting already
overlapped with other workers' CPU work: 77.83 s against 78.78 s, which is
noise. The replay is where it lands, because the replay is serial by
construction - one command per open item, one after another.

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

The front-matter comparison refuses rather than passes when it cannot be made
— an item file that resolves to nothing, or a base holding no store at all.
Both were an empty set of changed keys until `PL-20PT`, and an empty set is
what a clean comparison returns, so the check reported `PASS` on every branch
it had ever run against. A file the base does not hold *is* a clean answer: an
item captured on the branch that works it has no earlier commission to differ
from.

`--self` says the caller is auditing its own branch rather than reviewing a
delegated one, and it is a different question. Everything above assumes a
worker who might exceed a commission; a session running its own close-out *is*
the reviewer, and against it four guards fire by construction on the path the
project's own instructions prescribe — the capture and leading-id rules put
other items' files in the diff, an item whose declared work is a `.claude` file
trips `gate_paths`, an item non-delegable *because* it touches protected code is
one a session works itself, and closing an item edits the very front matter the
guard watches. So in `--self` those four **commission** checks report instead of
refusing: still run, still naming every path, with the reason they are not
refusing. The four **integrity** checks are untouched — no suppression added, no
assertion removed, the item's own command passes, the project's own checks pass.
A session may re-scope its own commission; it may not weaken what measures it,
and it may not skip the test (`PL-69JZ`, `PL-B5YN`, `PL-4LT9`).

What counts as an *added suppression* is narrowed by file rather than by shape,
and to a wider set of files than the assertion check below. An assertion is a
statement, so only a file Python executes holds one; a suppression is also
*configured*, and `xfail_strict = false` under `[tool.pytest.ini_options]` turns
every expected failure back into a pass without a line of Python changing - so
`.py`, `.pyi`, `.toml`, `.cfg` and `.ini` are read and nothing else is. Prose is
what that removes: a release note recording that a suppression was deleted, an
item's brief explaining why one is wrong, or the `ROADMAP.md` version row a
release cut re-adds whole when it drops the `current baseline` mark from one
cell. The real v0.4.30 cut reported seven such lines and REJECTed on them.
Counted before the narrowing was written, because the safe direction here is
reporting: across 1,109 commits the added lines the matcher finds are 69 `.py`
and 41 `.md`, with no other suffix carrying one at all (`PL-5MFL`, `PL-BHBZ`).
Prose *inside* a file Python executes is narrowed the same way, by blanking a
line's quoted spans, backtick spans and trailing comment before matching what
is left - so a docstring naming the tokens, a fixture writing a suppression
into a test file as a string, and a comment explaining why one was *not* used
are each read as what they are. Only `.py` and `.pyi` are stripped: in a `.cfg`
or `.ini` a quote is an ordinary character in a value and an inline `#` is part
of that value, so the same strip would delete configuration rather than prose.

`# type: ignore` is deliberately not one of the markers. Replayed over `main`'s
1,004 non-merge commits it is the only one that has ever matched a real
directive - 56 of them, all carrying an explicit error code, and none of them a
disabled test - and whether an ignore is load-bearing is a question for mypy,
which `warn_unused_ignores` asks of every directive in the repository:
`strict = true` over `[tool.mypy] files`, and `tools/ignore_check.py` over the
two test trees that list excludes. The four markers that remained had matched a
real directive zero times, and stayed at that price because a count of zero
cannot tell deterrence from absence (`PL-G21K`, `PL-J5NN`).

`none` means none of the markers, so the markers are listed rather than
implied. `xfail` reads the mark, the call and `xfail_strict`; `pytest.skip`
the imperative call; `mark.skip` reads `@pytest.mark.skip` and
`@pytest.mark.skipif`, and leaves off `pytest.` so that `@mark.skip` after
`from pytest import mark` is read too; `unittest.skip` reads the standard
library's `skip`, `skipIf` and `skipUnless`, and `@skip` their bare imported
form; `typing.no_type_check` the decorator that switches a function's type
checking off. The two pytest decorators - the commonest ways a test is
disabled - had no entry until `PL-5B88`, so the check reported `none` with
one in the diff. The widening owed the count a narrowing does: replayed over
`main`'s 1,115 non-merge commits, it flags one added line, a
`@pytest.mark.skipif` on a test that needs `bash` - a real directive, which a
reviewer should see - and no prose in any suffix the check reads. Not read,
and absent from that history too: `pytest.importorskip`,
`unittest.expectedFailure`, `self.skipTest`, a raised `unittest.SkipTest`, and
`collect_ignore` in a `conftest.py` (`PL-DNZ0`). A deselection in `addopts` is
configuration: in `pyproject.toml`, one of `gate_paths`' defaults, the gate
check reads it, and in a `.cfg` or `.ini` file nothing does.

What counts as a *removed assertion* is decided by the parser rather than by a
line (`PL-4W2L`): an assertion the base's copy of a `.py` file holds - an
`assert` statement's test, its message excluded; a call whose name begins
`assert`, such as `assertEqual`, `assert_called_once_with` or
`assert_allclose`; or a `raises` or `warns` item of a `with`, which asserts by
expectation and is how this project pins the guards that *reject* an input
(`PL-QJQL`) - that is absent, as `ast` reads it, after the item's own commits.
Existing assertions are read-only, so every such absence refuses unless
`falsifies:` declares it. A reflow, a wrap, a new message and a move within the
file change nothing the parser reads, so none of them is a removal; an edit to
what an assertion asserts is one, on whichever line of a wrapped statement it
falls. A comment, a docstring, a release note or an item's brief carrying the
word never is (`PL-7TYC`).

What the check deliberately does not decide is whether a changed assertion is
stronger, weaker or merely restated, and every rule over the shape of an edit
had been a guess at it: the insertion fold that paired `f(a, b)` with
`f(a, b, c)` (`PL-K1WS`) also folded `approx(2.05)` into `approx(2.05,
rel=0.5)` (`PL-CNJH`), and the listing of one-string candidates (`PL-K4R5`)
printed up to six because it could not choose. So the report groups each
refusal under its test function - what left the function and what arrived in
it, the unchanged ones counted rather than printed - and pairs nothing.
Replayed over `main`'s 1,127 non-merge commits at the decision, it refuses 124
where the line matcher refused 121: it stops refusing six, none of which
changed an assertion, and starts refusing nine, every one of which did
(project owner, 2026-09-22, ratified, over refusing only an assertion that left
its test and over patching the line matcher).

Three details keep that fact about the item. Its commits are folded per file,
so an assertion cut in one and restored in the next is no change, and a form is
charged only where the base holds it, so an assertion a sibling commit added on
the same branch is never this item's to lose (`PL-2DTK`). A renamed file is
followed as `git show` follows it, and a merge commit is read against every
parent, as git reads one. And a file the running interpreter cannot parse -
`bin/docket` runs on the bare `python3`, which can be older than the project's
own - is read line by line with the predicate the parser replaced, and named on
the page as read that way. Not decided, as before: whether a new test asserts
the right value, an assertion moved to another file, which stays two facts, and
anything outside `.py`.

Two of the four take a **declared** exemption, which is what lets them stay
absolute rather than a softening of them. Both were checks a correct close-out
could trip with no passing route at all, leaving a session to game the fold or
push through a red integrity check — and either sets the precedent the split
exists to prevent.

- **`falsifies:`** names enough of an assertion to identify the one subject
  the item's work makes untrue. Not weakened — *falsified*: the string the
  assertion pins is what the item was commissioned to delete, so no
  arrangement of the tests keeps it. An absent assertion whose source contains
  that substring folds out of "no existing assertion removed" and is printed
  beside it, so the removal stays on the page and reads as a commissioned act
  rather than an unexplained one (`PL-K82G`). **One class of removal cannot be
  folded by anything**: where the item's deliverable *is* a changed output
  string, the old string is simply gone, and the diff holds nothing separating
  the commissioned rewrite from an expectation dropped. The refusal stands,
  printed under its test function beside every assertion that arrived there,
  and none is chosen - 15 of the 20 such close-outs in this history had more
  than one candidate, so choosing would print a guess as fact (`PL-K4R5`). **One commission cannot write the field in advance**, and
  takes it from the branch instead. A `needs-decision` item's answer is the
  session's to make, so which assertions it falsifies is not known until it is
  made: `PL-G6J5` asked whether an advisory should be re-based on a different
  denominator or retired, the count said retire, and the close-out that deleted
  the advisory and its 29 assertions printed `FAIL no existing assertion
  removed` with `make check` green and every other guard passing. There the
  gate is the base's **status** rather than the base's field — `status:
  needs-decision` on the base's copy *is* the standing statement that the
  answer is this session's to make — and the branch must be the one closing the
  item. The fold names itself on the page rather than happening quietly: the
  check says the declaration is the closure's own, and that the base is what
  let it be (`PL-ZMGR`).
- **A `dropped` item, or one carrying `not-delegable:`**, has no `verify:`
  command by construction — the first built nothing, and the second is what
  `docket check` accepts *instead of* a command. The check names which applies
  and the remaining checks still run, where a missing command used to stop the
  audit dead. `docket check` and `docket verify` had disagreed about every
  such item, so the close-out the `docket` skill prescribes had no passing
  state (`PL-L4KX`).

Neither is anything a session can grant itself, because each turns on the item
as the **base** holds it — the commission — rather than on the branch. A
`falsifies:` line added beside the deletion it excuses folds nothing and is
reported as the worker's own word for it, and the one declaration that is read
from the branch is gated on a base `status: needs-decision`, which a session
can no more write on its own branch than it can the field. That matters most in
`--self`, where `front_matter_check` is an advisory by design and so catches
nothing; reading the base holds the property in both modes and needs no second
guard. Where the base's copy cannot be read at all, the report says so rather
than folding nothing silently. Where the base holds no copy — an item captured
on this branch, which is also the one route by which a session could write both
halves of the `needs-decision` gate itself — the commission declares nothing
and carries no status, so neither exemption is reached.

`--self` also adds one line when the audited commits name other items' ids.
`item_commits` selects by id so a batch can be judged per item, and a commit
closing several items leads with all of them, so on a batch branch the
selection is the whole branch whichever id is asked about. That is reported
rather than repaired: which item commissioned which path is not recoverable
from the diff, and the failure before was that the widened scope was silent.

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
a failure rather than a vacuous pass. A read git does not answer ends the
audit and is never read as a diff: a `--base` that does not resolve, or a
commit git cannot find, reports `the diff could be read` as failed with git's
own reason, keeps the checks that ran before it, and stops.

What it does not decide is whether the work is *right*. A new test can
exercise the intended line and assert the wrong value, and nothing here can
tell. The report says so on every run, because a tool that implied otherwise
would be worse than no tool.

## What is checked, and what is left alone

Everything mechanically decidable is decided by code: a duplicate id, a
blocker that is not an item, a brief section that is missing or that has
nothing written under its heading, a safety-classed item
sitting in a band it is not allowed to sit in, a `done` item recording a pull
request the default branch has never seen, a `touches` entry naming an item
file no item lives in. These are errors and they exit non-zero.

Everything requiring judgment is left alone. The tool will tell you the top
band has grown past what anyone can choose between at a glance — and how much
of that band is pinned there by a class rather than demotable, because the
same checker refuses to seat safety work lower and "demote what is not
genuinely next" is otherwise advice it would reject — or that most of it is
blocked on decisions nobody has made, or that an item file carries a slug its
title no longer generates. That last one is an advisory rather than an error
for a reason worth stating: deriving the slug and comparing it is exactly
decidable, but renaming the file is not, because whoever does it has to know
which open branch is holding that file first. It also names the items whose
`touches` declare that file, because renaming it without repairing them turns
an advisory into the error above - `PL-3V6C` and `PL-GNXG` both sat on the
default branch declaring a path a rename had moved. But it will not tell you what to
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
new_work_classes = ["feature", "planning"]   # what `next --oldest` leaves out
top_band_limit = 5
untriaged_stale_days = 14
instruction_stale_days = 90        # a dated assertion goes this long
                                   # unchecked before it is named
instruction_paths = []             # the instruction files it reads;
                                   # empty = the audit is off
verify_required_from = 2026-08-30   # omit to leave the `verify:` rule off
verify_prerequisite_refused_from = 2026-09-20   # when a command may no longer
                                   # re-run a tree `check_command` collects
collected_test_paths = ["tests"]   # the trees it does collect; empty = rule off
verify_k_selector_refused_from = 2026-09-23   # when a command may no longer
                                   # narrow a run over those trees with `-k`
payoff_required_from = 2026-09-20  # omit to leave the `payoff:` rule off
recommendation_required_from = 2026-09-21   # a `needs-decision` brief
                                   # marks a recommendation; omit for off
minor_classes = ["feature"]
protected_paths = []
gate_paths = ["Makefile", "pyproject.toml", ".github", ".claude", "docket.toml"]
code_paths = ["src", "tests"]      # what `docket trend` counts as code
notes_file = ""                    # a threads file `docket show` points into
version_file = "pyproject.toml"
roadmap_file = "ROADMAP.md"
```

### Where the settings are resolved from, and why the run says so

From the root of the repository the store belongs to, walked up from the store
itself — `_root` in `cli.py`, run once per command by `_invocation`, whose
`Invocation` every read then shares (`PL-NGBM`). Not from wherever the command
was run, and not from the store's parent: with no
`--items` those three are the same place, and with `--items docs/items` they are
three different ones. A store in no checkout at all keeps the parent, there
being no repository to walk up to.

Resolving from the store's *project* rather than from the caller's is the part
that is deliberate: pointing `--items` at another project's queue must not
answer it under this project's policy. Resolving from the store's *parent* was
a bug, and one that hid two louder ones with it — `PL-P757` has the full
account. Its settings half is the one this section is about: `--items
docs/items` looked for `docs/docket.toml`, found none, and ran the whole store
on package defaults, with no `known_classes`, no `workflow_paths` and
`top_band_limit` at 5 rather than 12.

That failure is fixed. What it cost to find is the reason for the line below:
it was the quietest of the three, spotted only incidentally while the other two
were being repaired, and nothing about a run said which policy had governed it.
So `docket check` now names its settings on its own second line, whether or not
it found a file:

```
docket: 346 open (0 P0, 1 P1, 197 P2, 130 P3, 18 untriaged), 0 errors, 4 advisories
  settings: docket.toml
```

```
docket: 21 open (0 P0, 0 P1, 14 P2, 7 P3, 0 untriaged), 0 errors, 1 advisory
  settings: no /srv/other-project/docket.toml, so library defaults govern this
  run rather than this project's - a finding below may be this store read under
  the wrong policy rather than a store that is wrong
```

The second form is what a project running on the defaults sees, which is a
supported way to use this tool rather than a fault. It is also what a
regression of `PL-P757` would look like: root resolution moving again makes the
line change, and a changed line is the signal. That is the whole of why it is
printed on the run that *found* its config too — silence is ambiguous, a reader
who sees no line cannot tell a config that was found from a version of the
command that reports nothing, and it is the difference between two runs' lines
that carries the diagnosis.

It is a fact about the run rather than a finding — the category the `verify:`
cost line beside it is in, and the open-item counts above it — so nobody is
asked to act on it.

Refusing such a run instead was considered and is wrong: reading another
project's store under its own defaults is correct behaviour and a real use.

### `notes_file`: making a threads file reachable

A project that keeps a running cross-session log beside its queue - threads
that outlive an item, span several, or have none - has a discovery problem the
file cannot solve for itself. The instruction such a file carries is some form
of *read this if your task touches an open thread*, and the condition cannot be
evaluated without reading the file, which is the whole cost it was meant to
avoid. So it resolves to reading all of it every session, or to reading none of
it and losing the continuity it exists for.

Point `notes_file` at it and `docket show <id>` answers the decidable half. It
splits the file at its `##` headings and prints one `file:line` per thread
naming that id:

```
  notes: 2 thread(s) in docs/WORKING_NOTES.md name PL-2FM6
    docs/WORKING_NOTES.md:1187 (about) Measured and answered: a server-rendered chart is not the way out
    docs/WORKING_NOTES.md:1006 (mentions) Decided: no numpy, and the reason is fit rather than dependency avoidance
    Whether a thread is still true is not something this can tell you.
```

`about` means the thread's heading names the id; `mentions` means its body
does. The distinction is worth its column: on this repository's own notes file,
31 of the 106 ids cited appear in a heading, so a heading-only reading would
have printed nothing for the other 75 - and silence there is indistinguishable
from "no thread concerns your item", which is the failure rather than a cheaper
version of it. Reading bodies too reaches 105 of 106 without becoming noise:
74 ids match exactly one thread, 23 match two, 7 match three, and one
cross-cutting id matches six.

Nothing is printed when the setting is empty, the file is absent, or no thread
names the id. That silence is deliberate - a line reporting any of the three
would print on nearly every `show` and change no decision.

**It points; it does not summarize.** Whether a thread is still true is not
derivable from the file, and a generated precis of a stale thread would be read
as current. The line is a pointer with a line number, and the judgment stays
with the reader.

### The one thing `check` says about that file: a thread the heading calls open

A notes file usually carries a policy that a resolved thread is deleted rather
than left stale, and nothing reads it. `docket check` raises **one grooming
advisory** naming each `##` section where both of these hold:

1. the heading's own leading word says the thread is open - `Open thread:`,
   `Open:`, as against `Settled:`, `Decided:`, `Measured`, `Built`, `Shelved`,
   `Aspirational`, `Long-term`; and
2. every id the section cites, heading and body alike, resolves to an item
   that is `done` or `dropped`.

```
docs/WORKING_NOTES.md: 4 thread(s) the heading calls open, whose every cited
item has closed - "Open: the repository has no README - PL-WB5K, PL-N092,..."
(line 868); … ; delete what is finished, once its outcome is recorded
somewhere that maintains itself, and re-head what outlived its items
```

**Both clauses, because the second alone is noise.** Measured on the notes file
this package grew beside, 2026-09-21: clause 2 by itself names 16 of 26
sections, most of them correct content that other rules cite - a settled
decision kept because the question recurs, a measurement another document
points at. Both clauses together name 4, of which 3 had already been filed as
separate items, one at a time, by six different sessions.

**A section citing no id is never named.** Direction with no item is one of the
things such a file is for, and an id the store cannot resolve leaves its thread
unnamed too: an unreadable citation is not evidence that a thread is spent.

**An advisory, and it cannot become an error.** The fourth section the pair
names on that file has all three of its items closed and is genuinely still
open - what is left is a published value nothing in the project can settle.
That false fire is permanent rather than tunable, which is also why this is a
grooming advisory rather than a close-out check: one permanent false fire at
every close-out trains a reader to skim the block a real advisory shares.
Whether a thread's outcome is recorded somewhere that maintains itself is the
judgment, and it stays with the reader.

The advisory is skipped where the project configures no `notes_file`.

### The instruction set's dated assertions

Instructions assert facts about a world that changes - a network policy, what a
tool does, what a check catches - and nothing expires any of them. A rule that
is long costs attention; a rule that was true when it was written and is false
two years later gets *obeyed*. Every size gauge a project keeps is blind to
that, because it measures how much text there is rather than how old what the
text claims has become.

`instruction_paths` names the files: a markdown file, or a directory every
`.md` beneath it is read from. Each line carrying an ISO date is one assertion,
dated by the **newest** date on it, and one more than `instruction_stale_days`
old puts it in a grooming advisory - oldest first, the five oldest named and
the rest counted.

Only the decidable half is here. *Which* assertions are due is arithmetic on
dates; whether an aged one is still true is left to whoever reads the line.

**It can reach zero, which is what shaped it.** A raw age list cannot, since
every assertion ages and the report would name more of them every day - and
the cost of an advisory that cannot reach zero is not the entries it names but
the next advisory, which gets read the same way. The threshold bounds the set;
re-verifying a line and writing today onto it empties it. Reading the newest
date is what makes that work for both kinds of dated text: a measured fact is
re-measured and re-dated, and a record - what was decided, and when - keeps its
own date and gains a re-verification one, so neither has to be falsified to be
cleared.

A date inside a code fence is skipped: a dated example command is a template
rather than a claim, and an entry a reader cannot honestly clear is the one
thing that stops the report reaching zero.

**Age is a proxy for staleness, not staleness.** A dated record does not go
stale; a measured environmental fact does, and this cannot tell them apart.
Early precision is mediocre by design, and the narrowing that fixes it is
meant to be learned from the first firing rather than guessed beforehand -
which is also why `instruction_stale_days` defaults to 90 rather than to a
half-year: a threshold that first fires in about ten weeks is validated by its
own first firing, while a threshold nothing reaches for five months is a
mechanism discovered to be broken at exactly the moment it was built to help.

The advisory is skipped where the project names no `instruction_paths`.

## Requirements

Python 3.11 or newer, and nothing else. Standard library only, so a
session-start hook can run it in a bare checkout with no virtualenv and no
install step.

## Running the tests

From the **repository root**, never from inside `subprojects/docket/`:

```bash
uv run pytest subprojects/docket/tests
```

The root `pyproject.toml` declares
`testpaths = ["tests", "subprojects/docket/tests"]` and puts
`subprojects/docket/src` on `pythonpath`, so these tests are part of the root
suite and resolve against the root environment and the root `uv.lock`. That is
what `make check` and CI run, so it is where an answer about them has to come
from.

`cd subprojects/docket && uv run pytest` also works, and that is the problem
rather than a convenience. This directory has its own `pyproject.toml`, so
`uv` builds a **second** environment from a lockfile it resolves on the spot -
and the tests then pass against a dependency set nobody reviewed and CI never
runs, which is a weaker answer wearing the same green tick. It leaves
`subprojects/docket/.venv/` and `subprojects/docket/uv.lock` behind, both of
them ignored, so nothing in `git status` says it happened (`PL-8PT6`).

Named by path rather than in prose, which it could not be until `PL-MXSL`:
both are ignored, and `doc_check` required a cited path to exist, so a citation
to either resolved on a developer's machine and reddened CI. It now asks git
whether `.gitignore` covers the path and stops requiring one it does, which is
what `PL-F933` was open for.
