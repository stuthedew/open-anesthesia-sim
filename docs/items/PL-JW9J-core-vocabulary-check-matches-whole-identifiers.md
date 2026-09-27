---
id: PL-JW9J
title: core_vocabulary_check matches whole identifiers because two live names would have failed a substring rule, and since PL-6KNM neither exists: decide whether to tighten
priority: P3
effort: S
status: dropped
classes: defect
feature: dev-tooling
touches: tools/core_vocabulary_check.py, tests/unit/test_core_vocabulary_check.py
added: 2026-09-14
closed: 2026-09-27
reason: Not tightened (project owner, 2026-09-27, ratified, over a substring rule): a substring rule would newly flag 0 identifiers under src/anesthesia_sim/core/ for the 7 names RETIRED_NAMES holds, counted with the tool's own identifiers() reader on 2026-09-27 and retaken on main after #1171; the only substring hits anywhere are 2 legitimate identifiers in tests/, which the rule does not read. The count and the script to retake it are in this brief's design round.
---

**Problem.** core_vocabulary_check matches whole identifiers because two live names would have failed a substring rule, and since PL-6KNM neither exists: decide whether to tighten

**Verified 2026-09-14.** `tools/core_vocabulary_check.py:46` states the rule in
the tool's own words - "**Matching is on the whole identifier, never on a
substring.**" - and gives the reason it was written that way: two live names
would have failed a substring rule. `PL-6KNM` renamed one of them and the item
records that neither now exists, so the constraint the rule was relaxed for is
gone.

**Why it matters.** A whole-identifier rule cannot see a retired name embedded
in a longer one, which is the shape the retirements actually take - a local, a
keyword argument, a docstring phrase - so the check passes over exactly the
residue a rename leaves behind. Against that, tightening to a substring rule
buys nothing if the population it would newly catch is empty, and costs a false
positive on every legitimate identifier that contains a retired word.

**Decision needed.** Whether to tighten `core_vocabulary_check` from
whole-identifier matching to substring matching now that `PL-6KNM` has removed
the two names the relaxation was written for.

`.claude/rules/expert-review.md` requires the number that would make tightening
wrong to be named and then counted before the proposal is made, and this item
was filed without it. The count to take is on `src/anesthesia_sim/core/`, under
the retired-name list the tool already holds: how many *additional* occurrences
a substring rule would flag, and how many of those are real residue rather than
an unrelated identifier that happens to contain the word. Tightening is right
only if the second number is a clear majority of the first.

- **Tighten.** Right if the substring rule finds real residue and few or no
  false positives.
- **Leave it, and record why.** Right if the additional population is empty or
  is dominated by legitimate identifiers - and then this item closes as
  `dropped` with the count as its reason, so the question is not re-raised.

[superseded 2026-09-27: the count was taken, § "Design round 2026-09-27"]
Whoever answers it should take the count first; the answer follows from it
rather than from an argument.

**Done when.** The count above has been taken and acted on: either
`tools/core_vocabulary_check.py` matches on substrings with
`tests/unit/test_core_vocabulary_check.py` covering a retired name embedded in a
longer identifier, or this item is closed `dropped` with the count as its
reason.

## Design round 2026-09-27: the count, and the recommendation

**The count, taken 2026-09-27** with the tool's own `identifiers()` reader,
so it sees exactly what the rule sees - names bound or read in code, never
docstrings, comments or strings - over the 17 modules under
`src/anesthesia_sim/core/`, for the seven names `RETIRED_NAMES` holds:

| Population | Whole-identifier hits (the rule today) | Additional substring hits | Of those, real residue |
| --- | --- | --- | --- |
| `src/anesthesia_sim/core/`, the tree the rule reads | 0 | **0** | 0 |
| `tests/`, which the rule deliberately excludes | 0 | 3, at 2 sites | 0 |

A token-bounded variant - the retired name as a run of whole `_`-separated
words inside a longer identifier, the shape a prefixed local or keyword
argument would take - finds the same 0 in `core/`, and `grep` over `core/`
for the seven names finds no docstring, comment or string carrying one. The
two `tests/` sites are `expected_concentration_fraction`, a local in
`tests/reference/test_circuit_wash_in.py` naming an expected value, and the
test `test_a_concentration_fraction_reaching_the_mac_awake_band_is_refused_by_mypy_alone`
in `tests/unit/test_formatting.py`: both legitimate, both exactly the false
positive the brief's cost side predicted, and both outside the tree the rule
reads.

The tool's docstring recorded the same measurement on 2026-09-14 ("no live
identifier contains a retired name as a substring"). Thirteen days of `core/`
edits later it still holds, and the residue the brief hypothesised - a local
or a keyword argument left behind by a rename - has not appeared once.

Reproducible from a bare checkout, and the count to retake if this is ever
reopened:

    python3 - <<'PY'
    import sys; sys.path.insert(0, "tools")
    from pathlib import Path
    import core_vocabulary_check as cvc
    retired = [r.name for r in cvc.RETIRED_NAMES]
    hits = [(p.as_posix(), i.line, i.name)
            for p in Path("src/anesthesia_sim/core").rglob("*.py")
            for i in cvc.identifiers(p.read_text(), p.as_posix())
            for n in retired if n in i.name and n != i.name]
    print(len(hits), hits)
    PY

**Q1. Tighten to substring matching?** **Recommendation: no - leave the
whole-identifier rule, and close this item `dropped` with the count above as
its `reason`.** The brief's own test is that tightening is right only if real
residue is a clear majority of what a substring rule would newly flag, and
the additional population is empty; the only substring hits anywhere in the
tree are two legitimate identifiers. A substring rule today would change no
verdict and would add a false-positive class - every qualified identifier
containing a retired word - that the whole-identifier rule cannot produce,
which is `CLAUDE.md`'s "a check earns its place every run" failing at birth.
`tests/unit/test_core_vocabulary_check.py`'s
`test_a_live_name_that_merely_contains_a_retired_one_passes` stays as the pin
on the rule's shape.

*What would reopen it:* a retirement followed by an observed residue of the
embedded shape in `core/`. Then the script above is run again and this brief
is the record to cite. The paragraph of `tools/core_vocabulary_check.py`'s
docstring that sends a reader here for the question can gain one clause saying
it was answered, if the thread that drops this item is already editing that
file; it is not worth a change of its own.

**Whose answer this is.** By `.claude/skills/docket/modes/triage.md`'s test -
an item answerable by running a measurement is a session's - the count decides
this, and the item sat at `needs-decision` only because nobody had taken it.
It is put to the project owner here because the design round was asked to put
every open question, and a one-word answer closes it.

## Answers 2026-09-27

**Answered 2026-09-27: Q1 ratified - not tightened** (project owner,
2026-09-27, ratified, over tightening to a substring rule). The
whole-identifier rule stays, and this item closes `dropped` with the count in
§ "Design round 2026-09-27: the count, and the recommendation" as its
`reason`. That is one `bin/docket set PL-JW9J --status dropped --reason ...`
write by the thread that takes it, and no code changes.
