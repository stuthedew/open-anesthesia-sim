# Planning model

This project uses a lightweight rolling-wave planning model: keep the distant future broad, make the next few releases ordered, and make only the current/next milestone fully executable.

## The layers

1. **Vision and product boundary** — what the finished project is for and what counts as MVP. This belongs in `ROADMAP.md`.
2. **Capability roadmap** — the major capability sequence and important dependencies. This belongs in `ROADMAP.md` and stays intentionally broad beyond the next few releases.
3. **Release train** — the ordered near-term sequence of milestones and debt gates. This also lives in `ROADMAP.md`; it is the answer to “where are we in the plan?” and “what comes next?”
4. **Scoped milestone** — goal, required scope, definition of done, explicit out-of-scope list, dependencies, and its frozen debt gate. Only the current and immediately upcoming milestone should normally have this level of detail.
5. **Feature and item queue** — `docs/items/`, grouped by `feature`, holds actionable defects, safety/science work, refactors, performance work, decisions, and small features. The queue records work; it does not define project direction.
6. **Active work** — `bin/docket status` chooses at feature altitude and `bin/docket next` chooses the next executable item once the current project step is known.

## Progressive elaboration

Planning detail increases as work approaches:

- **Far future:** capability and dependency only. Do not decompose into speculative tasks.
- **Next few milestones:** ordered release train, major prerequisites, and known promotion points.
- **Next milestone:** scope it fully and freeze its debt gate.
- **Current milestone:** actionable items, acceptance criteria, and implementation work.

Do not maintain a second long-range task-by-task implementation plan. It will become stale faster than it can be kept authoritative.

## How work moves

`idea -> roadmap intent -> scoped milestone/feature -> queue items -> active work -> done`

The transition between layers is deliberate:

- A future capability stays broad in the roadmap until its design is close enough to matter.
- When it becomes the next milestone, do the design/scoping round, define its boundaries, promote the relevant existing items, create only the new actionable items the scope requires, and freeze the debt gate.
- Before feature implementation begins, clear the gate according to `ROADMAP.md`.
- During implementation, capture findings immediately in the queue. Findings do not silently change the active milestone; the gate rules determine whether they re-enter now or wait for the next gate.
- At milestone close, reconcile the queue and roadmap, then elaborate the next milestone one level deeper.

## Answering “what should we work on next?”

Always answer from the project step first, not from a flat backlog.

1. Read the current baseline and release train in `ROADMAP.md`.
2. Determine whether the project is clearing a debt gate, implementing a scoped milestone, closing a release, or ready to scope the next milestone.
3. If a gate is active, gate-clearing work comes before ordinary feature work.
4. If a milestone is active and its gate is clear, finish the feature already underway before starting another where practical.
5. Use `bin/docket status` to select the relevant feature/workstream, then `bin/docket next` for the specific item.
6. If the current milestone is complete or nearly complete, do not mine the queue indefinitely; close the release and promote/scope the next roadmap milestone.

A good answer therefore sounds like one of these:

- “We are clearing the gate before vX.Y; these remaining items are the next work.”
- “The gate is clear and vX.Y is active; finish this feature, then move to the next required-scope feature.”
- “vX.Y is complete; the next step is to scope vX.Z, which is currently only broad roadmap intent.”

## Queue review checkpoints

The queue is reviewed at predictable points rather than whenever it becomes noisy:

- when a milestone is scoped and its debt gate is frozen;
- before milestone implementation begins, to verify the gate is actually clear;
- when a feature within a milestone finishes, to choose the next required-scope feature rather than a random backlog item;
- at milestone close, to classify findings and reconcile what moves forward;
- when the release train reaches an unscoped milestone, to promote that milestone from broad intent into executable scope.

This is the lightweight equivalent of roadmap planning, release planning, backlog refinement, and iteration planning on a larger software team. The repository remains the source of truth; no external project-management system is required.

## Current adoption

This model formalizes the structure already in use; it does not restart the project.

The existing near-term sequence remains authoritative:

`v0.3.0 foundation -> v0.4.0 teachable case -> Gate 1 -> v0.5.0 branch and compare -> Gate 2 -> v0.6.0 schematic -> Gate 3 -> v0.7.0 multi-substance/N2O -> beyond`

Existing scoped milestones, frozen gates, queue items, feature groupings, and completed releases keep their current meaning. Apply the planning model prospectively as the project moves through that sequence.
