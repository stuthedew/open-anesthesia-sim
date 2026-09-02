---
id: PL-ZBJ0
title: Nothing creates counter-pressure to retire a check that has stopped earning its place, so the gate can only accumulate
priority: P3
effort: S
status: dropped
classes: infra
feature: dev-tooling
touches: CLAUDE.md, tools/doc_check.py, subprojects/docket/src/docket/checks.py
added: 2026-09-02
closed: 2026-09-02
reason: both halves of its Done when are satisfied by other work - CLAUDE.md:183 now states the retirement test beside the build test, and PL-V87X was fixed outright (pr 236) rather than re-banded - and its own brief argues against the remaining decidable half
---

**Problem.** Every rule this project holds pushes one way: add a check.
`CLAUDE.md`'s "prefer deterministic tooling" section is a standing approval to
move decidable work into code, "needing no case put for it each time"; the
behavior-change rule guarantees a session acts on a finding rather than
deferring it; and the routing dispositions end with "a rule that lands in none
of the four has been lost, which is worse than this file staying long: never
delete a rule for being wordy."

There is no matching pressure in the other direction. Nothing asks whether a
check still earns its runtime, whether an advisory has stopped changing any
decision, or whether a warning has become something sessions skim past.
`CLAUDE.md` names the symptom once - "a check that cries wolf" appears in the
compounding-friction list - and provides no mechanism that would ever find one.

**Why it matters.** This is the documented failure mode for exactly this kind
of apparatus, and the project already has an instance of it.

The evidence: an evidence-led review of agentic software engineering warns that
"every incident adds a permanent test or gate, making feedback slower and
noisier until people and agents route around it", and states outright that
"sometimes the correct improvement is to remove a noisy check". It cites a
Microsoft study naming irrelevant checks, poorly phrased warnings, false
positives, slow feedback and weak workflow integration as the major barriers to
static-analysis adoption. The same review separates *gates* (exact rules, hard
failure) from *ratchets* (noisy signals needing context) and warns that a
threshold used as an optimization target stops being a decision guide.

The instance is already open and mis-banded. `PL-V87X` (ruff warns on every run
that `isort.split-on-trailing-comma` conflicts with `skip-magic-trailing-comma`)
sits at `P3` as a config nit. Its own brief describes the literature's failure
mode precisely: "a warning printed on every run of the quality gate is a warning
nobody reads - it trains a session to skim past `make check`'s output, which is
where a real advisory would also appear." That is not a nit. It is the leading
indicator that the gate has begun to be routed around, and it is the one
category of workflow defect whose cost is paid by every other check in the
suite rather than by the item that carries it.

The asymmetry compounds in the direction this project is least able to see:
a check that fires uselessly costs a little attention on every run forever,
and nothing will ever propose removing it.

**Where.** `CLAUDE.md`'s "Prefer deterministic tooling over repeated model
work" section, which states the four gates for building a mechanism and none
for retiring one. The advisory sites it would govern are
`tools/doc_check.py` and `subprojects/docket/src/docket/checks.py`.

**Approach.** The cheap half is prose and belongs beside the build gate: a
fifth bullet stating that a check firing on every run without changing a
decision is a defect in the check, that removing one is a legitimate and
recommendable outcome of a workflow pass, and that the gates/ratchets
distinction decides which advisories may fire routinely at all.

The decidable half, if it is worth building at all: `docket check` already
knows which advisories it raised. Recording how many consecutive runs an
advisory has fired without the underlying item closing would make "this one
has fired thirty times and nobody acted" visible. Weigh that against this
item's own thesis before building it - a mechanism to detect unnecessary
mechanism is the failure mode arriving through the door marked measurement,
and `PL-SZ56` already declined that trade once.

**Found.** 2026-09-02, during an audit of the open workflow items, while
looking for the stopping rule that says when workflow investment has gone far
enough. The literature answers with a property - checks being routed around -
rather than with a ratio, and the project has no way to observe that property.

**Done when.** `CLAUDE.md`'s deterministic-tooling section states the
retirement test alongside the build test, and `PL-V87X` has been re-banded to
reflect that a permanently-firing warning degrades every other advisory in the
suite rather than being a cosmetic nit.
