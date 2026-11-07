---
id: PL-WHG6
title: "Cut v0.4.18: the release where the project checked what it tells the next session"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.19
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-13
closed: 2026-09-13
pr: 529
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.18"' pyproject.toml && test -f docs/releases/v0.4.18.md
---

**Problem.** Seventeen items finished since v0.4.17 and none had shipped, so
`bin/docket next` and the session-start digest asked every session to offer a
release before taking new work.

**Why it matters.** Filed before the cut rather than after it, per `CLAUDE.md`'s
rule that repository work taking a commit of its own is filed first: every
in-flight guard this project has matches a `PL-` id, and a release cut has none
until somebody starts one. `PL-66FP` is what the unfiled version cost - two
sessions cut v0.3.7 within the hour and the second was discarded at the merge.
The live session list was checked before starting and no other session was
cutting.

**Done when.** `pyproject.toml` is at 0.4.18, `docs/releases/v0.4.18.md` exists,
`ROADMAP.md` carries the version-table row, the moved `current baseline` mark
and the baseline section, and `make check` passes.

**What the release turned out to be about.** Twelve of the seventeen entries are
a statement this repository makes about itself - to a session or to a reader -
that was wrong, missing or unreachable, and none of the twelve was a wrong
calculation. `ROADMAP.md`'s baseline section carries the account.

**The "nothing moved" claim is a measurement here rather than a byte
comparison**, because `PL-9SH6`'s accessor rename reaches `core/` and the
reference suite and so rules byte-identity out. Measured instead, across
`v0.4.17..HEAD`: `src/anesthesia_sim/data/` and `.github/` byte-identical;
`core/` carrying the same 401 numeric literals as a multiset, so the rename
moved no number; and no numeric literal removed from `tests/reference/` (1,405
to 1,445, every addition new), so every pinned published and canonical value
still stands.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.18 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Twelve of the seventeen entries are a statement this repository makes — to a session or to a reader — that was wrong, missing, or unreachable: the gate's own counts and deferrals (`PL-SL70`, `PL-9S30`), a recommendation that never said how the item it named related to the gate (`PL-J790`), `docs/MODEL.md`'s symbol map (`PL-H46J`, `PL-212V`) and a margin its prose called comfortable at three percent (`PL-WT07`), the architecture pointer no session was shown (`PL-39K7`), the apparatus test bar that was never written down (`PL-N6Y0`), a v0.4.0 Goal still in the present tense about problems since fixed (`PL-DXQC`), and the README's scope word (`PL-XF89`). Two go further and measure reception instead of correcting prose: `PL-VV16` instruments which item files sessions actually open, and `PL-NB35` gives failed approaches a bounded startup tier so they are not rediscovered. **Nothing a learner can observe was recomputed**, and this release says so with a measurement rather than a byte comparison: `src/anesthesia_sim/data/` and `.github/` are byte-identical to `v0.4.17`, and `core/` holds exactly the same 401 numeric literals before and after, so `PL-9SH6`'s accessor rename across every compartment moved not one number. The reference suite is *not* byte-identical this time, because that rename reaches it — what is measured instead is that no numeric literal was removed from it, so every pinned published and canonical value still stands. `PL-V6M0` is the one safety entry: `_apply_setting` caught the exception hierarchy's base class, so a `SimulationExecutionError` would have been reported as a refused setting over a run that kept producing readings. Seventeen items.
