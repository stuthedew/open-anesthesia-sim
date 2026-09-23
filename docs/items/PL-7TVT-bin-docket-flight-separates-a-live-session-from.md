---
id: PL-7TVT
title: bin/docket flight separates a live session from an abandoned branch only by commit age, which cannot fire in the first hour: PR #757 sat green and unclaimed 25 minutes after its session was archived, with its three items still reading 'do not start these again'
priority: P2
effort: M
status: done
classes: defect, infra
feature: carrier-detection
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, subprojects/docket/README.md, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_vcs_silence.py, tools/open_pull_requests.py, tests/unit/test_open_pull_requests.py, docket.toml, docs/ARCHITECTURE.md, .claude/skills/docket/modes/start.md, .claude/rules/instruction-writing.md
added: 2026-09-20
closed: 2026-09-23
verify: grep -q 'def test_a_branch_minutes_old_carries_its_pull_request_rather_than_a_verdict' subprojects/docket/tests/test_cli.py && uv run pytest -q subprojects/docket/tests/test_cli.py -k a_branch_minutes_old_carries_its_pull_request
root-cause-of: PL-N2PP, PL-HX5C, PL-99YZ, PL-X3NY, PL-Q664
generator: spent - the project owner accepted on 2026-09-23 the one shape left as its documented limit: a session that ends mid-work before opening a pull request leaves a branch that reads as young with none open for about its first hour. flight says so in those words, the minute age exposes it within the hour, it only ever withholds an item, and the session-list read in start.md and rule 14 is the backstop; PL-SK88 keeps docket from reading session state. Every other shape of an ended session reads as what it is
---

**Problem.** bin/docket flight separates a live session from an abandoned branch only by commit age, which cannot fire in the first hour: PR #757 sat green and unclaimed 25 minutes after its session was archived, with its three items still reading 'do not start these again'

**Why it matters.** `bin/docket flight` is the guard that stops two sessions
starting the same item, and its output is written in the imperative - "do not
start these again". Commit age is the only signal it has for telling a live
session from an abandoned branch, so for the first hour of a branch's life the
two are indistinguishable and the guard reads as a claim it cannot support:
PR #757 sat green and unclaimed for 25 minutes after its session was archived
with its three items still reserved. The failure is silent and it is in the
direction of *withholding* work rather than duplicating it, which is why it has
never announced itself - a session told not to start an item simply picks
another one.

**Reproduced 2026-09-20.** `bin/docket flight` reads commit timestamps and
branch refs only; nothing in `subprojects/docket/` reads a session's state, and
nothing can, since `bin/docket` is required to run from a bare checkout with no
virtualenv and no network.

**Decision needed.** What signal, readable from a bare checkout, separates a
live session from an abandoned branch inside the first hour - or whether the
honest answer is that none exists and `flight`'s wording should stop implying
one.

**Recommended:** change the wording, not the signal. Nothing git can see
distinguishes the two cases, and the two candidate signals both fail the bare
checkout requirement: session state needs the harness, and a merged-or-closed
pull request needs the network. So the cheap, honest repair is for `flight` to
say what it actually knows - a branch exists and carries commits for this item,
last commit N minutes ago - and to stop issuing an instruction it cannot back.
A reader who sees "claimed 3 minutes ago" and knows the claim may be stale
behaves correctly; one told "do not start these again" cannot tell the two
apart at all.

**Done when.** `bin/docket flight`'s output either carries a signal that
distinguishes a live session from an abandoned branch, or states what it knows
without instructing on what it does not - and a test under
`subprojects/docket/tests/` drives a branch whose last commit is minutes old.

**Design round, 2026-09-22 (the session that recorded the generator).** The
generator has two faces, and they want different fixes.

- **Live work nobody has pushed reads as startable** (`PL-N2PP`, `PL-HX5C`,
  `PL-99YZ`; `PL-0HPV` on 2026-09-22). No signal git can see precedes a
  session's first push, so the only deterministic fix is to make that push come
  first. It needed no code: `_annotates_only` already reads a commit with no
  diff as a claim, so `git commit --allow-empty -m "PL-K7QX: start"` and a push
  claim an item before any work. `.claude/skills/docket/modes/start.md` now
  says so, both at the start and when a second item is picked up (the rider and
  mid-session shapes of `PL-N2PP` and `PL-HX5C`), and
  `test_an_empty_commit_leading_with_an_id_claims_the_item_before_any_work`
  pins what that rests on. Rule 14's session-list bullet in
  `.claude/rules/instruction-writing.md` covered only work with no id, because
  it assumed the ref guards cover work that has one. This generator is what
  breaks that assumption, so the bullet now covers recommending an item to start
  as well. That is the reading-side backstop for a session that did not claim.
