---
id: PL-PLSJ
title: doc_check and the scoped verify replay turn pull requests red every day - 64 of 391 red runs, rising from W37 - and a 15-log sample splits them in two: branch text quoting a file that does not exist, which make check refuses locally, so the push went out unchecked; and a store-wide rule tripped by main's state at CI time, not by the branch
status: untriaged
feature: fewer-red-runs
touches: .claude/hooks/push-check-guard.sh, .claude/settings.json, tests/unit/test_push_check_guard.py, docs/items
added: 2026-09-27
---

**Measured 2026-09-27** by `PL-JYJJ`'s census:

| Check | Red runs on pull requests | By week (W37, W38, W39) |
|---|---|---|
| `doc_check` | 32 | 3, 8, 21 |
| scoped verify replay | 32 | 5, 10, 14 |
| `docket check` | 9 | |
| `branch_id_check` | 8 | |

A subagent read the logs of 15 of these failures (job ids are in this
session's census). It found two different mechanisms.

**1. Caught by `make check`, but pushed without it.** All 4 `doc_check`
failures in the sample were the branch's own text:

- an item quoting `start.md` or `capture.md` by bare name, which
  `doc_check` cannot resolve; both live under
  `.claude/skills/docket/modes/`;
- an item quoting `CLAUDE.md` for words that file does not contain;
- `ROADMAP.md` citing a path that does not exist.

The one `branch_id` failure was also local: a branch that had claimed no item.
`make check` runs both checks, so each of these went out without it. Three of
the four were item files, which is the capture path, and capture is kept cheap
on purpose.

**2. Red because of `main`, not because of the branch.** All 4 scoped-verify
failures said "PL-X is open but its `verify:` command already passes". In two
of them PL-X was not the branch's own item, so the work had landed on `main`
through another branch. One `docket check` failure read an item "marked done
on `origin/main`" that records no `pr`. `pull_request` runs check the merge
with the current `main`, so these fail on state the branch did not create.

**Options.**

- For mechanism 1, a push guard: `.claude/hooks/` already guards Bash
  commands. It would run `doc_check` and `branch_id_check`, the two checks
  that account for the sampled cases and are fast, before any `git push`.
  Measure their time first. This costs seconds per push, where a red run
  costs a whole fix cycle.
- For mechanism 2, the question is whose failure it is. The check correctly
  reports that the store is inconsistent, but it reports it to a branch that
  can neither cause nor fix it. `PL-85NT` (repository-level breakage visible
  to every session, claimed by none) was dropped on 2026-09-16, and this data
  bears on reopening it.

**Recommendation.** Build the push guard for mechanism 1, since the fix and
the failure sit in the same session. Put mechanism 2 back to the project owner
as a reopening of `PL-85NT`, with these counts.

**Approved 2026-09-27: build the push guard** (project owner, 2026-09-27,
ratified, over leaving `make check` before a push to each session's memory). The
request lifts the generator pause for this build (`PL-6Q9L`). The session that
designed it ran out of budget before starting, so the design is here:

- **Cost, measured.** `doc_check` takes 10.5 s bare (9.4 s under `uv run`) and
  `branch_id_check` 0.9 s. Run in parallel, a push waits about 11 s, and a pass
  costs no tokens.
- **Where.** A new PreToolUse hook on Bash, push-check-guard.sh, beside the
  three Bash guards, reading the command through `shell_split.commands` as they
  do. The earlier `touches` named `docket-branch-guard.sh`, which guards Edit
  and Write, so it was wrong.
- **What counts as a push.** A git call whose command name, after git's own
  options (`own_options` in `no-prune-guard.sh`), is `push`. Skipped:
  `--delete`, `-d`, a `:branch` refspec, `--dry-run`, `-n` and `--no-verify`.
- **Which tree.** The push's repository: `git -C` if given, otherwise the
  payload's `cwd`. It checks only where `git rev-parse --git-common-dir` matches
  the project's, so a worktree counts and another repository does not. Like
  `make check`, it reads the working tree.
- **Refusal.** On exit 1 it denies with the check's output, capped, saying how
  many lines it cut. A traceback, a timeout or a missing python3 fails open, as
  the sibling guards do.
- **Bypass.** A work-in-progress push to a branch with no pull request open
  runs no CI, and `CLAUDE.md` asks sessions to push as they go. The refusal
  therefore offers `git push --no-verify` for that case only.
- **Known gap.** In `git commit ... && git push`, the hook runs before the
  commit, so `branch_id_check` reads the history without it. `doc_check` reads
  the working tree and is unaffected.
- **Tests.** test_push_check_guard.py under `tests/unit/`, modelled on
  `tests/unit/test_no_prune_guard.py`. It uses a temporary repository with stub
  `tools/` scripts and `CLAUDE_PROJECT_DIR` pointed at it. Cases:
  - a refusal naming the check;
  - a pass;
  - non-pushes: `git commit -m "... git push ..."`, a heredoc, a delete, `--no-verify`;
  - another repository;
  - a crashing check.
- **Wiring and sweep.** Add the hook to `.claude/settings.json` with
  `"timeout": 120`. Update the files that list the sibling guards:
  `docs/ARCHITECTURE.md`, `docs/worker.md`, `docs/resident-instructions.md`,
  `ROADMAP.md`, `.claude/skills/docket/modes/capture.md`. Check the mention in
  `src/anesthesia_sim/app_metadata.py`, and whether `bin/docket arm` holds a
  pull request that changes a hook (#1198).

**Mechanism 2, checked before `PL-85NT` is reopened.** The owner approved
reopening it with these counts (2026-09-27, ratified). But "the work had landed
on `main`" above was inferred, not checked. `main`'s own whole-store replay has
been green since 2026-09-23, which suggests the branch did another item's work,
not `main`. The census's 43 store-rule red runs are 32 scoped-verify and
11 `docket check`. Sort each by three questions:

- whether the offending item was the branch's own;
- whether the branch's diff reached that item's `touches`;
- whether `main` already held its work at run time.

Reopen `PL-85NT` for the share that belongs to `main`, and fold the rest into
mechanism 1.
