---
id: PL-G7RD
title: Cut v0.4.25 from the ten finished items, renumbering the Qt port's section to v0.4.26 as ROADMAP.md's own risk paragraph provides for
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.26
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-14
closed: 2026-09-14
pr: 576
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.25"' pyproject.toml && test -f docs/releases/v0.4.25.md && ! grep -q 'v0.4.25 - the interface moves to Qt' ROADMAP.md
---

**Problem.** Cut v0.4.25 from the ten finished items, renumbering the Qt port's section to v0.4.26 as ROADMAP.md's own risk paragraph provides for

**Approved by the project owner, 2026-09-14**, after the pre-port survey put
it first: ten finished items sit unshipped since `v0.4.24` (`bin/docket
release --dry-run`), the digest withholds the offer only because the
*mechanical* bump is `0.5.0` and that number is reserved, and `v0.4.24` is
tagged on `origin` so the refusal-on-untagged-predecessor does not bind.

**Why it matters.** The Qt port is the one stretch during which nothing is
releasable: once `app/` is half-ported, no tag can be cut until parity is
reached. Left uncut, the ten - the fork spine (`PL-TFX5`, `PL-J2TD`,
`PL-ZMRT`, `PL-3LZB`, `PL-B9PY`) and five workflow items - sit untagged for the
whole of a 5 133-line rewrite, and `PL-3LZB` is `P1` `safety`. A tag also
gives the port's definition of done a fixed referent: "every capability the
Flet build has" then means `v0.4.25`, immutable and diffable, rather than
whatever `origin/main` was on the day. The ten cross no capability boundary
(`PL-XJ37` records that nothing in v0.5.0's scope yet lets a learner take a
fork), so § "Versioning decision" makes this a patch; Gate 1 has nothing left
it can clear, so § "The cadence"'s no-interim-release rule does not bind.

**What the cut carries with it, all in `ROADMAP.md`, because the number it
takes is the one the port's section holds.** § "the interface moves to Qt"
records this as its one risk and its disposition - "this section's heading
moves to the next free number and nothing else moves with it ... a rename,
not a re-scope" - and every `blocked-by` on a port-dependent item already
names a port item, verified across all nine, so the rename is textual. Under
`PL-YVM1`'s rule the number survives only in the heading, the timeline row and
the `§` citations `tools/doc_check.py` resolves; running prose in the section
names the port by name. Three corrections ride the same pass because they sit
in the lines being edited: the v0.5.0 timeline row records that five of its
Required-scope ids shipped early in the `v0.4.x` track (the precedent sentence
already there covers four others); planned-milestone item 34's "not recorded
here" is replaced by the decision `PL-8VL1` recorded inside the port's
Required scope; and the sentence crediting `tools/import_boundary_check.py`
with a Flet count it does not check cites `PL-9KDK` instead.

**Done when.** `pyproject.toml` and `uv.lock` read `0.4.25`,
`docs/releases/v0.4.25.md` exists, the version table carries the row and the
"Current baseline" section stands on it, no line of `ROADMAP.md` reads
"v0.4.25 - the interface moves to Qt", `make check` is green, and `v0.4.25` is
tagged on the merge commit on `origin/main`.

## Cut 2026-09-14

`make release VERSION=0.4.25` stamped twelve items - the ten the dry run
listed and the two closures already on this branch, `PL-YVM1` and `PL-T7PY`,
so the release carries its own cleanup - and relocked `uv.lock`. The port's
section moved to `v0.4.26` in the same commit, with its running prose named
by name under `PL-YVM1`'s rule and its `§` citations in eleven item files
moved with the heading, which `tools/doc_check.py` proved. The three
corrections named above landed with it, and Required-scope item 4 now states
what `PL-JRS3` measured rather than the premise it refuted.

**Docs swept:** `ROADMAP.md` (the row, the baseline, the port section, the
v0.5.0 row, item 34), `docs/releases/v0.4.25.md` (generated), `docs/MODEL.md`
and `docs/ARCHITECTURE.md` (checked: neither names a release version or the
port by number), `README.md` (checked: no version claim to move).

The tag is the project owner's, after the merge, and is the last line of
"Done when".

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.25 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. The row's first sentence, which stays in the table, reads: "**The release where the run became forkable underneath the interface, and the last Flet build was tagged.**"

> A patch, because a learner cannot reach the first half: `PL-XJ37` records that nothing in the interface lets a learner take a fork or select between runs, so a case runs as it did in v0.4.24 and every displayed value is the same value. Three measurements: `src/anesthesia_sim/data/` resolves to `6960c78` here as at `v0.4.24`, `v0.4.23` and `v0.4.22`, unmoved across four releases; eight files under `src/` change, three in `core/`, and **every numeric constant the diff adds to executable code is a 0, a 1 or a 2** - an index, a count, a lower bound - measured by parsing both revisions with `ast` and diffing the constants; `tests/reference/` changes in one file and the change is the fork-reproduction probe list moving onto the case's own axis, no published-reference expected value with it. **A branch's definition opens at the fork instant on the case's own axis** (`PL-ZMRT`, project owner, 2026-09-14): with a fork at 900 s, `(900.0 + 1e-6) - 900.0` is `9.999999974752427e-07` rather than `1e-6`, so a child asked for its own first microsecond propagated over a different interval from its parent; after the change the branch agrees with its parent at **all 601 shared case instants**, where a definition opened at its own zero differs at **354 of 601**, and `PL-2R2C` dissolved with it - a branch's drawn columns went from 2 of 8 shared with the trunk to 8 of 8. `SimulationController.origin_s` and both subtractions are gone. **`PL-3LZB` is `P1` `safety` and had to land first**: `RunDefinition`'s lower bound was the literal `0.0` and `_segment_index_at` wrapped, so a definition opening after zero answered from its *last* segment instead of refusing - `state_at(0.0)`, `state_at(100.0)` and `state_at(599.9)` all returned 0.005664 alveolar fraction on a definition opening at 600 s, and `evaluate_anchored(0, 500, 100)` drew a varying curve across a span the run did not exist for. A strict no-op on the v0.4.24 tree and reachable the moment a branch opens at 600 s. `PL-TFX5` forks a run at any control-input event, flat rather than as a tree; `PL-J2TD` is what a fork resumes into, a live run opened at a canonical keyframe state guarded by `require_canonical_state` and `resume_at`, advancing by the ordinary path; `PL-B9PY` decomposes `SimulationView` so two runs render, the 211 existing tests unchanged except for reaching the sole run through `view.runs[0]`. Five of the twelve are v0.5.0's own Required-scope ids shipped early in the `v0.4.x` track. **`PL-RKWB` moved the Qt port ahead of v0.5.0's display half**, and this cut takes the number that section held, as its own risk paragraph provided for: the heading moved to `v0.4.26` and nothing else moved with it - because `PL-YVM1` found the earlier renumber had left **51 references in 29 open items, `app/theme.py` and `docs/MODEL.md`** naming the port `v0.5.1`, all six of its build items among them, invisible to `tools/doc_check.py` because none was a section citation, and adopted the rule that outside this file [`ROADMAP.md`] the port is named by what it is, never by a version. `PL-6T4L` stopped the digest offering v0.5.0 with 8 of 22 scope entries open; `PL-H27D` corrected eight statements `PL-ZMRT`'s own sweep never reached; `PL-5328` re-briefed `PL-RD3B` against the tree `PL-2FM6` left; `PL-1V3X` is the v0.4.24 cut.
