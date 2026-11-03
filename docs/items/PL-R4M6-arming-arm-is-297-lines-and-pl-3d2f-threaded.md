---
id: PL-R4M6
title: arming.arm is 297 lines, and PL-3D2F threaded its owner-ask fast path through it as five if owner_ask checks; split it into stages that the full answer and the fast path each compose
priority: P3
effort: M
status: ready
classes: refactor
feature: guard-code-structure
touches: subprojects/docket/src/docket/arming.py
deferred-from: v0.7.0 - captured after the freeze; a workflow-lane code-structure change, not safety or science, and no learner sees it
added: 2026-11-03
payoff: a change to what arm checks edits one stage, and the owner-ask fast path cannot drift from the full answer by a missed check
verify: grep -q 'def _read_change' subprojects/docket/src/docket/arming.py
---

**Problem.** arming.arm is 297 lines, and PL-3D2F threaded its owner-ask fast path through it as five if owner_ask checks; split it into stages that the full answer and the fast path each compose

**Why it matters.** `arm` reads the branch, the forge, the change's paths, the
prose and blind-review records, the owner-read and owner-ask records, the
claims and the commits behind, in one 297-line function. `PL-3D2F` added a fast
path for `--owner-ask` by putting `not owner_ask` into five of those steps and
returning early from the middle. A later change to any step has to find each
check by hand, and a missed one makes the fast path answer differently from
the full one.

**Done when.** Each step is its own function that returns what it read and
what went unread: where the branch stands, the forge's answer, the change's
paths, the review counts, and the claims. `arm` composes all of them. The
owner-ask path composes the subset it needs, with no `owner_ask` test inside a
step. Every existing test of `arm`'s answers passes unedited.

**Generator check.** No generator: one function.
