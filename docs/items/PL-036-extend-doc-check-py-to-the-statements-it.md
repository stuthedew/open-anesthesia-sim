---
id: PL-036
title: Extend `doc_check.py` to the statements it currently cannot decide
priority: P2
effort: M
status: done
classes: docs, infra, session-cost
feature: dev-tooling
milestone: v0.5.4
touches: docs/MODEL.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-08-24
closed: 2026-09-22
pr: 900
verify: python3 tools/doc_check.py check && grep -q 'heading="Minimum displayed outputs"' tools/doc_check.py && grep -q 'def _list_members' tools/doc_check.py
recurrences: 2026-09-21 PL-L609
---

**Problem.** `tools/doc_check.py` checks that cited things *exist*. It cannot
check that a sentence about them is *true*: a `must` in `docs/MODEL.md` the
code no longer satisfies, a shipped feature still described as deferred, a
displayed value whose units the interface changed.

**Why it matters.** Those are the remaining close-out failure modes, and they
are the ones with clinical consequence — `CLAUDE.md` calls a stale statement
about what a value means a safety issue, not tidiness.

**Where.** `tools/doc_check.py`, `docs/MODEL.md` ("Minimum displayed
outputs").

**Decided.** Some of it is mechanizable, provided the tool checks **linkage,
not truth**. That is what `check_provenance` already does: it does not
validate that a partition coefficient is scientifically right, only that the
table and the JSON agree, and nobody misreads it because its report says what
it checked.

This item implements one link. Each of the fifteen bullets under
`docs/MODEL.md` "Minimum displayed outputs" names the `SimulationSnapshot`
field behind it, and `doc_check.py` verifies that each named field exists on
the dataclass. The mechanism fits the tool's stated constraints: `ast.parse`
over `app/controller.py`, find the `SimulationSnapshot` class definition,
collect its annotated assignments — standard library only, no import of the
application package, runs in a bare checkout.

What it catches is a renamed or deleted snapshot field silently breaking a
required output, which is live risk: PL-004 deletes a snapshot field and
PL-006 renames a core class across four documents.

Its limit, to be stated in the tool's own docstring rather than discovered:
this proves the field *exists*, not that the interface *displays* it.
`circuit_time_constant_s` is the standing proof that a snapshot field can
exist with no widget behind it. The doc → field → widget chain has a second
link, and `doc_check.py` cannot own it, because reaching the widget needs the
application package the tool deliberately never imports. That link belongs in
a test, filed separately.

**Recorded, and not to be revisited by tooling:** whether a documented
statement is still true stays human. No check here decides it, and a check
that appeared to would be the confident nonsense this item asked about.

The harder half the item raised — tying `docs/MODEL.md`'s eighteen "Required
invariants" to named tests — is worth doing and is filed separately. It is the
same shape as a citation check and would report something true and useful
("every invariant names a test that exists"), but the work is the annotation
pass, which is eighteen judgments, not the forty lines of checking.

**Done when.** "Minimum displayed outputs" names a snapshot field per bullet,
`doc_check.py` checks each against the dataclass with unit tests of its own,
`make check` gates it, and the tool's docstring records both the new check and
the limit above.

**Re-scoped 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
This is the annotation pass for `docs/MODEL.md` § "Minimum displayed outputs"
under clause 2, mechanism unchanged. Its recorded principle - the tool checks
**linkage, not truth** - is kept whole and is now clause 1's own line rather
than an exception to anything. What changes is only the altitude: this list is
one bound family among several rather than the whole of the idea, so the
bullets are annotated here and the general rule lives in `docs/MODEL.md` §
"How this document is held to the tree".

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation): still real, with stale numbers corrected here rather than in the text above.** § "Minimum displayed outputs"
carries **21** bullets, not fifteen; none names a `SimulationSnapshot` field,
`SimulationSnapshot` appears nowhere in `tools/doc_check.py` or its tests, and
`BOUND_FAMILIES` at `:1766` still holds only the hazard table, so the
annotation pass is untouched. One illustration has expired:
`circuit_time_constant_s` no longer exists in `src/`, so the "standing proof"
of the doc-to-field-to-widget limit needs a live example when the pass is
written.

**Built 2026-09-22, naming the test that holds each entry rather than the
`SimulationSnapshot` field** (project owner, 2026-09-22, ratified, over the
field mechanism this item's own `Decided` section chose and `PL-4FBP`'s
re-scope carried forward unchanged). The recorded principle is untouched:
`doc_check` checks **linkage, not truth**, and what it asks of an entry is only
whether it named a test at all. Resolution stays with `check_named_tests`,
which is already scoped to `docs/MODEL.md`, so no second resolver exists to
disagree with the first.

**Why the field mechanism could not be finished honestly.** Three of the 21
entries have no `SimulationSnapshot` field and should not be given one. The
playback rate is a `PlaybackRate`, passed into `dashboard_frame.readouts()`
beside the snapshot and documented there as a view setting; the chart's time
base is a `ChartTimeBase` in `app/chart_time_base.py`, with
`SimulationController.drawn_window` a method rather than a field; and
$`F_A/F_I`$ is derived by `app/wash_in.py`'s `wash_in_ratio` at the point of
drawing. `SimulationSnapshot` is read-only *simulation* data, so adding fields
to satisfy an annotation would have let the annotation decide the architecture.
Under clause 3 those three could only have written ``no field yet
(`PL-XXXX`)`` - an absence nothing owed, which is the permanent hole wearing a
forward reference's label that clause 3 exists to make impossible. A fourth
entry degraded rather than failed: the MAC-multiple entry would have named
`agent_mac_percent`, the divisor rather than the multiple.

**And it checked the wrong half of the chain.** This item's own limit above -
"this proves the field *exists*, not that the interface *displays* it" - is
the live risk named by § "What this list requires once the layout is the
reader's": a workspace that removes a readout while the value goes on
travelling, where "the failure is silent". A display test closes that; a field
cannot. A renamed field already fails its display test under `pytest`, so the
field check would have been largely redundant with the suite beside it.

**What landed.** `_list_members` in `tools/doc_check.py` reads a family laid
out as a list, borrowing `docket.roadmap.list_entries` rather than walking a
list a fourth time. § "Minimum displayed outputs" states the promise in its
lead-in and every one of its 21 entries names the display test holding it -
no declared-none forms, because every entry already had one. The family joins
`BOUND_FAMILIES`, so `make check` gates it. Watched to fail both ways before
closing: stripping one entry's annotation gives
`docs/MODEL.md:5680: § "Minimum displayed outputs" promises that every entry
names the test that holds it`, and misspelling one test name gives
`check_named_tests`' own unresolved-name error; both at exit 1.

**The doc -> value -> widget chain's second link is still `PL-41YP`'s**, and is
not widened into here. Four entries - the agent-accounting group - are held
only at the `dashboard_frame` view-model layer, with no Qt-widget assertion
that the text reaches the screen, and two more (mixed-venous and vessel-rich)
have no on-screen readout assertion. That is the gap `PL-41YP` was filed for.

**The expired illustration is replaced.** The 2026-09-19 sweep noted that
`circuit_time_constant_s` no longer exists in `src/`, so the standing proof
that a snapshot field can exist with no widget behind it needed a live example.
It has one that is stronger than a field with no widget: three required outputs
with no field at all.
