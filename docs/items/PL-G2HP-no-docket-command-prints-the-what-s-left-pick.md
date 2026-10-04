---
id: PL-G2HP
title: No docket command prints the what's-left pick list - the gate's open entries grouped by feature with sizes, lanes and waiting decisions, and the Required-scope entries that can start now with what each unblocks - so every report rebuilds it by script
priority: P2
effort: M
status: ready
classes: feature, infra
touches: subprojects/docket/src/docket/picks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_picks.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/skills/docket/modes/picking.md, docs/items/PL-QWF8-a-report-on-a-frozen-gate-cannot-read-every.md
added: 2026-10-04
payoff: a what's-left answer is one command: the gate's open work by feature with sizes, lanes and waiting decisions, and the build entries that can start now, where a helper used to rebuild it by script for every report
verify: grep -q 'def test_picks_collapses_a_one_entry_feature_into_its_lanes_line' subprojects/docket/tests/test_picks.py
---

**Problem.** No docket command prints the what's-left pick list - the gate's open entries grouped by feature with sizes, lanes and waiting decisions, and the Required-scope entries that can start now with what each unblocks - so every report rebuilds it by script

**Asked for.** The coordinator offered on 2026-10-04 to file an item for a
`bin/docket` command printing the "what's left" pick list, and Stuart answered
"yes, but build now as well" in the project thread at 15:14 UTC (project
owner, 2026-10-04). It is the Projects trial's Order item 20.

**What was observed.** That morning's "what's left" answer took a helper about
11 minutes, of which docket's own commands ran about 30 seconds (`wave` 0.5 s,
`status` 1.8 s, `next` 1.9 s). The rest was a clone, a fetch of every branch,
and a script grouping `bin/docket wave`'s open gate ids by each item's
`feature:`, taking lanes from `Item.lane` and the build from
`docket.roadmap.parse_milestones`. `next` gives three picks, one per lane, and
`wave`, `status`, `gate` and `digest` each give a part, so the list the
project instructions' Report paragraph asks for on every such question is
rebuilt by hand each time.

**Why it matters.** Every part of that list is decidable from the store and
the roadmap, which is what `CLAUDE.md` § "Prefer deterministic tooling over
repeated model work" says belongs in code; summarizing counts is the same win
as deciding. Only a feature-level sentence of what a line buys, and which line
to recommend, are judgment, and those stay the reply's.

**The pause on new mechanisms does not hold it.** `CLAUDE.md` § "What this
project is" captures and does not build a new command while an open item
carries `generator: live`, which `PL-R417` did when this was filed. Its last
sentence lifts that for a request from the project owner, for that request
(`PL-6Q9L`), and Stuart's "build now" is one. Nothing else is lifted.

**What it prints, decided at triage.** Read from the Report paragraph and from
the list the coordinator built by hand on 2026-10-04, which these rules
reproduce:

1. *Population.* The open entries the current gate can clear,
   `GateStatus.clearable` exactly as `bin/docket wave` computes it, so the
   count matches `wave`'s "N this gate can clear". Entries the milestone
   clears itself and entries blocked outside the gate are counted in one
   closing line, never offered.
2. *Grouping.* By each item's `feature:`. A feature holding two or more of
   those entries gets a line of its own, largest first. A feature holding one,
   and items with no feature, collapse into one line per lane, in
   `plan.GATE_LANES` order: product, workflow, crossing, unplaced.
3. *Each line.* Its lane, or the mix where a feature's items differ
   (`product 3, workflow 1`). The open count with sizes (`plan.effort_total`).
   How many await a decision (`plan.awaits_decision`), are blocked, or are in
   flight on a branch (the claims `next` excludes). The line's next pick,
   which is `plan.recommend` over the line's items alone, with its `payoff:`.
   The member ids follow on one line, so a name given back maps to items.
4. *Build.* The `Required scope` entries of the gate's milestone
   (`MilestoneSection.scope_entries`, numbered from 1) holding an item
   `plan.offerable` now, one line each: the entry's bold lead as its name, the
   startable ids with sizes, and how many of the scope's other open items wait
   on it through `blocked-by`, transitively and directly. Measured 2026-10-04:
   entry 1, `PL-1FT6` (L), holds 21 of the 25 open (8 directly), and entry 9's
   `PL-VN6M`, `PL-CNCF` and `PL-PGZF` (M each) hold none. While the beat is
   clearing the gate, the section says the roadmap clears the gate first, with
   the gate's open count.
