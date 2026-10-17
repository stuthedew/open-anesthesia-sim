---
id: PL-PTHZ
title: Record which model the project Explore definition at .claude/agents/Explore.md runs on in a cloud session, read from the Explore subagent transcript of the first session started after PL-2D28 merged, the probe PL-2D28's Done-when named and could not run before the merge
status: untriaged
feature: model-evidence
added: 2026-10-17
---

**Problem.** Record which model the project Explore definition at .claude/agents/Explore.md runs on in a cloud session, read from the Explore subagent transcript of the first session started after PL-2D28 merged, the probe PL-2D28's Done-when named and could not run before the merge

**Why.** `PL-2D28` (project owner, 2026-10-17, ratified) built the project
Explore definition with `model: opus`. Its Done-when asked the first session
started after the merge to record the model the definition runs on. That
session cannot run before the merge, and a closed brief is a record rather
than a live assertion (`.claude/rules/citation-drift.md`), so the probe is
this item's. It also measures the one risk the design round could not:
whether a cloud session loads `.claude/agents/` at all. Claude Code's file
watcher covers only an `agents` directory that existed when the session
started, so the first session that can see the file is one started after
the merge.

**How.** In a session started after `PL-2D28` merged, run one Explore
subagent, then read its transcript under `~/.claude/projects/` with
`jq -r 'select(.type=="assistant") | .message.model'`, the way `PL-KLN5`
read it. Expected: `claude-opus-5-5` in an Opus 5.5 session, and the Opus
model the `opus` alias points to in a Fable session. A Fable model id in a
Fable session means the definition did not load. The brief then says which
cause it was: the directory missing from the watcher's set, which a second
session started later rules out, or the hosted harness not reading
`.claude/agents/`. Record the model id, the session's own model and the
date here, and correct `docs/maintainer.md` § "Settings that make sessions
cheaper" if what it says no longer holds.

**Done when.** This brief carries the model id the transcript showed, the
session's own model and the date, and the maintainer guide's sentence is
still true or has been corrected.
