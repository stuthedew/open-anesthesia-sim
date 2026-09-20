---
id: PL-3NKZ
title: Item briefs are outside doc_check's document set, so a brief's path citations are never resolved - and they cannot simply be added, because a brief names paths it intends to create as well as paths that exist
priority: P2
effort: M
status: ready
classes: infra
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-19
payoff: settles whether a brief's 62 dangling path citations are drift worth catching or the specifications a brief exists to write, so nobody re-opens it
verify: grep -q 'def test_a_brief_citing_a_path_it_declares_is_quiet' tests/unit/test_doc_check.py
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

**Confirmed at triage, 2026-09-20.** `DOC_GLOBS` in `tools/doc_check.py` holds
`README.md`, `ROADMAP.md`, `CLAUDE.md`, `AGENTS.md`, `docs/*.md`,
`.claude/rules/**/*.md`, `.claude/skills/*/SKILL.md` and
`subprojects/*/README.md`. `docs/*.md` does not match `docs/items/*.md`, so the
queue is outside the set as the problem statement says.

**Done when.** The `touches` exemption is measured against the 62 dangling path
citations - how many resolve to a path the citing item declares, and how many
are drift - and either `docs/items/*.md` joins the checked set behind that
exemption with a test driving both cases, or the item is dropped with the count
recorded and the reason a brief's path citations cannot be checked without
reading intent.
