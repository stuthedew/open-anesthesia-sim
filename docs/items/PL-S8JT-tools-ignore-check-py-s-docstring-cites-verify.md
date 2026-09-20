---
id: PL-S8JT
title: tools/ignore_check.py's docstring cites verify.py's SUPPRESSIONS tuple as its worked example of a type: ignore that is not a directive, and PL-G21K removed it from that tuple - the file now holds the marker in comments, which is the one carrier the tool does count
status: untriaged
added: 2026-09-20
---

**Problem.** tools/ignore_check.py's docstring cites verify.py's SUPPRESSIONS tuple as its worked example of a type: ignore that is not a directive, and PL-G21K removed it from that tuple - the file now holds the marker in comments, which is the one carrier the tool does count

**Where it comes from.** `PL-G21K`'s close-out, 2026-09-20. `tools/ignore_check.py`'s
`directives()` docstring justifies tokenizing over grepping with three worked
examples: "`subprojects/docket/src/docket/verify.py` holds one in a tuple of
suppression markers, `test_release.py` names one in prose, and `test_verify.py`
writes one into a fixture file as a string literal."

`PL-G21K` dropped `# type: ignore` from `SUPPRESSIONS`, so the first example is
no longer true. The other two are untouched and the argument is unaffected -
but the file now carries the marker in comments explaining why it was dropped,
and a comment is the one carrier that tool *does* count as a directive. So the
stale example names the file's new shape as its counter-example.

**No behavior changes.** `verify.py` sits in `subprojects/docket/src`, outside
`TREES`, so `ignore_check.py` never scans it; and `strict = true`'s
`warn_unused_ignores` reads those comments as prose, which `make check` proves
each run. This is a docstring whose example needs replacing, not a defect in
the check.

**Done when** the example names a file that still holds a `type: ignore` in a
tuple or a string, or is replaced by one that does.
