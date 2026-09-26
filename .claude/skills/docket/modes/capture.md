# docket: capture

Read this when something needs recording - a passing thought, a finding this
session will not fix - or when the session is about to do repository work that
no item names.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

## Mode: capture

Triggered by the owner raising a passing thought they are not developing, or
by a finding this session makes that it will not fix.

**Whether a finding this session made is one it may fix instead is decided in
`CLAUDE.md`, not here.** Its capture bullet holds the three tests that all have
to pass and the cap of two per branch; the door is deliberately narrow, and a
second copy of it here is how the two drift apart. Read it there, and treat
everything below as being about a finding that is being recorded.

**This is the opposite case to the one above, and the difference is whether a
design conversation is happening.** A thought dropped in passing — "the
induction curve looks wrong at low flows" — is captured immediately, because
the owner has moved on and nothing is lost by recording it. An idea being
worked through with you is not captured yet, because it is still changing. If
unsure, ask yourself whether the next reply is likely to change what the item
says: if it is, propose rather than create.

```bash
docket new "The induction curve looks wrong at low flows"
```

That is the whole procedure. No id to allocate, no band to choose, no file to
edit, nothing to conflict with another branch. Write the brief into the item
if the context is live and worth keeping — it is expensive to reconstruct
later and cheap to write now — but never let a missing brief stop the
capture.

**Append the brief below what capture wrote, rather than writing a second
problem statement above or around it.** Capture writes one line — the title
under a `**Problem.**` — precisely so that appending is the correct operation,
and the fuller sections elaborate the statement already there. `docket check`
errors where a required heading is left empty with a `**Problem.**` starting
again below it, which is the shape an older four-heading template produced and
which reads as an item with no brief at all (`PL-D188`).

**A finding that completes a frozen or in-progress item is not a new item.**
When work turns up something such an item needs in order to be properly
finished, the two are worked together - one branch, closed together - rather
than filed as sequential items. A freeze closes new behavior and features, not
the completeness of a fix; `ROADMAP.md` § "The gate is a snapshot, not a moving
target" carries the rule and the reasoning.

Never hold a finding in conversation until the current work lands. The
container is ephemeral; an uncommitted thought is one interruption from gone.
Commit the new item on its own so it survives an abandoned branch.

Where the branch carries only item files, `CLAUDE.md`'s commit-and-push rule
opens its pull request at its first push and arms auto-merge. Before arming,
record the body with `python3 tools/pr_body_check.py --record` and commit and
push the file it writes, since `pr-title` holds a pull request until
`docs/pr-bodies/<N>.md` holds its body; `bin/docket arm` still answers `arm`,
a record arming on green like the item store (`PL-979D`).

**A diagnosis that produces more than one item files them under one
`feature:`, in the same call.**

```bash
docket new --feature session-start-cost \
  "Attribute the session-start hook's wall-clock cost to a stage" \
  "Replace the per-blob git show fan-out with one git cat-file --batch" \
  "Memoize the runner: 82 of 192 git subprocesses are exact duplicates"
```

One flag, spent at the only moment anybody knows the items are one problem.
Without it the group exists in the reply and nowhere else: `feature:` is the
store's only grouping, and `docket feature <name>`, `docket status` and
`recommend`'s finish-a-feature preference all read it, so an ungrouped group
is ranked, surfaced and reported as unrelated work forever. The project owner
tracks problems rather than ids - "when do we fix the slow session start",
not "when do PL-XD3C, PL-0J9K and PL-MMVF land" - and five items filed across
five commits on 2026-09-16 carried no feature at all (`PL-N638`).

**Pitch the name at what completes.** A feature here is a group with a "done
when" the owner would notice closing: `session-start-cost` at 5 items,
`doc-consistency-checks` at 4, `core-boundaries` closed at 6. Not a standing
theme - `dev-tooling` is 134/212 and answers no question about whether
anything finished. The big end already has a home: anything release-sized is
a `ROADMAP.md` milestone, so the gap this closes is at the small end, where a
two-to-five item fix would otherwise scatter.

**Two consequences to know before using it.** A small feature outranks a
large one inside its band, because `recommend` orders by open items
remaining, fewest first - so grouping tightly also pulls the rest of a group
up `docket next` once one of them lands, which is the point rather than a
side effect. And `docket gate --feature <name>` splits a milestone's debt by
this same field, so moving an item into a fine group moves it from "cleared
by the milestone" to "cleared before it begins".

