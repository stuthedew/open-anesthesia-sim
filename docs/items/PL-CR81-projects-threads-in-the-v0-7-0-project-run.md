---
id: PL-CR81
title: Projects threads in the v0.7.0 project run without this repository's hooks: no session-start digest and no guard hook fired in one thread on 2026-10-25, although it started inside the checkout with one repository
priority: P1
effort: S
status: blocked
classes: infra
feature: projects-trial
touches: docs/items/PL-CR81-projects-threads-in-the-v0-7-0-project-run.md, docs/items/PL-8Z38-report-to-anthropic-that-projects-threads-on.md, docs/items/PL-876V-until-projects-threads-load-claude-again-pl.md
blocked-by: PL-8Z38
added: 2026-10-25
payoff: every thread in the project runs with the repository's guard hooks and session-start digest again, or the project knows it does not and why
verify: grep -qE '^\*\*Probe refused in a thread\.' docs/items/PL-CR81-*.md
recurrences: 2026-10-25 PL-876V withdrawn 2026-10-25 PL-PNSV
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

**Cause.** Found on 2026-10-25, about 21:00Z, and not fixed. No change in this
repository can fix it. The work was done from an ordinary session outside the
project (`session_01WW87TkT7FA8qoh7zvupQL3`), which read the threads'
`init` records through `list_events`. A Projects thread no longer reads the
repository's `.claude/` directory at all, so the missing hooks are one symptom
of a wider loss. Three comparisons narrowed it:

- **Today's thread reads nothing from `.claude/`.** Its four `init` records
  from 18:42Z to 18:46Z report `cwd: /home/user/open-anesthesia-sim`. They list
  none of the repository's four skills: `docket`, `pull-request`,
  `run-the-app` and `model-review`. No `PreToolUse` hook fired in that window.
  That includes `owner_ask_guard.py`, which `.claude/settings.json` binds to
  `mcp__hearthbot__post_message`, and the thread called that tool three times.
  The hooks that did fire are the harness's own: `UserPromptSubmit`, `Stop`,
  and `PostToolUse` on hearthbot tools and on Edit. The repository declares no
  `PostToolUse` hook on Edit.
- **The tags and the repository list do not separate the two cases.** The
  2026-09-27 thread that `PL-9DYK` confirmed against
  (`session_01N7QD5ZmCCj9PX3dUwRPNQ8`) carries the same `hearth-thread`,
  `config:hearth-thread-own-tools` and `config:static-sysprompt` tags. It has
  the same origin, one repository and the same working directory. Its `init`
  lists `docket`, and each Bash call fired three `PreToolUse:Bash` hooks. That
  thread ran Claude Code 2.1.283. Today's thread runs 2.1.310.
- **Preloading alone does not cause it.** The ordinary session also runs
  2.1.310, and its process was started the same way: `/proc` shows `claude
  --preload /home/claude/.claude/remote/spare.sock`, with
  `CCR_PRELOAD_CLAUDE=1`. Its entrypoint is `remote_desktop`, not
  `remote_projects`. It lists all four skills, its `SessionStart` hooks printed
  the digest, and each Bash call fires the repository's `PreToolUse:Bash`
  hooks.

What is left is the `remote_projects` entrypoint together with a change in the
CLI between 2.1.283 and 2.1.310. Today's thread recorded
`startup_timing.hooks_init_source: "resume"` at its latest worker spawn. That
suggests, but does not confirm, that a restarted thread worker restores a set of
hooks and skills captured without the project's settings. The earlier
suggestion, that a preloaded process reads its settings before the checkout is
attached, is not confirmed either. The ordinary session's preloaded process
read them. The thread's earliest `init`, from its first worker at 01:44Z, was
not read. It would show whether the thread lost `.claude/` on a restart or never
had it, but reaching it means paging back through thousands of events.

**What this means until it is fixed.** A thread in this project runs with no
guard hook, no session-start digest and no permission rule from
`.claude/settings.json`. It also cannot load the `docket`, `pull-request`,
`run-the-app` or `model-review` skills through the Skill tool, so it has to read
their files by path. The fix belongs to Anthropic. This item stays blocked until
the owner reports the defect and a thread started after a fix runs the probe
above and records here that it was refused, in a paragraph that opens
`**Probe refused in a thread.**`, which the `verify:` command reads.

**Narrowed 2026-10-26, about 00:15Z, in the "Fix recurring and P1 items" thread** (Claude Code 2.1.310, `CLAUDE_CODE_ENTRYPOINT=remote_projects`). The CLI's diagnostics log (`CLAUDE_CODE_DIAGNOSTICS_FILE`) records `settings_load_completed` with `source_count: 2` at start, when the checkout and its `.claude/settings.json` were already on disk. The project's `CLAUDE.md` and rules were loaded (`claudemd_length: 82813`). A `PreToolUse` hook written into `~/.claude/settings.json` mid-session fired on the next Bash call, with `CLAUDE_PROJECT_DIR` set to the checkout. The same hook written into `.claude/settings.local.json`, and a touch of `.claude/settings.json`, caused a reload that again read two sources, and neither fired. So the CLI reads user and launcher settings and skips the project and local ones. Copying the repository's `hooks` block into `~/.claude/settings.json` made the repository's hooks fire, and `gate-status-guard.sh` refused the probe. That is a working stop-gap for one session, and a setup-script line that writes the same file is a candidate for every thread. Whether a file the setup script writes survives the thread's start was not tested. Neither was whether skills copied into `~/.claude/skills` would load, since the skills sync manages that directory.
