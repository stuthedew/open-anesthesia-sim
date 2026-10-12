---
id: PL-MPJL
title: docket roadmap's _subsection_ids reads an id inside an indented code block under an Explicitly out of scope heading as excluded, where it skips one inside a fence; latent
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
payoff: An example id quoted in an indented code block is never read as a milestone excluding real work.
verify: grep -q 'def test_an_id_in_an_indented_code_block_is_not_read_as_excluded' subprojects/docket/tests/test_roadmap.py
---

**Problem.** docket roadmap's _subsection_ids reads an id inside an indented code block under an Explicitly out of scope heading as excluded, where it skips one inside a fence; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.roadmap`. `_subsection_ids` gives `parse_milestones` the ids under a
milestone's `Explicitly out of scope` heading, and leaves out the lines of a
fence or an HTML block (`LITERAL_BLOCKS`), but not those of an indented code
block, which holds a literal too (CommonMark 0.31.2 § 4.4).
`_subsection_declared_ids` reads the same section through its prose statements
and leaves the block out.

```text
### Explicitly out of scope for v9.9.0

An example:

    example: PL-BCDF

- PL-HJKM is out.
```

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16: `parse_milestones` gives `excluded_ids` of `PL-BCDF` and `PL-HJKM`;
with the example in a fence it gives `PL-HJKM` alone. markdown-it-py 4.2.0
reads the indented line as a code block. Latent: `ROADMAP.md` holds no indented
code block.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, under python3 3.13.16:
`parse_milestones` gives `excluded_ids` of `PL-BCDF` and `PL-HJKM` with the
example indented, and `PL-HJKM` alone with it fenced. The omission is
`LITERAL_BLOCKS` in `roadmap.py`, which lacks `markdown.CODE` and is shared by
`_subsection_lines`, `_scope_entries` and `_gate_entries`. Still latent:
`docket.markdown` reads no indented code block in `ROADMAP.md`.

**Generator check.** Not a member of `PL-R417`: the wrong kind of block is
read, and no statement is cut short. `PL-KR6M` and `PL-2B0B` hold the same
misread in other readers. No head's `misread:` states that fact - which
block kinds hold a literal rather than prose, which `markdown.PROSE` already
records - so the three, all open and latent, are a candidate head, put to the
2026-10-11 triage pass's parent session rather than recorded here. Recorded
2026-10-12 as a `spent` head on `PL-KR6M` at its triage, with this item a
member, and the two worked in one pull request.

**Why it matters.** `excluded_ids` is what reports an id as out of a
milestone's scope, so an example id quoted in an indented block would read as
the milestone deciding to exclude real work. `PL-KR6M`, untriaged, names the
same `LITERAL_BLOCKS` omission for the `Required scope` readers, and adding
`markdown.CODE` to it fixes both, so whoever takes either should take both.

**Done when.** `_subsection_ids` leaves an indented code block out as it does a
fence, so an id in an example is not excluded; a test pins the form above.
