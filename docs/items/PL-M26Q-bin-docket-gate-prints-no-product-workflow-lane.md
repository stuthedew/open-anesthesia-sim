---
id: PL-M26Q
title: bin/docket gate prints no product/workflow lane split, so the session freezing a milestone's gate computes it by hand
priority: P3
effort: S
status: done
classes: infra
milestone: v0.5.21
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests, subprojects/docket/README.md, .claude/skills/docket/modes/release.md, .claude/skills/docket/modes/capture.md
added: 2026-09-06
closed: 2026-10-03
pr: 1287
verify: grep -rq 'def test_gate_reports_lanes' subprojects/docket/tests
---

**Problem.** `bin/docket gate` prints the store's open debt, split by whether
each item carries the feature `--feature` names, with effort totals for each.
It says nothing about the product/workflow lane split, which `docket.toml`'s
`workflow_paths` already decides and which `docket next` already computes.

Re-confirmed against the tree on 2026-10-03, 27 days after filing: still true.
Only the split this sentence first described had moved - since `PL-RFHH` the
groups are named for the feature and never for what a milestone clears itself -
and the work reaches `plan.py`, where `Gate` is computed, and the three
documents that describe `gate`'s output, so `touches` names them.

**Why it matters.** The lane split is the number that decides how a gate is
*worked*. Freezing Gate 1 on 2026-09-06 meant answering "can this be cleared in
two parallel sessions, and how evenly does it divide" - and the answer, 40
product against 50 workflow, is what made a 99-item precondition a fortnight of
two lanes rather than a serial queue. Getting it required a throwaway script
importing `docket.model` directly, which is the shape of thing this project
moves into the tool rather than re-deriving per session.

It is not urgent: a gate is frozen a handful of times across the remaining
plan, so the recurrence gate in `CLAUDE.md` is only just met. `gate` is also
run during grooming, where the same split would say which lane the debt is
accumulating in.

**Not a defect.** `gate` never claimed to print lanes, and "What counts" says
building a new capability into the tooling is new work rather than debt, so
this holds no gate.

**Where.** `subprojects/docket/src/docket/cli.py`'s `cmd_gate`, and whatever
renders its groups; `Item.lane(config.workflow_paths)` already answers the
question per item.

**Done when.** `bin/docket gate` reports each of its groups by lane as well as
by effort, using the same `lane()` reading `docket next` uses, so the two can
never disagree, and `subprojects/docket/tests` carries a
`test_gate_reports_lanes` asserting it. The `verify:` command names that test
rather than grepping the source: the first one written here grepped
`render.py` for `lane`, which it already says fifteen times, so it passed on a
tree that had done none of the work and `docket check --verify-base` failed the
branch that recorded it.
