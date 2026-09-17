
---

**The `r_vcs = 1.05` figure above does not survive measurement, 2026-09-17
(`PL-M2SD`).** That number counted *every* item spawned by work on a `vcs.py`
item, including captures about unrelated parts of the tree. Counting only
children that land back in `vcs.py` — which is what "this cluster generates its
own work" claims — gives **r_vcs = 0.71**, below 1.0. The cluster closes more
than it creates. Two attribution bugs fixed in `tools/generator_check.py`
account for the rest of the gap: a multi-title `bin/docket new` commit made
each captured item the others' parent, and a `touches` entry written
`docs/items/` escaped the store exclusion.

On the corrected measure **no cluster in this repository reports at all**, and
`vcs.py` is not the lane's worst: `docs/MODEL.md` carries 40 open items at
0.55, `ROADMAP.md` 32. `vcs.py` has 12 open of 67, and its filings fell 26 to
14 over the two weeks to 09-17.

**What this retracts, and what it does not.** The urgency framing is retracted:
this is not a runaway generator and should not be ranked as one. The design
argument is untouched and is the reason to keep this item — nineteen items each
choosing their own answer to one question is duplication, and it is counted
from the items themselves rather than from any spawn rate. So the case for one
design round still holds; the case for doing it *ahead of everything else* does
not.
