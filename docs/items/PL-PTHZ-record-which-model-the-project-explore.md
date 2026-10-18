---
id: PL-PTHZ
title: Record which model the project Explore definition at .claude/agents/Explore.md runs on in a cloud session, read from the Explore subagent transcript of the first session started after PL-2D28 merged, the probe PL-2D28's Done-when named and could not run before the merge
priority: P3
effort: S
status: done
classes: docs
feature: model-evidence
milestone: v0.5.26
touches: docs/maintainer.md, docs/items
added: 2026-10-17
closed: 2026-10-17
pr: 1514
payoff: docs/maintainer.md says from a measurement, not only from the documentation, that a cloud session loads the project Explore definition and which model it runs on
verify: grep -qE '^\*\*Explore model measured [0-9]{4}-[0-9]{2}-[0-9]{2}' docs/items/PL-PTHZ-*.md && grep -qF '(measured 2026-10-17, `PL-PTHZ`)' docs/maintainer.md
---

**Problem.** Record which model the project Explore definition at .claude/agents/Explore.md runs on in a cloud session, read from the Explore subagent transcript of the first session started after PL-2D28 merged, the probe PL-2D28's Done-when named and could not run before the merge

**Why it matters.** `PL-2D28` (project owner, 2026-10-17, ratified) built the project
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

**Generator check.** Not a member of a head. The fact is whether a cloud
session loads `.claude/agents/` and which model a subagent then runs on. That
is external behaviour that nothing in the tree models. This item is the probe
`PL-2D28` deferred to after its merge, not a reader that misread the fact.

**Explore model measured 2026-10-17.** The session was
`session_01BZ2oaQaoV2QwVrq1zC35DP`, an ordinary cloud session
(`origin: desktop_app`, `environment_kind: anthropic_cloud`) on Claude Code
2.1.302. It was created at 20:47:24 UTC. `PL-2D28`'s pull request `#1510` had
merged as `441a9e78` at 20:42:13 UTC, five minutes earlier. So
`.claude/agents/` was in the checkout when the session started, and the file
watcher's restart case did not arise. The session's own model was
`claude-opus-5-5` in all three model fields `get_session` reports, at effort
`xhigh`.

One Explore subagent ran a quick search, as agent `a8f6f6c1e1a69814b`,
started at 20:48:57 UTC. Its transcript is
`subagents/agent-a8f6f6c1e1a69814b.jsonl` in the session's folder under
`~/.claude/projects/`, and the `.meta.json` beside it records
`"agentType":"Explore"`. Both assistant entries record `claude-opus-5-5`, read
with `jq -r 'select(.type=="assistant") | .message.model'`. The same entries
record `claude-opus-5-5` as `requestedModel` and `xhigh` as `effort`.

**The model id cannot say whether the definition loaded, so other evidence
decides it.** In an Opus session the built-in Explore and the `opus` alias
both run on the session's own model. In a Fable session on a Claude
subscription both run on the Opus model the alias points to. So the test this
brief expected, a Fable model id in a Fable session, could not have fired in
either case (subagents page, § "Built-in subagents" and § "Choose a model",
https://code.claude.com/docs/en/sub-agents.md, read with curl 2026-10-17).
Four readings show that the project definition loaded:

- The transcript's `prompt_snapshot` attachment records a system prompt that
  opens "You search this repository and report what you find". That is the
  first line of the definition's body.
- The Agent tool listed Explore with the definition's description and with
  "Tools: Read, Grep, Glob".
- The report ended with the `Searched:` and `Not searched:` lines that the
  definition requires.
- No line of `CLAUDE.md` appears in the transcript, as `omitClaudeMd: true`
  asks. The built-in Explore also skips `CLAUDE.md`, so this reading alone
  does not tell the two apart.

The subagent ran at the session's effort level, as expected for a definition
with no `effort` line. No Fable session was measured, and none is owed. The
prompt snapshot answers the load question whatever the session's model, and
the documented model is the same for the definition and the built-in in both
kinds of session. One quick search says nothing about whether the narrow tool
set loses recall. That is `PL-G2D4`'s measurement.

`docs/maintainer.md` § "Settings that make sessions cheaper" still agreed with
the subagents page. Its sentence pointing at this item now states the result.
