---
id: PL-V82M
title: ROADMAP.md says the next release stamps a release's own cut pull request every time, but since PL-KRS6 a cut item ships in no release, and the version rows that stated that rule are now one sentence each
status: untriaged
feature: roadmap-structure
touches: ROADMAP.md, tools/doc_check.py
added: 2026-11-07
---

**Problem.** `ROADMAP.md` § "Release tags and release notes" says a release's
own cut pull request is inside its own span by construction, "and the next
release stamps it every time". `tools/doc_check.py`'s docstring for
`check_tag_span_covers_its_notes` says the same. Since `PL-KRS6` (decided
2026-09-26), the release procedure gives a cut item no `milestone:`, and its
`resource: release-train` keeps it out of every later release's count and
notes (`.claude/skills/docket/modes/release.md`, "Close the release item after
the cut"). So no release names it, and the sentence is stale.

Until `PL-DWGC` trimmed the version table on 2026-11-07, about 45 rows stated
the current rule as "`PL-...`, the cut, ships in no release under `PL-KRS6`".
Each row now keeps one sentence, and the rule is stated nowhere in the
roadmap. Chapter read 2 of the structure read asked for it to be stated once,
above the table.

**Done when.** `ROADMAP.md` states once that a release's own cut item ships in
no release, with `PL-KRS6`, and the exemption sentence and the `doc_check`
docstring say why the cut's own pull request is exempt in terms that are true
since then.

**Generator check.** One stale sentence and one docstring, left behind when
`PL-KRS6` changed the rule, plus a statement the table trim removed. No
mechanism keeps producing it, so nothing is recorded as a generator.

**Found by** the review of `PL-DWGC`'s first part (`#2061`), which checked
that no rule a reader needs left the roadmap with the rows.