The digest names an item that exists only on a branch when it finds one, and
`bin/docket stranded` prints it with the `git checkout` line that restores the
file. The command cannot tell live work from an abandoned branch, so that
judgment is the reply's: leave a branch someone is working, and recover from
one nobody will merge - restore the file, commit it on its own, and say in the
reply which branch it came off.

**Run the command; do not act on the digest's copy of its line.** The digest is
written once, at session start, and then resent on every turn for the rest of
the session, so its stranded line ages while the reply reading it does not. The
command refreshes the default branch before it compares and the digest cannot,
which is the difference between "this item is lost" and "this item merged nine
minutes ago" - and the recovery is a `git checkout` that overwrites the merged
copy with the older one, which is what `PL-XLQ5` cost (`PL-KBFN`, `PL-39B7`).

**A second list below it names items `main` already holds, and hands a `git
diff` rather than a recovery.** An item file is created once and appended to by
every session that learns something about it, so the unmerged *section* is the
commoner loss and nothing used to report it (`PL-KSCW`). Read the diff and
carry across what is worth keeping - a section appended to a brief usually
whole, a field both sides have edited never from a command line. There is no
`git checkout` for these on purpose: `main` holds a copy of its own, and
restoring the branch's over it discards whatever landed since. A branch holding
an *older* copy is not listed at all, which is the other half of the same
comparison (`PL-MBTZ`).

**The same command's second half is not about items at all, and it is not a
judgment call in the same way.** It names a branch whose pull request already
took part of its work and left the rest - a commit pushed after the merge,
which nothing merges and nothing else reports (`PL-3D2M`). Restart the branch
on the merged `main` and carry the commit forward as a new pull request, never
by pushing to the merged branch again, which is what lost it:

```bash
BRANCH=claude/the-branch-stranded    # the ref `stranded` named

git push origin --delete "$BRANCH"   # the branch itself - the owner's to run
git branch -dr "origin/$BRANCH"      # this clone's remote-tracking ref
git fetch origin main
git checkout -B "$BRANCH" origin/main
```

**`bin/docket branch` now names this case while the commit is still
recoverable**, which is the cheaper end of the same problem: it prints the
restart advice above rather than "merge the base in" where the base already
holds a whole commit of the branch (`PL-8M8H`). That is the session holding the
commit being told, rather than the next session finding it stranded. Reaching
`stranded` still means the push already happened.

**The first command is the project owner's, and the second is not a substitute
for it.** `git branch -dr` clears this clone's remote-tracking ref and nothing
else, so where the branch still exists on the remote the next `git fetch
origin` recreates it under the default refspec `+refs/heads/*:refs/remotes/origin/*`.
The deletion does not survive the next fetch, let alone the next session:
`bin/docket stranded` names the branch again and the next session repeats the
whole recovery, which is the re-discovery loop `CLAUDE.md`'s housekeeping rule
exists to stop, arriving through the procedure rather than through the absence
of one. Measured 2026-09-05 on `origin/claude/next-item-75htc6`, where `git
ls-remote --heads origin` still returned the branch after the ref had been
cleared. Deleting a branch on the remote is destructive and outward-facing, so
run the other three, then **say the remote deletion is outstanding and leave it
to the owner** (`PL-K2C8`). This is also why none of it weakens the `--prune`
prohibition below: prune and `branch -dr` clear local refs and nothing else, so
neither one finishes the job.

**These commands destroy a branch, so confirm the merge before running
them.** The check now requires the base to have taken one of the branch's
commits whole, which is what a squash merge leaves and what two sessions
writing identical `docket record` lines does not (`PL-5TRV`, `#372` reported
as merged while its pull request was open with two commits on it). That
narrows the false verdict; it does not remove the reader's part. One look at
the pull request's state settles it, and where the session cannot reach
GitHub, `git log --oneline origin/main` for a squash subject naming the
branch's ids does. A branch whose pull request is open is live work: leave it.

**Clearing branch refs does not finish the job after a history rewrite.** A
local clone keeps purged content reachable through its release tags, which
still point at pre-rewrite commits until something re-points them by force -
observed 2026-09-06 across `v0.3.7` to `v0.4.4`, against a remote that was
already clean, and `git log --all` is what shows it (`PL-YGF3`):

```bash
git fetch --tags --force origin
```

`bin/docket branch` prints that line itself where it finds a rewritten
history, which is the moment it is wanted; this is for the pass that clears
refs without being on a diverged branch.

