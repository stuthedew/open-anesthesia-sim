---
id: PL-ZWBK
title: docket next's '{n} open' line takes the same count that PL-4WQS fixed in render.py, so cli.py:715 still understates the queue by the untriaged count
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-09-07
closed: 2026-09-12
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_next_reports_the_same_open_count_as_status' subprojects/docket/tests/test_cli.py
---

**Problem.** docket next's '{n} open' line takes the same count that PL-4WQS fixed in render.py, so cli.py:715 still understates the queue by the untriaged count

**Why it matters.** It is the same defect `PL-4WQS` fixed, surviving in the one
command that is read most often. `render.py` grew `_open_count` - open plus
untriaged - and `status`, `list` and the session digest all call it; `cmd_next`
does not, so `bin/docket next` prints a smaller number than every other view of
the same store. A reader who runs `next` and `status` in one session sees two
counts of one queue and has no way to tell which is the queue.

The direction is the harmful one: it *understates* the backlog, and it
understates it by exactly the count of the items nobody has looked at yet. The
number is small when the untriaged pile is large, which is when it most needs
to be big.

**Done when.** `bin/docket next` reports the same open count as `bin/docket
status`, `bin/docket list` and the session digest against the same store, with a
test asserting the two agree when untriaged items exist.
