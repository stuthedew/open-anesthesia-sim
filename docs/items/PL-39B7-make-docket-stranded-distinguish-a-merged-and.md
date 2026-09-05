---
id: PL-39B7
title: Make docket stranded distinguish a merged-and-deleted branch from an abandoned one, and say when its main is stale
priority: P2
effort: S
status: untriaged
added: 2026-09-05
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py
---

**Problem.** `bin/docket stranded` answers "which items exist only on a branch"
by comparing branch refs against **this checkout's** `origin/main`, and reports
the answer as "the hole is a branch nobody will merge". Both halves can be
wrong at once, and they were on 2026-09-05:

- **The comparison point goes stale silently.** This checkout fetched
  `origin/main` at 01:05. `claude/next-workflow-item-c2b07p` merged as #325 at
  01:13:48, landing `PL-XLQ5`. At 01:16 `stranded` still reported `PL-XLQ5` as
  existing only on that branch, because the ref it compares against was eight
  minutes old. The session-start digest prints the same line, so every session
  inherits the same staleness.
- **A deleted remote branch is not evidence of abandonment.** Confirming the
  branch was gone from the remote — `git ls-remote origin 'refs/heads/claude/*'`
  did not list it — reads as corroboration and is not: a merge deletes the
  branch too. The two histories are indistinguishable from the ref's absence
  alone, and only one is a hole.

**What it cost.** The recovery command `stranded` prints was run and restored
the **pre-triage** copy of `PL-XLQ5` — `status: untriaged`, no `priority`,
`effort`, `classes`, `feature`, `touches` or `verify` — over the triaged one
#325 had just landed. Committed, it would have reverted that item's triage
silently, on a branch whose stated purpose was to protect it. `PL-KBFN` is the
item that made the mistake and carries the timeline.

That is the failure mode `CLAUDE.md` calls a check giving a wrong answer
silently: the guarantee `stranded` stands for is "nothing captured is about to
be lost", and here it reported loss where there was none and handed over a
command that destroyed newer work.

**Fix.** Three parts, cheapest first, and the first alone removes most of it.

1. **Fetch the default branch before comparing, or say the comparison point is
   old.** `fetch_remote` already exists and already declines to prune, so the
   safe fetch is available; where it cannot run, print the age of the
   `origin/main` ref alongside the finding so a reader knows what the answer
   rests on.
2. **Check the item against the freshly fetched default branch, not only
   against the branch refs.** An item present on `main` is not stranded however
   many dead branches also carry it, which is one `git cat-file -e` per
   candidate.
3. **Stop reporting a live unmerged branch as having "already taken the rest of
   its work".** The second section of the report treats "some of this branch's
   files are on `main`" as evidence that the branch partly merged; it is also
   what an independent branch landing the same files produces, which is exactly
   what happened here. Distinguish the two by whether the branch's own commits
   are ancestors of `main`.

**Done when.** `docket stranded` fetches (or dates) its comparison point,
reports nothing that is already on the default branch, and does not describe an
unmerged branch as partly landed; tests cover a merged-and-deleted branch, an
abandoned one, and a live branch duplicating another's files.

**Sequencing.** Independent. Worth doing before the next session that acts on a
`stranded` line, which is every session — the digest prints it at startup.
