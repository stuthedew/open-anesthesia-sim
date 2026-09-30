---
id: PL-KKX4
title: A fresh web session started with no repository checked out at all
priority: P3
effort: S
status: dropped
classes: infra
feature: dev-tooling
touches: docs/items
added: 2026-08-31
closed: 2026-09-30
reason: Fixed in the environment. All four sightings (2026-08-31 to 2026-09-07) were sessions spawned by another session through create_session with no outcome branch; one spawned the same way on 2026-09-30, container 2.1.286, was cloned by the harness and started in the checkout with CLAUDE.md loaded. The brief's last three paragraphs carry the sessions and the evidence.
not-delegable: the cause is outside this repository and no command here can reach it; the only action this queue can carry is to add a dated observation when it recurs, and the disposition - drop as a one-off, or escalate to the harness - is decidable only on a second sighting
root-cause-of: PL-KX9N, PL-3SGR, PL-483K, PL-2H0K
generator: spent - the harness now clones the sessions another session spawns (reproduced 2026-09-30, container 2.1.286), the one path seen handing a session a depth-1 clone made by hand
misread: What clone a session's checkout is: how much history it holds and which branches it fetches
---

**Problem.** A web session on 2026-08-31 started with no checkout. The
working directory `/home/user` was empty, `git status` reported "not a git
repository", and a search of the filesystem found no clone anywhere -
no `pyproject.toml`, no `bin/docket`, no `CLAUDE.md`. The session had been
given work to do on two named items and had nothing to do it in.

The session recovered by calling the `add_repo` tool for
`stuthedew/open-anesthesia-sim` and cloning by hand into
`/home/user/open-anesthesia-sim`, then `register_repo_root` to load
`CLAUDE.md` and the `docket` skill. That worked, and the work landed. But
the repository had to be *identified* first, which was possible only because
`list_repos` showed one repository pushed to a minute before the container
started; a session with less to go on would have had to ask.

**Why it matters.** A session that starts with no checkout cannot do
anything it was asked to do, and the failure does not announce itself as an
environment problem - it looks like a missing file. Every session this
happens to pays a filesystem search, a guess at which repository is meant,
a clone, and a context reload before any work begins. It also silently
changes what the session is working from: a hand-made clone is shallow and
on the default branch, where a harness-made one is set up for the branch the
session was named after.

**Where.** Outside the repository, like PL-4CW7: the Claude Code environment
and how it attaches sources to a session. Nothing in this checkout can fix
it. Recorded here so the finding is not lost.

**Notes.** Two circumstances may or may not be related, and are recorded
rather than concluded from. First, the same session was the one that
confirmed PL-4CW7's setup-script fix had finally taken - so this container
did run its setup script, and the missing clone is a separate failure from
that one. Second, the harness normally names a session's branch before the
session starts; this one had no such branch, and the branch
`claude/pl-zn0n-pl-69j3-ruf100` was created by hand inside the clone.

**Done when.** Either the cause is known and fixed in the environment, or -
if this proves to be a one-off - the item is dropped with what was learned.
A repeat observation in another session is what would tell the two apart,
so the next session that hits it should add a dated note here rather than
filing a second item.

**Did not recur, 2026-08-31 (observation 1 of the "not a one-off" test).** The
web session that triaged this item started normally: working directory
`/home/user/open-anesthesia-sim`, a git repository, on the harness-named
branch `claude/triage-v0.2.8-items-5phbzm`, with the session-start digest
printed before the first turn. So the failure is not reproducing on every web
session, which is one point against it and nothing like proof. Add the next
observation - working or broken - beneath this one.

**Triaged 2026-08-31.** P3, `infra`, `dev-tooling`, `not-delegable` and no
`verify:` command: nothing in this checkout can prove or disprove it, which
the front matter records. No `touches` either, for the same reason - the only
file this item ever edits is itself.