5. *A live generator head* (open, and `model.ranks_as_generator`) leads with a
   line of its own, since `next` ranks it above all of these.
6. *At most eight lines*, the Report paragraph's cap. Heads, build entries and
   lane lines are placed first; feature lines fill what is left, largest
   first, and a feature that does not fit folds into its items' lane lines.
   Build entries past the cap collapse into one line.
7. *Fails visibly.* No recorded gate, an unreadable plan, or a gate naming an
   id the store lacks is said and exits non-zero, as `wave` does.
8. *Reads as `next` does.* It fetches once, ranks from the default branch's
   copy of an item moved since the fork (`cli._from_base`), and says which
   refs went unread.

On 2026-10-04 that gives eight lines: `PL-R417`; `qt-port` (product 3,
workflow 1; 2 in flight); `stranded-report-fidelity` (3 M, workflow); the
product, workflow and crossing lines (7, 11 and 1, `PL-VV6N` the one
decision); entry 1; entry 9. `provenance` (2) folds into the product line.

**Done when.** `bin/docket picks` prints that list in one call. Tests in
`subprojects/docket/tests/test_picks.py` pin the grouping and the one-entry
collapse, lanes, sizes, the decision and in-flight counts, the build entries
and their wait-on counts, the eight-line cap and the visible failure.
`subprojects/docket/README.md` documents the command and
`.claude/skills/docket/modes/picking.md` names it for "what's left".

**Generator check.** Work the owner asked for: a new reading surface, not a
reader misreading a fact. `bin/docket new` matched this capture to `PL-QWF8`
(a frozen gate's report cannot read every open entry's lane from docket) on
the shared path `render.py` alone, and that filing is withdrawn under this
item. The two are related and are not one problem: this prints a lane for
each entry the gate can clear, while `PL-QWF8`'s two, `PL-5B1N` and
`PL-B396`, wait outside it, so building this leaves `PL-QWF8` open.

**Near items, read 2026-10-04.** `PL-7B3G` (a gate filter on `concurrent`'s
batch) and `PL-CM40` (one command for a closing block's refreshed picture)
answer other questions, and this extends neither.

**Next steps, for the thread that builds it.** Written 2026-10-04 by the
thread that filed and triaged it, which stopped at its context budget (179k of
spend before filing) rather than start the build; the triage merges on its
own as an item-only pull request.

1. After that pull request merges, branch from `origin/main`, fetch every
   branch, and run `bin/docket flight` and `bin/docket concurrent PL-G2HP`. At
   15:26 UTC it named no file shared with the Order's item 19 (`PL-DSMK` and
   `PL-MFVV`, on `claude/r417-dsmk-mfvv-2mule9`). `PL-MFVV`, untriaged then,
   declares `subprojects/docket/tests` whole, which covers this item's two
   test files: same area only. Read the observed section again. If item 19's
   branch has changed a file this item touches, start after its pull request
   merges, as the Order requires.
2. Claim it (`bin/docket claim PL-G2HP` with the attribution trailers), and
   open a draft pull request on the claim commit.
3. Build `picks.py` pure: a dataclass for the list and one function taking
   the items, the `Wave`, the in-flight ids and the config. Then
   `render.format_picks` and `cli.cmd_picks`, with `add("picks", ...)` beside
   `wave` in `build_parser`. Reading is `cmd_next`'s: `_from_base`, `_plan`,
   `_flight`, then `_say_read_from_base`, `_say_unread` and `_say_snapshot`.
4. Add `("picks",)` to `READ_ARGV` in `subprojects/docket/tests/test_cli.py`.
   `test_every_read_command_names_what_its_snapshot_rests_on` refuses a
   subcommand the census does not place; check the `--no-git` census beside
   it too.
5. Tests per Done when, then the README section and its line in the command
   block, and the `picking.md` line. `make check`, then `bin/docket verify
   --self PL-G2HP`, and `bin/docket arm` before arming.
