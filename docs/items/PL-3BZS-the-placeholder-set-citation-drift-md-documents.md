---
id: PL-3BZS
title: The placeholder set citation-drift.md documents as the project's illustrative ids includes PL-A1B2, which is outside store.ID_ALPHABET, and modes/ideas.md prints it as an example
status: done
feature: one-id-grammar
milestone: v0.5.2
touches: .claude/rules/citation-drift.md, .claude/skills/docket/modes/ideas.md
added: 2026-09-21
closed: 2026-09-21
pr: 865
reason: closed with PL-7922: citation-drift.md and modes/ideas.md now name PL-B1C2, and tools/fixture_id_check.py refuses an unmintable literal anywhere under .claude/ so the hand-fix cannot regress
verify: uv run python tools/fixture_id_check.py
---

**Problem.** `.claude/rules/citation-drift.md:103` names the project's
illustrative placeholder ids as `PL-K7QX`, `PL-A1B2`, `PL-XXXX`. `PL-A1B2` is
outside `store.ID_ALPHABET` - Crockford base32 *minus the vowels* - so it is an
id `new_id` can never mint and `ID_PATTERN` never matches.
`.claude/skills/docket/modes/ideas.md:19` prints it as the example of what a
premature filing looks like ("I created PL-A1B2, PL-C3D4"). `PL-C3D4`,
`PL-K7QX` and `PL-XXXX` are all mintable; `PL-A1B2` is the only one that is not.

**Why it matters.** An example is copied. `PL-DPY6` is the same defect one file
over, and `PL-GXPP` is what it costs once it has spread: 261 substitutions
across 9 test files, where an id outside the alphabet makes any assertion
resting on it pass vacuously. `citation-drift.md` is the worse of the two here
because it is the document a session reads to learn *what a placeholder is* -
it teaches the false grammar as the convention rather than by accident.

Neither file is reachable by any guard. The fixture-id guard
(`test_every_fixture_id_is_one_the_store_could_mint`) globs
`subprojects/docket/tests/*.py` only (`PL-7922`), and nothing at all scans
`.claude/` or `tools/` for the grammar.

**Done when.** Neither file prints a `PL-` literal outside `store.ID_ALPHABET`,
and `citation-drift.md`'s documented set is one a session can copy without
writing an id the store could not have minted.

**Measured 2026-09-21** (the sweep is in `PL-DPY6`, do not re-run it): 62
non-resolving `PL-` mentions outside `docs/items/` and the two test trees, 9
outside the alphabet. Six of the nine are correct as they stand - `PL-NOPE` in
`model.py:736` and three `PL-M01` in `ROADMAP.md` are prose *about* invalid ids,
and `ROADMAP.md:86` is `PL-GXPP`'s release note quoting the bad literal.
`tools/generator_check.py` was the seventh and is fixed by `PL-DPY6`. These two
are the remainder.

**Not a rename of `PL-K7QX` or `PL-XXXX`.** Both are mintable and both are
load-bearing across 23 uses; the question here is only the one id that is not.
