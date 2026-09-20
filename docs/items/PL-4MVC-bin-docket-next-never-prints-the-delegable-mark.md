---
id: PL-4MVC
title: bin/docket next never prints the delegable mark that docket list already prints, so the one command that recommends what to work on is silent about the 141 open items a cheaper model may take
priority: P2
effort: S
status: done
classes: defect, session-cost
feature: model-capability-routing
milestone: v0.4.31
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_plan.py
added: 2026-09-19
closed: 2026-09-19
pr: 733
verify: uv run pytest subprojects/docket/tests/test_plan.py -q && bin/docket next workflow | grep 'cheaper model' > /dev/null
---

**Problem.** bin/docket next never prints the delegable mark that docket list already prints, so the one command that recommends what to work on is silent about the 141 open items a cheaper model may take

**Why it matters.** The classification was already built and already correct.
`Item.delegability` decides it from the store — `ready`, no `safety` or
`science` class, no open decision, a `verify:` command, `touches` declared and
wholly outside `protected_paths` and `gate_paths`, `S` or `M` effort — and it
is derived rather than stored, so no session can grant it to its own work.
`render._marks` prints `delegable` from it, which means `bin/docket list` and
`bin/docket delegable` both answer the question.

`bin/docket next` did not, and neither did the session-start digest's `Top:`
line. Those two are the surfaces a session and the project owner actually read
when deciding what to pick up: `plan.Recommendation.describe` appended
`use your strongest model` from `model_guidance` and nothing from
`delegability`, and `format_digest` called `_marks` with no path configuration
at all, so its fail-closed default silently suppressed the mark.

So the queue answered *what should I work on* and *what may a cheaper model
work* in two different places, and only the expensive half of the answer
reached the recommendation. 141 of 325 open items qualified on 2026-09-19 —
43% of the queue — which is the number that makes this worth fixing rather
than noting.

**Scope covers both surfaces**, because they are one threading change:
`recommend()` gains `protected_paths`/`gate_paths` the way it already takes
`workflow_paths`/`generator_paths`, `Recommendation` carries the answer the
way it already carries `scoped_to` and `generator`, and `format_digest`
forwards the same two lists to `_marks`.

**The tool names no model, deliberately.** It prints `a cheaper model may take
this`, and `docs/maintainer.md` resolves which one — the same split the
`strongest model` flag already uses, and the reason is
`.claude/rules/expert-review.md`'s: a model name is a dated instance and the
tool is not where dated instances belong. `PL-9FNV` is that half.

**Done when.** `bin/docket next` and the session-start digest both print the
delegable offer on an item that qualifies, neither prints it beside
`use your strongest model`, and a caller threading no path configuration still
offers nothing.
