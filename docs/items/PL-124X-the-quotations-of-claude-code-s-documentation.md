---
id: PL-124X
title: The quotations of Claude Code's documentation already recorded in live documents were never checked against the pages: some came through WebFetch, which returns a model's answer rather than the page (PL-B1BW), so each quotation in the standing documents and open items citing code.claude.com should be compared with the page's .md and corrected where it differs
priority: P3
effort: M
status: ready
classes: docs
touches: docs/ARCHITECTURE.md, docs/maintainer.md, docs/resident-instructions.md, .claude/skills/docket/SKILL.md, docs/items
added: 2026-10-01
payoff: the rules resting on Claude Code's documentation rest on what its pages say, not on a summarizing model's paraphrase
verify: grep -qE '^\*\*Compared [0-9]{4}-[0-9]{2}-[0-9]{2}\.\*\*' docs/items/PL-124X*.md
---

**Problem.** The quotations of Claude Code's documentation already recorded in live documents were never checked against the pages: some came through WebFetch, which returns a model's answer rather than the page (PL-B1BW), so each quotation in the standing documents and open items citing code.claude.com should be compared with the page's .md and corrected where it differs

**Why it matters.** Rules here rest on quoted sentences from Claude Code's documentation - the compaction cap opening `.claude/skills/docket/SKILL.md`, the `env` lines in `docs/maintainer.md` - and `PL-B1BW` showed WebFetch can put words into a quote. A rule built on a misquote is obeyed by every session and checked by none.

**Done when.** Each quotation of code.claude.com in the four live files below and in every open item has been compared with the page's `.md`, each that differs is corrected or its claim withdrawn, and the comparison is recorded here under a `**Compared <date>.**` heading with its count.

**Reproduced 2026-10-01.** Four live files outside `docs/items` cite code.claude.com: `docs/ARCHITECTURE.md`, `docs/maintainer.md`, `docs/resident-instructions.md` and `.claude/skills/docket/SKILL.md` (`docs/pr-bodies/733.md` is a record and is left alone). The `.md` form answers from a cloud container: https://code.claude.com/docs/en/skills.md returned HTTP 200.

**Generator check.** `PL-B1BW` (done) fixed how a quote is fetched, and this backfills what was fetched before it: bookkeeping. If the comparison finds two or more misquotes, WebFetch's summary is a fact misread by two or more items with no head, and is recorded as a generator then.
