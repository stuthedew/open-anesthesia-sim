---
id: PL-036
title: Extend `doc_check.py` to the statements it currently cannot decide
priority: P2
effort: M
status: ready
classes: docs, infra, session-cost
feature: dev-tooling
touches: docs/MODEL.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-08-24
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
