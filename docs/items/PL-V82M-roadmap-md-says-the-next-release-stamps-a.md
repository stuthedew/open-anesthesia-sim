---
id: PL-V82M
title: ROADMAP.md says the next release stamps a release's own cut pull request every time, but since PL-KRS6 a cut item ships in no release, and the version rows that stated that rule are now one sentence each
priority: P2
effort: S
status: ready
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md, tools/doc_check.py
added: 2026-11-07
payoff: A session checking a release's span stops waiting for a stamp that never comes, and the roadmap again states that a cut item ships in no release.
verify: ! grep -qF 'the next release stamps it every time' ROADMAP.md && ! grep -qF 'stamped by the *next* release' tools/doc_check.py
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

**Why it matters.** A session checking a tag's span looks for a later release to stamp the cut's own pull request, and none ever does. The rule that a release's cut item ships in no release is now stated nowhere in the roadmap, so a reader of the version table cannot tell why no release lists its own cut.

**Done when.** `ROADMAP.md` states once that a release's own cut item ships in
no release, with `PL-KRS6`, and the exemption sentence and the `doc_check`
docstring say why the cut's own pull request is exempt in terms that are true
since then.

**Generator check.** One stale sentence and one docstring, left behind when
`PL-KRS6` changed the rule, plus a statement the table trim removed. No
mechanism keeps producing it, so nothing is recorded as a generator.

**Found by** the review of `PL-DWGC`'s first part (`#2061`), which checked
that no rule a reader needs left the roadmap with the rows.

**Checked 2026-11-09:** § "Release tags and release notes" still says "the next release stamps it every time", and the docstring of `check_tag_span_covers_its_notes` in `tools/doc_check.py` still says the cut "is stamped by the *next* release, every time".

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. `ROADMAP.md` there already said a release's own cut pull request is "inside its own span by construction and stamped by the" next release, and `tools/doc_check.py` said the same. `PL-KRS6` had changed the rule on 2026-09-26.
