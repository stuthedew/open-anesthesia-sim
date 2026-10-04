---
id: PL-M7QH
title: The simulator's design principles do not name parse, don't validate, so a quantity's own check - a supported range, a whole count - is repeated at each way in, and a way in nobody guarded lets an out-of-range value through, as PL-HSFV's settings record did
priority: P2
effort: S
status: done
classes: docs
touches: .claude/rules/expert-review.md, .claude/rules/core-domain.md, docs/resident-instructions.md
added: 2026-10-04
closed: 2026-10-04
pr: 1346
payoff: a quantity with a check of its own is checked once, into a type, so a new way in cannot skip the check, and a session choosing a fix reads that before writing one
verify: grep -qF 'the same preference, in the code' .claude/rules/expert-review.md && grep -qF '## A quantity with a check of its own is a type, checked once' .claude/rules/core-domain.md
---

**Problem.** The simulator's design principles do not name parse, don't validate, so a quantity's own check - a supported range, a whole count - is repeated at each way in, and a way in nobody guarded lets an out-of-range value through, as PL-HSFV's settings record did

**The request.** The project owner, 2026-10-04, in their own words: "We should
add "parse, don't validate" as a design principle for the simulator". It came
out of `PL-51B7`'s design round, where the owner refused building checked types
only once another unchecked way in turned up, and chose a checked type for every
supported-range quantity instead.

**Why it matters.** With no principle named, the default fix for a gap is the
narrowest check where the gap was found, which is how the guarded quantities
grew one way in at a time: the step, captured eight times before `PL-0GJC` gave
it a type, then the flows (`PL-HSFV`). A principle in the design list is read
when a route is chosen, before any code is written.

**What was done.**

- `.claude/rules/expert-review.md`: one bullet in the principles list, beside
  "Favor interfaces that prevent errors", stating the principle. Resident,
  because it governs the moment an approach is chosen, which no read precedes
  (`PL-WWDT`).
- `.claude/rules/core-domain.md` § "A quantity with a check of its own is a
  type, checked once": the pattern, with `SimulationStep` as the instance; the
  two facts about Python it depends on, that a `NewType` is erased at run time
  and that arithmetic on a `float` subclass returns a plain `float`; where it
  stops; and the sources. Path-scoped, because it fires with a `core/` file
  open.
- `docs/resident-instructions.md`: one sentence recording the cost.

**Resident growth: +508 characters, nothing cut.** The nearest line, "Favor
interfaces that prevent errors over interfaces that merely warn after an error
occurs", is about what a user is shown and stays. The new bullet carries only
the principle and points at the path-scoped pattern.

**Altitude.** It binds a quantity whose check is its own - a supported range, a
whole count - and not every field. A frozen record that refuses its own fields
is already a parsed type for them, and a relation between fields belongs to the
record holding them. The shared sign-and-finiteness guards stay per record,
because the way in `PL-HSFV` found unguarded checked those and skipped the
ranges. What would widen it: a record found letting a bad sign through.

**No check added.** The decidable half is `PL-51B7`'s third slice, the edge test
that finds every guarded quantity by type, together with `mypy --strict`, which
already refuses a bare `float` where a checked type is expected. A second check
would duplicate them.

**Not a workflow mechanism.** It is a design standard for `src/`, held to the
simulator's bar. Were it read as apparatus, the owner's request lifts the
`generator: live` pause for it (`PL-6Q9L`).

**Generator check.** Not a head. The mechanism behind `PL-HSFV` and `PL-4R3W`,
a quantity checked by hand at each way in, is `PL-51B7`'s to remove in code;
this item states the principle that keeps a new quantity out of it.

**Done when.** Both rule files carry the principle and `make check` passes.

**Sources.** Alexis King, "Parse, don't validate" (2019),
https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/. Momot,
Bratus, Hallberg and Patterson, "The Seven Turrets of Babel: A Taxonomy of
LangSec Errors and How to Expunge Them", IEEE SecDev 2016,
https://www.iti.illinois.edu/credc/publications/seven-turrets-babel-taxonomy-langsec-errors-and-how-expunge-them,
for *shotgun parsing*.