**Delete that one ref by name; never `git fetch --prune`.** A stale
`origin/<branch>` can be the only surviving copy of an item captured on a
branch nobody merged, which is why `fetch_remote` does not prune and what
`stranded` recovers - `PL-HKF4` came within one prune of exactly that.
`.claude/hooks/no-prune-guard.sh` refuses the call and prints these three
commands, which is why the prohibition is no longer resident in `CLAUDE.md`
(`PL-JK0M`); `PL-1Q3S` and `PL-PF8H` are the two ways such a ref arises.

## Mode: housekeeping nobody filed

Triggered by the session being about to *do* repository work that no item
names: resolving a merge, clearing a stale `origin/<branch>` ref, a docs
sweep, a lint fix, recovering a stranded item, backfilling a field the store
wants.

**The rule: file the item first, then start it under its id** — `docket new`,
then **Mode: start an item**, in
`.claude/skills/docket/modes/start.md`. This is the cheap half of a problem the project has
already paid for the expensive half of. `flight`, `show`, `next`, `concurrent`
and the digest are all id-matchers, so work carrying no id gets a clean answer
from every one of them, correctly and uselessly. And unlike a race between two
sessions starting the same item, which closes the moment one of them pushes,
this stays invisible after *both* have pushed (`PL-CP74`).

**Class it `housekeeping`, and it owes no argument for itself.** The id is
load-bearing; the brief is not. `docket check` excuses a `housekeeping` item
`**Why it matters.**` and `**Done when.**`, so the whole of filing one is:

```bash
bin/docket new "Triage the 12 untriaged captures standing in the queue on 2026-09-19"
bin/docket set PL-CSV0 --priority P2 --effort S --classes housekeeping \
  --touches docs/items --status ready --verify "..." --payoff "..."
```

`**Problem.**` is what `docket new` writes from the title, and that is the
brief. The two sections that go are the two such a pass cannot answer without
restating the category - "why it matters" is the standing rule above, and "done
when" is the `verify:` command in prose. The command itself still stands: the
exemption is the argument, never the proof - and `payoff:` stands too, for the
same reason. It is one line rather than a section, the ranking can still put a
housekeeping item in front of the owner, and "the queue stops carrying twelve
captures nobody can read" is not a restatement of the category.

Two limits, both enforced. It may not sit beside a `debt_classes` entry -
`defect`, `safety`, `science`, `refactor`, `perf` - because debt is the work
that most needs a brief, and a pass that also fixed a defect is two items. And
it is process work for the top-band rule, so a housekeeping item cannot seat
above product work in `P1`.

Measured before it was built: 22 items titled "Triage ..." carrying 1,127 lines
of brief, 12 repeating the same rationale and 2 holding a finding a later
session needs (`PL-TQFB`, project owner, 2026-09-19, ratified, over pointing
the requirement at a standing rationale and over dropping the item altogether -
the second was refused because the id is what `tools/branch_id_check.py` and
the in-flight mark both read). The existing 22 are left as they are; this is
for the next one.

It buys a record as well as visibility. Housekeeping is obvious enough that two
sessions recommend it in the same hour; unfiled, it leaves nothing behind
saying it was already done, so the next session rediscovers it and recommends
it again.

**How small is too small to file is the judgment here, and the line is whether
the work gets a commit of its own.** A rule demanding an item for a one-line
typo fix would convert the queue into a log, which is worse than the collisions
it prevents — so a fix riding inside a commit already led by an item's id is
filed by that id and needs nothing more. A fix `CLAUDE.md`'s fix-now rule
admits needs nothing more either, even though it takes a commit of its own:
that commit leads with the current item's id, so every id-matcher still sees
it. File it when it is the reason this session exists, or when it will take a
branch of its own. Not deleting remote branches, even when that is why the
session exists: it takes no commit at all, so there is nothing for an id to
lead, and the reply hands the owner the list and the command (`PL-S8LZ`).

`tools/branch_id_check.py` catches the case where none of this happened: `make
check` and CI fail a branch ahead of `main` that carries no id in its name and
leads no commit subject with one. It decides visibility only, never whether the
work deserved an item — that judgment is the paragraph above and stays here.
Since `PL-J9S0` it also fails a branch whose work outside the queue claims
nothing, so housekeeping filed as an item is claimed like any other work,
`bin/docket claim <id>` before its first commit; the first-edit hook says so.

It binds the `claude/*` namespace and nothing outside it (`PL-8P6D`), so a
session that names its branch anything else is unchecked rather than exempt:
the rule above still applies to it, with nothing left to enforce it.