- **A ref whose session has ended still reads as live** (this item's own
  instance, `PL-X3NY`, `PL-Q664`). Not yet addressed, and it is why the verdict
  stays `live`. `flight` already reads the two pieces of evidence it needs and
  throws most of it away:
  - the commit timestamp: `COMMIT_FORMAT` carries it in full (`%cI`), but
    `_since` prints the day. So "last commit today" cannot separate three
    minutes from twenty hours, and across midnight a fresh branch reads as a
    day old (`PL-3QM9`).
  - the open-pull-request lookup `PL-Q664` added (`open_pull_requests_command`),
    which `flight` asks only about settled candidates.

  **Next:** carry the timestamp through `Branch.last_commit` and `_since` to
  the minute, and print each live row's pull-request state wherever the forge
  answered. That meets this item's **Done when.** and `PL-3QM9`'s together.
  Then decide `PL-X3NY` on the same lookup: its brief predates `PL-Q664`, which
  made route 1's "new network dependency" an existing one. Set the verdict to
  `spent` only once a ref whose session has ended can no longer read as someone
  working on it.
- `PL-N2PP` and `PL-HX5C` meet their **Done when.** through the start rule
  above, and close out next session. `PL-99YZ` (fresh ids for one subject) is
  out of reach of any claim keyed on an id, and keeps its own count-first brief.

**Second half, 2026-09-22.** Landed on `claude/clever-thompson-1sdll0`,
leaving the verdict to decide.

- Ages are elapsed time to the minute (`PL-3QM9`, closed with it). The full
  `%cI` timestamp now reaches `Branch.last_commit` and `render._since`.
- Every live `flight` row says whether a pull request is open on its branch,
  and which: `pull request #757 open`, `no pull request open`, or no clause at
  all where the forge could not be asked. `vcs.open_pull_requests` does the
  matching and shares one request with `settled_branches`, and
  `tools/open_pull_requests.py` now prints the number after the branch name.
  It costs +0.50 s a run (1.15 s median against 0.65 s with `--no-remote`,
  measured 2026-09-22).
- "Do not start these again" is gone, from the digest and from `show`. The
  digest line gives each in-flight item's age and says a branch outlives its
  session. `show` says the branch already carries the item's work, so starting
  it elsewhere redoes it, which is true of a live session, a pull request and
  an abandoned branch alike. `flight`'s closing lines say what an age and a
  pull request can and cannot establish, and no longer tell the reader what to
  conclude from an age. That meets the **Done when.** above, and
  `test_a_branch_minutes_old_carries_its_pull_request_rather_than_a_verdict`
  drives a branch 7 minutes old.

**The verdict, against the owner's test: "spent only if a ref whose session
has ended can no longer read as someone working it."** Shape by shape:

- **The session ended with a pull request open** (this item's own `#757`).
  The row reads `pull request #757 open`, and the work waits on review. Met.
- **It ended with every claimed item closed and no pull request** (`PL-Q664`).
  The row moves to the settled section, which says nothing there is being
  worked. Met.
- **It ended mid-work days ago.** The digest and `flight` show the age, such
  as "3 days", where the line used to be an undated order. Met.
- **It ended mid-work before opening a pull request, under about an hour
  ago.** The row reads as a young branch with none open, and `flight` itself
  says that is usually a live session and that an ended one reads the same.
  **Not met.** Nothing a checkout can read separates the two: only the
  harness's session list can, and `PL-SK88` keeps `docket` from reading it.
  The session-list read in rule 14 and in `start.md` is the backstop at the
  point where the difference matters, which is starting or recommending an
  item.

So the verdict stays `live`, and the item stays open for one decision.

**Decision needed.** Should that last shape count as the generator's
documented limit, making it `spent` and closing this item? Or should the
generator stay live until something can read session state?

**Recommended: accept it as spent.** The shape is bounded in time: within
about an hour the age exposes it. It is also bounded in direction: it withholds
an item and never puts two sessions on one. A new finding about it would repeat
a limit `flight` now prints about itself, not report a new defect. The only way
to close it is a session-state read. That would be a new mechanism that no
script can build today, because the session list is reachable only by the
model. While the verdict stays `live`, `CLAUDE.md` keeps every new workflow
mechanism paused on this one shape. If the answer is yes, the change is
`bin/docket set PL-7TVT --generator "spent - ..."` plus closing this item, one
commit.

**Verdict: spent, and closed** (project owner, 2026-09-23, ratified, over
keeping the generator live until something can read session state). The
remaining shape is recorded as this generator's documented limit rather than as
a mechanism still producing members. That shape is a session that ends mid-work
before opening a pull request: for about its first hour, its branch reads as
young with none open. `flight` states that limit in its own closing lines. The
age exposes the shape within the hour. It only ever withholds an item. The
session-list read in `.claude/skills/docket/modes/start.md` and rule 14 is the
reading that separates it at the moment it matters. The **Done when.** was met
by `#924`, and the `verify:` above drives the 7-minute-old branch that
demonstrates it. **Reopen this on ordinary evidence:** a new finding in which an
ended session's branch misled a reader in some way `flight` does not already
say, or a way to read session state that stays outside `docket` per `PL-SK88`.
