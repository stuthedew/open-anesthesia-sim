---
id: PL-QM5P
title: README.md's description of doc_check candidates still says it prints lines mentioning anything the diff touched, which PL-B2NS narrowed to code mentions
status: untriaged
added: 2026-09-05
---

**Problem.** `README.md:179` says `doc_check.py` "also has a `candidates` mode
that prints the documentation lines mentioning anything a diff changed".
`PL-B2NS` narrowed that: a term that is also an ordinary English word is now
reported only where a line marks it as code, and the output names the terms it
narrowed. The two other statements of the same gloss - `CLAUDE.md` and the
`docket` skill's close-out step - were corrected in `PL-B2NS`'s own commit.

**Why it matters.** A session reading the README gloss and then seeing three
candidate lines where the old tool printed thirty-eight has no way to tell a
narrowed list from a broken tool. It is one word of drift, not a safety
statement, which is why it can wait for the freeze to lift.

**Where.** `README.md`, the tooling paragraph at line 179.

**Not fixed here because.** `.claude/rules/readme-hold.md` freezes `README.md`
until the owner says what the document is for (`PL-RM83`). That rule names this
exact case - a doc sweep reaching the README - and says to file rather than fix.

**Done when.** The README sentence says the mode prints the lines naming
anything the diff touched *as code*, matching `CLAUDE.md`. Fold it into
`PL-N092` (the README rewrite) if that lands first.
