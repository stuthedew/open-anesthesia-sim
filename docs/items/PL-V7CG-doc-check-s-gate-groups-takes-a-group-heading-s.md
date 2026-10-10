---
id: PL-V7CG
title: doc_check's _gate_groups takes a group heading's opening line from statement_lines but reads its extent with STATEMENT_RE, whose soft break refuses every ordered marker, so a heading wrapped before a line opening with a number and a full stop that cannot start a list there is cut at that line and check_gate_counts fails a correct frozen list twice; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: a frozen list's group heading wrapped before a year reads whole, so check_gate_counts counts a correct list correctly
verify: grep -qF '"gate groups, a heading wrapped before a year' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _gate_groups takes a group heading's opening line from statement_lines but reads its extent with STATEMENT_RE, whose soft break refuses every ordered marker, so a heading wrapped before a line opening with a number and a full stop that cannot start a list there is cut at that line and check_gate_counts fails a correct frozen list twice; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing the
first half of `tools/doc_check.py`. `_gate_groups`, which feeds
`check_gate_counts` and `check_self_cleared_group`, walks
`docket.markdown.statement_lines`' spans to find each group heading, then reads
the heading's text with `STATEMENT_RE` from its first line, discarding the span
it already holds. `STATEMENT_RE`'s soft break refuses a line opening with any
ordered marker, but CommonMark 0.31.2 lets only a list starting at 1 interrupt
a paragraph (§ 5.2), so a heading wrapped before a year such as `2026.` goes on
past it - `PL-2S1G` recorded that early end as a known cost of the pattern and
left the context to `statement_lines`, which this reader holds and does not
use.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0. A frozen list's group heading over three entries,
its count wrapped onto the line the year opens:

```text
*Stops new debt, each one found after the freeze of 30 September
2026. — three entries:*
```

`check_gate_counts` reported two false errors, the heading saying 2 entries
where 5 follow it, and the headings counting 2 between them where the list holds
5; the same heading on one line reported none. `statement_lines` and markdown-it
both read the heading as one two-line paragraph. Latent: over `ROADMAP.md` all
33 group headings read the same either way.

**Why it matters.** `check_gate_counts` and `check_self_cleared_group` hold each frozen list's group heading to the entries under it, so a heading wrapped before a year fails a correct list with two false errors.

**Generator check.** A member of `PL-R417`: a reader ends a statement at a line
its format carries it past. `PL-VQBY`, a member, fixed where such a heading
opens and left where it ends.

**Done when.** `_gate_groups` reads each heading as `lines[first:end]` of the
span `statement_lines` gave it, pinned by a `gate groups, ` case in
`PL-R417`'s guard that fails on today's reader.
