---
id: PL-WVJ0
title: The docket skill says bin/docket show prints no placement at all, but PL-J790 added the plan: line to show in v0.4.18, so a session is sent to look up what the command already prints
priority: P2
effort: S
status: ready
classes: docs, defect
touches: .claude/skills/docket/SKILL.md
added: 2026-09-19
verify: ! grep -qF 'prints no placement at all' .claude/skills/docket/SKILL.md
---

**Problem.** The docket skill says bin/docket show prints no placement at all, but PL-J790 added the plan: line to show in v0.4.18, so a session is sent to look up what the command already prints

**Where.** `.claude/skills/docket/SKILL.md:517`, closing the "Every item you
offer carries its relation to the gate" section: *"`bin/docket wave` prints the
gate's open entries by id and settles membership; `bin/docket show` prints no
placement at all, so an item reached by name — the way the owner usually starts
one — carries no relation until you go and look."*

`cmd_show` has printed one since `2242daf` (`PL-J790`, state an item's relation
to the current gate wherever it is recommended, #528, shipped in v0.4.18). It
calls `placement_line` and prints `  plan: ...` for every item, including the
"placed by no section" case - which is exactly the relation the sentence says a
session has to go and find for itself. Observed 2026-09-19 while working
`PL-C97K` (print the generator that explains a member on `docket show`):

    $ bin/docket show PL-8LDF
      plan: placed by no section of v0.5.0 — the case you can branch - it ranks on its band alone

**Why it matters.** It is the apparatus telling a session something untrue
about its own commands, which `.claude/rules/apparatus-standard.md`'s floor
refuses: the answer has to be true or has to say what it could not read. The
cost is a session spending a `wave` call and a read of `ROADMAP.md` to recover
a line already on its screen, and the wrong half of the sentence is the half a
session acts on.

**Done when.** The sentence says what `show` prints and what it does not - the
`plan:` line is the item's placement, and `bin/docket wave` is still what
settles gate *membership*, which placement is not - and nothing else in
`.claude/skills/docket/SKILL.md` claims `show` is silent about placement.
