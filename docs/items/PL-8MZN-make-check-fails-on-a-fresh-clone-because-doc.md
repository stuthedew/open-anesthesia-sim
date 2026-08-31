---
id: PL-8MZN
title: make check fails on a fresh clone because doc_check.py reads absent tags as missing releases, not as tags never fetched
status: dropped
added: 2026-08-31
closed: 2026-08-31
reason: duplicate of PL-J295, which shipped the fix inside this same gate; the behaviour this describes no longer exists
---

**Problem.** make check fails on a fresh clone because doc_check.py reads absent tags as missing releases, not as tags never fetched

**Why it matters.**

**Where.**

**Done when.**

**Problem.** A web session's clone arrives with only the tags reachable from
its shallow history. Measured 2026-08-31 in this container: `git tag` listed
`v0.2.5`, `v0.2.6`, `v0.2.7` and nothing older. `tools/doc_check.py`'s
release-tag check reads that as eight broken releases and errors:

```
ROADMAP.md:37: v0.0.1 is marked completed but git holds no tag for it, so no
commit in its span maps to the release it went out in
```

`tests/unit/test_doc_check.py::test_this_repository_is_clean` asserts
`analyze(root).errors == []`, so `make check` goes red with a failure that has
nothing to do with the diff. `git fetch --tags origin` fixes it, and the same
`make check` then passes.

**Why it matters.** Every fresh web session that runs `make check` before
fetching tags pays a diagnosis - eight errors naming a real provenance rule,
reported in the voice of a genuine finding - and the natural reading is that
someone deleted the tags. This is the same class of bug `PL-XCYB` (a
provenance check must refuse to answer in a shallow checkout, not answer
wrongly) fixed on the `docket` side: `vcs.py` learned to say "this checkout
cannot answer" rather than answering wrongly, and `docket check` now prints a
"Not checked" section for exactly this. `tools/doc_check.py` never got the
same treatment.

**Where.** `tools/doc_check.py`, the release-tag check.
`tests/unit/test_doc_check.py::test_this_repository_is_clean`.

**Approach.** Follow `PL-XCYB`'s resolution rather than inventing one: detect
that the checkout cannot answer - `git rev-parse --is-shallow-repository`, or
a fetch refspec that excludes tags - and downgrade the release-tag check to
"not checked" in that case rather than reporting errors. A tag genuinely
missing from a full clone must still be an error; the distinction is whether
the checkout is in a position to know.

**Done when.** `make check` passes in a fresh shallow clone with no tags
fetched, still fails when a release is genuinely untagged in a full clone, and
a regression test covers both.


**Dropped 2026-08-31.** `PL-J295` (the release-train check reads a tag missing
from a shallow clone as a release that was never tagged) is the same defect,
was triaged with the full brief, and is `done` — merged under `v0.2.8`.

Verified rather than assumed: `python3 tools/doc_check.py check` in this
container now reports the shallow-clone case as *not checked* rather than as an
error —

    Not checked (this checkout cannot answer; nothing is claimed):
      release tags: the checkout is a shallow clone, so the 8 releases with no
      tag here cannot be told from a release whose tag was never fetched;
      `git fetch --tags` makes the question answerable

— which is exactly what this item asked for. `make check` no longer fails on a
fresh clone for this reason.

Recorded rather than deleted so the finding is not raised a third time. If the
shallow-clone case ever errors again, that is a regression against `PL-J295`
and belongs on a new item citing it.
