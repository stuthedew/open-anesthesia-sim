---
id: PL-9DYK
title: This project configures two repositories, so its threads start above the checkout and load none of .claude/settings.json: no SessionStart digest, no guard hook, no permission rule and no env line applies to a Projects thread
priority: P2
effort: S
status: ready
classes: infra
feature: projects-trial
touches: docs/items/PL-NZC0-a-claude-code-projects-trial-needs-project.md
added: 2026-09-27
payoff: confirms Projects threads run with the repository's hooks, permission rules and env again, or reopens the question
not-delegable: only a thread started in the Project after the 2026-09-27 removal can observe its own shell and SessionStart digest; no command run in another session can
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

**The documentation states it outright** (read 2026-09-27,
https://code.claude.com/docs/en/claude-projects, § "What threads pick up from
your repositories"): "Permission rules, hooks, and env come only from the
.claude/settings.json in the directory the thread starts in: inside the
repository when the project has one, and above the clones when it has several,
where no repository's file is read for them." Its advice for a project with
several is to "put standing rules in project instructions and give threads
environment variables through the cloud environment", which carries the `env`
lines and the rules but no hook. The repositories new threads clone are set in
Project settings > Environment > Project repositories, and a change there
"reach[es] new threads, not threads already running". Still unknown: whether
the second repository was added after `PL-NZC0`'s plan was written.

**Decision needed: keep the references repository in the project, or take it
out so threads load `.claude/settings.json` again.**

- **Take it out.** New threads start inside `open-anesthesia-sim`, so its
  hooks, permission rules and `env` apply. A thread whose task reads a source
  then has to add `open-anesthesia-sim-references` to itself, which the
  documentation allows mid-task. This project's instructions say "Do not
  create routines, add repositories, or start threads for anything I have not
  picked", and the coordinator's briefs have read that as no repository at
  all, so the line would need an exception naming this one repository.
- **Keep it.** Every thread keeps the corpus from its first turn, and runs with
  no hook at all; the `env` lines move to the cloud environment and the guards
  that matter are restated as project instructions, which a session has to
  remember rather than meet.

**Recommended: take it out, with that one exception.** The hooks are the
deterministic layer `CLAUDE.md` prefers over rules a session has to remember,
and the corpus is read now and then rather than by every thread: no
`claude/project-thread-*` branch in `open-anesthesia-sim-references` differed
from its `main` on 2026-09-27, so no thread had written to it. That count
cannot see reads, which is where it could be wrong: if most of this project's
threads open a source at start, keeping it is the better trade. Which guards
the trial needs stays the owner's call, alongside `PL-NZC0`.

## Answered 2026-09-27

**Taken out** (project owner, 2026-09-27, ratified, over keeping the
references repository in the project). The project owner removed
`open-anesthesia-sim-references` from the project's repositories at about
19:00Z. By the documentation quoted above, threads started after that begin
inside `open-anesthesia-sim` and read its `.claude/settings.json`, so its
hooks, permission rules and `env` block apply again. Threads already running
keep the layout they started with, which is why this one cannot confirm it.
The coordinator added the one exception to the project instructions: a thread
whose work needs the references library may add it to its own session.

**Still to confirm before closing:** the first thread started after the
removal checks that `CLAUDE_PROJECT_DIR` is set in its shell and that the
SessionStart digest printed, then closes this item.

**Done when.** The first thread started in the Project after the 2026-09-27
removal records here whether `CLAUDE_PROJECT_DIR` was set in its shell and
whether the SessionStart digest printed, then closes this item; if either
failed, the decision above is reopened.

**Generator check.** An external behaviour nothing models (which
`.claude/settings.json` a Projects thread reads), met once because the Project's
repository set changed after `PL-NZC0`'s plan; a one-off.
