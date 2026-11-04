---
id: PL-X4MD
title: The owner-ask guard guesses which Projects messages are asks from their wording; attach the recorded question to every message naming a pull request that waits on the owner, and flag a waiting pull request with no recorded question by state
priority: P2
effort: M
status: ready
feature: owner-ask-by-state
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py, docs/maintainer.md
added: 2026-11-04
payoff: every Projects message about a pull request that waits on the owner arrives carrying the recorded question, or a plain line that none is recorded, and no progress note is ever refused for its wording
verify: grep -q 'def test_an_ask_about_a_waiting_pull_request_carries_the_recorded_question' tests/unit/test_owner_ask_guard.py
---

**Problem.** `.claude/hooks/owner_ask_guard.py` decides which Projects messages are asks by matching their wording against a list of ask phrasings, plus a match on the recorded question-and-options form. Wording is a guess. An earlier version of the guard refused ordinary progress updates on that guess, and the owner rejected it. The guard that merged in #1984 checks only messages whose wording matches, so a non-question phrased in words the list does not hold still reaches the owner. A "non-question" is an ask that carries no recorded question, as `PL-3D2F` defines it.

**Why it matters.** The owner decides from the message in chat. If a thread's ask reaches them without the recorded question, they either decide on something no record backs, or have to go and find what is being asked. The fact that settles this is already recorded: `bin/docket arm --owner-ask` says whether a branch waits on the owner's read and prints the recorded question when there is one. The guard should read that fact rather than guess from wording. That is the repository's one-source-of-truth rule.

**Decision (project owner, 2026-11-03, ratified, over keeping the wording match, over flagging by state alone, which loses the question in chat, and over a dedicated ask tool for Projects threads, which this repository cannot add).** The recommendation, as approved:

1. **Test first.** In a Projects thread, check whether a PreToolUse hook that rewrites a `mcp__hearthbot__` message with `updatedInput` and returns `permissionDecision: "allow"` actually changes what reaches the owner. Record the result here. Everything below depends on it.
2. **Attach the question from the record.** On any Projects message that names a pull request waiting on the owner's read, the hook appends the recorded question when the message does not already carry it word for word. With no question recorded, it appends "No question is recorded on this pull request yet, so there is nothing to decide." It returns `"allow"` with the rewritten input, and `additionalContext` telling the thread what was added. A message naming no waiting pull request goes out untouched.
3. **Flag the gap by state.** The coordinator's summary lists every pull request that waits on the owner with no recorded question. That catches a waiting thread before it messages the owner.
4. **Then remove the wording match.** Once steps 2 and 3 work, `ASKS`, `_HANDOFF`, `renders_owner_ask`'s use in the hook and their tests go.
5. **Build on the single guard entry point.** `PL-S3TF` (#1990, open on 2026-11-03) routes every guard through one entry point, this one included, so this waits for it. It landed with #1990 as `.claude/hooks/guard.py`, which runs this guard's `decide` in the `pre-mcp` group. `hook_input.verdict` there accepts only a refusal or a note, and `hook_input.output` merges the guards' outputs into one, so a rewrite through `updatedInput` with `permissionDecision: "allow"` needs both extended: one guard's `updatedInput`, and an `allow` that a refusal from another guard still overrides.

If the step 1 test fails, keep the guard from #1984 unchanged and build only step 3.

**Step 1, tried 2026-11-04 and not yet run.** A Projects thread (branch
`claude/project-thread-6lcfyq`, pull request #2005) tried the test by adding a
temporary hook to its own `~/.claude/settings.json`. The hook would have
appended one marked line to a `mcp__hearthbot__post_message` call whose text
held a marker, returning `permissionDecision: "allow"` with `updatedInput`,
and the thread would then have read its own message back with `read_thread`.
The session's permission check refused the write to the settings file as a
session changing its own configuration. So the test needs the owner's
go-ahead to add that one hook for one message, or another way to run it. Its
probe script is short: read the call, and where `tool_input.text` holds the
marker, print the hook output above with the marker removed and a line
appended.

**Done when.** Step 1's result is recorded here. Where it passed, a Projects
message that names a pull request waiting on the owner leaves carrying the
recorded question, or a line saying none is recorded, and the wording match is
gone. A test sends such a message through `.claude/hooks/guard.py` and finds
the question in what goes out. Where it failed, the coordinator's summary
lists each waiting pull request that has no recorded question.

**What the sources say.** A question to a human is best sent as a structured payload that the system renders, not as text the agent writes and something else checks:
- 12-Factor Agents, factor 7, "Contact humans with tool calls": https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md
- Claude Code's own `AskUserQuestion` takes `question` and `options` as fields: https://code.claude.com/docs/en/hooks
- Anthropic, "Building Effective Agents", appendix 2, "Poka-yoke your tools. Change the arguments so that it is harder to make mistakes": https://www.anthropic.com/engineering/building-effective-agents

Here the `Owner-ask` record plays the part of the payload, and the hook renders it.

**Caveats from the hooks docs (https://code.claude.com/docs/en/hooks, read 2026-11-03).**
- `updatedInput` "Replaces the entire input object, so include unchanged fields alongside modified ones." The hook must copy every field of the Projects tool's input. Nobody has yet read which field holds the message text.
- § "PreToolUse `updatedInput` in auto mode" says that when a hook returns `updatedInput` with no `permissionDecision`, "Claude Code can deny the changed call". If Claude then retries, "Any `updatedInput` it returns is dropped". The question would then silently fail to attach. That is why step 2 returns `"allow"`. The cost is that the hook approves those sends itself, skipping the permission check for them. Each one is a message to the owner only.
- An MCP tool marked `_meta["anthropic/requiresUserInteraction"]` cannot be approved by a hook. If a Projects tool carries that mark, step 2 cannot work for it.
- No source was found on hooks that edit an agent's outgoing message. The two caveats above come from the documentation, not from a published pattern.

**Costs.** A progress note that names a waiting pull request carries the question too, so the owner sees some repetition. The coordinator's own checkout is on no pull request's branch, so the hook cannot look up a question there. The coordinator case needs its own answer in step 2: the coordinator quotes the thread's recorded question, or the hook looks the pull request up by number, which was turned down on 2026-10-24 for its cost.

**Generator pause.** This adds workflow machinery while workflow-lane items are still generating. The owner's approval on 2026-11-03 lifts the pause for this item.

**Generator check.** This belongs with `PL-3D2F` and `PL-GPJ7` (hard gates that recognise what they check by wording), and adds no head of its own. `PL-3D2F` keyed the guard's answer on arm's recorded state but kept wording to decide which messages it checks at all. This item replaces that last use of wording with the same recorded state.
