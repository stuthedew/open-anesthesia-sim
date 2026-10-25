---
id: PL-GTH6
title: Which run a displayed value belongs to once two runs are shown: eight members from 2026-09-06 to 2026-09-21, none since
priority: P3
effort: S
status: done
classes: defect
feature: defect-review-2026-10
touches: docs/items
added: 2026-10-25
closed: 2026-10-25
pr: 1783
payoff: the audit records that run attribution was one mechanism behind eight defects, so a ninth is recognised as a recurrence
verify: grep -qE '^generator: spent' docs/items/PL-GTH6-*.md
root-cause-of: PL-1XPX, PL-25DD, PL-MN4J, PL-JVHL, PL-4KZD, PL-LHBY, PL-TSZM, PL-C3GS
generator: spent - no member filed since 2026-09-21 across 34 days of compare-mode changes (inferred from the store); a new member makes it live
misread: Which run a displayed value belongs to once two runs are shown
---

**Problem.** Which run a displayed value belongs to once two runs are shown: eight members from 2026-09-06 to 2026-09-21, none since

**The fact the members misread.** Once a case shows two runs, every displayed value belongs to one of them, and the display must say which. Each member drew or named a value without its run:

- `PL-1XPX` and `PL-25DD`: displayed values carried no run once two runs were shown.
- `PL-MN4J`: the hover named the agent and the instant but not the run.
- `PL-JVHL`: the hover answered for an arbitrary run when two runs' points lay inside its radius.
- `PL-4KZD`: a panel drew every run's standings from `snapshots[0]`.
- `PL-LHBY`: the marks panel drew the reference run's standings as the case's.
- `PL-TSZM`: banners in the shared notice column carried no run name.
- `PL-C3GS`: a panel's record was not tied to its run once two runs shared a sidebar column.

**Why it is spent.** No member has been filed since 2026-09-21, across 34 days in which the compare mode kept changing. That is inferred from the store, not traced to one structural fix. A new member makes this head live again.

**Why it matters.** The audit of where product defects come from needs each shared cause recorded, so that a recurrence is recognised as one.

**Done when.** This head records its members and why it is spent.

**Generator check.** Recorded for the audit by `PL-R4Y2`'s defect review.
