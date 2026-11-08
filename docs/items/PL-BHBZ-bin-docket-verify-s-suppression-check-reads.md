---
id: PL-BHBZ
title: bin/docket verify's suppression check reads every added line regardless of file type, so prose naming xfail in ROADMAP.md or a release note REJECTs a correct close-out - the .py narrowing PL-VHVJ's sibling assertion check already has at verify.py:160 was never applied at verify.py:1269
priority: P2
effort: S
status: done
classes: defect
feature: verify-false-reject
milestone: v0.5.0
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-19
closed: 2026-09-20
pr: 783
payoff: stops a correct close-out being REJECTed for writing the word xfail in a release note, on the one check bin/docket verify may never relax
verify: grep -q 'def test_a_roadmap_line_naming_xfail_is_not_a_suppression' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify's suppression check reads every added line regardless of file type, so prose naming xfail in ROADMAP.md or a release note REJECTs a correct close-out - the .py narrowing PL-VHVJ's sibling assertion check already has at verify.py:160 was never applied at verify.py:1269

**Read against the tree 2026-09-20, and one line citation in the title is
stale.** The suppression check is at `subprojects/docket/src/docket/verify.py:1336`,
not `:1269` - the title was written against an earlier revision. The two halves
are otherwise as the title says:

```python
# the sibling assertion check, verify.py:161
if path and not path.endswith(ASSERTION_BEARING_SUFFIX):
    return False

# the suppression check, verify.py:1336
suppressed = [line.strip() for _, line in added if _SUPPRESSION_RE.search(line)]
```

`_net_line_changes` yields `(path, line)` pairs, so the path is in hand at the
suppression check and is discarded. `SUPPRESSIONS` holds `"xfail"`,
`"pytest.skip"`, `"@skip"`, `"# type: ignore"` and `"typing.no_type_check"`,
matched as bare substrings.

**Why it matters.** "No suppression added" is one of the four integrity checks
`bin/docket verify` may never relax - `.claude/skills/docket/SKILL.md` makes it
absolute even under `--self`, where four other guards are downgraded to notes.
So it is the check least able to afford a false positive: a session meeting a
`REJECT` on it has been told, in the strongest terms the tool has, that its
branch weakened a test.

Prose is what trips it. An item whose work is to *write about* a suppression -
a release note recording that an `xfail` was removed, a `ROADMAP.md` entry
naming one, a brief in `docs/items/` explaining why a skip is wrong - adds a
line containing the word, and the check reads it as the suppression itself. The
correct close-out then fails on its own documentation.

The cost is not only the one rejection. `PL-69JZ` and `PL-7XTS` record what a
`REJECT` on correct work does to a reader: it trains the block to be skimmed,
which is where a real protected-path failure is also printed. The narrowing the
sibling check already carries removes the false positive without touching what
the guard refuses, because a suppression only suppresses anything in code.

**Done when.** `bin/docket verify` reads added lines for suppressions only in
files whose suffix can carry one, a test drives a `ROADMAP.md` line containing
`xfail` through a close-out and gets no `REJECT`, and a `.py` line containing
one still fails.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". This item is also named in paragraphs quoted in the briefs of `PL-WQF1` and `PL-G21K`.

> - PL-BHBZ (S) `bin/docket verify`'s suppression check reads every added line regardless of file type, so prose naming `xfail` in `ROADMAP.md` or a release note REJECTs a correct close-out
