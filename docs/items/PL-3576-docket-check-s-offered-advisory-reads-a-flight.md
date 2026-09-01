---
id: PL-3576
title: docket check's offered-advisory reads a flight answer that may be partial and says nothing about it
priority: P3
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_cli.py
added: 2026-08-31
closed: 2026-09-01
verify: uv run pytest subprojects/docket/tests/test_checks.py subprojects/docket/tests/test_cli.py && grep -q 'def test_an_offering_ranked_on_refs_that_went_unread_says_so' subprojects/docket/tests/test_checks.py
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

**Triaged 2026-09-01.** P3, `defect`/`infra`, `parallel-sessions`, and
**admitted to v0.2.8's frozen list** under the scope test: `PL-S1P1` fixed six
of the seven readers of the flight answer as a frozen entry, and this is the
seventh, left out as a placement question rather than because it was out of
scope. The `verify:` command was run first and selects nothing today, so it
exits 5 until the test exists; `-k check` and `-k declined` both select passing
tests and would prove nothing.

**Worked 2026-09-01.** The placement is the brief's - the `Not checked`
section - and it reads `whether the grooming advisories name the items `next`
will really offer:` followed by the same sentence the other six readers print,
worded by `render.format_unread` so no second wording exists to drift.

*The fix is wider than the brief's `Where`, and deliberately.* That section
named `_offered` and `cmd_check`, which would have meant `cmd_check` appending
to `report.declined` after `analyze` returned - a second author for a list
`analyze` otherwise owns alone. The cause is one level up: `history`, `landed`
and `closures` are all report types carrying their own `declined`, while
`offered` was a bare `frozenset[str]`, which is exactly the shape that cannot
say a ranking was partial. `FlightReport`'s own docstring makes this argument
about its ids; this is the same collapse one layer above it. So `plan.py` gains
`OfferedReport`, `analyze` takes it in place of the set, and the decline is
recorded beside the other three. Cost: fourteen test call sites, mechanically
updated behind a `_offering()` helper.

*The seventh reader is now in the test that lists them.*
`test_the_queue_commands_say_when_a_ref_went_unread` enumerated the six
`PL-S1P1` fixed; `check` joins the list rather than getting a test of its own,
because the list is what would have caught this omission.

*Verified end to end on this checkout, which is genuinely truncated.* Before
the change `docket check` reported one declined line here - shallow-clone
provenance - while two refs went unread by the ranking; after it, both are
reported. The `verify:` command was a bare `-k flight`, which selected no test
and exited 5 before and after the work; it is now the paired shape.
