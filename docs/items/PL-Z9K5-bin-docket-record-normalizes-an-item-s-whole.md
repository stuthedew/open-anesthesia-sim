---
id: PL-Z9K5
title: bin/docket record normalizes an item's whole front matter as well as inserting pr:, so PL-ZYQC's 'pr, not counted' exemption misses and the close-out audit reports files the skill told the session to touch
priority: P3
effort: S
status: dropped
classes: defect, infra
feature: delegation
touches: subprojects/docket/src/docket/store.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-15
closed: 2026-09-21
reason: Fixed by PL-7K8Y (closed 2026-09-20, #785, commit 388d2c50), which landed the narrower of the two fixes this brief proposed: store.insert_field now writes one front-matter field 'leaving every other byte as it was' and cli.py's _write_pr calls it instead of a re-rendering writer, so record no longer reorders a non-canonical file and sanctioned_queue_edit's 'pr, not counted' exemption no longer misses. Verified against the tree 2026-09-21 in PL-C4W8's Gate 2 staleness sweep.
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_pr_insertion_into_non_canonical_front_matter_is_not_counted' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket record normalizes an item's whole front matter as well as inserting pr:, so PL-ZYQC's 'pr, not counted' exemption misses and the close-out audit reports files the skill told the session to touch

**Observed 2026-09-15** on `PL-Y1W6`'s own close-out audit, which had let
`bin/docket record` ride its commit exactly as the `docket` skill directs.
`bin/docket verify --self PL-Y1W6` reported:

```text
NOTE  diff stayed inside `touches` - 2 path(s) outside
        docs/items/PL-F933-doc-check-resolves-a-path-citation-against-the.md
        docs/items/PL-MXSL-doc-check-requires-a-cited-directory-to-exist.md
        docs/items/PL-RD3B-app-controller-py-holds-the-run-s-trace.md - pr, not counted
        docs/items/PL-YMKV-recover-pl-syg4-and-pl-dl4m-which-exist-only-on.md - pr, not counted
```

Four files, one command, two verdicts.

**Mechanism.** `PL-ZYQC` (`#496`) exempts a queue edit that is *only* a `pr:`
insertion, which is what the skill sanctions. `PL-RD3B` and `PL-YMKV` already
carried canonical front-matter field order, so their diffs are one added line
and the exemption fires. `PL-F933` and `PL-MXSL` were written by `#593`'s
session with `closed:` and `verify:` above `classes:`, so `record` re-serialized
them into canonical order - `closed:` and `verify:` move below `added:` - and
the diff is an insertion *plus* a reordering. The exemption sees more than a
`pr:` line and declines.

**Why it matters, and the bound on it.** The harm is small and is the shape
`PL-ZYQC` exists to remove: a session that followed the skill is shown paths it
did not choose to touch, in the one check whose job is to say which paths were
unexpected. Under `--self` that is a `NOTE` rather than a refusal, so nothing
is blocked; a *delegated* review would REJECT, which is what `PL-ZYQC` fixed
for the narrower case. It fires only where an item's stored field order is
already non-canonical, so its frequency is the rate at which sessions write
front matter out of order - unmeasured, and worth counting before deciding the
fix is worth building.

**Two candidate fixes, and they are not equivalent.** Widening the exemption to
"a front-matter-only diff whose sole *semantic* change is an added `pr:`" keeps
the normalization and teaches the audit to read past it. Making `record` write
the `pr:` line without re-serializing the rest removes the reordering
altogether, which also stops `record` producing diff noise on files it was only
asked to add one line to. The second is narrower and does not touch the audit;
the first covers any future field `record` might add. Deciding between them
wants the count above.

Not a duplicate of `PL-ZYQC` (done, `#496`) or of `PL-1KXX` (dropped as
`PL-ZYQC`'s duplicate): both describe the audit having *no* exemption. This is
a residual gap inside the exemption they produced.

**Done when.** A close-out that let `bin/docket record` ride its commit, as the
`docket` skill directs, no longer reports the item files `record` only
re-serialized.

The count the brief asks for is taken first, because it is what chooses between
the two candidate fixes rather than decorating a choice already made: how often
an item's stored front matter is already non-canonical when `record` reaches it
- measurable across the store's history, since that is the only condition under
which the exemption declines. Then either the `pr`-only exemption is widened to
a front-matter-only diff whose sole *semantic* change is an added `pr:`, or
`record` writes the `pr:` line without re-serializing the rest. The second is
narrower, does not touch the audit, and also stops `record` producing diff
noise on files it was asked to add one line to; the first covers any future
field `record` might add. A test pins whichever is chosen against an item whose
stored field order is non-canonical.

**Measured 2026-09-19, as `PL-L4YG` landed `docket set`.** 96 of 1,189 item
files carry a key order `render_item` would not write, so `record` reorders
any of those it reaches. `docket set` writes canonical order at triage, which
shrinks that population from here on and leaves the existing 96 as they are.
