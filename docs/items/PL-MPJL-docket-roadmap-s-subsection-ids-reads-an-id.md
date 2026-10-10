---
id: PL-MPJL
title: docket roadmap's _subsection_ids reads an id inside an indented code block under an Explicitly out of scope heading as excluded, where it skips one inside a fence; latent
status: untriaged
added: 2026-10-10
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

**Generator check.** Not a member of `PL-R417`: the wrong kind of block is
read, and no statement is cut short. `PL-KR6M` and `PL-2B0B` hold the same
misread in other readers.

**Done when.** `_subsection_ids` leaves an indented code block out as it does a
fence, so an id in an example is not excluded; a test pins the form above.
