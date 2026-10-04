---
id: PL-F5B9
title: tools/dead_ends.py reads a docs/dead-ends.md bullet one line at a time, so a bold title wrapped onto a second line drops the entry from the digest with nothing reported, and a lazy continuation opening with #, *, - or a pipe cuts the entry short with its ids unchecked; latent
status: untriaged
feature: one-answer
added: 2026-10-04
---

**Problem.** tools/dead_ends.py reads a docs/dead-ends.md bullet one line at a time, so a bold title wrapped onto a second line drops the entry from the digest with nothing reported, and a lazy continuation opening with #, *, - or a pipe cuts the entry short with its ids unchecked; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `- **One shared queue\ndocument** - rejected ... PL-KM3X` gives `entries` [], an empty emit and `check` [], where CommonMark reads one list item; `...measured in\n#1234 and PL-ZZZZ` is emitted cut at "measured in", with no continuation error and the nonexistent `PL-ZZZZ` unchecked. It errors only on a continuation line opening with a letter. Latent: all 11 bullets in `docs/dead-ends.md` are one line.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
