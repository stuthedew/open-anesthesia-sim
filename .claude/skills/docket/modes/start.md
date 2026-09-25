# docket: start

Read this before starting a named item: the in-flight guards, the concurrency
read, and what to name after the item.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

## Mode: start an item

**First, ask whether anybody else is already on it: `git fetch origin` and
then `bin/docket show <id>`, which marks it `IN FLIGHT` where a branch has
claimed it or is named for it, `STATUS HELD` where a branch moved its status
(a triage or grooming pass, or a close-out), and names the refs it could not read.** This is the one step with no other guard. `docket next`
excludes in-flight work, so a session that got here through `next` is already
covered — but an item named by the project owner skips `next` entirely, and
`triage`, `check` and reading the file with `cat` all say nothing. That is
backwards: naming an item is the higher-confidence path and was the one with
no check.

**The fetch is not optional, and it is the half that was missed.** Only
`docket branch` refreshes; `flight` and `show` read the refs this checkout
already holds, deliberately, so that they answer in a bare or offline
checkout. Without a fetch the answer is as old as the clone. Observed
2026-09-01: a session checked, was told nothing was in flight, and a branch
carrying the item was pushed four minutes later — the owner caught it, not the
tooling. Even fetched, the answer is bounded to what has been *pushed*, so
read a clean result as "nothing visible", never "nothing".

