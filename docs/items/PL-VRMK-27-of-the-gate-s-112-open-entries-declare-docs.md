---
id: PL-VRMK
title: 27 of the gate's 112 open entries declare docs/MODEL.md, so a quarter of Gate 1 can only be worked one item at a time
status: needs-decision
priority: P2
effort: M
classes: infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/concurrency.py, subprojects/docket/tests/test_concurrency.py, subprojects/docket/README.md
added: 2026-09-06
---

**Problem.** Counted 2026-09-06 against the frozen Gate 1 list: of its 112 open
entries, 27 name `docs/MODEL.md` in `touches`. `shared_paths` treats any shared
path as contention and `conflicts_for` turns it into a `Conflict`, so those 27
mutually exclude one another and each appears in the other 26's "Cannot run
alongside" list. The gate's science half is therefore serial by declaration,
whatever the owner's session budget - a session asked for three concurrent gate
items can be offered at most one of them.

**Why it matters.** The beat is clearing the gate, and the science entries are
the expensive part of it - the ones wanting the strongest model at high effort.
Serializing them is the single largest limit on how fast the gate closes. It is
also only partly real: most of these items add or correct one section of
`docs/MODEL.md` and would merge cleanly against a different section, so the
declaration is coarser than the actual contention. `concurrent` cannot see
that, because `touches` has no unit smaller than a file.

**Where.** `conflicts_for` and `shared_paths` in
`subprojects/docket/src/docket/concurrency.py:74`; the `Conflict` it builds is
what `cmd_concurrent` prints under "Cannot run alongside"
(`subprojects/docket/src/docket/cli.py:570`). `docs/MODEL.md` is the contended
file; the declarations are the `touches:` fields across `docs/items/*.md`.

**Decision needed.** Should `concurrent` keep the file as its unit and give
sequencing advice instead of a refusal, or should `touches` gain a sub-file
unit? Two routes, with different costs and probably only one worth building:

- **Sequencing advice.** `concurrent` keeps the file as its unit but stops
  treating a shared path as a refusal, and instead says which of the group to
  land first - the skill already tells a session to expect to resolve rather
  than to pick something else, so the output would match the working practice.
  Cheap, and it helps every future gate rather than only this one.
- **A sub-file unit for `touches`.** A heading or section anchor, so two items
  in different sections of `docs/MODEL.md` run together. Precise, and expensive:
  it changes the item format, every declaration that wants the precision, and
  the parser - for a payoff bounded by how long `docs/MODEL.md` stays this
  contended.

**Done when.** One of the two is chosen and built, or the item is dropped with
the reasoning recorded. Decide before building: the second route is most of the
work and the first may be the whole answer.
