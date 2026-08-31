---
id: PL-KKX4
title: A fresh web session started with no repository checked out at all
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
added: 2026-08-31
not-delegable: the cause is outside this repository and no command here can reach it; the only action this queue can carry is to add a dated observation when it recurs, and the disposition - drop as a one-off, or escalate to the harness - is decidable only on a second sighting
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
