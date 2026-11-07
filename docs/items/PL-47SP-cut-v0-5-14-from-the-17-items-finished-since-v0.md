---
id: PL-47SP
title: Cut v0.5.14 from the 17 items finished since v0.5.13
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
resource: release-train
added: 2026-09-27
closed: 2026-09-27
pr: 1156
payoff: the 17 items finished since v0.5.13 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.14\"" pyproject.toml
---

**Problem.** Cut v0.5.14 from the 17 items finished since v0.5.13

The project owner asked for it on 2026-09-27 ("cut new version"), with the
session-start digest offering 0.5.14 on 17 finished items completing
`bash-guard-bound` and `interface-pass-narrative`.

**What was checked at filing.** `git ls-remote --tags origin` shows v0.5.13 as
the annotated tag `6abf31b4` peeling to `c7fcd6f2`, the cut's own merge
(`#1141`), so the cut is not refused on an untagged predecessor. `bin/docket
flight` shows no release item claimed - its one row is `PL-384P` on
`claude/nifty-hawking-gvi5r7` - and `list_sessions` shows no other session
cutting one: the three running beside this one are a triage pass, `PL-384P`,
and `PL-FBY3`'s session confirming its own merge. `bin/docket release
--dry-run` named 17 finished items, and they match `main`'s own history: the 19
pull requests merged after `#1141`, whose ids not among the 17 are `PL-P813`,
`PL-Y04W`, `PL-MLRX` and `PL-N6JP`, all `dropped`, and `PL-5XG1`, `blocked` -
and an item not `done` ships in no release.

**The version is a patch**, on both halves of `ROADMAP.md` § "Versioning
decision": nothing a learner can reach moved, measured by tree object -
`src/anesthesia_sim/core/` resolves to `d9e3ca9f`, `src/anesthesia_sim/data/`
to `ab3499fd`, `src/anesthesia_sim/app/` to `f3c6e26e` and `tests/reference/`
to `a1848300` at both ends - and every minor from v0.6.0 up is given to a
milestone. What did move is `docs/MODEL.md`, +210 lines of prose from
`PL-WMCJ` and `PL-FBY3`: intertissue diffusion is now a named assumption and
known limitation, with the direction it biases the fat compartment, which is a
statement about the model rather than a change to it.

**Cut 2026-09-27, at 17 items**, with `make release VERSION=0.5.14`. The
project owner asked mid-cut for `main` to be refreshed; the fetch found it
still at `a264cfcb` (`#1153`), the tip the cut was taken from, so nothing was
left to absorb. The ROADMAP.md row, its `current baseline` mark and the
baseline section are written by hand. `tools/pr_body_check.py` found no
squash commit that lost its body, and no closure among the 17 merged inside
v0.5.13's tag, so v0.5.13's notes owe no pointer.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.14 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Seventeen items, and a patch on both halves of § "Versioning decision"'s test: no capability boundary is crossed, and the next three minor numbers, v0.6.0 through v0.8.0, are given to milestone sections. **Nothing in the simulator's code or reference cases moved**: `src/` resolves to `37b0a4c` at v0.5.13 and here, and `tests/reference/` (`a184830`), `README.md` (`9938368`) and `.github/` (`11d3072`) with it. **`docs/MODEL.md` moves by a statement about the model rather than a change to it** (`9c23c5a` to `83153ba`): `PL-WMCJ` names the route in § "Assumptions" and records in § "Known limitations" that the Yasuda washout fits this model is validated against found a faster fat-like store it does not have, so fat holds too little agent, the fat trace shows the slow fat alone, and the late washout tail loses its largest measured term inside the supported run length; `PL-FBY3` reads Eger and Saidman 2005 at full text, adds the bias in the lean tissues that feed that store, and separates the route, measured once outside Eger's group, from its size, which rests on that group's fits alone. **It completes `bash-guard-bound`**: `PL-R295` and `PL-VM7C` close two routes past the prune guard to deleted refs, `PL-0FGH` and `PL-1DW7` two false refusals the gate guard gave in ordinary work, and `PL-ZS13` the remedies it printed. `PL-8BR0` has `branch` and `arm` read whether a pull request merged from GitHub's own record, `PL-RLTK` stops `landed_whole` reading a restored file as landed, `PL-RW3T` makes gate parity compare a script's mode as well as its path, and `PL-2TDX` and `PL-C0C0` make the unmerged-cut advisory's absorb route work once a cut's notes exist and keep the advisory speaking after a base merge. `PL-V1Y7` takes break-out off the timeline on the owner's word - the schematic is now v0.7.0 and multi-substance v0.8.0 - dropping `PL-Y04W`; `PL-C7XV` completes `interface-pass-narrative`, and `PL-NDKC` records the PySide6 temporary-`QByteArray` trap where the Qt build will meet it. **Two are Gate 2 entries**, `PL-WMCJ` and `PL-NDKC`, which with `PL-Y04W` dropped leaves it at 78 of 187 cleared; ten are v0.6.0 deferrals, and `PL-9MK6`, the v0.5.13 cut, ships in no release under `PL-KRS6`.
