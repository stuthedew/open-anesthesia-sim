---
id: PL-XQGH
title: verify's assertion check anchors on with, so the parenthesized multi-manager form leaves pytest.raises on a line of its own that matches nothing
priority: P3
effort: S
status: dropped
classes: defect, infra
feature: verify-assertion-check
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
blocked-by: PL-4W2L
added: 2026-09-19
closed: 2026-09-22
reason: superseded by PL-4W2L's decision (2026-09-22): the check parses assertions with ast, which reads every context-manager item wherever the formatter puts it; the parenthesized form is a named test in PL-4W2L's done-when
verify: grep -q 'def test_a_parenthesized_multi_manager_with_is_an_assertion_removed' subprojects/docket/tests/test_verify.py
---

**Problem.** verify's assertion check anchors on with, so the parenthesized multi-manager form leaves pytest.raises on a line of its own that matches nothing

**Where.** `ASSERTION_RE` in `subprojects/docket/src/docket/verify.py`. Its
third alternative, added by `PL-QJQL`, anchors on the `with` keyword exactly as
the first anchors on `assert` - both open their statement, so the line a
whole-statement deletion puts in the diff is the line that carries them. The
parenthesized multi-manager form breaks that correspondence: `with (` opens the
statement and each context manager sits on a line of its own, so the line
carrying `pytest.raises(ValueError),` carries no `with` and matches nothing.
Deleting such a block puts both lines in the diff and neither is reported.

**Not an oversight; a scope decision, recorded so it can be revisited.**
Measured 2026-09-19 with `ast` over the whole tree: **zero** `with` statements
with two or more context managers, of any kind, in 97,687 lines. So the shape
cannot occur today, and covering it would have been the widest rule the hazard
could motivate rather than the narrowest that removes it -
`.claude/rules/expert-review.md` § "Say what would falsify it". The residual is
named in `is_assertion_line`'s docstring rather than left silent.

**What would falsify the decision.** One multi-manager `with` wrapping a
`pytest.raises` - combining it with `caplog.at_level` or `monkeypatch.context`
is ordinary enough - formatted past `ruff`'s 100-character line length, which is
what makes `ruff format` emit the parenthesized form. That is a condition on the
tree rather than an argument, so it is checkable: `ast` for a `With` node with
`len(node.items) > 1`.

**Why it matters, and why it is P3 rather than higher.** `no existing assertion
removed` is one of the four integrity checks `verify --self` will not relax, and
a blind spot in it lets a delegated or self-audited diff delete a rejection
guard and pass the audit. But the blind spot is unreachable while the tree holds
no multi-manager `with`, so nothing is currently at risk - this is a latent risk
with a nameable trigger, not a live defect.

**Done when.** Either the alternative covers a context-manager item on a line of
its own, with `subprojects/docket/tests/test_verify.py` driving it and the prose
direction still held; or the shape is confirmed still absent and the item is
dropped with that measurement as its `reason`.
