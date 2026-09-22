---
id: PL-KVDK
title: Scrutinize every new workflow-lane item for an unresolved generator or a cause the code does not recognize: a triage step, and a first pass over the 161 items filed 2026-09-20 to 09-22
priority: P2
effort: M
status: done
classes: planning, docs
feature: generator-identification
touches: .claude/skills/docket/modes/triage.md, .claude/skills/docket/SKILL.md, docs/items
added: 2026-09-22
closed: 2026-09-22
pr: 915
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

**What the first pass found (2026-09-22).** Seven read-only reviewers read all
161 items, grouped by family. Their three answers to "why is inflow not
falling":

1. **Six of the fourteen closed heads are still live.** Each closed on a
   decision or a partial fix, not on a stopped mechanism. Post-close instances:
   `PL-6TP8` (verify string) 5, `PL-G21K` (diff-text intent) 3, `PL-BHVM` (ref
   landing) 7, `PL-4Q9B` (clone trusted as remote) 5, `PL-HWW1` (gate prose) 7,
   `PL-G424` (apparatus drift) 8 or more, plus `PL-TZ7T` (duplicate filing) 2.
   Spent, and holding: `PL-6T44` (the fix in `PL-PQC7` held), `PL-9HD1`, the
   id grammar, and the platform palette.
2. **Generators no head named.** Recorded this session as live on the open
   item closest to the fix:
   - `PL-4W2L` (G21K's assertion half)
   - `PL-R808` (BHVM's landing test)
   - `PL-XYQW` (stored `pr:`, 23 items across the store)
   - `PL-WFFX` (merge-client parameters)
   - `PL-RFHH` (gate facts in ROADMAP prose)
   - `PL-NGBM` (no invocation object in `cli.py`, 9 items)
   - `PL-9RFP` (git failures that collapse to "no")

   Filed this session for the next one to head: `PL-1P5V` (verify string),
   `PL-WNCT` (session end strands captures) and `PL-G40Z` (fix-now test 2 turns
   repairs into items). Smaller clusters still unheaded:
   - `doc_check` reads a citation from how the text looks (6)
   - the citation rule's scope is restated per check (4)
   - wrapped prose is read one line at a time (3)
   - tools restate docket primitives (3)
   - `touches` drift (4)
   - adopted constants never replayed (4)
   - conventions adopted without a migration (about 9)
3. **Inflow the rules and the additions create, not defects.**
   - 36 of 161 are housekeeping records: 9 release cuts, 7 triage passes and
     about 10 recoveries.
   - 99 of 161 were filed inside another item's merge. The fix-now tests split
     sibling fixes into items.
   - At least nine apparatus changes were requested or ratified on 09-20 and
     09-21. The generator rule alone was re-specified four times in five days,
     and its tail is 24 items, this one among them.

   `PL-04KR`'s expectation was conditioned on no new functionality being
   added, so it has not yet been tested.

**Machinery defects found by the pass**, each a candidate for
`impairs-generators:`:

- `PL-TH9K`: closed heads are never asked for a verdict.
- `PL-BBT8`: `show` ranks a dropped live head.
- `PL-DSPM`: a misspelt `root_cause_of:` vanishes.
- `PL-RX3H`: recurrences never chain across items.

`PL-5DPF` also lacks the field it qualifies for.

**Done when.** The triage step is on the base, and every generator the first
pass establishes is recorded with `root-cause-of:` and a `generator:` verdict
or put to the owner.
