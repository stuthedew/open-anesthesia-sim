---
id: PL-3NKZ
title: Item briefs are outside doc_check's document set, so a brief's path citations are never resolved - and they cannot simply be added, because a brief names paths it intends to create as well as paths that exist
status: untriaged
added: 2026-09-19
---

**Problem.** Item briefs are outside doc_check's document set, so a brief's path citations are never resolved - and they cannot simply be added, because a brief names paths it intends to create as well as paths that exist

**Why it matters.** `DOC_GLOBS` holds the authoritative documents; `docs/items/`
is not among them, so `check_citations` - which resolves every path and section
a document cites - has never read a single item brief. `PL-G424`'s
`check_line_citations` now reads live briefs for *line* citations, which makes
the gap visible: the same file is checked for one kind of citation and not the
other.

**Measured 2026-09-19.** 62 path citations in live briefs resolve to nothing.

**But the obvious fix is wrong, which is the whole finding.** A brief
legitimately names paths that do not exist yet, because naming what the work
will create is what a brief is for: `PL-1FT6` cites `src/anesthesia_sim/layout/`
as the package it builds, `PL-49R8` cites `.claude/rules/run-is-its-definition.md`
as the rule it writes. Adding `docs/items/*.md` to `DOC_GLOBS` would fire on
every one of those - a check that fires without changing a decision, which
`CLAUDE.md` retires a check for.

So the question is whether a brief can distinguish *citing* a path from
*specifying* one, cheaply enough to be worth it. `touches` already lists the
files an item will change, and is the obvious candidate for the exemption: a
dangling citation to a path the item declares in `touches` is a specification,
and one to a path it does not is a citation that has drifted. Whether that
separates the 62 cleanly is the measurement this item owes before any check is
built.

**Do not treat this as a `PL-G424` leftover.** That head decided *line*
citations and closed. This is a different anchor with a different failure mode,
and its answer may well be that no check is worth building - which is a
legitimate outcome to record rather than a gap to close.

**Found.** Session closing `PL-G424`, 2026-09-19.
