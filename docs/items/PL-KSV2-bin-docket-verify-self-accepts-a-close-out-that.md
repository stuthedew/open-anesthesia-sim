---
id: PL-KSV2
title: bin/docket verify --self ACCEPTs a close-out that deletes its failing verify: and writes not-delegable: on the branch, though its docstring, the README and the close-out skill say that exemption is read from the base's copy
priority: P2
effort: S
status: done
classes: defect
feature: verify-close-out
milestone: v0.5.9
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md, .claude/skills/docket/modes/close-out.md
added: 2026-09-23
closed: 2026-09-23
pr: 956
payoff: A close-out can no longer skip its own failing verify: command by deleting it and writing a not-delegable: reason beside the deletion, so an ACCEPT from verify --self again means the commissioned command ran and passed, or there never was one
verify: grep -q 'def test_a_not_delegable_line_does_not_excuse_a_command_the_base_holds' subprojects/docket/tests/test_verify.py
---

**Problem.** bin/docket verify --self ACCEPTs a close-out that deletes its failing verify: and writes not-delegable: on the branch, though its docstring, the README and the close-out skill say that exemption is read from the base's copy

**Found 2026-09-23 building `PL-BX1C`** (verify runs a dropped item's stale
`verify:` command), whose fix widens the same exemption and so had to say how it
is read.

`PL-L4KX`'s exemption - a `dropped` item, or one carrying `not-delegable:`, has
no command to run - reads `status` and `not_delegable` off the item `cmd_verify`
loads, which is `read_items` over the working tree: the branch's copy. Three
documents said otherwise until `PL-BX1C`'s sweep rewrote them, quoted here as
they stood on `main` at `7ab0ea3a`:

```
verify.py, verify_item's docstring:
    Each turns on the item as the *base* holds it - the commission - rather
    than on the branch, so neither is anything a session can grant itself
    mid-work
subprojects/docket/README.md:
    Neither is anything a session can grant itself, because each turns on the
    item as the **base** holds it
.claude/skills/docket/modes/close-out.md:
    Both turn on the base's copy of the item rather than on your branch
```

`PL-L4KX`'s own **Worked** note and the v0.4.27 row of `ROADMAP.md` say the
same, and stay as the record. It is true of `falsifies:`, and of neither half of
this exemption.

**Reproduced 2026-09-23** in a throwaway test on `test_verify.py`'s own
helpers: the base holds `PL-K7QX` at `ready` with `verify: false`; the branch
sets `status: done` and `closed:`, deletes the `verify:` line and writes
`not-delegable: proving it means cutting a release`. `bin/docket verify --self`
printed `NOTE has a verify: command - none recorded: the item records why no
command can prove it`, then `NOTE item front matter unchanged - closed,
not-delegable, status, verify`, then `ACCEPT`. The failing command never ran.

**Why it matters.** "The item's own command passes" is one of the four
integrity checks `--self` holds absolute, and the documents told a session that
neither exemption could be granted mid-work. One can, and the only trace is the
front-matter `NOTE`, which fires on every close-out because every close-out
changes `status` and `closed` - so it is the line a reader has learned to skim.
A delegated audit is unaffected: its front-matter check refuses any change to
either field.

**The dropped half is not the hole.** It has to be read off the branch, since
the drop is what the close-out writes and the base still holds the item open,
and it grants nothing: a drop claims no work for a command to prove.
`PL-BX1C` records that where it widens the exemption.

**Shape of a fix, not chosen.** Reading `not-delegable` off the base's copy is
the obvious route, and it breaks the case `PL-L4KX` was built for wherever the
base holds no copy at all: 452 of 842 closed items, 54%, carried the same
`added` and `closed` date when `PL-TKFD` counted on 2026-09-17, and a release
cut is the usual `not-delegable` shape. The narrower route refuses only the
exact self-grant - the base's copy carries a `verify:` and the branch both
removes it and adds `not-delegable:` - and leaves an item filed and closed on
one branch alone. Which of the two, or leaving the `NOTE` to carry it, is the
decision.

**Recommended: the narrow route** (2026-09-23, by the session that filed this).
It refuses exactly the self-grant and nothing else, so the item filed and closed
on one branch - the case `PL-L4KX` was built for - keeps its passing route.
Reading the base's copy wholesale would take that route from every closure the
base holds no copy of, and `PL-TKFD`'s count puts those at about half. Either
route narrows an existing exemption rather than adding a mechanism, so the
generator pause holds neither.

**Done when.** A `--self` close-out that deletes the base's `verify:` and adds
`not-delegable:` on the branch no longer reaches `ACCEPT` on the exemption
alone; the close-out of an item filed and closed on one branch with
`not-delegable:` still does; and a test drives both.

**Not a recurrence of `PL-BX1C`**, though `docket new` matched it there on the
two shared paths: that item is a false `REJECT` on a dropped item's command,
this one a false `ACCEPT` on a `not-delegable:` line, and fixing either leaves
the other standing.

**Worked 2026-09-23.** The narrow route, one notch wider than recommended:
`not-delegable:` now excuses a missing command only where the base's copy
commissions none. Deleting a command the base holds is refused whether the
reason is the branch's own or one the base already carried beside the command,
because a reason can say who should do the work rather than that nothing can
prove it - `wants the strongest model` is that shape, and an item carrying a
reason *beside* a command is where one lives. A base whose copy cannot be read
excuses nothing. `Commission` gains `verify`, read with `falsifies` and
`status`, and `_check_item` reads the commission once, ahead of the command
check. `test_a_not_delegable_item_close_out_is_not_a_missing_command` had been
closing an item whose base held `verify: true` - the self-grant itself - so it
now drives the two shapes that keep the exemption: filed and closed on one
branch, and held by the base with no command.

Counted before tightening: of the 12 first-parent commits on `main` that
removed an item's `verify:` line without adding one, 10 dropped the item, 1
deleted the file and 1 moved it to `needs-decision`; none wrote
`not-delegable:`. So none of the 83 items now carrying a reason and no command
reached that state by removing one, and the refusal takes away no route any
close-out in this history used. Every one of those 83 reasons is about
provability, which is why the field's other meaning is not filed as a finding.
