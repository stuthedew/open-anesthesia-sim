---
id: PL-8349
title: Outside-contributor accessibility: find what stops a professional developer who finds this repository from landing a quick fix, without lowering the quality bars
priority: P3
owner-priority: P3, 2026-10-20
effort: M
status: ready
classes: infra
touches: README.md, .github/workflows/quality.yml, CLAUDE.md
added: 2026-10-20
payoff: a developer who finds the project can land a small, correct fix without first learning the owner's workflow, so the simulator can gain contributors without losing its quality bars
not-delegable: the deliverable is a findings report and a design round with the owner; no command can prove that the hurdles found are the ones that matter
---

**Skeleton, to be fleshed out** (project owner, 2026-10-20: "will flesh out
later"). Priority P3 is the owner's (project owner, 2026-10-20:
"should not be p1. Can be untriaged or P3"), corrected from a P1 filed by
mistake.

**Problem.** The repository is tailored to one owner's workflow. Its checks
cover code quality, and also pull request formatting, item ids in commit
subjects and titles, the docket queue, and agent-session rules. A competent
developer who finds the project and wants to submit a quick fix may hit
hurdles that have nothing to do with the quality of their fix.

**Why it matters.** The project is meant to last years. Outside contributors are one way it outlives a single maintainer's attention, and a contributor who bounces off formatting checks is lost for reasons unrelated to the simulator.

**Goal.** An outside developer can land a small, correct fix without having
to learn the apparatus first. The simulator's quality bars stay where they
are: the safety-critical clinical-output standard, tests with every core
change, and determinism are not negotiable.

**Proposed method (owner's sketch, open to a better route).** Have agents
simulate a professional developer who found the project and wants to submit
a quick fix. Record each hurdle they hit trying to open a pull request: what
they had to read, which checks failed for reasons unrelated to the fix, and
where they would have given up.

**Questions to settle when this is fleshed out.**

- Which personas to simulate: for example a Python developer with no
  anesthesia background, a clinician-developer, and a drive-by typo fixer.
- Which quick fixes to give them: one in `src/`, one in docs, one in tests.
- Which checks separate a contributor's code quality from the owner's
  workflow conventions, and whether the second kind can be waived, automated
  or applied at merge time instead of at submission.
- Whether the run starts from a fresh clone with no `.claude/` context, so the
  agent sees what a human would.

**Done when.** Simulated contributors have attempted the quick fixes, each hurdle is recorded with the check or document that caused it, each is classed as a quality bar to keep or a workflow convention a stranger should not have to meet, and the owner has decided which to change. The changes themselves are filed as items.

**Constraint.** While any open workflow-lane item carries `generator: live`,
no new workflow mechanism is built (`CLAUDE.md` § "What this project is").
The simulation and its findings can run. Any new check, command or
contributor path it recommends is captured, and built only once that pause
lifts or the owner lifts it for this request.
