---
id: PL-ZBRB
title: An item can name a prerequisite in prose without declaring it in blocked-by, and nothing notices
priority: P2
effort: S
status: ready
classes: infra
feature: planning-cadence
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
verify: bin/docket check && grep -q 'def test_prose_dependency_without_an_edge_raises_an_advisory' subprojects/docket/tests/test_checks.py
added: 2026-09-04
---

**Problem.** `PL-5WFS` decided that a stated prerequisite is declared with
`blocked-by`. Declaring one is a one-off edit; *noticing* that one is undeclared
is the recurring cost, and it currently falls entirely on a person reading a
brief. Measured across the store on 2026-09-04: **18 items name another item in
a dependency-shaped sentence** ("Depends on `PL-XXXX`", "Blocked on `PL-XXXX`",
"land this after it"), and for **three of them the named blocker was still
open** while the item itself carried no `blocked-by` - `PL-SN2C` -> `PL-VM40`,
`PL-88GQ` -> `PL-X9KD`, `PL-W8DQ` -> `PL-GVXP`. Against 13 declared edges
store-wide.

**Why it matters.** The wrong answer is silent, which is the property
`CLAUDE.md` names as earning attention rather than a filing. `docket next` ranks
on front matter and never reads a body, so it states a sound-looking reason for
an order the briefs contradict, and a session that trusts it either discovers
the dependency on reading the brief - the cheap outcome - or does not, and
redoes work. Every instance so far cost a person to find: `PL-9K7K` found
`PL-ZRSP` -> `PL-DR1Z`, `PL-THVN` found `PL-011` -> `PL-W3DD` and needed a whole
item to say so, `PL-5WFS` found `PL-F52R` -> `PL-DHV7` -> `PL-WB0X`, and
`PL-SN2C` -> `PL-VM40` turned up on a grep while deciding `PL-5WFS`.

**Where.** `subprojects/docket/src/docket/checks.py`, as a grooming advisory
beside the existing ones; tests in `subprojects/docket/tests/test_checks.py`.

**Approach.** Regex the body for an id in a dependency-shaped sentence, and
raise an advisory where that id is **open** and absent from this item's
`blocked-by`. Three properties keep it from becoming noise:

- **Only open blockers.** Most of the 18 hits name a blocker that has since
  closed; those are history, not a defect, and firing on them would make the
  advisory unreadable within a week.
- **Advisory, never an error.** Whether the sentence really states a
  prerequisite - and whether `blocked` is the right word for it - is judgment.
  The check decides only the decidable half: is the id declared.
- **It must be able to reach zero.** An advisory that cannot be cleared trains
  a session to skim past it, and the next one is then read the same way
  (`PL-H7XN`, `PL-G049`).

**The honest limit, which belongs in the item and not discovered later.** This
would have caught three of the four live instances. It would **not** have caught
`PL-011` -> `PL-W3DD`, because neither brief mentions the other - that
dependency was visible only to someone who understood that re-keying the record
invalidates a memory measurement, and no regex reaches it. Do not let the check
imply the store is clean; the advisory says what it looked at.

**Done when.** `docket check` raises an advisory for an item whose body names an
open item in a dependency-shaped sentence that its `blocked-by` does not carry;
the advisory names the item, the blocker and the sentence; closed blockers do
not fire; and the check's own docstring states what it cannot see.