`ready` rather than `needs-decision` is deliberate. The status is honest about
what a session can do on meeting this - append a dated line - whereas
`needs-decision` would tag it "open design decision" and route it to the
strongest model at high effort, which is a false signal for an item whose
whole content is a wait. It should be dropped, with what was learned, on the
first session that starts cleanly *and* has reason to believe the harness path
changed; or escalated the moment a second session starts with no checkout.

Not admitted to v0.2.8's frozen list: it is outside the tree that release
touches, and `PL-4CW7` (the web container's uv floor) is the precedent for
carrying an environment finding as an ordinary P3 queue item.

**Still not admitted after the 2026-08-31 reassessment, and now for a stated
reason rather than the completion rule.** `ROADMAP.md`'s scope test admits a
defect in machinery the release's goal names *and* workable in this tree; this
one fails the second limit. Its own `not-delegable:` field says the cause is
outside the repository and the only action available here is to record a
second sighting, so admitting it would put an entry on the frozen list that
nothing in the tree can close, holding the gate open indefinitely. That limit
is written into "What the freeze closes" so the case does not have to be
re-argued.

**Dropped 2026-09-30: it recurred three times, and the harness has since fixed
it.** This was not a one-off, and the cause is now known. Every sighting was a
session that another session had started through `create_session`, never one
the project owner started. `get_session` on each shows
`origin: claude_code_mcp_seed`, a `parent_session_id`, and the repository
recorded as a source. None of them has an `outcomes` block, which is where a
harness-named branch appears, so this is the missing branch the Notes above
describe:

| Created (UTC) | Session | Working | Container | Recorded in |
| --- | --- | --- | --- | --- |
| 2026-08-31 | `session_01SnmsWdVQXrmjLK5S7cwJEQ` | `PL-ZN0N`, `PL-69J3` | 2.1.251 | this item |
| 2026-09-06 | `session_01CrynufWsZmGzLuNUfeGa2t` | `PL-GYH2` | 2.1.263 | `PL-KX9N` |
| 2026-09-07 | `session_014rf4LaX2Y9djHMUp1BpPgW` | `PL-GBBZ` | 2.1.263 | `PL-483K` |
| 2026-09-07 | `session_01ESsFLCrxiiVBFtHj6SgGfg` | `PL-GZP6` | 2.1.263 | `PL-3SGR` |

The second sighting this item was waiting for came on 2026-09-06, six days
after it was filed. It was written into another item instead of this one, so
the escalation it called for never happened. The later three recovered with
`add_repo` and a hand clone at `--depth 1`, and that clone cost more than the
recovery did. Because it was shallow and single-branch, it made `bin/docket
record` write four wrong pull request numbers (`PL-KX9N`). It made the stop
hook demand a push of work that was already pushed (`PL-3SGR`, and `PL-483K`'s
second observation - that item's first trigger was a restart). And it put
"the harness clones with `git clone --depth 1`" into the tree (#419, #496),
which `PL-2H0K` is correcting. Hence the `root-cause-of:` above, recorded as
spent.

**Reproduced 2026-09-30, and it no longer fails.** A session was spawned the
same way: `session_01WdkRb9z8M4nz11r99XkHML`, through `create_session` with
`source_url` and no `outcome_branch`, on container 2.1.286. Its provisioning
log ran a clone step, "Fetching repository stuthedew/open-anesthesia-sim", in
seven seconds. It started in `/home/user/open-anesthesia-sim` on the tip of
`main`, with `CLAUDE.md` loaded and the session-start digest shown. Its clone
was the harness's depth-50 one, which the session-start hook then unshallowed
to 1,553 commits. So the environment was fixed at some point between
container 2.1.263 and 2.1.286.

**One difference remains, and it is by design.** A spawned session given no
`outcome_branch` starts on a detached `HEAD` (`## HEAD (no branch)`), so it has
to make its own branch before it commits. `create_session`'s `outcome_branch`
names one. Nothing in the current workflow spawns sessions: `PL-YJG1` weighed a
session starting its own successor and declined it on 2026-09-25. So the
difference is recorded here rather than filed.
