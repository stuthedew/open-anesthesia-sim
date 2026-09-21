---
id: PL-L609
title: tools/fixture_id_check.py cannot see an id spelled with underscores as a keyword argument, which is how PL-AAAA-open.md reached the doc_check fixtures
status: untriaged
feature: one-id-grammar
added: 2026-09-21
---

**Problem.** tools/fixture_id_check.py cannot see an id spelled with underscores as a keyword argument, which is how PL-AAAA-open.md reached the doc_check fixtures

**Problem.** `tools/fixture_id_check.py` matches `(?<![A-Za-z0-9])PL-[A-Za-z0-9]+`
and so cannot see an id written with an underscore separator. That form exists
because a fixture id has to be a keyword argument:
`tests/unit/test_doc_check.py`'s `_items(root, **briefs)` writes
`items / f"{name.replace('_', '-')}.md"`, so `PL_AAAA_open=` produced
`PL-AAAA-open.md` - an id outside `store.ID_ALPHABET` as a fixture *filename*,
which is exactly what the check exists to refuse.

**Why it matters.** It is the same vacuous-assertion hazard as `PL-GXPP`, in a
form the new guard is blind to, in the one file that has the helper making it
convenient. Four instances existed; `PL-7922` renamed them to `PL_8888_open`
while adding the check, so nothing is currently wrong and nothing would say so
if it were.

**Why it was not simply widened.** Adding `PL_` to the candidate pattern would
reject ordinary module constants - `PL_PREFIX`, `PL_RE`, `PL_ITEMS` - for a
reason that has nothing to do with ids, which is the false-positive class
`CLAUDE.md` retires a check for. Measured 2026-09-21: 4 `PL_[A-Za-z0-9]{3,}`
tokens in the whole repository, all of them this one fixture, so the widening
would have been free *today* and the risk is entirely about what gets written
next.

**Worth deciding when this is worked.** Three candidates, cheapest first: read
the kwarg name only where it is passed to a helper that converts it to a
filename (a narrow AST rule, no false positives, one file); or have `_items`
itself refuse a name outside the alphabet (moves the guard to the helper, where
nothing else can reach it); or change the helper to take a mapping so the ids
stay hyphenated literals the existing scan already sees. The third is the only
one that removes the form rather than policing it.