**Then claim it before any work: `bin/docket claim <id>`, passing each
attribution line your commits must end with as `--trailer "Key: value"`.** It
fetches, refuses with exit 3 and writes nothing where another branch holds the
item first, and otherwise makes one empty commit - subject `<id>: start`, a
`Claim: <id> <branch> <session>` trailer - with the attribution lines in the
same paragraph, since git reads a trailer from the last paragraph alone and one
added below it afterwards turns the claim into prose. On a branch with no
upstream of its own - none, or the default branch, which is how the web harness
starts some sessions (`PL-KX73`) - and no copy on the remote, it pushes with
`--set-upstream`, fetches again and re-reads, so a claim another session
pushed in the same minute is seen: exit 3 then prints the line to yield by, and
exit 4 means the claim is only in this checkout - the push failed, or the
branch was already on the remote and none was tried - so nobody else can see
it until you push (`PL-1X56`). Who holds
an item is that recorded claim, read by `claims.holdings` (`PL-MB2W` § "Design
round, 2026-09-24"), and not whatever shape the first push happens to take;
`show`, `flight` and `next` answer from the same read, so a takeover or a yield
reaches all of them. The
reading side above is as hard as it can get - a fetched `show` still answers
only for what has been *pushed* - so a claim that waits for the first real
commit waits as long as that work takes: `PL-0HPV`'s session ran twenty minutes
before its first push on 2026-09-22, and another session reported the item
unstarted inside that window (`PL-7TVT`). It costs nothing here -
`.github/workflows/quality.yml` triggers on `pull_request` and on `push` to
`main`, so a push to a branch with no pull request open runs no CI, and the
squash merge folds the commit away.

**Where the claim's push opens the branch's first pull request, open it as a draft**
(`draft: true`), because a claim rides it and GitHub will not merge a draft by
hand or otherwise. `#978` was merged by hand six minutes after it
opened, with its claimed cut still uncommitted (`PL-H14W`). Mark it ready
(`draft: false`) in the push that closes or blocks the claimed item, which is
also the push that arms it under `CLAUDE.md`'s commit-and-push bullet.

**A session has two things to remember: `claim` at pickup and for every rider,
and `bin/docket yield <id>` when it stops without closing.** A rider is a second
item picked up mid-session - one filed as housekeeping, or the item the first
turned out to be waiting on - and a session named after one item is invisible
under every other: `PL-HX5C` implemented `PL-W8XP` in full inside a session
titled for other work, and `PL-N2PP`'s rider was seen by no guard until its
push. On a branch that already has an upstream of its own, or a copy on the
remote, `claim` commits and does not push, because a pull request may be open
and armed and the push would merge the claim away with the branch (`PL-QP9Z`);
it says so, names the push command and exits 4, since until that push no other
session can see the claim; the claim rides your next push, made after
disarming auto-merge if it is armed. The remote's copy of
the branch decides that, not the tracking setting. Running `claim` again on an
item the branch already holds writes nothing, and pushes a claim an earlier run
could not.

**Taking over a dead claim is `bin/docket claim <id> --over <branch> --reason
"..."`, and only on the owner's word or with `get_session` showing the holding
session ARCHIVED or failed.** A claim lasts seven days past its branch's last
commit, so an abandoned one would otherwise hold the item for a week. The
reason goes into the commit's body, and the claim sorts where the one it names
stood, in the order `claim` and `show` both read. A claim past its lease is
not dead in that sense but gone: it holds nothing, `claim` passes it with no
`--over` and no evidence, and `show` prints it under `LAPSED` - only where
nothing else claims the item - with `--over` offered for the record it adds
rather than as a condition. The `<session>`
token in a claim is `CLAUDE_CODE_REMOTE_SESSION_ID`,
which reads `cse_...` where `get_session` wants `session_...`; the part after
the prefix matched on the one session compared in full, on 2026-09-24. A branch that
already contains the holder's tip is a continuation, and `claim` writes the
takeover without `--over`.

`bin/docket show` prints `Its file is already edited on <branch>` where no hold
is live (`PL-N1JK`): a branch is in that file, which says nothing about whether
anybody has claimed the item.

The cost is that an abandoned branch and a live session look alike in `flight`
for as long as neither has aged or opened a pull request. It says so, and gives
each branch's age to the minute and whether a pull request is open on it
(`PL-3QM9`, `PL-7TVT`); `bin/docket stranded` recovers what one strands. Where a
young branch with none open is the question, the session list below is the one
reading that can answer it. That trade is worth taking - a session picking a different item
because one looked busy costs almost nothing against a queue this size, while
two sessions on one item costs a session and a merge conflict (`PL-PRHN`).

**One shape of abandonment is separated outright rather than by age**
(`PL-Q664`). A branch whose every item it holds is closed in its own copy and
which has no pull request open is finished work that has stalled, and `flight`
moves those rows out of the list the age is meant to separate, into one saying
that nothing there is being worked. Read it as what it says: nobody is on that
branch, so the item is not being worked by a live session - and nothing there
says the work is reviewed, correct or ready, which is still a branch to read
rather than a merge to make.
The ids stay in flight for `docket next`, because the work exists and starting
it again would redo what is already written.

`claim`'s read after its push narrows the race rather than closing it: a
claim written first and pushed last still orders first, and the session it
overtakes learns that only by reading `show` again.

**So read the session list too, which sees what no ref can.** `list_sessions`
from the `claude-code-remote` MCP server (`mine: true`) returns every session's
title and its branch, including a session that has committed nothing at all —
the window the two rules above leave open. Scan the live ones for the id
(`session_status` `RUNNING` or `IDLE`; archived and completed ones are finished
work), in the title and in `external_metadata.current_branches` both, because
either can carry it and neither reliably does.

**It adds a warning and never a clean bill of health.** It rests on the rename
rule below, which is followed about three times in four: measured 2026-09-02
over a twenty-session window, nine titles carried an id and at least three
sessions demonstrably working one item had never been renamed. A session
working an item under a generic title is indistinguishable from one working no
item at all — so unlike `show`, which names the refs it could not compare, this
read cannot name its own gaps. Finding nothing here means nothing; finding
something is decisive. It is also this harness only: `docket` knows nothing
about it and must not (`PL-SK88` records why).

**Where two branches have claimed the item, `bin/docket show <id>` says
which session yields. Read the verdict; do not reason one out.** It prints
the live claims in order — whichever branch claimed the item first holds it, a
tie breaking on the claim commit's hash, and a takeover standing where the claim
it names stood — and both sessions compute that order from the same commits, so both read the same answer. Reasoning it out instead is how two
sessions reach *opposite* answers from one set of facts, and the outcome that
costs most is not both continuing, which is where the project already was, but
both standing down: the item is then unstarted and each session believes the
other has it.

One consequence worth acting on before the verdict is ever needed: a branch
nobody can fetch is not in the other session's copy of the order at all, which
is the second reason `claim` pushes at once, and why exit 4 - a claim only this
checkout holds - wants the push made, or retried, before any work.

**Yielding costs a session's work only if the session throws it away**, so hand
it over instead:

1. Stop implementing, and open no pull request.
2. Commit what you have, run `bin/docket yield <id>` with the same `--trailer`
   lines as the claim, and push your branch. The container is ephemeral, and a
   diagnosis nobody receives is a session spent for nothing. Pushing cannot flip
   the verdict — your claim is the later one, which is what made you the
   session that yields - and the yield ends your claim in the record
   `claims.holdings` reads, which `show`, `flight` and `next` all answer from.
3. Say in the reply which branch you yielded to, which branch your findings are
   on, and what they are: the root cause, the failing test, the file and line.
   A yield that discards the work is a session thrown away; one that hands it
   over is a session spent on reconnaissance, which is a different price.

**The holder never yields back, and the case that looks like it should is
already decided by the dates printed beside it.** A later session that has done
more work is only possible where the earlier one has been sitting still — so
where the branch holding the item has not committed since before your own first
commit, you are not racing a live session, and a branch's age is the reader's
call here exactly as it is in `flight` and `stranded`. Say so to the project
owner and keep the work; do not yield into silence. That test is one-sided
deliberately: applying it can leave two sessions working, which is where the
world already was, and can never leave neither.

**Then ask the other question: *is another session in these files?*** Every
step above answers "is another session on this item?", and that is not what
collides. Two sessions on different items are the normal case and neither
should yield — but they meet at merge if both edit the same file, which is
what `bin/docket concurrent <id>` exists to say. Run it. It needs no argument
the session does not already have.

It answers in two parts, and they are different kinds of evidence:

- **Declared overlap** — other items whose `touches` name a path this one
  names. A prediction written before either was started, so it fires on work
  nobody has begun and goes stale the moment a branch wanders outside its
  declaration.
- **Already changed on a branch in flight** — the files a live branch has
  *actually* changed, read from the branch itself. This one means the
  collision has already happened.

**Usually the answer is "proceed, and expect to resolve", not "pick something
else".** Two unrelated items legitimately touch one file; the point is that
the second to merge resolves deliberately instead of discovering it. Yield only
where the overlap is the same logic rather than the same file — and then it is
the yield rule above that decides which session stops, not this answer. What a non-empty answer always changes is
sequencing: land the smaller change first, and say in the reply which branch
you expect to resolve against.

Read a clean result the way `concurrent` states it: it rules work out and never
certifies it. Silence means no branch has touched these files *yet*, and says
nothing at all about a file this item touches without having declared it —
which is why filling `touches` in as work begins, below, is what makes the next
session's answer true.

**Then, where `show` printed `RE-CONFIRM`, re-confirm the item before writing
any code** (`PL-TQN2`). An item describes the tree as it stood on its `added:`
date, and this tree moves fast. The interface moved from Flet to Qt at
v0.4.26, and an item filed before that can describe code that is gone. `show`
has already printed the facts: for each declared path, whether it is in the
tree and how many commits changed it since filing. Read the brief against the
tree as it is now, and take one of three outcomes:

- **Still true.** Work it as written.
- **Changed shape.** The problem is real, but the brief places it wrongly: a
  moved file, a renamed function, a narrower or wider scope. Rewrite the brief
  first, `touches` included, in a commit leading with the id, then work it.
- **Gone.** Drop it with the evidence as the reason: `bin/docket set <id>
  --status dropped --reason "..." --closed DATE`, where the reason says what
  was checked and what showed the problem no longer exists. A dropped item
  clears as surely as a fixed one; `ROADMAP.md` § "What counts" counts both.

**A touched path that is no longer there is a question, not the answer.** A
problem can move with its code rather than leave with it. In five Java
projects, 20-50% of self-admitted-debt removals turned out to be the comment
deleted along with its class or method, not the debt paid (Zampetti,
Serebrenik and Di Penta, MSR 2018, doi:10.1145/3196398.3196423). So ask whether
the *problem* is gone, not the file: follow the code first, with `git log
--follow` on the old path or a search for the function the brief names. A path
reading `not in the tree, and untouched since` is most often a file the work
will create, and says nothing either way.

The session starting the item decides this and says what it decided in the
reply. An item's disposition is the session's call under
`.claude/rules/instruction-writing.md` rule 14, not a question for the owner.

Then decide where the work happens and act on it — do not ask. Continue here when
this session's context is an asset (short, already about this item, just
diagnosed it). Start fresh when it is a liability (already completed
something else, long, or the item wants a model this session is not running).

