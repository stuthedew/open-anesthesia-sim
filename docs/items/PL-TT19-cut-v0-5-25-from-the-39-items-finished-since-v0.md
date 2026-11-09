---
id: PL-TT19
title: Cut v0.5.25 from the 39 items finished since v0.5.24
status: done
resource: release-train
added: 2026-10-17
closed: 2026-10-17
pr: 1495
verify: grep -q "^version = \"0.5.25\"" pyproject.toml
---

**Problem.** Cut v0.5.25 from the 39 items finished since v0.5.24

**Done 2026-10-17.** `make release VERSION=0.5.25` stamped the items finished
since v0.5.24 and wrote `docs/releases/v0.5.25.md`. It was re-run once, after
`#1492` (`PL-X7D5`, `PL-1YDD`, `PL-DTJQ`, `PL-MMNX`, `PL-G3K7`) merged under
the draft, which took the filing's 34 items to 39. `#1494` merged under the
draft as well. It finished no item, but it added `PL-HQF5` to Gate 2, so the
gate counts below include it. The project owner asked for the cut in this
thread ("But first, cut version", 2026-10-17 14:35Z). It is a patch because no
capability boundary is crossed, and `bin/docket wave` lists 0.6.0, 0.7.0 and
0.8.0 as spent.

`ROADMAP.md` takes the row, the baseline mark and the baseline section. Nine
of the items are Gate 2 entries, and the gate stands at 213 of 234 cleared,
from 204 of 229 at the v0.5.24 tag. `core/` moved (`a0e4719` to `60697e5`),
so the trajectories were measured against the tag. The script played 81 runs
with two branches each, and three 24-hour runs, and compared every value as
exact bits. Every step's state, sampled state, canonical state, drawn window
and formatted string is identical, and the snapshot has the same fields at
both ends. The measurement ran on the 34-item cut and again on the 39-item
cut. Which screen changes a learner can reach was read from each item's own
record. `PL-T995`'s stop drawn at once is reachable today. The four members
that `PL-X7D5` closes, and `PL-85LJ`, each need a fault that no supported
setting produces. `PL-75P5`'s record does not say, so the section makes no
claim either way for it.

`#1467` (`PL-ZXCN`) merged inside v0.5.24's tag span without being stamped by
it, so v0.5.24's notes gain an `### also inside this tag's span` pointer to
this release. `tools/pr_body_check.py` found no squash commit that lost its
body.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.25 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item. In the quote, § "Versioning decision" is `ROADMAP.md`'s.

> 39 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: each new refusal sits on a route that no interface control takes, and each screen change corrects what an existing screen shows. v0.6.0 through v0.8.0 are given to milestone sections. **No equation, parameter or stored value changed, and every state a run plays is bit-identical**: `core/` changed (`a0e4719` to `60697e5`) because every checked field of the five run records refuses a bad value when it is written (`PL-19Y0`), the patient refuses a cardiac output that its blood flows do not match (`PL-KFNP`), and the tissue and venous closed forms, which the stepped model does not call, keep the sign of their gradient (`PL-XWFP`). Over 81 runs across the three agents, each with two branches, all 6,561,000 steps, 11,178 sampled states, 11,178 canonical states, 2,187 drawn windows and 19,447,290 formatted strings are identical at both ends, as are three 24-hour runs. `data/` changed only in three agents' source notes (`PL-0SG0`), and `tests/reference/` only in docstrings and in a table that orders the test workers' work (`PL-4Z5Y`). A learner can see a run that halts on a mark or at the supported length drawn stopped at once (`PL-T995`). A halted run's screen now has one writer, so every widget states the run the controller holds (`PL-X7D5`). The four members it closes, and `PL-85LJ`'s dial label, were reachable only through a fault that no supported setting produces. A one-run Reset also clears a refused branch (`PL-75P5`). **It finishes no feature, and closes two generator heads spent**, `PL-KFNP` and `PL-X7D5`. **Nine are Gate 2 entries**, and the gate stands at 213 of 234 cleared, from 204 of 229 at v0.5.24. `PL-TT19`, the cut, ships in no release under `PL-KRS6`.
