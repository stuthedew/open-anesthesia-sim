---
id: PL-YN60
title: owner_ask_guard.py and its .claude/settings.json matcher name the thread tools reply, update_message and ask_decision, but a Projects thread now has post_message, edit_message and request_decision, so a thread's reply gets only the coordinator's partial check and an edited message or a decision card gets no check at all
priority: P2
effort: S
status: done
classes: defect
feature: review-hold
milestone: v0.6.13
touches: .claude/hooks/owner_ask_guard.py, .claude/settings.json, tests/unit/test_owner_ask_guard.py, docs/maintainer.md, .claude/rules/apparatus-standard.md, docs/items
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-02
closed: 2026-11-02
pr: 1931
payoff: an ask to read or merge that a thread writes into a post, an edit or a decision card is checked again, and a renamed Projects tool is checked rather than skipped
verify: grep -q 'NOT_TO_THE_OWNER' .claude/hooks/owner_ask_guard.py && grep -qF '"matcher": "^mcp__hearthbot__.*$"' .claude/settings.json
reenters: PL-TLPH
---

**Problem.** owner_ask_guard.py and its .claude/settings.json matcher name the thread tools reply, update_message and ask_decision, but a Projects thread now has post_message, edit_message and request_decision, so a thread's reply gets only the coordinator's partial check and an edited message or a decision card gets no check at all

**Evidence, 2026-11-02.** The tool list of the thread "Finish generator-heads,
drift and stale source claims" (session `session_01GnrHQsDAznecqQ2CaGhJgr`)
offers `mcp__hearthbot__post_message`, `mcp__hearthbot__edit_message` and
`mcp__hearthbot__request_decision` for what reaches the owner. It offers no
`reply`, `update_message` or `ask_decision`. `.claude/hooks/owner_ask_guard.py`
lists the old three in `TEXT_FIELDS` and treats `post_message` as
`COORDINATOR_POST`, the coordinator's post. The `PreToolUse` matcher in
`.claude/settings.json` is
`^mcp__hearthbot__(reply|update_message|ask_decision|post_message)$`.

**What follows.** A thread's reply now goes out through `post_message`, so it
gets the partial check `PL-YV90` built for the coordinator: the hook looks for a
line in the rendered `Owner-ask:` form and does not run `bin/docket arm` to
see whether it is the line recorded for this branch. An edited message and a
decision card match no hook at all, so an ask written into either is not
checked. The full check that `PL-TLPH` built runs for no tool a thread has.
When the tools were renamed is not known.

**Why it matters.** `PL-TLPH`'s hook is the guard that keeps a bare read or
merge ask from reaching the owner. A guard keyed on tool names goes quiet when
the harness renames them, and nothing reports that it went quiet.

**Not decided here.** Whether repository hooks run in Projects threads at all
is `PL-CR81`'s question. This thread's session did print the session-start
digest on 2026-11-02, which `PL-CR81`'s probes of 2026-10-25 did not see. How
the hook should tell a thread's `post_message` from the coordinator's, now that
both use one tool name, is for the fix. One option is to run the full check
whenever the checkout's branch has an open pull request, and the partial check
otherwise.

**Generator check.** A new defect in `PL-TLPH`'s fix, filed after the answer
that `PL-5HQY` recorded for `PL-TLPH`'s line. Recorded as `reenters: PL-TLPH`.

**Done when.** The hook is wired on every `mcp__hearthbot__` tool and reads
every string in the call, skipping only the tools whose text goes to another
session or names a thread. A post, an edit and a decision card that ask the
owner to read or merge are each refused without the `Owner-ask:` line. Where
`arm` prints a recorded ask for the branch, the message must carry that line.
Otherwise it must carry a line in the rendered form, which is how the
coordinator's relay still passes. A test fails against the hook before the
fix.
