---
id: PL-VRMK
title: 27 of the gate's 112 open entries declare docs/MODEL.md, so a quarter of Gate 1 can only be worked one item at a time
priority: P2
effort: M
status: done
classes: infra
feature: parallel-sessions
milestone: v0.4.6
touches: subprojects/docket/src/docket/concurrency.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_concurrency.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-06
closed: 2026-09-06
pr: 402
verify: uv run pytest subprojects/docket/tests/test_concurrency.py && grep -q 'def test_two_items_naming_the_same_file_are_not_a_refusal' subprojects/docket/tests/test_concurrency.py
---

**Problem.** Counted 2026-09-06 against the frozen Gate 1 list: of its 112 open
entries, 27 name `docs/MODEL.md` in `touches`. `shared_paths` treated any
shared path as contention and `conflicts_for` turned it into a `Conflict`, so
those 27 mutually excluded one another and each appeared in the other 26's
"Cannot run alongside" list. The gate's science half was therefore serial by
declaration, whatever the owner's session budget.

**What it cost, in the session that found it.** Asked for three gate items that
could run concurrently, this session read the refusal literally and withheld
`PL-4GN8` - P1, science-classed, the strongest item in the gate - because a
running session on `PL-6Q8N` also declared `docs/MODEL.md`. Both edit different
sections. The right answer was the one the `docket` skill already gives:
proceed, and land the smaller change first.

**Second mechanism, same cause.** `_covers` lets a directory match a file
beneath it, and `shared_paths` collapsed both cases into one reason string. 38
of the store's 202 open declaring items name a directory, so an item declaring
`tests/` read as contending with every test change, in the same words as two
items naming the same module.

**Decision, answered by the project owner 2026-09-06:** fix it now rather than
carry it as a decision. Route taken is sequencing advice, not a sub-file unit
for `touches` - the second changes the item format, every declaration wanting
the precision, and the parser, for a payoff bounded by how long `docs/MODEL.md`
stays this contended. It is not deferred; it is declined.

**What changed.** `Conflict` gained a `strength`, and `conflicts_for` now
tiers: `ordering` (a `blocked-by` edge, the only real refusal), `same file`
(both name the identical path - proceed, smaller change first), `same area`
(one item's directory merely covers the other's file). `refusals` is the
subset that forbids. `parallel_batch` fills in two passes: the independent set
first, then - only when `--limit` asks for a batch of a given size - items
whose sole contention is a declared path, each annotated in the output with
what it shares and with which item. `sequenceable` names what a shared file
alone kept out. Unlimited, the batch is unchanged.

**Done when.** `docket concurrent PL-4GN8` reports nothing it cannot run
alongside, `docket concurrent --limit <n>` can offer n gate items where the
independent set holds fewer, and no output presents a shared file as a
refusal. All three hold.
