---
id: PL-MKCD
title: Call the person using the simulator by one name throughout docs/ARCHITECTURE.md (it says the user, the reader and the learner), choosing it with docs/MODEL.md in view, whose headings say the reader; left out of the PL-SVGH restructure because it is a wording change, which waits on the copy editor fix PL-F0Q2
priority: P3
effort: S
status: ready
classes: docs
feature: architecture-md-structure
touches: docs/ARCHITECTURE.md
added: 2026-11-07
payoff: a contributor reads one name for the person using the simulator, so a rule about whose action is meant cannot be misread
verify: ! grep -qiE 'the (user|learner)|a learner' docs/ARCHITECTURE.md
---

**Problem.** `docs/ARCHITECTURE.md` calls the person using the simulator three things, "the user", "the reader" and "the learner", so a contributor cannot tell whether these are one person. Choose one name with `docs/MODEL.md` in view, and use it throughout `docs/ARCHITECTURE.md`.

[superseded 2026-11-09: `PL-F0Q2` is done, so the wording can change now] **Why.** The structure review of `docs/ARCHITECTURE.md` (`PL-SVGH`, finding "One person, three names") found "the user" in § "Package map" and § "Data flow", "the reader" in § "Layering", both User state chapters and § "Where new code belongs", and "the learner" in the branch chapters. `docs/INTERFACE.md` has two headings that say "the reader's": § "What this list requires once the layout is the reader's" and § "A cost at the reader's price". `PL-SVGH` only moved and deduplicated text, so it left the wording, which waits on the copy editor fix `PL-F0Q2`.

[superseded 2026-11-09: `PL-F0Q2` is done, so the wording can change now] **How.** Once `PL-F0Q2` (the copy editor fix) has merged, choose the name with both documents in view, change each mention, and rename any heading that changes together with every file that cites it. `python3 tools/doc_check.py check` reports a § citation left pointing at a renamed heading.

**Checked 2026-11-09:** `grep -oiw 'the user\|the reader\|the learner' docs/ARCHITECTURE.md | sort | uniq -c` counts 1 "the user", 30 "the reader" and 5 "the learner", with 11 more "a learner" and 9 "a reader". So the document still calls the person using the simulator by three names. `PL-F0Q2`, the copy editor fix this item waited on, is done, so the wording can now change.

**Why it matters.** A contributor cannot tell whether "the user", "the reader" and "the learner" are one person or three. Several rules in the document, such as who owns a setting the learner changed, depend on knowing whose action is meant.

**Done when.** `docs/ARCHITECTURE.md` calls the person using the simulator "the reader" throughout, or "a reader". That name is a placeholder chosen at triage on 2026-11-09, because it is the name both documents use most and the one `docs/MODEL.md`'s headings use. "A user's file", where it names a file that `user_files.py` writes, may stay. Any heading that changes is renamed together with every file that cites it.

**Generator check.** One-off: a finding from the `docs/ARCHITECTURE.md` structure read (`PL-SVGH`).

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/ARCHITECTURE.md` already says "the user" (row 279), "the learner" (row 489) and "the reader" (row 128, among others). So the problem was present at the freeze, commit `817a4d88` (2026-10-24), but the item is classed `docs` only, which is not debt, so v0.7.0's gate does not take it and it stays off the frozen list.
