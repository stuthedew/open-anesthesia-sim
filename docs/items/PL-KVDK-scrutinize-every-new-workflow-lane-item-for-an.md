---
id: PL-KVDK
title: Scrutinize every new workflow-lane item for an unresolved generator or a cause the code does not recognize: a triage step, and a first pass over the 161 items filed 2026-09-20 to 09-22
priority: P2
effort: M
status: ready
classes: planning, docs
feature: generator-identification
touches: .claude/skills/docket/modes/triage.md, .claude/skills/docket/SKILL.md, docs/items
added: 2026-09-22
payoff: an unfound cause behind new workflow items is caught at the item it produces, instead of being patched one instance at a time
verify: grep -qF 'Ask every workflow-lane item where it came from' .claude/skills/docket/modes/triage.md
---

**Problem.** The project owner asked on 2026-09-22: "For each new workflow
item generated scrutinize for evidence of unresolved generator, or cause that
is unrecognized in the code." They expect apparatus inflow to be falling now
that the workflow is largely built. It is not visibly falling: 51 and 47
workflow-lane items were filed on 2026-09-20 and 09-21, after the 09-17 to
09-19 generator campaign that `PL-04KR` excludes from its baseline. That is
161 non-product items in three days (107 workflow, 40 crossing, 14 unplaced).
By class, 36 are housekeeping records, 65 are defects and 24 are docs.

Nothing asked each item where it came from. All 14 recorded generator heads
are closed and none carries a `generator:` verdict. `docket check` asks only
open heads for one, so nothing ever asks whether a closed head's mechanism
kept producing items after its fix landed. That is the "fix did not hold"
reading `PL-04KR` calls structurally impossible to see.

**Why it matters.** An unfound generator goes on handing every session new
instances while each one is patched on its own. The owner's convergence
expectation cannot be confirmed or refuted until each new item is read
against the causes already recorded.

**What this item does.** Two things. First, a standing step in
`.claude/skills/docket/modes/triage.md`, § "Ask every workflow-lane item
where it came from". Triage is the first pass that knows an item's lane,
because capture leaves `touches` unset. The step records a one-line
`**Generator check.**` in the brief. Second, a first pass over the 161 items,
fanned out to seven read-only reviewers by family. Their findings are
recorded below, and any generator they establish is recorded as one.

**Done when.** The triage step is on the base, and every generator the first
pass establishes is recorded with `root-cause-of:` and a `generator:` verdict
or put to the owner.
