---
id: PL-G7RD
title: Cut v0.4.25 from the ten finished items, renumbering the Qt port's section to v0.4.26 as ROADMAP.md's own risk paragraph provides for
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
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
