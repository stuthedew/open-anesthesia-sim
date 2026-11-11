---
id: PL-GW0P
title: ROADMAP.md's v0.6.0 and v0.7.0 gate sections defer a debt item captured after the cut by its capture date, while the snapshot rule re-admits any finding whose problem was present at the freeze, however late it was filed
priority: P2
effort: M
status: done
classes: defect, docs
feature: roadmap-structure
milestone: v0.6.17
touches: ROADMAP.md, subprojects/docket/README.md, docs/apparatus.md, .claude/skills/docket/modes/close-out.md, .claude/skills/docket/modes/release.md
added: 2026-11-07
closed: 2026-11-07
pr: 2063
payoff: a debt item filed after a gate froze joins that gate when its problem was already there, so v0.7.0's list holds every problem present at its freeze
verify: grep -qF 'Being filed after the freeze is not such a' ROADMAP.md && ! grep -qF 'An open debt item captured after the cut is deferred to the next gate' ROADMAP.md
---

**Problem.** Two parts of `ROADMAP.md` give different answers for a debt item
filed after a gate froze, when the problem it describes was already there at the
freeze.

§ "Which findings re-enter the gate" says such a finding re-enters the gate:

> A finding re-enters this gate, rather than waiting for the next one, when the
> problem it describes was already *present* at that moment. That is true
> whatever id the finding is filed under, and however long after the freeze
> someone happened to notice it.

The v0.6.0 and v0.7.0 sections, each under `### Deferred from this gate`, defer
it by the date it was filed. v0.7.0:

> An open debt item captured after the cut is deferred to the next gate, unless
> it is classed `safety` or `science` or an entry on this list waits on it.

v0.6.0 gives a reason that reads the presence test as a test of the item store,
not of the problem:

> An item captured after the cut was not in the store that the snapshot was
> taken from. § "The gate is a snapshot, not a moving target" therefore applies
> the presence test to it, and that test returns no.

The practice follows the gate sections. Triage writes `deferred-from: v0.7.0 -
filed after the gate froze` on post-freeze captures, as on `PL-9857`.

**Found by** `PL-P0C5` (slice 2 of the roadmap restructure), 2026-11-07, while
stating each gate rule once. The two `### Deferred from this gate` paragraphs
were left as written, because choosing between the rules is not a move.

**Why it matters.** A session that reads the snapshot section admits a late
finding whose problem predates the freeze. A session that reads the milestone's
own section defers it. The snapshot section also names re-entry cases that the
gate sections leave out: a finding that continues a frozen entry, and friction
that compounds.

**Done when.** `ROADMAP.md` states one rule for a post-freeze capture whose
problem was present at the freeze, in § "The debt gate", and the v0.6.0 and
v0.7.0 sections point at it rather than restating a different one.

**Recommendation (this session's, not yet put to the project owner).** Keep the
practice, because it is what `bin/docket check` and triage enforce and what keeps
the queue from refilling. State it in the snapshot section as the standing use of
its own "presence is a presumption" clause: a capture filed after the freeze
defers by default, and re-enters only on the cases that section lists. Then cut
v0.6.0's "that test returns no", which misreads the test.

**Generator check.** The cause is a rule stated in more than one place, with
the copies drifting apart. That is the cause the `roadmap-structure` feature
removes, so the feature is the fix and no new generator head is recorded.

**Put to the project owner on 2026-11-07.** The thread finishing the roadmap
restructure asked, on a decision card, whether cleanup filed after a list froze
waits for the next list. **Recommendation (that thread's, the same as above):
it waits, as now.** About 45 items filed since Gate 3 froze on 2026-10-25 stay
on v0.8.0's list. Only a `P0`, a live safety or science problem, a fix a frozen
entry needs, or friction every entry pays joins v0.7.0. The other reading
gives v0.7.0's list no point at which it closes.
**Answered 2026-11-07 at 22:09 UTC: join if present at the freeze (project
owner, 2026-11-07, chosen over the recommendation that a post-freeze capture
waits for the next list).** A finding filed after a gate froze joins that
gate's list when the problem it describes was already present at the freeze,
whatever its capture date. § "Which findings re-enter the gate" states the
rule. The v0.6.0 and v0.7.0 paragraphs under "Deferred from this gate", and
the triage practice of writing `deferred-from: ... filed after the gate
froze`, change to match. The work that follows: state the rule once in § "The
debt gate"; point both gate sections at it; check whether `bin/docket gate`,
`bin/docket check` or `tools/doc_check.py` defer by capture date; and
re-triage the open debt items deferred from v0.7.0 for being filed after the
freeze, adding to v0.7.0's list each whose problem was present on 2026-10-25.

**Applied 2026-11-07.** § "Which findings re-enter the gate" already stated the
rule, so it gains this answer's decision tag, and the presumption paragraph
says that being filed after the freeze is not a reason to defer a
presence-qualifying finding. v0.7.0's § "Deferred from this gate" now says a
capture joins the list when its problem was present at the freeze, and points
at that section. v0.6.0's paragraph is the record of a shipped gate, so it
keeps its reading and adds one sentence saying this item replaced it. The
docket README's example of a `deferred-from:` value gave "captured after the
freeze, and not safety or science" as a ground, and now gives a new problem.
`bin/docket gate`, `bin/docket check` and `tools/doc_check.py` read
`deferred-from:` and the frozen list, and none of them reads an item's
`added:` date, so no tool deferred by capture date.

**Re-triaged 2026-11-07.** The 41 open debt items deferred from v0.7.0 for
being filed after the freeze were each checked against `817a4d88`, and each
brief records what the check found. 34 join v0.7.0's frozen list, and so do
this item and `PL-8C8W`, which had not been triaged. The other seven stay
deferred, because their problems began after the freeze. ROADMAP.md's v0.7.0
section names the eight joiners that stay deferred and why. Two review passes
the same day corrected three verdicts. `PL-Z6FR` and `PL-HXF0` describe
disagreements that began after the freeze, so they stay deferred. `PL-KG6S`'s
not-live finding rested on the table that `PL-TDX0` questions, so it joins
undeferred. Two items were not re-checked. `PL-SG93` is classed `infra`, which
is not debt, so no gate holds it. `PL-BZ21` is held by #2054. Its deferral
reason predates this rule, and its problem probably began with `7baae320`
(2026-11-02), after the freeze, so its reason should say that when its branch
next changes it.
