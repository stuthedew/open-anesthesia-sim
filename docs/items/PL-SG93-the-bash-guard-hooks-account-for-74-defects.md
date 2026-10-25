---
id: PL-SG93
title: The Bash guard hooks account for 74 defects across 100 items, but nothing records what they block, so their cost cannot be weighed against what they prevent
priority: P2
effort: M
status: needs-decision
classes: infra
feature: defect-review-2026-10
touches: .claude/hooks
deferred-from: v0.7.0 - a workflow measurement that waits on the owner's choice of collection route; no v0.7.0 feature reads it
added: 2026-10-19
payoff: each Bash guard hook either shows what it blocked in return for its defect cost, or is simplified or retired
verify: grep -qE '^\*\*Block counts\.' docs/items/PL-SG93-*.md
---

**Problem.** The Bash guard hooks account for 74 defects across 100 items, but nothing records what they block, so their cost cannot be weighed against what they prevent

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Evidence.** Items whose `touches` include `.claude/hooks/` number 100, and 74 of them are defects, filed mostly in the week of 2026-09-21 (38). `PL-61FT` (the guards decide what a command does from its spelling) re-entered 8 times and closed by recording known gaps in a table rather than fixing more spellings. Nothing records what the guards blocked.

**What to do.** Measure before deciding anything. Count each guard's blocks across recent session transcripts, or have the hooks log them, then weigh each guard's defect cost against what it prevented. Keep any guard against an irreversible action whatever the count.

**Done when.** Each guard has a block count and a keep, simplify or retire verdict recorded here.

**Why it matters.** A guard that blocks nothing still costs a defect every time a session meets one of its gaps. A guard against an irreversible action may be worth that cost. Without a block count, nobody can tell which guard is which.

**Generator check.** One-off. The 74 defects are `PL-61FT`'s mechanism (drained 2026-09-27). This item measures them and misreads nothing. Record the counts under a `**Block counts.**` heading here.

**Measurement attempt, 2026-10-25.** The guards' refusals are recorded in each
session's transcript, as `hook_response` events whose output carries
`"permissionDecision": "deny"`. They can be read through `list_events` from the
`claude-code-remote` MCP server, 100 events a page. A sample of 12 ordinary
sessions from 2026-10-17 to 2026-10-25 was drawn: every fourth of the 52
non-thread sessions in the ledger that cost at least $2.50. Reading it failed
for a reason no script can get around. A page larger than the tool-output limit
is saved to a file that a script can count. A smaller page comes back inline,
and copying it into a file means a model retyping 30 to 50 KB of JSON, which is
neither cheap nor faithful. About half the pages were inline. One session was
read in part: 5 of at least 8 pages, 48 minutes of work, about 22 Bash calls,
no guard refusals and one auto-mode classifier refusal. That is too little to
weigh any guard.

Projects threads add nothing to the count. A thread in this project runs none
of the repository's hooks (`PL-CR81`), so its guards refuse nothing.

**Decision needed.** How should the block counts be collected? Two routes:

- **A local log copied at record time.** Each guard appends one line per
  refusal to a local log, and `bin/docket record` copies the branch's lines
  into a tracked `docs/hook-blocks.tsv`. A line holds the guard's name, the
  time, the session id and which rule refused. Command text is left out,
  because a command can carry a token. A session that never records a pull
  request loses its lines with its container, which undercounts, but most
  working sessions record one. Cost: a few lines in each of the six guards,
  the tracked file, and a step in `record`. After four weeks each guard has a
  count and a verdict here.
- **Record the inability and decide from defect cost alone.** Keep the two
  guards against irreversible actions (`no-prune-guard.sh` and
  `direct-merge-guard.sh`) whatever their count, and leave the others as they
  are. This costs nothing, but it cannot tell a guard that blocks nothing from
  one that blocks often.

**Recommendation:** the local log copied at record time. It is the only route
that produces the count this item exists for, and its cost is small and paid
once. The choice is the owner's because it is a new mechanism in the workflow
lane. Stuart's request to complete the workflow items lifts the generator pause
for it.
