---
id: PL-F5B9
title: tools/dead_ends.py reads a docs/dead-ends.md bullet one line at a time, so a bold title wrapped onto a second line drops the entry from the digest with nothing reported, and a lazy continuation opening with #, *, - or a pipe cuts the entry short with its ids unchecked; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/dead_ends.py, subprojects/docket/src/docket/roadmap.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1352
payoff: an entry of docs/dead-ends.md is read whole or refused by name, so no refuted approach drops out of the digest while make check calls the file sound
verify: grep -qF '"dead ends, ' tests/unit/test_doc_check.py
---

**Problem.** tools/dead_ends.py reads a docs/dead-ends.md bullet one line at a time, so a bold title wrapped onto a second line drops the entry from the digest with nothing reported, and a lazy continuation opening with #, *, - or a pipe cuts the entry short with its ids unchecked; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. `- **One shared queue\ndocument** - rejected ... PL-KM3X` gives `entries` [], an empty emit and `check` [], where CommonMark reads one list item; `...measured in\n#1234 and PL-ZZZZ` is emitted cut at "measured in", with no continuation error and the nonexistent `PL-ZZZZ` unchecked. It errors only on a continuation line opening with a letter. Latent: all 11 bullets in `docs/dead-ends.md` are one line.

**Reproduced 2026-10-04, at triage.** `dead_ends.entries` reads `- **One shared\nqueue document** — rejected.` as no entry and `check` reports nothing, and `- **An approach** — measured in\n#1234 and PL-ZZZZ` is emitted cut at "measured in", its `PL-ZZZZ` unchecked.

**Why it matters.** The digest resends these entries every turn so that a session about to re-propose a refuted approach sees it. An entry dropped or cut short with nothing reported is a refutation nobody sees, while `make check` calls the file sound.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** A bullet is read whole through docket's list walker - an indented line joined into it and still refused as a second line, one carried on from the margin refused by name - pinned by `dead ends, ...` cases in `PL-R417`'s guard.

**Built 2026-10-04 (`#1352`).** `dead_ends` reads the file through `roadmap.document_entry_lines`, the list walker started under each heading, and holds every bullet opening `- **` to the entry's rules even where its title wraps. An indented continuation is joined and refused as a second line; one carried on from the margin is refused by name. The shipped file's emit is byte-identical. Two guard cases, each failing on main's reader.
