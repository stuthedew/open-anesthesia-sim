---
id: PL-TQ4J
title: Close-out step 8 tells a session to start the copy-editor agent, but a Projects thread cannot: threads do not load .claude/agents/, so the Agent tool answers "Agent type 'copy-editor' not found" (PL-J37P, 2026-11-04), and the thread falls back to a general-purpose agent given the agent file's text, which loads the resident instructions that the agent's omitClaudeMd exists to leave out
priority: P2
effort: S
status: done
classes: defect
feature: reader-first-prose
touches: tools/copy_edit.py, tests/unit/test_copy_edit.py, docket.toml, .claude/skills/docket/modes/close-out.md, .claude/skills/pull-request/SKILL.md, .claude/rules/instruction-writing.md, docs/prose-review/README.md, docs/apparatus.md, tools/new_prose.py, tools/rejected_prose.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science; fixed on its own branch the day it was filed
added: 2026-11-04
closed: 2026-11-04
pr: 2026
payoff: a Projects thread runs the copy editor with only its own instructions, as a terminal session does, so each copy edit starts small and judges the text by the writing rule alone
verify: uv run pytest -q tests/unit/test_copy_edit.py
---

**Problem.** Close-out step 8 tells a session to start the `copy-editor` agent, but a Projects thread cannot start it. A thread does not load `.claude/agents/`, so the Agent tool returns "Agent type 'copy-editor' not found" (on `PL-J37P`'s branch, 2026-11-04). The thread then falls back to a general-purpose agent given the agent file's text. That agent loads the resident instructions that the agent file's `omitClaudeMd` setting exists to leave out.

**Why it matters.** Every Projects thread closes out its branches through step 8, and the pull-request skill and reply rule 16 send drafts to the copy editor the same way. In a thread, the copy editor then either does not run or runs with every resident instruction loaded. `PL-J1ZM`'s design left that context out so that a run starts small and judges the text by the writing rule alone. On 2026-11-04 a request of two passages, run through `claude -p --agent copy-editor` inside the repository, loaded those instructions and started at about 48,000 tokens. The same request run from an empty directory read 18,739 tokens.

**Done when.** One command runs the copy editor in every kind of session, a Projects thread included, from a directory that holds only the request, with the agent file's body as its instructions and Read as its one tool. Close-out step 8, the pull-request skill, reply rule 16 and `docs/prose-review/README.md` name that command. A test shows that the copy editor's directory holds the request and nothing else.

**Generator check.** This is a defect in `PL-J1ZM`'s fix, found by the first thread to use that fix (`PL-J37P`). The fact at stake is how a session starts the copy editor. Its one home is now `tools/copy_edit.py`, which the four instructions above name. The agent file stays the one home of the copy editor's instructions. No other open item reports this defect, so no new head.

**Done 2026-11-04.** `tools/copy_edit.py FILE` runs the copy editor as its own `claude -p` process. The process starts in an empty temporary directory that holds only the request. Its system prompt is the agent file's body, its one tool is Read, and it loads no settings file and no memory index. It runs on the model and effort that `docket.toml`'s `[models]` table chooses for the role `copy-editor`. A run on `#2023`'s pull request body read 14,140 tokens and cost $0.19. The coordinator reported that the `copy-editor` agent type appeared in a thread after its session resumed. This session never saw that agent type listed, so the command is the route that does not depend on how a session started.
