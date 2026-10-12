---
id: PL-CGBK
title: PL-SL16's title and census name model versions in a pushed artifact, against PL-B11M's no-model-id rule the same item restates, and the title carried one into docs/releases/v0.5.11.md, whose bullet PL-DRRG reworded by hand
priority: P3
effort: S
status: done
classes: docs
feature: public-history
milestone: v0.5.24
touches: docs/items/
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-25
closed: 2026-10-12
pr: 1441
payoff: PL-B11M's record says what its no-model-id rule reaches, so no session re-raises the nine files on main that name a model deliberately
verify: grep -qF 'governs attribution' docs/items/PL-B11M-detect-a-silent-model-fallback-last-served.md
---

**Problem.** PL-SL16's title and census name model versions in a pushed artifact, against PL-B11M's no-model-id rule the same item restates, and the title carried one into docs/releases/v0.5.11.md, whose bullet PL-DRRG reworded by hand

**What is there.** `PL-SL16`'s title quotes the harness reminder's
model-named co-author trailer verbatim, and its census (the lines counting
co-author lines by name, and the paragraphs on `#580` to `#582` and on
`PL-LWMS`'s session) names four model versions. `PL-B11M`'s decision, which
`PL-SL16` exists to state, allows no model id in any pushed artifact, and
`#1001`'s own review removed one from `docs/resident-instructions.md` for that
reason, so the item is the one place on `main` the rule was not applied.

**Corrected at triage, 2026-09-25: not the one place.** `git grep -lE 'Claude
(Opus|Sonnet|Haiku|Fable) [0-9]|claude-(opus|sonnet|haiku|fable)-[0-9]'
origin/main` lists nine files. `PL-LWMS` carries the same census.
`docs/maintainer.md` names model ids as the owner's model-choice guidance,
which it cannot give without naming them. `PL-13PB` and `PL-9FNV`'s `verify:`
name ids too, and `docs/pr-bodies/108.md`, `126.md` and `171.md` keep a
model-named `Co-Authored-By:` trailer as the verbatim body they recover. So
nobody on `main` reads the rule literally. All three of `PL-B11M`'s reasons are
about attribution: the trailer records the configured model, `Co-authored-by`
is a people field, and a rule requiring an id would conflict with the harness.

Reproduced 2026-09-25 against 46954a81: `PL-SL16`'s title still quotes the
reminder's model-named trailer, and its census still names four versions.
`docs/releases/v0.5.11.md`'s bullet already reads "a model-named co-author".
`#1001`'s squash commit (`21f05486`) names no model, and no commit message on
`origin/main` since 2026-09-24 does.

**Why it reached a release.** `bin/docket release` renders each bullet from the
item's title, so the v0.5.11 notes carried the model name until `PL-DRRG`
reworded that one bullet to "a model-named co-author" by hand. No later cut
renders `PL-SL16` again, so the title's only remaining reach is the item file
and whatever quotes it.

**Why it matters.** Not much, now that the release bullet is repaired. What
remains is the scope of `PL-B11M`'s rule. Read literally, it condemns nine
files on `main`, the owner's own model guidance among them. Read by its
reasons, it condemns none. A later session that reads the rule literally
will re-raise this finding against each of those files.

**Decision needed.** Reword the title and census to count "model-named" lines without
naming versions, which loses the per-version breakdown the census used to show
where the trailer came from, or keep them as quoted evidence and write that
exception into `PL-B11M`'s record. Either way, whether `docket check` should
refuse a model id in an item title is a new check, held by the pause while any
item carries `generator: live`.

**Recommendation:** keep them as quoted evidence, and record the scope in
`PL-B11M`, under its decision. Suggested wording: the rule governs
attribution, meaning a trailer or any line that credits a model as an author.
It does not govern quotation, measurement or model-choice guidance. Three
reasons:

- The recorded reasons reach no further than attribution.
- `PL-SL16` is `done`, and `.claude/rules/citation-drift.md` treats a closed
  brief as a historical record, not a live assertion. The per-version census
  is the evidence that located where the trailer came from.
- A title check would fire on the nine files above. It would refuse the owner's
  own guidance rather than a violation.

Rewording `PL-SL16` would erase evidence and still leave `PL-LWMS` and
`docs/maintainer.md` in the same state. A session can take this: it applies
`PL-B11M`'s stated reasons, and the change is the wording of one record. If the
owner prefers the literal reading, the consequence to put to them is rewording
all nine files, `docs/maintainer.md` included.

**Done when.** Either `PL-B11M`'s record states the rule's scope and this item
closes with nothing else changed, or the literal reading is chosen and every
file it condemns has been reworded.

**Generator check.** One-off. The fact misread is the reach of `PL-B11M`'s rule,
and no head's `misread:` states it. The eight other files on `main` name models
deliberately, so they are not misreadings of it. The one reach that mattered, a
release bullet rendered from a title, happened once and `PL-DRRG` repaired it.

**Decided and done** (2026-10-12, in the first batched design round, a
session's call, as the brief itself says a session can take it): the
recommendation. The scope is recorded under `PL-B11M`'s decision, dated and
naming this item: the rule governs attribution - a trailer, or any line that
credits a model as an author of a pushed artifact - and not quotation as
evidence, a census, or the owner's own model-choice guidance; a closed brief's
census stays as the evidence it is (`.claude/rules/citation-drift.md`). What a
session writes anew still follows the harness's own instruction against model
identifiers, which is broader and binds the session whatever the record says,
so the note licenses no new model name. Nothing else changed: `PL-SL16`'s
title and census stand, and no title check was built, which the pause on new
workflow mechanisms would have held in any case. It reads the owner's own
decision of 2026-09-16 by its three recorded reasons rather than reversing it;
if he reads it literally instead, the consequence is rewording all nine files,
`docs/maintainer.md` included, and that is the one line this item leaves for
him.
