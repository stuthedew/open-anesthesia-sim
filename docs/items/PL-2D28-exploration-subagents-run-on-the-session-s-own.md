---
id: PL-2D28
title: Exploration subagents run on the session's own model, Opus 5.5 in this project's threads, because CLAUDE_CODE_SUBAGENT_MODEL never reaches the built-in Explore subagent and a cloud session applies none of the env block in .claude/settings.json: decide whether a project Explore agent pins a cheaper model, and whether the variable stays (found in PL-KLN5)
status: untriaged
touches: .claude/settings.json, .claude/agents, docs/maintainer.md
added: 2026-10-17
---

**Problem.** Exploration subagents run on the session's own model, Opus 5.5 in this project's threads, because CLAUDE_CODE_SUBAGENT_MODEL never reaches the built-in Explore subagent and a cloud session applies none of the env block in .claude/settings.json: decide whether a project Explore agent pins a cheaper model, and whether the variable stays (found in PL-KLN5)

**What is known.** The subagent documentation says the built-in Explore and
Plan subagents run on the main conversation's model, and that setting
`CLAUDE_CODE_SUBAGENT_MODEL` by itself does not change that. The variable is
only a default for a subagent that nothing else gives a model, such as
`general-purpose` (https://code.claude.com/docs/en/sub-agents, "Choose a
model" and the Explore tab of "Built-in subagents", read 2026-10-17). In a
cloud session the variable does not even do that. `PL-KLN5` started a
`general-purpose` subagent with no model in a Projects thread on 2026-10-17,
and its transcript records `claude-opus-5-5`, the parent's model, on every
assistant entry. So every subagent this project's cloud sessions start runs on
the session's own model. That probe only replied "OK", and it still wrote
86,286 tokens to the prompt cache on that model.

**Routes the documentation gives.** A project subagent named `Explore` in
`.claude/agents/` overrides the built-in one and keeps its own `model` field
(same page, Explore tab). Setting `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` to `1`
forces the variable's model onto every subagent, teammate and workflow agent
(same page, "Run every subagent on one model"). That would also move the
workflow agents this project runs on Opus for hard work. And a cloud session
may apply no `env` value at all, so neither variable is a route there until
that is explained.

**Question for the owner: should exploration run on a cheaper model?** The
case for it is `CLAUDE.md`'s own. Sessions are told to delegate broad search to
exploration subagents, whose transcripts stay out of the main context and
whose results are checked against the source anyway. The case against it is
the quality of the leads they return. `docs/maintainer.md` also records the
owner's preference for Opus whenever there is doubt, though the owner stated
it for delegated items rather than for search.

**Recommendation (this session's, not yet the owner's).** First check that a
project agent file loads in a cloud session at all, with one throwaway probe
agent whose transcript shows its model. If it does, add
`.claude/agents/Explore.md` with `model: sonnet`, read-only tools, and a short
body saying what it is for. Use Sonnet rather than Haiku for the reasons
`docs/maintainer.md` § "Which model each flag means" gives for delegated work,
which `PL-XJV3` may update. Separately, remove `CLAUDE_CODE_SUBAGENT_MODEL`
from `.claude/settings.json`. It does nothing in a cloud session. Two sessions
read its absence from the shell as the file not loading (`PL-9DYK`,
`PL-0MLZ`). And in a local session, once the folder is trusted, it would move
`general-purpose` subagents onto Haiku, though this project uses them for
review passes and fixes.

**Generator check.** Not a member of a head. It follows from `PL-KLN5`'s
measurement of how Claude Code chooses a subagent's model, an external
behaviour nothing in the tree models, and no other open item rests on that
fact.
