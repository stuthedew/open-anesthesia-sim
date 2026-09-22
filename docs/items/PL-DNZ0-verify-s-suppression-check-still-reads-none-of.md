---
id: PL-DNZ0
title: verify's suppression check still reads none of pytest.importorskip, unittest.expectedFailure, self.skipTest, a raised unittest.SkipTest or a conftest collect_ignore, so 'no suppression added' reports none with any of them in the diff
status: untriaged
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
added: 2026-09-22
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

**Done when** each of the five forms is reported, a test pins each, and the
replay count beside `SUPPRESSIONS` is updated.
