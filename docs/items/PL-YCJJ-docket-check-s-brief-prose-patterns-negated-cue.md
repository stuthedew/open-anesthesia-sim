---
id: PL-YCJJ
title: docket check's brief-prose patterns - NEGATED_CUE, the prerequisite cue words, PROSE_DEPENDENCY_LIST and PROSE_DEPENDENCY_CONTINUATION, OWN_STATUS and _labels' label words - read a statement's raw text, where a block quote's continuation line carries its >, so inside a quote a negated wait is advised on, a second blocker and a wrapped cue go unread, and a wrapped Decision needed label reads as no question, which makes docket check refuse a needs-decision item that poses one beneath its answer; latent
status: untriaged
feature: one-answer
added: 2026-10-06
---

**Problem.** docket check's brief-prose patterns - NEGATED_CUE, the prerequisite cue words, PROSE_DEPENDENCY_LIST and PROSE_DEPENDENCY_CONTINUATION, OWN_STATUS and _labels' label words - read a statement's raw text, where a block quote's continuation line carries its >, so inside a quote a negated wait is advised on, a second blocker and a wrapped cue go unread, and a wrapped Decision needed label reads as no question, which makes docket check refuse a needs-decision item that poses one beneath its answer; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`checks.py`. `_statements` finds each statement's extent through
`docket.markdown`, correctly, but the patterns then run on the statement's raw
slice of the brief, where a block quote's continuation line keeps its `>`
(CommonMark 0.31.2 § 5.1). The soft break between two words (§ 6.8) is then a
newline, a `>` and a space, which `\s+` does not cross, and `_labels`' joined
label text keeps the `>` too. `SUPERSEDED` already admits `[ \t>]*` after its
line break (`PL-TY1Z`); `NEGATED_CUE`, the cue words `_cue_pattern` builds,
`PROSE_DEPENDENCY_LIST`, `PROSE_DEPENDENCY_CONTINUATION`, `OWN_STATUS` and the
label patterns `ANSWER_LABEL` and `QUESTION_LABEL` read through `_labels` do
not.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0, which gives the quoted and the top-level form of
each input the same inline content. Each input inside a block quote:

```text
> This item is not
> blocked by `PL-BBBB`; it only reads its output.

> **Blocked on `PL-BBBB` and
> `PL-CCCC`.**

> Blocked on `PL-BBBB` and
> on `PL-CCCC`.

> This item depends
> on `PL-BBBB`, which is open.
```

Quoted, `_prerequisite_matches` read `PL-BBBB` for the first, where top level it
reads nothing, so `analyze` advised that the brief names `PL-BBBB` as a
prerequisite it does not list; read `PL-BBBB` alone for the second and third,
where top level it reads both; and nothing for the fourth, where top level it
reads `PL-BBBB`. A quoted own-status phrase wrapped between its two words, at
`ready`, goes unread where top level it is advised on. And under a recorded
`Answered` label at `needs-decision`, a quoted paragraph posing a further
question under a `Decision needed` label wrapped between its two words reads as
no question: `_answered_beneath` returns the answer, and `analyze` raises the
error that the item sits at `needs-decision` beneath a recorded answer -
refusing the layout its own message asks for. Latent: re-running the readers
over the 90 item files holding block-quote lines, with the markers removed,
changed no answer.

The same raw slice reaches `_marks_recommendation`, which does not blank a
list bullet with `_NOT_EMPHASIS` as `_labels` does, so a `*` bullet opens
emphasis: a brief line `* We recommend nothing yet.` reads as a marked
recommendation where the same line led by `-` does not. That half is a misread
within one line rather than across lines, and is folded here because the
accessor below fixes it too. No needs-decision item reads differently today.

**Generator check.** A member of `PL-R417`: readers take a statement's physical
lines, container markers and all, for its text. `PL-WF35` (the cue patterns
across a soft break) and `PL-HKHP` (`_labels`' wrapped labels), both members,
fixed the top-level form only.

**Done when.** A `docket.markdown` accessor yields each statement's text with
its container markers blanked in place, keeping offsets - as `_blanked` does for
code spans - and every pattern above reads it, `_marks_recommendation` included,
pinned by a `brief prose, ` case in `PL-R417`'s guard for each quoted form above
and for the `*` bullet, failing on today's reader.
