---
id: PL-LN69
title: Instruction-set growth is measured but never tested for effect, so a rule can be added on an argument and can never be retired on evidence
priority: P2
effort: L
status: dropped
classes: docs, session-cost
touches: CLAUDE.md, .claude/rules/, .claude/hooks/, tools/, docs/resident-instructions.md
added: 2026-09-21
closed: 2026-09-21
reason: Answered rather than built: the project owner ratified no retirement mechanism on 2026-09-21. The three shapes this item proposed were declined, and an independent re-measurement found its own successor's counter-proposal already refused in docs/resident-instructions.md. Four of its derived claims are corrected in the resolution section; the stock figures stand. The real gap was staleness rather than bloat, filed as feature instruction-staleness-audit.
root-cause-of: PL-H7XN, PL-NJTZ, PL-034, PL-JQY5, PL-JQVB, PL-QV1F, PL-BKQW
generator: spent - answered rather than stopped: the owner ratified on 2026-09-21 that rule retirement gets no effect test, so growth under the add-versus-retire asymmetry is accepted rather than filed, and no item filed since names it; reopens on a measured adherence failure traceable to resident size, or ~150 rules with the rate still positive over 60 days
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

## Resolved 2026-09-21: no retirement mechanism (project owner, ratified)

**Decision (project owner, 2026-09-21, ratified, over adding a subsumption
retirement test and a rule-count tripwire, both of which this item's own
successor session proposed and then withdrew).** Rule retirement gets no second
test and no new signal. Citation frequency, the read-log extension and evals are
all declined. The instruction set is left as it is.

**Why the recommendation was withdrawn.** An independent re-measurement session
proposed a subsumption test, an enforceable pay-for-it check, and a 150-rule
tripwire — then found all three already in `docs/resident-instructions.md`:

- The "second test" is the existing one reworded. § "When a resident rule is
  retired" already admits "a check, a hook, **or a command that prints the rule
  at the moment it fires**" — which *is* a carrier firing at the same moment.
  This item's claim that the section "admits exactly one test" is true as a
  count and misleading as a description.
- The enforceable pay-for-it check is the fourth bullet of § "Reductions
  considered and refused", refused because it keys on prose and so "would fire
  without changing a decision".
- The rule-count tripwire is the refused ceiling in a different unit.

**Measurement corrections, from walking all 244 commits rather than every
ninth.** This item's stock figures are right; four of its derived claims are
not.

| Claim | Filed | Re-measured |
| --- | --- | --- |
| Resident / total characters | 66,773 / 258,640 | **Confirmed** on `origin/main` (was measured on an unmerged branch) |
| Total instruction text "never fell" | never | **Fell at 17 commits**, sum −35,106 — but every one is a relocation to files outside the denominator, so the conclusion survives its evidence |
| The 2026-09-01 illustration | −13,997 resident while total rose 81,063 → 86,035 | The commit is **2026-08-31**, and total **fell 5,820** at it; the filed span brackets ~20 unrelated commits |
| Stripping justification buys | ~9,029 chars, 14% | Regex proxy reproduces at 16.9%; **paragraph-level classification gives 71.3%**, of which only 2.0% is bare provenance |
| "Never retired a rule" | never | **19 rules left residence at once on 2026-08-31** (64 → 45). False in the rule unit |

**Generator attribution was overstated.** Of the seven items named in
`root-cause-of:`, three (`PL-JQVB`, `PL-QV1F`, `PL-BKQW`) are measurement
defects, which this brief concedes in its own words — they are caused by the
absence of a good gauge, not by the retirement test. `PL-JQY5` was dropped as a
duplicate. Four members, not seven.

**What survives, and it is not nothing.** Since 2026-09-05: 92 consecutive
commits with zero reduction under every denominator tried. The asymmetry is real
as a *description* — addition has a moment, retirement has none. But no measured
adherence failure attributable to resident size exists anywhere in this
repository, and 65 rules sits an order of magnitude below where any published
benchmark shows degradation (IFScale, https://arxiv.org/pdf/2507.11538, puts
2024-era models at 200–300 simultaneous instructions). `PL-6SBB` looks like such
a failure and is not: it was a co-location problem and co-location fixed it.

**The urgency did not survive either.** 0.95 rules/day came from 21 days with
sd 1.29 against a mean of 1.11, seven of eighteen observations at zero, and two
single commits supplying 8 of the 20 rules — remove those two and it is
0.57/day. Extrapolating that 3–8 months is not defensible.

**What would reopen this**, on ordinary evidence since the decision is ratified:
a measured adherence failure traceable to resident size, or rule count past ~150
with the rate still positive over a 60-day window rather than a 21-day one.

**The real gap was elsewhere, and is now filed.** Every mechanism here fires on
an *edit*; nothing fires with the passage of *time*. The failure that outlives a
size problem is staleness, not bloat — a rule true in 2026 and false in 2029
gets obeyed. That is `feature: instruction-staleness-audit` (`PL-T5K1`,
`PL-PHK4`, `PL-44DG`), approved the same day.
