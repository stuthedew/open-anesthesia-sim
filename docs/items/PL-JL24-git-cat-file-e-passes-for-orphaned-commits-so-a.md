---
id: PL-JL24
title: `git cat-file -e` passes for orphaned commits, so a hash check that uses it can pass on a dangling hash
status: untriaged
added: 2026-08-25
---

**Problem.** `git cat-file -e <hash>` returns success for any object still in
the local object database, including a commit that nothing references — one
orphaned by an amend or a reset, reachable only through the reflog. A check
that uses it to confirm a recorded `commit:` hash therefore passes locally on
a hash that a fresh clone would not have.

**Why it matters.** PL-68XK exists to hold every recorded commit hash to
resolving. If it is implemented with `cat-file -e`, it will report green on
exactly the hashes it was written to catch, which is worse than no check: the
provenance chain from an item to the commit that closed it is the thing a
later reviewer relies on to find out why a change exists.

This is not hypothetical. Closing PL-G3TG produced one: the hash was recorded,
then the commit was amended to include the recording, orphaning the hash that
had just been written. `cat-file -e` passed on it.

**Where.** Whatever PL-68XK builds. `git merge-base --is-ancestor <hash> HEAD`,
or `git rev-list --all | grep`, answers reachability rather than mere presence.

**Note on the underlying trap.** Recording a hash by amending cannot converge —
amending to write the hash changes the hash. The item's `commit:` has to be
written in a follow-up commit, or name the merge commit instead.

**Done when.** PL-68XK's check tests reachability rather than object presence,
with a regression test covering an orphaned commit.
