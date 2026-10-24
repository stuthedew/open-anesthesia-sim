---
id: PL-646J
title: owner_ask_guard.py reads only the top-level string fields of mcp__hearthbot__post_message, whose input schema no session has read, so a coordinator post carrying its text in a nested field passes unchecked
status: untriaged
feature: review-hold
added: 2026-10-24
---

**Problem.** owner_ask_guard.py reads only the top-level string fields of mcp__hearthbot__post_message, whose input schema no session has read, so a coordinator post carrying its text in a nested field passes unchecked

Found building `PL-YV90` on 2026-10-24. The building session could not read the tool's schema, so `TEXT_FIELDS` maps `mcp__hearthbot__post_message` to `None`, which reads every top-level string field. A coordinator session, which holds the tool, can read its schema and either confirm the field or narrow the read to it. The hook fails open on a text it cannot find, so a nested field would let a bare read ask through with no refusal.
