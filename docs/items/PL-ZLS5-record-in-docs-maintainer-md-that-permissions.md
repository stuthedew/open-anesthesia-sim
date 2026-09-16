---
id: PL-ZLS5
title: Record in docs/maintainer.md that permissions.defaultMode auto is user/managed scope only and a cloud session takes its mode from the dropdown, so no repo-side setting can carry it
status: untriaged
added: 2026-09-16
---

**Problem.** Record in docs/maintainer.md that permissions.defaultMode auto is user/managed scope only and a cloud session takes its mode from the dropdown, so no repo-side setting can carry it

**Problem.** The project owner set `"permissions": {"defaultMode": "auto"}` in
`~/.claude/settings.json` on 2026-09-16 to make auto mode the default across all
projects. That is the correct file, and it is the only one that works - but its
reach is narrower than "all projects" suggests, and nothing in the repository
records the limits, so a later session is free to recommend the two routes that
cannot work.

Verified against the documentation on 2026-09-16:

- **Project scope cannot carry it.** From
  https://code.claude.com/docs/en/settings: "`permissions.defaultMode` values
  `auto` and `bypassPermissions` don't take effect from project or local
  settings; set them in user or managed settings instead, or pass
  `--permission-mode` for one session." So adding it to this repository's
  `.claude/settings.json` would be silently ignored - no error, no effect.
- **A cloud session does not read it.** From
  https://code.claude.com/docs/en/claude-code-on-the-web: "You pick a cloud
  session's permission mode from the mode dropdown, both when you create the
  task and while the session runs." A cloud container's home directory is
  fresh per session - `~/.claude/settings.json` was confirmed absent in the
  container that filed this item - so the user-scope default reaches local
  sessions only.

**Why it matters here.** `PL-W4H9` already established that `.claude/` is a
protected directory, which is what makes a session's permission mode a live
question in this project rather than a preference. Recording the scope rule
next to it stops a future session proposing the repo-settings route and
stops the owner wondering why a cloud session prompted when their default
says it should not.

**Done when** `docs/maintainer.md` carries the two quotes above with their URLs
and read date, under the settings the owner controls.
