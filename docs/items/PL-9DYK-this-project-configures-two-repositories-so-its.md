---
id: PL-9DYK
title: This project configures two repositories, so its threads start above the checkout and load none of .claude/settings.json: no SessionStart digest, no guard hook, no permission rule and no env line applies to a Projects thread
status: untriaged
feature: projects-trial
touches: docs/items/PL-NZC0-a-claude-code-projects-trial-needs-project.md
added: 2026-09-27
---

**Problem.** This project configures two repositories, so its threads start above the checkout and load none of .claude/settings.json: no SessionStart digest, no guard hook, no permission rule and no env line applies to a Projects thread

**Measured 2026-09-27, in the "Dev tooling build chain" thread of the "Ship
v0.6.0" project, while working `PL-0MLZ`.** The thread's working directory is
`/home/user`, which is not a git repository; both configured repositories are
checked out below it (`open-anesthesia-sim` and
`open-anesthesia-sim-references`). `CLAUDE.md` still arrives, through
`CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD`, but `.claude/settings.json`
does not: its `env` block sets `CLAUDE_CODE_SUBAGENT_MODEL`, which is unset in
the thread's shell, and `CLAUDE_PROJECT_DIR`, which every hook command in that
file is written against, is unset too.

**Why it matters.** `PL-NZC0` planned the trial on "Hooks and permission rules
load only in a single-repository project: the project has one", citing
https://code.claude.com/docs/en/claude-projects. The project now has two, so
every thread runs without the SessionStart digest and stop-hook patch, the
`docket-branch-guard`, `no-prune-guard`, `floor-interpreter-guard` and
`gate-status-guard` hooks, the permission allow-list and the `env` block -
silently, since nothing a thread reads says a guard is missing. `PL-0MLZ` met
it as a carrier ruled out: a `PYTHONDONTWRITEBYTECODE` line in the `env` block
would have reached no thread.

**Not yet established.** Whether the second repository was added after the
trial's instructions were written, and whether removing it (Project settings >
Repositories) restores the settings file for new threads. Which of the guards
the trial actually needs is the owner's call, alongside `PL-NZC0`.
