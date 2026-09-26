---
id: PL-DNZ0
title: verify's suppression check still reads none of pytest.importorskip, unittest.expectedFailure, self.skipTest, a raised unittest.SkipTest or a conftest collect_ignore, so 'no suppression added' reports none with any of them in the diff
priority: P2
effort: S
status: done
classes: defect, infra
feature: verify-false-reject
milestone: v0.5.12
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the first 2026-09-23 triage pass
added: 2026-09-22
closed: 2026-09-25
pr: 1033
payoff: a session that silences a test with self.skipTest, a raised SkipTest, expectedFailure, importorskip, or a conftest collect_ignore or pytest_ignore_collect gets it put in front of a reviewer, instead of the clean 'no suppression added: none' an integrity check --self may never relax now prints
verify: grep -q 'importorskip' subprojects/docket/tests/test_verify.py && grep -q 'expectedFailure' subprojects/docket/tests/test_verify.py && grep -q 'skipTest' subprojects/docket/tests/test_verify.py && grep -q 'SkipTest' subprojects/docket/tests/test_verify.py && grep -q 'collect_ignore' subprojects/docket/tests/test_verify.py && grep -q 'pytest_ignore_collect' subprojects/docket/tests/test_verify.py
---

**Problem.** After `PL-5B88`, `SUPPRESSIONS` in
`subprojects/docket/src/docket/verify.py` reads pytest's `skip` and `skipif`
decorators, its imperative `pytest.skip`, `xfail` in every form, and the
standard library's `unittest.skip` family. Five standard ways to disable a test
still match no entry, so `no suppression added` reports `none` with any of them
in the diff:

| form | what it does |
| --- | --- |
| `pytest.importorskip("mod")` | skips the module when the import fails |
| `@unittest.expectedFailure` | unittest's `xfail` |
| `self.skipTest("why")` | unittest's imperative skip |
| `raise unittest.SkipTest("why")` | the exception both frameworks skip on |
| `collect_ignore = ["test_x.py"]` in a `conftest.py` | drops a file from collection |

**Measured 2026-09-22** with the replay `PL-5B88` recorded beside
`SUPPRESSIONS`: none of the five appears on any added line of `main`'s 1,115
non-merge commits, in any suffix the check reads, after `strip_non_code`. So
adding them would refuse no work in this history.

**Why it matters.** It is the same silent `none` that `PL-5B88` removed for the
commonest forms, here for the rarer ones, and it falls under the floor in
`.claude/rules/apparatus-standard.md`: an answer must be true, or must say what
it could not read. The docket README now names these five as unread, so the
documentation is honest, but the report line itself still is not. They were
left out of `PL-5B88` because that item named the decorators, and each form
wants its own test pin, which `CLAUDE.md`'s fix-now door refuses.

**Approach - recommended.** Add one entry each: `importorskip`,
`expectedFailure`, `skipTest`, `SkipTest` and `collect_ignore`. The existing
rule anchors each on the left, and each is distinctive enough that the open
right-hand side finds only what it should (`collect_ignore_glob` included).
Add one parametrize case each to `test_a_pytest_mark_skip_is_a_suppression`,
update the README's "Not read" sentence and the comment above `SUPPRESSIONS`,
and rerun the replay. `importorskip` is the one form with a common legitimate
use, an optional dependency. The check would put it in front of a reviewer the
same way it now does the `bash` guard `PL-5B88` counted. That is the check
doing its job, not a false positive.

**Not a marker's job, noted so it is not lost.** A deselection in `addopts`,
such as `--deselect` or a `-k` or `-m` filter, is read by neither check when it
sits in a `setup.cfg` or `pytest.ini`. `gate_paths`' defaults in
`subprojects/docket/src/docket/config.py` name `pyproject.toml` alone, and `-k`
and `-m` are too generic to match as text. If a remedy is wanted, it is adding
those files to the defaults, which is a different file and a different decision
from this item. This project has neither file.

**Done when** each of the five forms, and the `pytest_ignore_collect` hook
below, is reported, a test pins each, and the replay count beside
`SUPPRESSIONS` is updated. The approach puts the cases in
`test_a_pytest_mark_skip_is_a_suppression`'s parametrize list.

**A sixth form, found at triage 2026-09-23.** `pytest_ignore_collect` is the
hook form of `collect_ignore`: a `conftest.py` function that returns `True` to
drop a path from collection. The docstring in the installed pytest 9.1.1 reads
"Return ``True`` to ignore this path for collection." `collect_ignore` does not
match it, because the words run in the other order, so the five entries above
would still report `none` with it in the diff. It is distinctive, it appears
nowhere on `origin/main`, and it is on no added line in the history. One more
entry and one more case finish the family at the same size, and leaving it out
would make it the next capture.

**Reproduced 2026-09-23.** A scratch script called `is_suppression_line` from
the shipped `verify.py` on one line of each form. It returned `False` for all
five: `pytest.importorskip("numpy")`, `@unittest.expectedFailure`,
`self.skipTest("why")`, `raise unittest.SkipTest("why")`, and
`collect_ignore = [...]` in a `conftest.py`. The `@pytest.mark.skip` control
returned `True`. `SUPPRESSIONS` holds six entries and none of the five. The
history claim above holds: on `origin/main`, the names occur in `.py`, `.toml`,
`.cfg` and `.ini` files only on the three comment lines `#910` put above
`SUPPRESSIONS`, which `strip_non_code` blanks. None of the six names appears in
`subprojects/docket/tests/test_verify.py` yet. `strip_non_code` also blanks
quoted and backtick spans, so the new cases' strings are not read as
suppressions on this item's own close-out. That holds only while a docstring
names each form inside backticks, as the existing test's already does.

**Generator check.** This is the unfinished tail of `PL-5B88`, a defect in what
exists, and not an instance of `PL-G21K`'s mechanism filed after that head
closed. It was split off in `PL-5B88`'s own close-out (`#910`, 917ecfaa), and
`docket new` recorded it there as a recurrence. `PL-G21K`'s mechanism is false
positives: intent read into diff text, so each fix uncovered the next
misreading. Its ratified resolution kept a marker list on purpose. These forms
are that list's known remainder, drawn from the frameworks' documented ways to
skip, fail or ignore a test. That set is small and fixed, so the tail is
bounded, not generating. It widens an existing list and an existing test, so
the pause on new mechanisms does not reach it.

**Worked.** Each new case keeps the existing test's shape, so its marker is
one line above `def test_b()` in `tests/test_thing.py`: the imperative
`self.skipTest` and the raised `SkipTest` sit at module level there, and the two
collection forms are not in a `conftest.py`, since the check reads a line's
text and its file's suffix and never the file's name. The marker strings are
mine: `numpy = pytest.importorskip("numpy")`, `@unittest.expectedFailure`,
`self.skipTest("broken")`, `raise unittest.SkipTest("broken")`,
`collect_ignore = ["test_thing.py"]` and
`def pytest_ignore_collect(collection_path, config):`. With the six entries
reverted, those six cases fail and the five older ones pass. The replay was a
scratch script mirroring `_net_line_changes`'s per-file fold over each
non-merge commit on `origin/main`, 1,237 of 1,354: the six match no added line,
and the six older entries still match only the `bash` guard. I also named
`collect_ignore_glob` in `_SUPPRESSION_RE`'s comment on the open right-hand
side, and added a paragraph to the test's docstring naming the six forms in
backticks, so the item's own close-out does not read them as suppressions.
