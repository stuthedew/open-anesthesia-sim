---
id: PL-W4H9
title: A session in auto mode cannot edit .claude/settings.json, and the cheap way past that guard is to append to an already-wired hook script, which is exactly what it must not do
priority: P2
effort: S
status: needs-decision
classes: infra, session-cost
feature: worker-instructions
touches: .claude/settings.json, CLAUDE.md
added: 2026-09-04
---

**Problem.** `.claude/settings.json` is where this repository's hooks and
permissions are declared, and a session running in auto mode cannot edit it: the
`permissions.allow` list covers read-only shell commands and the project's own
gates, so any write to that file needs a prompt the mode does not raise. The
hook *scripts* it points at - `.claude/hooks/docket-digest.sh`,
`.claude/hooks/docket-branch-guard.sh`, `tools/stop_hook_patch.py` - are
ordinary files under no such guard. So the cheap way to change what a hook does
is to append to a script that is already wired, which changes hook behaviour
without the settings file ever being touched, and that is exactly what the guard
exists to prevent.

**Why it matters.** The guard is on the wrong noun. What it protects is not the
JSON file but the set of commands that run automatically in every session, and
that set is editable through a file nothing guards. A session that wants a new
hook and finds the front door shut has a working side door and no rule telling
it not to use one - which is the failure mode `CLAUDE.md` names for tooling: a
check whose guarantee is void while it goes on looking sound.

**Where.** `.claude/settings.json`'s `permissions` block; `CLAUDE.md` and
`docs/worker.md` for the rule half; `.claude/hooks/` for the scripts that are
the side door.

**Decision needed.** Which of two. *Open the front door*: allow the settings
edit explicitly, so a session that needs a hook changes the declaration where a
reviewer will read it, and the side door stops being the cheap option. *Write
the prohibition down*: state that a wired hook script is not to be extended in
order to avoid a settings change, which costs nothing and depends on a session
reading it. They are not exclusive, and the first is the one that does not
depend on anybody remembering.

**Done when.** A session that needs to change what runs automatically has a
sanctioned route to it, and extending an already-wired hook script to avoid the
settings file is either impossible or written down as prohibited.
