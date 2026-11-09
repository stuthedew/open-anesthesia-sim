---
id: PL-LJY8
title: docs/maintainer.md has the headless worker take its model from the [models] table, but gives a fixed Sonnet model through --model for PL-6FX6's trial; record whether that override is an agreed exception to the table (copy editor structure read, 2026-11-07)
priority: P3
effort: S
status: ready
classes: docs
feature: maintainer-guide-structure
touches: docs/maintainer.md
deferred-from: v0.7.0 - a new problem, not present at the freeze: the runner's model was first said to come from the [models] table in 65c3a41f (PL-KDG0)
added: 2026-11-07
payoff: the owner can tell that --model is a one-run override the model trial uses by design, not a second way of choosing the worker's model
verify: ! grep -qF "the form used for \`PL-6FX6\`'s trial" docs/maintainer.md
---

**Problem.** docs/maintainer.md has the headless worker take its model from the [models] table, but gives a fixed Sonnet model through --model for PL-6FX6's trial; record whether that override is an agreed exception to the table (copy editor structure read, 2026-11-07)

**Checked 2026-11-09:** `docs/maintainer.md` § "Spend the monthly API credit on delegable items" still says the runner "asks the `[models]` table for its model and effort", and later that "`--no-push --model claude-sonnet-5-5` is the form used for `PL-6FX6`'s trial". `PL-6FX6` is still `ready`. Its brief runs the same five items on Haiku 5.5 and on Sonnet 5.5 so as to compare the two, so the trial chooses its model by design.

**Why it matters.** A reader cannot tell whether `--model` is a sanctioned way to override the table or a leftover. Taken as the usual form, it would put worker runs on a model that no table entry chose. The section also names only Sonnet, while the trial runs two models.

**Done when.** The section says that `--model` overrides the table for one run, that `PL-6FX6`'s trial uses it to run each item on both models it compares, and that an ordinary run takes the table's model.

**Generator check.** One-off: a finding from the `docs/maintainer.md` structure-read sweep. The fact is which model a headless worker runs, which the `[models]` table records; no head states it.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** Not present. At 817a4d88, `docs/maintainer.md` said that each run "works one item on Opus 5.5", and gave `--no-push --model claude-sonnet-5-5` as `PL-6FX6`'s trial form. The statement that the runner takes its model from the `[models]` table arrived in 65c3a41f (`PL-KDG0`, #2047, 2026-11-07), so this is a new problem and is deferred.
