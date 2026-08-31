---
id: PL-3576
title: docket check's offered-advisory reads a flight answer that may be partial and says nothing about it
status: untriaged
added: 2026-08-31
---

**Problem.** `PL-S1P1` carried the unread refs to the six answers that rank or
mark against in-flight work - `next`, `list`, `status`, `concurrent`,
`delegable` and the digest. `check` is the seventh reader and was left out:
`_offered` calls `_flight(args).ids` to compute which items `next` is about to
suggest, and the grooming advisory it feeds ("`PL-68XK` is next to be offered
and names no `verify:` command") is therefore computed from an answer that may
be partial, with no line saying so.

**Why it matters.** Least of the seven, which is why it was left: the advisory
asks for a `verify:` command rather than for the item to be started, so a
partial flight answer names the wrong item to groom rather than sending two
sessions at one item. It is still the same shape of silence.

`check` is also the one command with somewhere to put it. It already prints a
"Not checked (this checkout cannot answer; nothing is claimed)" section, which
is exactly what an unread ref is - so this is a placement question rather than
a wording one, and that is why it was not folded into `PL-S1P1`'s one-sentence
footer.

**Where.** `subprojects/docket/src/docket/cli.py` - `_offered` and
`cmd_check`; `subprojects/docket/src/docket/checks.py` - `Report.declined`,
which is where a check that could not run is already reported.

**Done when.** A shallow checkout running `docket check` is told that the
offered-item advisory rests on a flight answer it could not complete, in the
section that already exists for checks that could not run.

**Relations.** `PL-S1P1` (the in-flight ids reach `docket next` without the
refs that went unread) is the same hole in the other six readers, done
2026-08-31. `PL-YSXF` (a ref named as unread loses the id its own branch name
carries) narrows the gap itself and is the more valuable of the two remaining.
