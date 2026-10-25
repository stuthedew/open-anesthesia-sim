---
id: PL-SG93
title: The Bash guard hooks account for 74 defects across 100 items, but nothing records what they block, so their cost cannot be weighed against what they prevent
priority: P2
effort: M
status: ready
classes: infra
feature: defect-review-2026-10
touches: .claude/hooks, tools/hook_blocks.py, tools/rules_paths_check.py, tests/unit/test_hook_blocks.py, tests/unit/test_tools_portability.py, tests/conftest.py, docs/hook-blocks, docket.toml, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_record_command.py, subprojects/docket/README.md, docs/apparatus.md
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

**Decided, 2026-10-25.** The local log, copied into a tracked file when a pull request is recorded (project owner, 2026-10-25, ratified, over recording the inability and deciding from defect cost alone). Stuart's words: "Agree with Recs except for 3", where 3 was `PL-5S71`'s run.

**Built, 2026-10-25.** Every guard now refuses through `hook_input.deny`, in `.claude/hooks/hook_input.py`. It appends one tab-separated line to `~/.local/state/open-anesthesia-sim/hook-blocks.tsv`: the time in UTC, the session id, the guard's name and the rule that refused. The command and the reason are left out, because a command can carry a token. A log that cannot be written is skipped, so a refusal still refuses. The guards and their rules are these.

- `no-prune-guard`: `delete-push`, `prune`, `delete-ref` and `remove`, joined with `+` where one call trips several.
- `direct-merge-guard`: `unreadable-call`, `no-answer` and `admins-unbound`. Its refusal when python3 cannot run is not logged, because logging needs python3.
- `floor-interpreter-guard`: `floor-interpreter`.
- `gate-status-guard`: `arm-piped` and `status-swallowed`.
- `push-check-guard`: `checks-failed`.
- `owner_ask_guard`: `bare-read-ask` and `coordinator-ask`.
- `pr-body-email-guard`: `email-address`, logged since `PL-HHKC` (#1802), below.

`bin/docket record N` now runs `docket.toml`'s new `record_command` once it has written the number, and this repository sets it to `python3 tools/hook_blocks.py copy`. That copies each line no file under `docs/hook-blocks/` holds yet into `docs/hook-blocks/<branch>.tsv`, named for the branch being recorded. Only that branch writes its file, so two branches' copies do not conflict at merge, and `count` counts a line held in two files once. Times are to the microsecond, so two refusals in one second stay two lines. A payload with no session id is a guard run by hand and is not logged. `pr-body-email-guard.sh` refused through `tools/pr_body_check.py --screen` and logged nothing until `PL-HHKC` made `screen` refuse through `deny` (#1802, merged 2026-10-25, two hours after this build). `python3 tools/hook_blocks.py count` prints each guard's and rule's refusals and sessions. The test suite points `HOOK_BLOCK_LOG` at a temporary file, so the guard tests' refusals stay out of the real log.

**The log is an outbox, not a second source** (project owner, 2026-10-25, ratified, over deleting each line from the local log once it is copied). The project owner asked whether a local log diverges from the single-source-of-truth principle. The tracked files under `docs/hook-blocks/` are the source, and `count` reads only them. The local log only holds lines until a record copies them, and a copied line never changes, so the two can differ only by lines not yet copied. Deleting copied lines would lose them whenever the record commit is never pushed. His answer: "That's fine. Keep".

**What is left.** Read the counts on or after 2026-11-22, four weeks from now, with `python3 tools/hook_blocks.py count`. Record them under a `**Block counts.**` heading here with a keep, simplify or retire verdict for each guard. Keep `no-prune-guard` and `direct-merge-guard` whatever the count, because each guards an action that cannot be undone. The counts are a floor, lowest for the guards that fire after `bin/docket record`: `push-check-guard`, `gate-status-guard` and `direct-merge-guard`. Their late refusals are copied only by a later record on the same machine, and a container that ends after one pull request loses them. A Projects thread runs no guard at all (`PL-CR81`). Weigh those three guards' counts with that in mind. `pr-body-email-guard` is counted from 2026-10-25 like the others, since `PL-HHKC`.

**Checked 2026-10-25:** nothing here can be done before 2026-11-22. The logging is on `main` and working: `python3 tools/hook_blocks.py count` already reads 14 refusals from five branches' files, from `floor-interpreter-guard`, `gate-status-guard` and `push-check-guard`. A session that picks this item before 2026-11-22 has nothing to do, and yields it. The item stays `ready`, because `blocked-by` takes an item or a milestone and no date.

**Scheduled, 2026-10-25.** A one-time scheduled task, `trig_01P9v9dUodFbP7kY8pXRFS94`, starts a fresh session at 2026-11-23 15:00 UTC (09:00 CST) to read the counts and write the verdicts (project owner, 2026-10-25, ratified, over leaving the read to whoever remembers the date). The task stores no connectors, and its session request names no repository, so its first step attaches the repository with `add_repo` and stops if GitHub tools are missing. If that session fails, the item is still `ready` and any session can do the work.
