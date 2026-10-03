---
id: PL-R4ZC
title: Cut v0.5.21 from the 51 items finished since v0.5.20
status: done
resource: release-train
added: 2026-10-03
closed: 2026-10-03
pr: 1289
verify: grep -q "^version = \"0.5.21\"" pyproject.toml
---

**Problem.** Cut v0.5.21 from the 51 items finished since v0.5.20

**Done 2026-10-03.** `make release VERSION=0.5.21` stamped the 51 items
finished since v0.5.20 and wrote `docs/releases/v0.5.21.md`; `ROADMAP.md`
takes the row, the baseline mark and the baseline section. It completes
`read-facts-through-docket`, `compaction-reset`, `frame-cost-harness` and
`commit-provenance`, and ten of the 51 are Gate 2 entries, putting the gate at
133 of 194 cleared, from 123 at v0.5.20. `src/anesthesia_sim/data/` and
`README.md` resolve to the same trees on the v0.5.20 tag and on this cut;
`core/` does not, because `PL-NJPB` holds the vaporizer dial as the percent it
was set to and derives the fraction the equations read.

**So the bit-identity claim was re-run rather than read off the diff.** One
script, run on the v0.5.20 tag and on this cut, set the dial each tree's way
from the same percents - through the interface's own `delivered_fraction` on
the tag, as the percent at the cut - and hashed `capture_state()` and
`state_vector()` once a minute for 90 minutes over 81 runs: the three agents,
three pairs of dial settings each (twelve settings, eight of them among those
whose fraction times 100 misses the percent), three cardiac outputs and three
fresh gas flows, with the dial changed at minute 30 and closed at 50, the fresh
gas flow raised to 10 L/min at 60 and the cardiac output by 1 L/min at 70. All
7,290 samples hash identically, sha256 `0df75096` at both ends. A second
script formatted the control timeline's entry for every setting from 0.00 to
18.00% at 0.01% steps, and the 1,801 strings are identical at both ends. Both
were one-offs and are not kept.

`PL-9DYK` (`#1253`) merged inside the v0.5.20 tag, at `0a0601b`, the commit
before that tag's cut, so v0.5.20's notes take the pointer to this release
under their tag-span heading; none of the other fifty did.
`tools/pr_body_check.py` found no squash commit that lost its body. No tag
step is filed: `.github/workflows/tag-release.yml` tags the cut when this pull
request merges (`PL-2FY6`).
