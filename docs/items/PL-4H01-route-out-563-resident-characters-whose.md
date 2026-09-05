---
id: PL-4H01
title: Route out 563 resident characters whose carriers already exist: the lane sentence, the finish-a-feature bullet, and the duplicated quality-suite line
priority: P3
effort: S
status: ready
classes: session-cost, docs
touches: CLAUDE.md, docs/resident-instructions.md
added: 2026-09-05
verify: python3 tools/doc_check.py check && test "$(grep -c 'configured type checker' CLAUDE.md)" -eq 0
---
**Problem.** Three blocks of `CLAUDE.md` are resident for rules whose
carriers already exist and already fire at the right moment: the lane sentence,
the finish-a-feature bullet, and a quality-suite line duplicated twenty-seven
lines above its fuller statement. Together they are 563 characters.

**Why it matters.** Resident text is paid by every session forever, and
`CLAUDE.md`'s own routing test asks for the cheapest carrier that delivers a
rule at the moment it is needed. These three have that carrier already, so the
characters buy a second copy rather than coverage — and a rule stated twice is
a rule that can drift, which is the concrete hazard in the third block, where
one copy names "the configured type checker" and the other names `mypy`.

The size is itself the finding, and it is why this item is not the answer to
resident growth: a block-by-block pass over the whole resident set found only
1.3% of it defensibly routable. `PL-NJTZ` is where the growth question goes.

**Where.** `CLAUDE.md` § "Session and tool-use efficiency" (the lane sentence),
§ "The queue, and how the project owner works" (the finish-a-feature bullet),
and the architecture bullet list (the quality-suite line);
`docs/resident-instructions.md`, which records what was routed and why.

**Measured, 2026-09-05.** Resident set is 44,545 characters over 637 lines. A
block-by-block pass against all six tools in `tools/`, all four hooks, and
`.claude/skills/docket/SKILL.md` found five routing candidates totalling ~1,980
characters, of which three are defensible at **563 characters, or 1.3% of the
resident set**. Every carrier already exists; nothing needs building.

1. `CLAUDE.md` § "Session and tool-use efficiency", the lane sentence (334
   chars). `bin/docket next` now prints the rule at the moment it fires, with
   the literal command: "Lane of this answer: PL-4GN8 is product work. The
   workflow lane's own pick is PL-JBZK (...) - `docket next workflow`."
   `SKILL.md` carries the full rule and the `PL-0D4X` history. Cost of the
   move: the printed line corrects a session *after* a bare run rather than
   before it, which is one extra command rather than a wrong item started.
2. `CLAUDE.md` § "The queue", "Prefer finishing a feature to advancing several"
   (159 chars). `plan.py`'s `rank()` implements it and prints the rationale
   verbatim beside every ranked item: "A shipped feature beats progress on
   several, so the feature nearest done ranks first." This is the only bullet
   in that section `docs/resident-instructions.md` never tested - grep returns
   zero matches for it.
3. `CLAUDE.md:143`, "Run pytest, Ruff, and the configured type checker before
   finishing" (70 chars). Strictly subsumed by lines 170-173, twenty-seven
   lines below and equally resident, which name `mypy` rather than "the
   configured type checker" and add when to run it. A de-duplication, not a
   routing: the rule stays resident, once. Caveat: it sits in the bullet list
   whose path-scoping the ledger refused, so it is a rider on another edit
   rather than a task of its own.

**Considered and not recommended.** `.claude/rules/instruction-writing.md`'s
`list_sessions` bullet is the largest single candidate anywhere at 1,287
characters, and its own cited evidence (`PL-66FP`, two sessions cutting v0.3.7)
is now deterministically refused by `release.py` and `cli.py`, with `render.py`
suppressing the duplicate offer. But three of its four named triggers - a tag,
a merge, a branch deletion - have no check and are not a `docket` mode, so a
reply recommending one loads nothing and would meet no version of the rule.
Cutting only the release clause is *rewriting*, which the policy forbids.
Left resident deliberately.

**Not re-proposed.** The four entries in `docs/resident-instructions.md`
§ "Reductions considered and refused" were read and none has a new argument
against it. In particular `import_boundary_check.py` enforces two of the seven
architecture invariants but cites `CLAUDE.md` as their source, so deleting the
prose strands the citation - which is the refusal's own reasoning.

**Why this is a small number, and that is the finding.** `PL-JK0M`'s routing
pass predicted it: "The honest expectation is that a large share of the 548
lines is required-resident under the project's own test." It was right. The
resident set is not bloated with routable material, so growth cannot be
answered by routing alone - which is what `PL-NJTZ` is for.

**Done when.** The three blocks named above are gone from `CLAUDE.md`,
`docs/resident-instructions.md` records each one with the carrier that replaced
it, and no rule has been removed without a carrier named — a de-duplication
keeps the rule resident once rather than routing it anywhere.
