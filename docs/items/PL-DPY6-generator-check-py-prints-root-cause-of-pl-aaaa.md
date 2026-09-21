---
id: PL-DPY6
title: generator_check.py prints 'root-cause-of: PL-AAAA, PL-BBBB, PL-CCCC' as the example to copy, and docket check rejects all three as not a valid item id
priority: P3
effort: S
status: done
classes: infra
feature: one-id-grammar
milestone: v0.5.1
touches: tools/generator_check.py, tests/unit/test_generator_check.py
added: 2026-09-21
closed: 2026-09-21
pr: 859
payoff: a session copying the root-cause-of example writes an id the store can actually mint, and the advisory agrees with docket set about what the field's placeholders are
verify: uv run pytest tests/unit/test_generator_check.py -q -k test_every_id_the_advisory_prints_is_one_the_store_could_mint
---

**Problem.** `tools/generator_check.py` closed its advisory with
`` `root-cause-of: PL-AAAA, PL-BBBB, PL-CCCC` `` as the line to copy.
`store.ID_ALPHABET` is Crockford base32 *minus the vowels*, so `PL-AAAA` is an
id `new_id` can never mint and `ID_PATTERN` never matches - the exact literal
`PL-GXPP` had removed from the test tree in 261 substitutions the same day.

**The title is wrong on two of the three, and the correction matters.**
Measured 2026-09-21: `PL-BBBB` and `PL-CCCC` are inside the alphabet and
perfectly mintable; only `PL-AAAA` is not. And `docket check` rejects all three
for a different reason than the title gives - `model.root_cause_faults` holds
the named ids to *existing in the store*, never to the grammar, so the error is
"names PL-AAAA, PL-BBBB, PL-CCCC, which no item in this store carries". That is
correct behaviour for a placeholder and is not the defect. A session reading the
title as filed would go looking for a grammar check on `root-cause-of:` that
does not exist anywhere.

**Why it matters.** An example exists to be copied. This one
taught that `A` is in the alphabet, which is how a fixture outside it gets
written - and a fixture outside the alphabet makes any assertion resting on it
pass vacuously, which is the trap `PL-GXPP` documents and `PL-R77L` measured.
`generator_check`'s own `ID_RE` is `PL-[A-Z0-9]{4}`, looser than the store's, so
nothing in the script would ever have objected to its own example (`PL-KYW3`).

**Done when.** `tools/generator_check.py` prints no `PL-` literal outside
`store.ID_ALPHABET`, a test holds it there against `store.ID_RE` rather than a
restatement of the grammar, and that test is red against the old literal.

**Fix.** The placeholders are now `PL-XXXX, PL-YYYY, PL-ZZZZ`, which is not an
invention: `docket set --root-cause-of` already prints exactly that triple as
its metavar for the same field (`cli.py:3177`), and the swept tree uses
`PL-XXXX` in 18 places across `README.md`, `CONTRIBUTING.md`, `docs/MODEL.md`,
`cli.py`, `model.py`, `verify.py`, `branch_id_check.py` and `doc_check.py`. Two
placeholder sets for one interface was the smaller half of the defect.

**Regression test.**
`test_every_id_the_advisory_prints_is_one_the_store_could_mint` runs the script
over a fixture store and holds every `PL-`-shaped literal in its *output* to
`store.ID_RE`, imported rather than restated - a fourth copy of the grammar is
the defect next door. Mutation-checked both ways: with the fixtures clean,
restoring the old literal turns it red and the fix turns it green.

**Rider (fix-now, own commit).** `tests/unit/test_generator_check.py` carried
`PL-AAAA` as a *fixture* id in 20 places, so the file asserting the advisory's
behaviour reproduced the defect it was asserting about. Renamed to `PL-8888`,
following `PL-GXPP`'s own substitution; the prose mention inside the new test's
docstring is left, as the guard in `subprojects/docket/tests` also leaves
docstrings alone. `PL-BBBB`, `PL-CCCC`, `PL-DDDD`, `PL-C000` and `PL-K000` were
already mintable and are untouched.

**Found and not fixed here.** A sweep of every `PL-` literal outside
`docs/items/` and the two test trees found 62 non-resolving mentions, 9 outside
the alphabet. Of those, `PL-NOPE` in `model.py:736` and the three `PL-M01` in
`ROADMAP.md` are prose *about* invalid ids and are correct as they stand, and
`ROADMAP.md:86` is `PL-GXPP`'s own release note quoting the bad literal. The two
live ones are `PL-A1B2` in `.claude/skills/docket/modes/ideas.md:19` and
`.claude/rules/citation-drift.md:103` - the second of which documents the
project's placeholder set and lists a non-mintable id among them. Both are
outside this item's `touches`; filed separately.
