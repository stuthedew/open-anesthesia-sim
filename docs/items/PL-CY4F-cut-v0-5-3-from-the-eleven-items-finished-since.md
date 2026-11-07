---
id: PL-CY4F
title: Cut v0.5.3 from the eleven items finished since v0.5.2: the four gates that were reporting a result they had not established, with the simulator's stillness readable off one tree hash
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.4
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-22
closed: 2026-09-22
pr: 888
payoff: the eleven items finished since v0.5.2 ship under their own number and stop being re-offered in every session digest, and the release whose theme is gates reporting unearned success states its own no-computational-movement claim from a tree hash rather than from an argument
verify: grep -q "^version = \"0.5.3\"" pyproject.toml
---

**Problem.** Eleven items have closed since v0.5.2 and are re-offered in every
session digest. They complete one feature - `instruction-staleness-audit` - and
are apparatus and documentation work throughout; none is a milestone, so this
is a patch on § "Versioning decision"'s test rather than a capability boundary.

## What this release contains, by tree object

The whole of `src/` is byte-identical at v0.5.2 and at this cut, so the
no-computational-movement claim needs no argument at all this time:

| Object | v0.5.2 | cut | |
| --- | --- | --- | --- |
| `src/` | `422b27e1` | `422b27e1` | identical |
| `src/anesthesia_sim/core/` | `061714b0` | `061714b0` | identical |
| `src/anesthesia_sim/data/` | `ab3499fd` | `ab3499fd` | identical |
| `src/anesthesia_sim/app/` | `01bc2d90` | `01bc2d90` | identical |
| `tests/reference/` | `a1848300` | `a1848300` | identical |
| `.github/` | `6f63412a` | `da3c9510` | **moved** |

**No equation, parameter, constant, numerical method, solver step or displayed
clinical value moves.** v0.5.2 could not say that from a hash - its `core/`
tree had moved on a docstring, and the claim had to be established by parsing
both files at each revision and comparing ASTs. Here one object answers it, and
the contrast is worth recording: the proof v0.5.2 built is what a release has to
do when the hash does not answer, not what it does instead.

`.github/` is the one shipped tree that moves, and it moves for the release's
own reason: `PL-PBP5` gives `quality.yml` the three standard-library checks that
had no CI backstop.

## The theme, and why it is not a coincidence

All four defects in the release are one shape at a different altitude - a check,
a gauge or a record reporting a result it had never established. `PL-D0W8` (a
pipeline's exit status is the last command's, so a red tree commits as green),
`PL-J3WK` (the local gate passing `verify:` commands that can prove nothing),
`PL-PBP5` (CI passing a tree `make check` would refuse), `PL-44DG` (the resident
size gauge 7.2% low on payloads it never counted). The three documentation items
are the same failure in prose rather than in code: `PL-R5HK`'s hook count,
`PL-G7ST`'s provenance claim inside the item about provenance, and `PL-K4BN`'s
eight `pr:` numbers whose absence was training sessions to skim the advisory
block. The baseline section in `ROADMAP.md` is written around that rather than
around the class labels.

## Shipped as cut

`list_sessions` showed no sibling session holding a release when this cut was
taken - the one that raised v0.5.3 in its closing block is `ARCHIVED` and was
waiting on the project owner's answer, which arrived as this session's prompt -
and `bin/docket flight` reported no branch claiming an item. So this is not the
two-sessions-one-release case `PL-66FP` records.

The cut ships as taken, on `PL-V065`'s ratified precedent (project owner,
2026-09-21): anything merging between this cut and the tag sits inside the
`v0.5.3` tag without being named in its notes, and is cited under the next
release. This item closes there for the same structural reason `PL-JYTJ` closes
under v0.5.3 - a cut cannot stamp itself.

