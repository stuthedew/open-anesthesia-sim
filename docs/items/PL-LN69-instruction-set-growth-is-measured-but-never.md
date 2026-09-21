---
id: PL-LN69
title: Instruction-set growth is measured but never tested for effect, so a rule can be added on an argument and can never be retired on evidence
priority: P2
effort: L
status: needs-decision
classes: docs, session-cost
touches: CLAUDE.md, .claude/rules/, .claude/hooks/, tools/, docs/resident-instructions.md
root-cause-of: PL-H7XN, PL-NJTZ, PL-034, PL-JQY5, PL-JQVB, PL-QV1F, PL-BKQW
generator: live - the mechanism is untouched and the store is still being handed members; PL-0GMC added 2348 resident characters on 2026-09-21 on an argument alone, and the 1550/day rate since the 2026-09-01 trough is unchanged by any of the seven items below having closed
added: 2026-09-21
---

**Problem.** Every rule in the resident set is there on an *argument* about the
moment a session would need it. Not one is there on evidence that it changed a
session's behavior, and nothing measures whether any of them fires. Retirement
therefore requires proving a negative — `docs/resident-instructions.md`
§ "When a resident rule is retired" admits exactly one test, that the failure
mode is "now caught deterministically" — while addition is mandated by
`CLAUDE.md`'s rule that a behavior change takes effect in the session that asks
for it. Addition is cheap and required; removal is expensive and nearly
impossible. The set can only grow, by construction rather than by anyone's
carelessness.

**Why it matters.** Adherence is the constraint, not size, and nobody has
measured it — so "adherence is holding at 66,773 characters" is a claim this
project has never tested. Chroma's July 2025 report measured degradation at
every input-length increment across 18 frontier models rather than only near
the window limit (https://www.trychroma.com/research/context-rot). Here the
rules that would be missed include the safety-critical clinical-output
standard, where a missed rule can mean a wrong displayed clinical value. The
cost is also paid forward: at 1,550 characters/day every future session pays
for every rule that no longer earns its place, and the project currently has no
way to name one.

**Measured 2026-09-21, so the next session need not re-derive any of it.**
All figures from this checkout's git history; method recorded below.

| Quantity | Value |
| --- | --- |
| Resident set, 2026-08-23 | 9,148 characters |
| Resident set, 2026-09-21 | 66,773 characters |
| Growth since the 2026-09-01 trough (35,721) | +31,052 in 20 days, ~1,550/day |
| Commits touching a resident file | 95 grew, 14 shrank, 32 unchanged |
| Largest single resident reduction | −13,997 (2026-09-01) |
| **Total instruction text, 2026-08-23 → 2026-09-21** | **12,806 → 258,640** |
| Sample points at which total instruction text fell | **none** |
| Justification/history inside the resident set | ~9,029 characters, 14% |

Two consequences the numbers carry and an argument would not:

- **Every reduction in this project's history was a relocation.** On
  2026-09-01 `CLAUDE.md` fell 13,997 characters and *total* instruction text
  rose, 81,063 → 86,035. The four dispositions are a cost-reduction mechanism
  with four tiers, not a retirement mechanism; once a rule sits at the cheapest
  tier that can carry it there is nowhere left to send it, which is why growth
  continued at 1,550/day with routing fully available throughout. The only true
  deletion the ledger records is 70 characters.
- **Stripping the justification is not the answer, which is worth knowing
  because it is the intuitive one.** The `PL-` citations, dates, measurements
  and refutation history inside the resident set total ~9,029 characters. At
  current velocity that buys six days.

**Why it is a generator.** Seven items have attacked this from different
angles and every one is closed, with the rate unchanged: `PL-H7XN` (keep every
rule resident whether or not a session needs it), `PL-NJTZ` (resident rules
have no retirement test while checks do), `PL-034` (a one-time trim, which
regrew inside a release), `PL-JQY5` (dropped as a duplicate, and the pass it
asked for was never run), `PL-JQVB` (the skills blind spot — the advisory
reported 16% of the instruction text actually added), `PL-QV1F` (lines were
the wrong unit), `PL-BKQW` (net growth hides a trim paid for by an addition).
Each fixed a *measurement* of the stock. None gave removal a test it could
meet, which is the mechanism underneath all seven.

**The instrument already exists and is pointed at the wrong target.**
`.claude/hooks/item_read_log.py` was built on this exact reasoning, in its own
words: "Every claim this project has made about `docs/items/` describes its
*shape*… Not one of them is a measurement of the store being *used*… This
closes that gap the only way it can be closed, which is by watching." That
sentence is true verbatim of the instruction set. The path-scoped rules and
skills — 191,336 characters — are *loaded by a read*, so the existing
`PostToolUse` matcher can already see them; the resident set cannot be seen
that way, because it loads at launch and is never read.

**Decision needed.** Whether retirement gets a second test that can actually be
met, and which signal feeds it. Three shapes:

1. **Citation frequency over the existing corpus.** Which rules do sessions
   invoke in briefs, commit subjects and pull request bodies. No hook, no model
   calls, computable today, and it produces a candidate list within one
   session. A crude pass over 1,674 files put `CLAUDE.md` § "Safety-critical
   clinical-output standard" at one mention. Weak alone — a session can obey
   without citing — so it selects candidates for review rather than deciding
   anything. **This is the recommendation**, on the ground that it is the only
   shape that converts "prove a negative" into a list a human can defend or
   drop.
2. **Extend the read-log hook to `.claude/rules/` and `.claude/skills/`.**
   Nearly free, and it measures loading rather than obeying. Covers the 191,336
   on-demand characters and none of the resident 66,773.
3. **Evals — run a scenario with and without a rule.** The only true
   counterfactual and the only thing that answers "if it changes nothing, what
   was the point". Expensive, and the judgment of whether a rule fired is
   itself model work.

Not mutually exclusive; 1 and 2 are complements, 3 is a different price class.

**Not to be decided by a session.** How the project governs its own
instructions is the project owner's, and the question was raised by them
(2026-09-21) rather than found in a sweep. The shapes above are this session's
recommendation and nothing has been built.

**Method, for replication.** Resident set = `CLAUDE.md` plus every
`.claude/rules/*.md` carrying no `paths:` frontmatter, measured per commit with
`git show`. Total instruction text adds the path-scoped rules,
`.claude/skills/**` and `docs/worker.md`. Growth trajectory sampled every ninth
commit touching those paths; the grew/shrank/unchanged counts walk every such
commit. The justification fraction splits resident text into sentences and
counts those carrying a `PL-` id, an ISO date, a character count, or an
explicit refutation/measurement phrase — a proxy, deliberately generous to the
"strip it" case, and still only 14%.

**Done when.** Retirement has a second test that a session can actually
satisfy without proving a negative, the signal feeding it is computable and
recorded in `docs/resident-instructions.md` beside the existing test, and the
first candidate list has been produced and ruled on by the project owner — so
that at least one rule has been either defended on evidence or retired on it.
Producing a list nobody acts on does not close this.
