---
id: PL-CGBK
title: PL-SL16's title and census name model versions in a pushed artifact, against PL-B11M's no-model-id rule the same item restates, and the title carried one into docs/releases/v0.5.11.md, whose bullet PL-DRRG reworded by hand
status: untriaged
touches: docs/items/
added: 2026-09-25
---

**Problem.** PL-SL16's title and census name model versions in a pushed artifact, against PL-B11M's no-model-id rule the same item restates, and the title carried one into docs/releases/v0.5.11.md, whose bullet PL-DRRG reworded by hand

**What is there.** `PL-SL16`'s title quotes the harness reminder's
model-named co-author trailer verbatim, and its census (the lines counting
co-author lines by name, and the paragraphs on `#580` to `#582` and on
`PL-LWMS`'s session) names four model versions. `PL-B11M`'s decision, which
`PL-SL16` exists to state, allows no model id in any pushed artifact, and
`#1001`'s own review removed one from `docs/resident-instructions.md` for that
reason, so the item is the one place on `main` the rule was not applied.

**Why it reached a release.** `bin/docket release` renders each bullet from the
item's title, so the v0.5.11 notes carried the model name until `PL-DRRG`
reworded that one bullet to "a model-named co-author" by hand. No later cut
renders `PL-SL16` again, so the title's only remaining reach is the item file
and whatever quotes it.

**To decide.** Reword the title and census to count "model-named" lines without
naming versions, which loses the per-version breakdown the census used to show
where the trailer came from, or keep them as quoted evidence and write that
exception into `PL-B11M`'s record. Either way, whether `docket check` should
refuse a model id in an item title is a new check, held by the pause while any
item carries `generator: live`.
