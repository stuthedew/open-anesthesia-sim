---
id: PL-646J
title: owner_ask_guard.py reads only the top-level string fields of mcp__hearthbot__post_message, whose input schema no session has read, so a coordinator post carrying its text in a nested field passes unchecked
priority: P3
effort: S
status: ready
classes: defect
feature: review-hold
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py
added: 2026-10-24
payoff: a bare read or merge ask relayed by the coordinator is refused wherever its text sits in the post, so the guard no longer depends on a schema nobody has read
verify: grep -q 'def test_a_coordinator_post_with_its_text_in_a_nested_field_is_refused' tests/unit/test_owner_ask_guard.py
reenters: PL-YV90
---

**Problem.** owner_ask_guard.py reads only the top-level string fields of mcp__hearthbot__post_message, whose input schema no session has read, so a coordinator post carrying its text in a nested field passes unchecked

Found building `PL-YV90` on 2026-10-24. The building session could not read the tool's schema, so `TEXT_FIELDS` maps `mcp__hearthbot__post_message` to `None`, which reads every top-level string field. A coordinator session, which holds the tool, can read its schema and either confirm the field or narrow the read to it. The hook fails open on a text it cannot find, so a nested field would let a bare read ask through with no refusal.

**Reproduced 2026-10-24.** A `post_message` call whose input was `{"channel": "project", "blocks": [{"type": "text", "text": "Read #1700 and merge it."}]}` went through the hook with no refusal: `python3 .claude/hooks/owner_ask_guard.py` printed nothing and exited 0. The same text in a top-level `message` field was refused. `message_text` keeps only the values of `tool_input` that are strings, so a string inside a nested dictionary or list is never read.

**Why it matters.** The guard exists so that a bare read or merge ask relayed by the coordinator never reaches the owner. If `post_message` carries its text below the top level of its input, every such ask goes through and the guard says nothing. It then looks like protection while giving none.

**Done when.** For `post_message`, the hook reads every string in the call's input at any depth, inside dictionaries and lists, so an ask in a nested field is refused as one in a top-level field already is. A regression test posts the ask in a nested field and sees it refused. This does not need the tool's schema: every string is a superset of any field the schema could name, and the hook already leans toward refusing.

**Generator check.** A re-entry of `PL-YV90`, closed 2026-10-24, whose fix wired the guard on `post_message` but read only the top level of the call's input. The fact is `PL-TLPH`'s: whether the owner may be sent a read or merge ask about a pull request. This reader misread where in a post that ask can sit, because nothing records `post_message`'s input schema. Recorded as `reenters: PL-YV90`.