**Done when.** `pyproject.toml` reads 0.5.3, `docs/releases/v0.5.3.md` holds the
notes, `ROADMAP.md` carries the version-table row with the `current baseline`
mark moved onto it and a baseline section, `make check` is green, and the tag is
run by the project owner on the explicit merge-commit sha.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.3 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Eleven items, all apparatus and documentation, and a patch on § "Versioning decision"'s test because no capability boundary is crossed. **Nothing in the simulator moved, and this cut says so by tree identity alone**: `src/` resolves to `422b27e1` at v0.5.2 and here, so `core/` (`061714b`), `data/` (`ab3499f`) and `app/` (`01bc2d9`) are byte-identical and `tests/reference/` (`a184830`) with them - the sentence v0.5.2 had to prove by comparing ASTs, because its `core/` tree had moved on a docstring. The eleven items' own work is 35 files, +2,818/-113, of which 14 are item files, and `.github/` is the one shipped tree that moves (`6f63412` to `da3c951`), for the release's own reason. **Four defects, one shape at four altitudes.** `PL-D0W8`: a session running `make check 2>&1 | tail` reads `tail`'s exit status, always 0, so a red tree is reported as green - it happened on `PL-2JRC`, also in this release, and the false claim reached both the commit message and the pull request body. The rule is a `PreToolUse` deny hook rather than resident prose because it has to fire when a command is *written*, which no read precedes, and inside exploration subagents, which carry no resident context but do run hooks; it recommends `set -o pipefail`, one token, so a session keeping a passing gate's output out of its context has no reason to route around it. It refused its own author on its first firing, right about the separator and wrong about the command, so reading `$?` in the segment immediately after the separator is now accepted. `PL-J3WK` and `PL-PBP5` are one seam from opposite sides: `make check` ran `bin/docket check` bare while CI ran it `--verify`, so a `verify:` command that can prove nothing - a literal `true`, or one recorded against three open items - passed every local gate and turned CI red after review had started; and `quality.yml` enumerated its own steps, leaving `dead_ends.py`, `type_ignore_check.py` and `possessive_section_check.py` with no CI backstop. Both halves were live: of 11 red runs in the 100 most recent `pull_request` runs, **6 were the `--verify` replay and 5 were at a step `make check` also runs**. The two statically decidable questions moved into the bare check and the replay stayed where it is, on a count that came back **zero and zero** against 220 open commands, so the rule catches the regression `PL-4W2L` had already produced rather than a backlog; and the gate lists are deliberately *not* merged - the floor section runs the standard-library tools before `uv` exists, which is what proves they need none - so `check_gate_parity` reconciles them in both directions instead, refusing any asymmetry not in `GATE_ONLY`, which holds exactly one entry. `PL-44DG`: the gauge the project consults about its own resident cost was **7.2% low**, counting neither the SessionStart digest nor the `docket` skill description, both resent every turn - and the digest is the half that grows with no edit to any instruction file, carrying the dead-ends list. **`instruction-staleness-audit` completes, 3 of 3**, against the failure that outlives a size problem: a rule that is long costs attention, while one that was true when written and is false two years later gets *obeyed*. `PL-T5K1` reports the dated lines past a threshold as a grooming advisory on `make docket`, dated by the newest date on each line so re-verify-and-re-date discharges an entry and the report can reach zero; `PL-PHK4` makes the threshold `instruction_stale_days`, defaulting to 90 (project owner, 2026-09-21, ratified, over 180), tested against synthetic dates because it cannot fire on this tree - all 74 dated assertions across 17 files are under 30 days old, the project being 30 days old. Age is a proxy for staleness, and the brief records that rather than smoothing it. **The rest is the record telling a reader something untrue.** `PL-K4BN` backfills the eight `pr:` numbers `origin/main` was owed, each verified against the squash subject naming its id - 8 of the 13 advisories that morning, 5 now - and records why they accumulated: "let it ride the commit you are already making" is right while commits are flowing and silently wrong once nobody has one in hand, which is the routed-around test rather than tidiness. `PL-R5HK` corrects `docs/ARCHITECTURE.md`'s wired-hook count, five where `.claude/settings.json` wires six, wrong since `item_read_log.py` landed and found twice independently. `PL-G7ST` removes a false provenance claim from inside the item about provenance: `PL-M7W1` said #880's squash subject was frozen at arm time and the commit carrying the sentence is its own disproof, the renamed title having landed, which narrows the hazard to auto-merge performing the merge itself - a hand merge composes from the live title, and is the ordinary case here. `PL-2JRC` is the triage pass, and `PL-JYTJ`, the cut of v0.5.2, closes here because a cut cannot stamp itself.

<!-- absent: item_read_log.py -->
