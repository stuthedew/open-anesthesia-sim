---
id: PL-JYTJ
title: Cut v0.5.2 from the work finished since v0.5.1: the one-id-grammar and remote-ref-deletion fixes, with core's only movement proved docstring-only rather than asserted
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.3
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-21
closed: 2026-09-21
pr: 881
payoff: the fifteen items finished since v0.5.1 ship under their own number and stop being re-offered in every session digest, and the first release since the MVP whose simulator tree is not byte-identical says exactly what moved in it
verify: grep -q "^version = \"0.5.2\"" pyproject.toml
---

**Problem.** Fifteen items have closed since v0.5.1 and are re-offered in every
session digest. They complete two features - `one-id-grammar` and
`remote-ref-deletion` - and are apparatus and documentation work throughout;
none of them is a milestone, so this is a patch release rather than a
capability boundary.

## What this release contains, by tree object - and why this one needed a proof

Every release since the MVP has been able to say "nothing computational moved"
by tree identity alone. **This one cannot, and that is the finding worth
recording.** Three of the four simulator objects are byte-identical at v0.5.1
and at the cut:

| Object | v0.5.1 | cut | |
| --- | --- | --- | --- |
| `src/anesthesia_sim/data/` | `ab3499fd` | `ab3499fd` | identical |
| `src/anesthesia_sim/core/` | `ca5a3542` | `061714b0` | **moved** |
| `src/anesthesia_sim/app/` | `01bc2d90` | `01bc2d90` | identical |
| `tests/reference/` | `a1848300` | `a1848300` | identical |

`core/` moves in exactly two files, `governing_equations.py` and
`uptake_system.py`, +6/-6 between them, and every changed line is inside a
docstring or module prose: `PL-316G`'s conversion of possessive document
citations to the section-mark form, so that `tools/doc_check.py` can hold them.

**The claim is proved rather than asserted.** Reading a diff and judging every
changed line to be a comment is exactly the judgment the safety-critical
standard says not to rest a clinical claim on. Both files were parsed at each
revision, every docstring `Constant` replaced with a fixed sentinel, and the
resulting ASTs compared - comments never reach an AST at all. Both are
identical, so **no executable statement moves in `core/` in this release**: no
equation, coefficient, parameter, numerical method, solver step or displayed
clinical value. `src/anesthesia_sim/data/` resolving to the same object is the
independent half of that, covering every stored scientific value.

## What the cut was shipped as, and what that was chosen over

Three sibling sessions were `RUNNING` when this cut was taken - one on roadmap
entry 20, one on `PL-PBP5`/`PL-J3WK`, one recovering the `PL-HWV1` withdrawal
onto `claude/magical-goodall-9xbbge`. **Ship the cut as taken**, on `PL-V065`'s
ratified precedent (project owner, 2026-09-21) rather than as a fresh decision:
while sibling sessions keep landing pull requests, any regenerated set of notes
goes stale before it can merge, and re-running `make release VERSION=0.5.2`
resumes the same cut under the same number and would pick the newly-`done`
items up.

The cost is stated rather than smoothed over: anything merging between this cut
and the tag sits inside the `v0.5.2` tag without being named in its notes, and
is cited under v0.5.3. `PL-4B1G` and `PL-V065` are the same shape already
accepted here - a cut cannot stamp itself, so each release's own cut item ships
in the release after it.

## Stranded work deliberately not recovered here

`bin/docket stranded` reports the `PL-HWV1` withdrawal as living only on
`claude/magical-goodall-9xbbge`, whose pull request `#873` merged at 20:53:19Z
with the withdrawal commit authored 49 seconds later. It is **not** this item's
to recover: `list_sessions` shows the session that wrote it still `RUNNING` on
that branch, reporting "rebased withdrawal commit; new PR for citation fix".
Recorded here so the next session reading `stranded` does not file it twice.

**Done when.** `pyproject.toml` reads 0.5.2, `docs/releases/v0.5.2.md` holds the
notes, `ROADMAP.md` has the version-table row with the `current baseline` mark
moved onto it and a baseline section, `make check` is green, and the tag is run
by the project owner on the explicit merge-commit sha.
