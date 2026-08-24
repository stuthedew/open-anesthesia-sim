---
id: PL-64LS
title: Detect inbox notes stranded on an unmerged branch
status: untriaged
touches: .claude/hooks/punch-list-digest.sh, tools/punch_list.py
added: 2026-08-24
---

`P3` · `S` · `session-cost`

**Problem.** An inbox note is committed on whatever branch the capturing
session was on. If that branch is never merged, the note exists only there:
`tools/punch_list.py` reads `docs/inbox/` in the current checkout, so no
other session's digest or `make punch-list` will ever mention it, and the
thought is lost as silently as if it had stayed in the conversation.
**Why it matters.** The inbox exists to make capture unloseable. A hole that
only opens on abandoned branches is exactly the hole nobody notices, because
the sessions that could notice are the ones that cannot see the note.
**Where.** `tools/punch_list.py` (`read_inbox`),
`.claude/hooks/punch-list-digest.sh`.
**First step.** Decide whether detection belongs in the tool or in CI. A CI
job on `main` can run `git log --all --diff-filter=A --name-only` for
`docs/inbox/` paths absent from both the working tree and `main`'s history,
which the standard-library-only local tool cannot do cheaply without
shelling out to git on every session start.
**Done when.** A note committed on a branch that is closed without merging
is reported somewhere a later session will see it, or the limitation is
documented in `docs/inbox/README.md` as accepted, with the reason.
**Context.** Raised while building the inbox itself. The mitigation already
in place is that a note is committed alone, so recovering one is a single
`git cherry-pick`. Captured as a note rather than an entry because the
session that found it was concurrent with another that allocated PL-042 and
PL-043 — the collision this channel exists to prevent.
