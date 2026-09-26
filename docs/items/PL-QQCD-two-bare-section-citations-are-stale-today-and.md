---
id: PL-QQCD
title: Two bare section citations are stale today and nothing checks a bare citation: ROADMAP.md cites a Current baseline v0.4.26 heading that is now v0.5.10, and docs/MODEL.md cites Published wash-in validation test, now Published wash-in and elimination validation test
priority: P3
effort: S
status: done
classes: defect, docs
feature: exact-gates
milestone: v0.5.12
touches: ROADMAP.md, docs/MODEL.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-25
closed: 2026-09-26
pr: 1083
payoff: a reader following a section citation in the roadmap or the model specification lands on the section it names instead of nowhere
verify: ! grep -qF 'Current baseline: v0.4.26' ROADMAP.md && ! grep -qF 'wash-in validation test' docs/MODEL.md
---

**Problem.** Two bare section citations are stale today and nothing checks a bare citation: ROADMAP.md cites a Current baseline v0.4.26 heading that is now v0.5.10, and docs/MODEL.md cites Published wash-in validation test, now Published wash-in and elimination validation test

ROADMAP.md cites § "Current baseline: v0.4.26"; the heading has been renamed at every cut since and the cited subsection exists nowhere. docs/MODEL.md cites § "Published wash-in validation test"; the heading is now "Published wash-in and elimination validation test". doc_check checks a quoted heading only after see/under or before above/below, so a bare `§ "X"` with no document named is read by nothing - 264 such citations across documents (182) and live items (82).

Re-confirmed 2026-09-25 against 46954a81. The references are anchored here by their text: the ROADMAP line number captured with this item had already drifted by 48 lines, so it was removed from the paragraph above rather than re-pointed. The ROADMAP one is the citation that places the comparison display's id and reasoning in the v0.4.26 baseline, in the sentence ending "deliberately rather than here"; the baseline heading has been renamed at every cut since, and the subsection it points into ("The comparison display landed early, and the patch survives it") is found by `git grep` nowhere but in the citation itself. The first MODEL.md one is in the sentence ending "already attributes to this model's rebreathing circuit", wrapped across a line break. **A third reference the brief did not name:** the paragraph opening **What bounds it is what this model omits.** quotes the same old heading name with no section mark, also wrapped.

Both MODEL.md references were written on 2026-09-07 (#421, #423), before `PL-B9VL` renamed the heading on 2026-09-13 (#512), so they are leftovers of that rename. The ROADMAP one was written at the v0.4.26 cut and orphaned by the v0.4.27 cut the same day: every cut renames the baseline heading by design, so a citation naming it goes stale at the next one. The `verify:` pins the two named citations; the third is wrapped mid-name, and no single-line `grep` pins it without also failing a correct rewrap.

**Generator check.** The fact misread is whether a bare quoted heading makes a section citation, which `doc_check` recognises only beside see, under, above or below - `PL-GPJ7`'s `misread:`, read from the passing side, and a member of it correctly: bringing bare section citations under checking, as its done-when does, would have caught all three. The MODEL.md pair is also a re-entry of `PL-B9VL` (closed 2026-09-13), whose rename should have carried its citations.

**Why it matters.** A reader of `docs/MODEL.md`, the simulator's authoritative specification, following a citation lands nowhere. Small, but it is the authoritative document, and the class is unchecked.

**Done when.** All three references name headings that exist - the two citations and the quote-only reference under **What bounds it is what this model omits.**; the check that makes bare `§` citations checked is the `exact-gates` head's work, not this item's.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Closed 2026-09-26, in `PL-GPJ7`'s first build.** The two `docs/MODEL.md` references now name "Published wash-in and elimination validation test", the quote-only one under **What bounds it is what this model omits.** marked as a citation with its neighbour "Known limitations". The `ROADMAP.md` citation points at the v0.4.26 row of the version table under "Versioning decision", which is where the id and the reasoning it named now live: the baseline subsection it cited exists only in the v0.4.26 tag's copy of the roadmap, since every cut rewrites that section. The same change reads a bare `§` citation wherever it stands, so all three would fail `make check` today were they still stale.
