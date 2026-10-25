---
id: PL-CR81
title: Projects threads in the v0.7.0 project run without this repository's hooks: no session-start digest and no guard hook fired in one thread on 2026-10-25, although it started inside the checkout with one repository
priority: P1
effort: S
status: ready
classes: infra
feature: projects-trial
touches: docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md
added: 2026-10-25
payoff: every thread in the project runs with the repository's guard hooks and session-start digest again, or the project knows it does not and why
verify: grep -qE '^\*\*Cause\.' docs/items/PL-CR81-*.md
---

**Problem.** Projects threads in the v0.7.0 project run without this repository's hooks: no session-start digest and no guard hook fired in one thread on 2026-10-25, although it started inside the checkout with one repository

**Measured 2026-10-25, about 03:50Z, in the "Complete workflow and CI items"
thread** (session `session_012rVrL9K8fsj5GubrbC9cuH`). The thread's working
directory is `/home/user/open-anesthesia-sim`, the only checkout under
`/home/user`, and its GitHub scope names one repository.

- **Two guards did not refuse what they refuse.** `bin/docket check | tail -1`
  ran, and so did `git fetch --prune --dry-run origin` (a dry run, so nothing
  was deleted). Fed the same command on standard input, by hand,
  `.claude/hooks/gate-status-guard.sh` and `.claude/hooks/no-prune-guard.sh`
  each return `"permissionDecision": "deny"`.
- **The transcript records none of the repository's hooks.** Its JSONL under
  `~/.claude/projects/` holds hook entries only for `UserPromptSubmit`, `Stop`
  and `PostToolUse`, which are the harness's own four hooks in
  `~/.claude/launcher-settings.json`. It holds no `SessionStart` entry, so the
  digest never printed, and no `PreToolUse` entry.
- **This contradicts `PL-9DYK`'s confirmation of 2026-10-01**, which found a
  thread started inside the checkout running the digest and three
  `PreToolUse:Bash` hooks. That was in the earlier "Ship v0.6.0" project.

**Re-probed 2026-10-25, about 04:25Z, in the same thread after it was compacted
and its worker restarted.** The probe still printed the pytest version. A
marker line added by hand to `gate-status-guard.sh` (`PreToolUse` on Bash) and
then to `docket-branch-guard.sh` (`PostToolUse` on Bash) was never written by
the next tool call, so neither event runs the repository's hooks; both edits
were reverted. The thread's Claude process is a preloaded spare, `claude
--preload /home/claude/.claude/remote/spare.sock`, with `CCR_PRELOAD_CLAUDE=1`
and `CLAUDE_CODE_ENTRYPOINT=remote_projects` in its environment, and its
working directory is the checkout. One plausible cause, not confirmed, is that
the spare process resolves its settings before the checkout is attached, so
`.claude/settings.json` is never read. `~/.claude/launcher-settings.json` sets
no `disableAllHooks` or managed-hooks-only key. One `docket-branch-guard.sh`
process was seen running at 04:20Z, and its origin is unknown.

**Re-checked 2026-10-25, about 17:00Z, in the same thread.** The documented
cause is ruled out. `get_session` on this session lists one source,
`https://github.com/stuthedew/open-anesthesia-sim`, so the project gives the
thread one repository. The environment documentation's permissions page says
only that cloud threads apply a repository's `permissions.allow` rules "only in
a project with one repository", and says nothing about hooks. The probe still
printed the pytest version, so the hooks were still not running. The session
records `CLAUDE_CODE_ENTRYPOINT=remote_projects` and the tag
`config:hearth-thread-own-tools`. Reading the Claude process's command line
from `/proc` to see whether it was started with a restricted setting source was
refused by this thread's permission classifier, so that question stays open for
a session that may read it. No change inside the repository can fix this: the
cause is in how the harness starts a Projects thread.

**Why it matters.** Every thread in this project may be working without the
guards: no refusal of a piped gate, of a ref prune or of a bare interpreter on
the 3.14 trees, no push check, and no session-start digest, which carries the
effort trial's arm line (`PL-HYRM`). Nothing a thread reads says a guard is
missing. The environment documentation says a cloud thread applies a
repository's permission rules "only in a project with one repository", so the
first thing to check is whether this project lists a second repository.

**A probe any thread can run.** `uv run pytest --version | head -1`. With the
hooks loaded, `gate-status-guard.sh` refuses it. Without them, it prints the
pytest version.

**Done when.** A `**Cause.**` paragraph here records what was found and whether it was fixed: either the
project's repository list, or a change in how Projects threads load
`.claude/settings.json`. A thread started afterwards then runs the probe above
and records here that it was refused.

**Generator check.** An external behaviour nothing in the repository models,
met once in this project. A one-off unless other threads report the same.
