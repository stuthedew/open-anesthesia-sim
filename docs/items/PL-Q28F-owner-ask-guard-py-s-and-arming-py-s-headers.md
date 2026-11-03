---
id: PL-Q28F
title: owner_ask_guard.py's and arming.py's headers carry decision history (68 and 206 lines) that belongs in the items, so a reader must get past the history to learn what the code does
priority: P3
effort: S
status: ready
classes: docs
feature: guard-code-structure
touches: subprojects/docket/src/docket/arming.py, .claude/hooks/owner_ask_guard.py
deferred-from: v0.7.0 - captured after the freeze; a workflow-lane code-structure change, not safety or science, and no learner sees it
added: 2026-11-03
payoff: a reader of arming.py or owner_ask_guard.py learns what the code does from its header, and finds each decision's history in its item
verify: ! grep -qF 'moved here from `CLAUDE.md` with it' subprojects/docket/src/docket/arming.py && ! grep -qF '**Why the state decides, and the wording only finds the ask.**' .claude/hooks/owner_ask_guard.py
---

**Problem.** owner_ask_guard.py's and arming.py's headers carry decision history (68 and 206 lines) that belongs in the items, so a reader must get past the history to learn what the code does

**Why it matters.** A reader opens `arming.py` to learn what `arm` checks. The
first 207 lines are its docstring, and lines 75 to 201 are a dated list of the
decisions behind each rule: who chose it, what it was chosen over, and the
counts that argued for it. `owner_ask_guard.py` does the same in its paragraphs
on why the state decides, why a hook, and the tool rename. The plain-writing
rule puts decision history in the item, so a reader of the code gets the rule
and a pointer.

**Done when.** `arming.py`'s header keeps the five answers, the precedence
between them, and one line per rule that names the rule and the item holding
its decision. The dated reasoning moves out of the header into this item's
body, under "The decisions arming rests on", word for word, so nothing is
lost. `owner_ask_guard.py`'s header says what the hook checks, which tools it
reads, what it cannot check and how it fails; its history paragraphs move
here the same way. No code changes.

**Generator check.** No generator. Other modules that carry history in their
headers are prose-quality work, one item each.
