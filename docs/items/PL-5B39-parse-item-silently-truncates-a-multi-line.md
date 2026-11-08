---
id: PL-5B39
title: parse_item silently truncates a multi-line front-matter value at its first line, so every reader sees a partial value and rewrite_item deletes the rest from the file
priority: P2
effort: M
status: done
classes: defect, infra
feature: front-matter-round-trip
milestone: v0.5.0
touches: subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_model.py
added: 2026-09-20
closed: 2026-09-21
pr: 826
payoff: an item that acquires a multi-line field keeps it, instead of every reader seeing a partial value and the next field write deleting the rest
verify: grep -q 'def test_a_multi_line_front_matter_value_survives_a_round_trip' subprojects/docket/tests/test_model.py
---

**Problem.** parse_item silently truncates a multi-line front-matter value at its first line, so every reader sees a partial value and rewrite_item deletes the rest from the file

`model.py`'s `_front_matter_pairs` keeps only the lines `FIELD_RE` matches -
`^[a-z][a-z0-9-]*:` - and an indented line continuing the value above it
matches nothing, so it is passed over rather than joined. `parse_item` then
returns the first line of the value and says nothing about the rest. On
`PL-9HDH` that is 63 characters of a `reason:` the file spells over 10 lines.

**Why it matters.** Two costs, and they are different in kind.

The read is an apparatus-floor violation: `.claude/rules/apparatus-standard.md`
requires that what this apparatus tells a session "must be true, or must say
what it could not read", and a truncated value handed over as a complete one
is indistinguishable from a complete one at the point of use. A `reason:` is
what stops a dropped finding being re-raised, so the field this silently
shortens is the one carrying the argument a later session is meant to read.

The write destroys the file. `render_item` emits the parsed value, so any
writer that re-renders - `rewrite_item`, which is what `bin/docket set` calls -
deletes the continuation lines outright. `PL-7K8Y` closed the one path this
was live on, `bin/docket record`, by inserting the line instead of rendering
the block; `set` still re-renders, so an open item that acquires a multi-line
value loses it to the next field write.

**Measured 2026-09-20.** 12 of 1,359 item files carry front-matter lines
`render_item` would delete, 3 to 15 lines each: `PL-9HDH`, `PL-B1DQ`,
`PL-BBQX`, `PL-CPLD`, `PL-H588`, `PL-HH52`, `PL-K1DL`, `PL-PVHD`, `PL-QD9K`,
`PL-SRMZ`, `PL-WFHN`, `PL-WK0N`. All 12 are `dropped` and all 12 are a
multi-line `reason:`, hand-typed before `bin/docket set` existed - so nothing
is losing lines today, and the exposure is an open item that acquires one.
`bin/docket check` reports none of it.

**Where.** `subprojects/docket/src/docket/model.py` `_front_matter_pairs` and
`render_item`; `subprojects/docket/tests/test_model.py`.

**Shape, not a decision.** Three routes, and they are not equivalent. Join the
continuation lines on read and re-emit them folded on write, which preserves
what is there and is the most work. Or read them and emit the value on one
line, which keeps every character and changes the file's shape. Or refuse a
continuation line at `docket check` so the store stops carrying them, which
fixes nothing already written. Whichever is taken, the floor asks that a value
the parser could not read whole travel with that fact rather than be rounded
off - `Item.duplicate_fields` is the existing instance of exactly that.

**Done when.** A front-matter value spread over continuation lines survives a
`parse_item`/`render_item` round trip without losing characters, or the loss
is reported rather than taken, and a test in `subprojects/docket/tests/` pins
it against a value of the shape `PL-9HDH` carries.

**Closed 2026-09-21 under `PL-9HD1`**, with `PL-FX0K` and `PL-V6CR`, because the
three were one regex. `bin/docket show PL-9HD1` carries the whole reasoning.

**Route taken: fold on read, emit on one line** - the second of the three this
brief named. The first (re-emit the wrapping) means carrying wrap positions
through a frozen dataclass nothing else reads; the third (refuse at `docket
check`) fixes nothing already written and leaves `bin/docket set` still
rewriting the file. Folding is what YAML does to a plain scalar, so it is a
faithful read rather than a guess, and it is what makes `render_item` safe on
the 12 files: the value comes back on one line with every character, where it
used to come back 9 lines shorter.

Measured after: `PL-9HDH`'s `reason:` parses to 731 characters where it parsed
to 63, and 11 of the 12 files round-trip byte-stable. The twelfth, `PL-CPLD`,
differs by a blank line `render_item` adds after the front-matter fence, which
the original parser did too - a canonicalisation, not a loss.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". The paragraph that disposed of it counts it among its entries without naming it, and is quoted in `PL-NQKP`'s brief.

> - PL-5B39 (M) `parse_item` silently truncates a multi-line front-matter value at its first line, and `rewrite_item` then deletes the rest from the file