Then name the work after the item, because a session list is unsearchable
otherwise:

- **Session name** — rename immediately to lead with the id. On a remote
  session, `set_session_title` via the `claude-code-remote` MCP server.
- **Commit subjects and PR title** — always carry the id. These outlive the
  branch.
- **Branch** — `claude/pl-k7qx-short-slug` where the session creates it. A
  branch generated before the session started cannot be renamed; that is
  expected, and the commits carry the id instead. Say so in the reply. Leading
  every commit subject with the id is what attributes such a branch's work -
  `tools/branch_id_check.py` and `flight`'s unattributed line read the
  subjects, and an id buried mid-sentence does not count - but it holds
  nothing: the `Claim:` trailer `bin/docket claim` wrote does. A `claude/*`
  branch with work outside the queue and no claim is refused in CI and listed
  as `unclaimed:` in `flight` (`PL-N162`).

**A `P0` is a hotfix.** Before feature work, on its own branch, with a patch
version bump and a regression test. It joins no milestone list.

**Never start an `L` item straight from a queue entry.** An `L` is aspirational
scope that reached the queue rather than `ROADMAP.md`. Promote it into a scoped
milestone first, per the development rules there, and start the items that
milestone produces.

Set the item's `status` and `feature` as work begins, and add `touches` if it
is missing — that is what makes the next concurrency answer correct.
