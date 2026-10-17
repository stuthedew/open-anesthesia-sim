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
