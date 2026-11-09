---
id: PL-MKCD
title: Call the person using the simulator by one name throughout docs/ARCHITECTURE.md (it says the user, the reader and the learner), choosing it with docs/MODEL.md in view, whose headings say the reader; left out of the PL-SVGH restructure because it is a wording change, which waits on the copy editor fix PL-F0Q2
status: untriaged
feature: architecture-md-structure
added: 2026-11-07
---

**Problem.** `docs/ARCHITECTURE.md` calls the person using the simulator three things, "the user", "the reader" and "the learner", so a contributor cannot tell whether these are one person. Choose one name with `docs/MODEL.md` in view, and use it throughout `docs/ARCHITECTURE.md`.

**Why.** The structure review of `docs/ARCHITECTURE.md` (`PL-SVGH`, finding "One person, three names") found "the user" in § "Package map" and § "Data flow", "the reader" in § "Layering", both User state chapters and § "Where new code belongs", and "the learner" in the branch chapters. `docs/MODEL.md` has two headings that say "the reader's": § "What this list requires once the layout is the reader's" and § "A cost at the reader's price". `PL-SVGH` only moved and deduplicated text, so it left the wording, which waits on the copy editor fix `PL-F0Q2`.

**How.** Once `PL-F0Q2` (the copy editor fix) has merged, choose the name with both documents in view, change each mention, and rename any heading that changes together with every file that cites it. `python3 tools/doc_check.py check` reports a § citation left pointing at a renamed heading.
