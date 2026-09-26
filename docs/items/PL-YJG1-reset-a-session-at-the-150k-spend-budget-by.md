---
id: PL-YJG1
title: Reset a session at the 150k spend budget by pushing its work and compacting in place, not by handing off to a new session through a pasted prompt
priority: P2
effort: S
status: done
classes: session-cost, docs
feature: context-budget-reading
touches: CLAUDE.md, docs/maintainer.md, docs/resident-instructions.md, .claude/skills/docket/modes/picking.md, tools/context_reading.py, docs/ARCHITECTURE.md, docs/items/PL-H253-measure-session-context-length-as-the-dominant.md
added: 2026-09-25
closed: 2026-09-25
pr: 1005
payoff: A session that reaches its budget resets with one command the owner types, keeping its branch, claim and pull-request watch, instead of costing the owner a copy, a new session and a paste
verify: grep -qF 'then ask the project owner to type `/compact`' CLAUDE.md
---

**Problem.** The budget (`PL-H253`, `PL-NW76`, `PL-W80S`) resets a session by
handing off to a new one, and the owner carries every handoff by hand: copy
the prompt, open a session, paste. Any item or feature larger than what is
left of 150,000 tokens of spend becomes a multi-session relay. The owner raised
it on 2026-09-25 as a code smell against a 1,000,000-token window.

**What the three earlier items argued about, and what they did not.** Each one
reopened the *number*. None priced the *route*. The token cost of a handoff was
counted, and it is stale: `CLAUDE.md` said it "costs about 25,000 tokens to
rebuild", while `PL-W80S` measured the floor a session starts at as 81,048
tokens bare and 115,320 with the `docket` skill loaded, before any file is
read. The owner's time was never counted at all. That is the quantification
fixation `.claude/rules/expert-review.md` names: the side with a number wins.

**Why compaction lands where a handoff does, once the work is pushed.**
- A handoff gives: the floor, plus a summary the old session wrote, plus files
  re-read.
- `/compact` gives: the floor, plus a summary the session writes, plus files
  re-read. The project-root `CLAUDE.md` and the unscoped rules are re-injected
  from disk
  ([context window](https://code.claude.com/docs/en/context-window)).
- The pasted prompt is itself a model-written summary. That is the "lossy
  summarization pass" `docs/maintainer.md` held against compaction.
- Provenance has to be on disk before either reset, so compaction loses
  nothing a handoff keeps.
- It keeps the branch, the claim, the pull-request subscription and scheduled
  check-ins, which a new session sets up again or loses.
- `/compact` works in cloud sessions and takes focus instructions. `/clear`
  does not
  ([cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web)).

**Path-scoped rules are not lost, checked against the implementation.** The docs
say compaction "summarizes them away". Claude Code 2.1.282's compaction path
(`/opt/claude-code/bin/claude`) runs `readFileState.clear()` and deletes every
key of `loadedNestedMemoryPaths`. So each rule re-attaches on the next read of a
matching file, and editing an existing file after compaction needs a fresh read
anyway. The `SessionStart` `compact` hook this reset seemed to need is
therefore not built. Re-check it if a Claude Code release changes compaction.
An invoked skill comes back capped at 5,000 tokens, which the `docket` skill was
already split to survive.

**Routes weighed and not taken.**
- **Automatic compaction** (`CLAUDE_CODE_AUTO_COMPACT_WINDOW`): it fires
  wherever the count lands, mid-item included, which is the failure `PL-NW76`
  fixed.
- **A session starting its own successor** (`create_session`): it removes the
  paste but keeps every other handoff cost, and it lets sessions chain without
  the owner.
- **Raising the number**: never measured in either direction (`PL-LKGL`).

**Decided, project owner, 2026-09-25, ratified**, over handing off to a new
session through a pasted prompt at the budget. The 150,000-token spend figure
is unchanged. A fresh session is still the reset for an unrelated topic, where
the multi-turn evidence (Laban P, et al., *LLMs Get Lost In Multi-Turn
Conversation*, arXiv:2505.06120, 2025) favours a clean prompt over a carried
conversation.

**Rode along.** `PL-H253`'s brief overstated two of its three citations, and
it is corrected here.
- arXiv 2605.12922 measures attention to system-prompt tokens across turns in
  2B-32B open-weight models, not adherence.
- The EACL 2026 paper's abstract does not carry the "independently of
  instruction size" claim.

**Done when.** `CLAUDE.md` § "Session and tool-use efficiency" states the
budget reset as push-then-`/compact`, with its figure corrected. Four files
agree with it: `docs/maintainer.md`, `docs/resident-instructions.md`,
`.claude/skills/docket/modes/picking.md`, `tools/context_reading.py`'s
docstring, and `docs/ARCHITECTURE.md`'s name for the budget. `PL-H253`'s citations say what their sources say.
