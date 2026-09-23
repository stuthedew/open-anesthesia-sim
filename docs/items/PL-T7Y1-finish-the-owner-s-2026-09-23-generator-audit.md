---
id: PL-T7Y1
title: Finish the owner's 2026-09-23 generator audit: adversarially verify PL-5MYR's claim family, compare every head once for a shared record, and critic the not-generators list and the 09-19 to 09-23 non-product inflow
priority: P2
effort: M
status: ready
classes: housekeeping
touches: docs/items
added: 2026-09-23
payoff: The owner's question 'are we sure we have all the generators?' gets a verified answer: which claim-family members survive, which heads share a record, and whether any family is unrecorded
verify: grep -q 'Verified counts (PL-T7Y1' docs/items/PL-5MYR-generator-identification-reaches-one-level-up.md
---

**Problem.** Finish the owner's 2026-09-23 generator audit: adversarially verify PL-5MYR's claim family, compare every head once for a shared record, and critic the not-generators list and the 09-19 to 09-23 non-product inflow

**Method.** One workflow run, 196 agents, 2026-09-23. Each claim-family
candidate faced three skeptics told to refute it (mechanism, what the fix's
diff changed, and whether a recorded lease would have prevented it); a member
survives when fewer than two refute. The head comparison was proposed from
three angles (record first, reader first, member first), merged, and each group
faced three skeptics (distinct records, shared code only, membership both
ways). Each of `PL-5MYR`'s four not-generators got three critics (store search,
code history, the items' own generator checks). The inflow was swept by eight
date slices and two modal finders, merged, and each candidate family faced
three skeptics, who also judged live or spent. A completeness critic read the
whole result. Its verdict-changing gaps went to a second round, below.

**Round one, claim family.** 15 of `PL-5MYR`'s 19 instance members survive
(`PL-MB2W` is the head, not a member, which is what refuted it). By day, 5, 2,
1, 4 and 3: `PL-3CTW`, `PL-VYSP`, `PL-2BZY`, `PL-61MD`, `PL-MFM4`; `PL-7TVT`,
`PL-N2PP`; `PL-3QM9`; `PL-3W3P`, `PL-8FJK`, `PL-8GV1`, `PL-J16N`; `PL-QP9Z`,
`PL-1MCK`, `PL-KWCY`. Two are open, `PL-MFM4` and `PL-J16N`. Four refuted:

- `PL-RY2R` (2 of 3) and `PL-1X2C` (3 of 3): the file-edit collision mark
  kept one carrier per id (`_Walk.edited`) before the landing test ran. The
  read from touched paths was right; the collapse to one ref was the defect.
- `PL-X3NY` (3 of 3): `stranded` cannot tell a branch with an open pull
  request from an abandoned one. That is a forge fact, not a derived claim.
- `PL-WM46` (3 of 3): verify's batch NOTE regexes every id in a subject
  instead of calling `vcs.leading_ids`. It asks which item commissioned a
  path, not who holds one.

So of the five `PL-5MYR` called open, two survive. The four members
`PL-MB2W`'s branch copy adds, `PL-X3WZ`, `PL-7790`, `PL-N1JK` and `PL-VFJ3`,
all survive 3 of 3. The verified family is 19, three of them open (`PL-MFM4`,
`PL-J16N`, `PL-VFJ3`).
