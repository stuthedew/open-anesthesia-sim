---
id: PL-5B88
title: verify's suppression check misses @pytest.mark.skip and @pytest.mark.skipif, the two commonest ways a pytest test is disabled: @skip needs its @ against the name and pytest.skip needs its halves adjacent, so the check reports none while a disabled test sits in the diff
priority: P2
effort: S
status: done
classes: defect, infra
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
added: 2026-09-20
closed: 2026-09-22
payoff: makes the check able to fail on the two decorators that actually disable a pytest test, which it has never been able to report
verify: grep -q 'def test_a_pytest_mark_skip_is_a_suppression' subprojects/docket/tests/test_verify.py
recurrences: 2026-09-22 PL-DNZ0
---

**Problem.** verify's suppression check misses @pytest.mark.skip and @pytest.mark.skipif, the two commonest ways a pytest test is disabled: @skip needs its @ against the name and pytest.skip needs its halves adjacent, so the check reports none while a disabled test sits in the diff

**Problem.** `SUPPRESSIONS` in `subprojects/docket/src/docket/verify.py` holds
`pytest.skip` and `@skip`, and neither matches the two forms that actually
disable a pytest test:

| line | reported today |
| --- | --- |
| `@pytest.mark.skip(reason="broken")` | no |
| `@pytest.mark.skipif(sys.platform == "win32", ...)` | no |
| `@unittest.skip("x")` | no |
| `@pytest.mark.xfail` | yes, via `xfail` |
| `pytest.skip("no")` | yes |
| `@skipif(True)` | yes |

`@skip` requires the `@` against the name, which `@pytest.mark.skip` separates;
`pytest.skip` requires its two halves adjacent, which `.mark.` separates. So
the two markers catch the imperative call and a bare decorator almost nobody
writes, and miss the decorator everybody does.

**Measured on the module, before and after `PL-G21K`'s edit**, by importing
each version of `verify.py` and calling `is_suppression_line` on the lines
above. The result is identical on both, so this is a standing gap rather than
one that edit introduced.

**Why it matters.** This is the first of `CLAUDE.md`'s three
compounding-friction tests - it gives a wrong answer silently. `no suppression
added` is one of the four integrity checks `--self` may never relax, and it
reports `none` with `@pytest.mark.skip` in the diff. A check that cannot fail
on the hazard it names is worse than no check, because the report says the
question was asked.

**It also weakens the argument that kept the check.** `PL-G21K` refused
retiring it outright on the deterrence reading - that zero hits across
`main`'s 1,004 non-merge commits might mean nobody writes `xfail` or
`pytest.skip` *because* the check
is there. A deterrent that does not fire on the common form deters less than
the zero count suggests, so this wants settling before that reading is leaned
on again.

**Approach.** Add `pytest.mark.skip` to `SUPPRESSIONS`, which covers
`@pytest.mark.skip` and `@pytest.mark.skipif` in one entry with the existing
open-right-hand-side rule, and consider `unittest.skip` alongside it. Then
re-run `PL-G21K`'s replay over `main` and record what the widened list matches:
a widening owes the same count a narrowing does, in the other direction - not
"how many does it catch" but how many of them are real, since `.mark.skip`
inside prose is the false positive `strip_non_code` now handles for `.py` and
does not handle for `.toml`, `.cfg` or `.ini`.

**Done when** `@pytest.mark.skip` and `@pytest.mark.skipif` are reported, the
count of what the widened matcher flags across `main` is recorded beside
`SUPPRESSIONS`, and a test pins each form.

## Worked 2026-09-22

**`mark.skip` and `unittest.skip` joined `SUPPRESSIONS`.** I used `mark.skip`
rather than the `pytest.mark.skip` the approach named. It reads both
decorators, and it also reads `@mark.skip` after `from pytest import mark`,
which is why the assertion check matches a bare `raises`. On this history the
two entries flag the same lines. `unittest.skip` reads `skip`, `skipIf` and
`skipUnless`.

**The count, run against the shipped module** with `PL-G21K`'s replay over
`main`'s 1,115 non-merge commits (of 1,232):

| | lines |
| --- | --- |
| flagged by the list as it stood | 0 |
| flagged by the list as it now stands | 1 |
| of those, prose or a string | 0 |

The one line is `@pytest.mark.skipif(shutil.which("bash") is None,
reason="bash is not installed")` in `tests/unit/test_stop_hook_patch.py`, from
`PL-WW08`'s `#300`. It is a real directive: an environment guard, not a test
silenced to reach green. A branch adding it now gets `REJECT` and goes to a
reviewer, which is one refusal in 1,115 commits, on a line a reviewer should
see. No `.toml`, `.cfg` or `.ini` line matched either way, so the gap the
approach flagged, `strip_non_code` not covering those suffixes, costs nothing
on this history. The count is also recorded in the comment beside
`SUPPRESSIONS`.

**Pinned:** `test_a_pytest_mark_skip_is_a_suppression`, parametrized over
`skip`, `skipif`, the imported `@mark.skip`, a module-level `pytestmark` and
`@unittest.skip`. Each case asserts that the decorator line is exactly what the
check reports. All five failed with `detail='none'` before the fix. With the
decorators read, the deterrence reading that `PL-G21K` kept the check on no
longer rests on a check that cannot see the commonest form.

**The rest of the family is `PL-DNZ0`**: `pytest.importorskip`,
`unittest.expectedFailure`, `self.skipTest`, a raised `unittest.SkipTest` and
`collect_ignore`. None of them appears on an added line in that history
either. The docket README names them as unread, so `none` is read against a
stated list.
