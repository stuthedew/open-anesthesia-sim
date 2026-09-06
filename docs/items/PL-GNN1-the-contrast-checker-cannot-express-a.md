---
id: PL-GNN1
title: The contrast checker cannot express a requirement met by either of two channels
priority: P3
effort: S
status: done
classes: defect, infra
feature: presentation-safety
milestone: v0.4.6
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py
added: 2026-09-02
closed: 2026-09-06
verify: uv run pytest tests/unit/test_contrast_check.py && grep -q 'def test_a_requirement_met_by_either_channel' tests/unit/test_contrast_check.py
---

**Problem.** `tools/contrast_check.py`'s `Requirement` models one foreground
against one background, which cannot express "this element is perceivable if
*either* of two channels carries its edge". The agent swatches are exactly that
case, and measuring them one channel at a time gives an answer that is wrong in
both directions:

| Agent | Fill vs page | Border vs page | Perceivable? |
| --- | --- | --- | --- |
| Sevoflurane | 1.27 | 10.70 | yes, by its border |
| Isoflurane | 6.60 | 1.08 | yes, by its fill |
| Desflurane | 6.06 | 1.08 | yes, by its fill |

Every badge has a perceivable boundary. The checker reports sevoflurane as a
shortfall because it measures the fill only, and it would report the other two
as shortfalls if it measured the border only. Neither reading is true.

**Why it matters.** A checker that reports a false shortfall is the failure its
own module docstring names: output that looks authoritative and is not. The
present entry is worse than silence, because it points at `PL-2SVR` as though
there were work to do on a badge that is already legible - and the natural
response to a tracked shortfall is to "fix" something that is not broken.

It also hides the real defect, which the table above makes obvious: the three
badges are legible by *three different accidents*. Nothing in the code says a
swatch must be perceivable, so nothing would catch an agent added later whose
fill is mid-tone and whose foreground is white - invisible by both channels.

**Approach.** Add a requirement kind that takes several candidate foregrounds
against one background and holds the *best* of them to the minimum - the
disjunction the situation actually has. Keep the existing single-pair kind: it
is the right model for text, which has no second channel. Name the swatch case
in the table as "fill or border", so the reason a reader sees is the reason
that holds.

Do not generalise past this. Two-channel disjunction is the case that exists;
an arbitrary boolean requirement language would be the tool deciding judgment,
which the module refuses to do.

**Where.** `tools/contrast_check.py` (`Requirement`, `analyze`,
`format_report`); `tests/unit/test_contrast_check.py`.

**Done when.** The three agent swatches are checked as "fill or border" and all
three pass, the `sevoflurane.fill` shortfall entry is gone, and a test covers a
requirement that passes on its second channel and fails when both are weak.

**Depends on.** Nothing. `PL-2SVR` should be re-read after this lands - most of
what it describes turns out to be already satisfied.
