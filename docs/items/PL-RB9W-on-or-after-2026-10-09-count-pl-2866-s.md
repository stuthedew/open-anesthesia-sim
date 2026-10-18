---
id: PL-RB9W
title: On or after 2026-10-09, count PL-2866's falsifier: apparatus findings that blocked or were captured during product items, against simulator items closed since the 2026-09-25 switch; the blocking rule is wrong above about 1 per 10
priority: P2
effort: S
status: done
classes: infra
feature: workflow-stress-2026-09
milestone: v0.5.28
touches: docs/items/PL-RB9W-on-or-after-2026-10-09-count-pl-2866-s.md
added: 2026-09-25
closed: 2026-10-18
pr: 1557
payoff: The owner learns from a count fixed in advance whether letting product sessions defer apparatus findings is costing product work, and so whether product focus's blocking rule should be reopened
verify: grep -q '^\*\*Counted 20' docs/items/PL-RB9W-*.md
---

**Problem.** On or after 2026-10-09, count PL-2866's falsifier: apparatus findings that blocked or were captured during product items, against simulator items closed since the 2026-09-25 switch; the blocking rule is wrong above about 1 per 10

**How.** `PL-2866` pre-registered it. Its blocking rule (an apparatus finding stops a product session only when it blocks it) is wrong if deferred apparatus defects bite product sessions more often than about 1 per 10 product items. The baseline is 7 apparatus defects found during product work against 72 simulator items closed, 2026-09-15..25, counted by the inflow scripts in `docs/stress-2026-09-25/evidence.tar.gz`. Re-run them over 2026-09-25..10-09 and count two things apart: findings that *blocked* a product item, so it stopped for them, and findings captured during one and deferred. A deferred one that later bit a product session counts against the rule. Not before 2026-10-09, the two weeks the decision named.

**Why it matters.** `PL-2866`'s blocking rule was ratified, so ordinary evidence reopens it, and this count is the evidence it named in advance. Left uncounted, a rule that lets product sessions defer apparatus findings stands whether or not the deferred ones are biting product work.

**Not before 2026-10-09, and how the store says so (triage, 2026-09-25).** The store has no field for a date. `blocked-by` takes an item id or a milestone version only (`subprojects/docket/README.md` § "`blocked` means "not first", and that is the whole of it"), and `model.py`'s `FIELD_ORDER` holds no date field. Adding one would be a new field, which the generator pause holds. So the date rides the title's first words, which `next` and the digest print, and the item is `ready`. A session offered it before 2026-10-09 leaves it: counted early, the window falls short of the two weeks the decision named.

Re-confirmed 2026-09-25 against 46954a81: `PL-2866`'s brief states the falsifier ("wrong if deferred apparatus defects bite product sessions more often than about 1 per 10 product items"). In the archive, `inflow/classify.py` puts the 7 in discovery class (i), found in or captured by a simulator item. `inflow/inflow.py` hard-codes its window (`D0, D1` and `W0`), and `inflow/run_all.sh` the stress session's scratch paths, so the re-run re-points both.

**Done when.** This brief carries a `**Counted YYYY-MM-DD.**` section with both counts over 2026-09-25..10-09 against simulator items closed in the window: findings that blocked a product item, and findings captured during one and deferred, with how many of those later bit a product session. It says whether the rate is above about 1 per 10. Above it, the blocking rule goes back to the owner as a decision on a new item; at or below it, the count is recorded and the rule stands.

**Generator check.** Bookkeeping: a measurement the owner's decision pre-registered (`PL-2866`), with no misread fact behind it.

**Counted 2026-10-18.** The rate is below about 1 per 10, so the blocking rule
stands. Over 2026-09-25..10-09, 64 simulator items closed done (67 counting
the dropped ones). In the same window, 5 apparatus defects were found during
product work, by the archive's own lane rule and its discovery class (i). The
baseline was 7 against 72 over 2026-09-15..25.

| Item | Found during | What happened |
| --- | --- | --- |
| `PL-7LCY` | `PL-WMCJ` | The floor guard refused a JSON read. The session used `grep` instead, so nothing was blocked. Fixed 2026-10-17. |
| `PL-0FGH` | `PL-FBY3`'s commit | The gate-status guard refused a correct `&&` chain. It cost one retry. Fixed the same day. |
| `PL-LK62` | `PL-QRBB`'s commit | A session told "read only" left its auto-merge armed, so `#1213` merged. Fixed in `CLAUDE.md` the same day. |
| `PL-Y4NS` | `PL-F08Y` | Two tests failed in a clone with a local `origin`. The timing work went on. Fixed 2026-10-01. |
| `PL-HNXS` | `PL-YZ17`'s review | Two checks counted files in a nested worktree. The review went on. Fixed 2026-10-12. |

- **Blocked a product item:** 0. None of the five stopped the item it was found in.
- **Captured and deferred:** 5.
- **Deferred, and later bit a product session:** 0. The one recorded
  recurrence, `PL-HNXS`'s on 2026-10-12, came in `PL-9NZ3`, an apparatus item.
  `PL-7LCY` was met a second time by the triage pass that classed it, which is
  apparatus work too.

So the rate the falsifier names is 0 in 64. Even if every one of the five
findings counted as a bite, the rate would be 5 in 64, or 0.078, which is still
below 0.1.

One limit applies to the third count. A later bite is visible only where a
session wrote it down, as a `recurrences:` line or a "met again" paragraph. A
product session that met one of these defects and said nothing is not counted.
The lane and discovery rules are the archive's, applied unchanged so that the
two windows compare. The archive's `labels.py` has no labels for this window, so
discovery comes from `classify.py`'s automatic rules alone. Run from the
repository root, with `docs/stress-2026-09-25/evidence.tar.gz` unpacked into a
scratch directory and this script saved as `inflow/recount.py` beside
`inflow.py`:

```python
import sys, datetime as dt, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, "subprojects/docket/src")
sys.path.insert(0, str(HERE))
import inflow

inflow.D0, inflow.D1, inflow.W0 = dt.date(2026, 9, 25), dt.date(2026, 10, 9), dt.date(2026, 9, 25)
import labels

labels.L = {}
labels.DISC = {}
src = (HERE / "classify.py").read_text()
# Reuse classify.py's discovery() only: execute up to the tabulation.
head = src.split("tab = collections.Counter()")[0].replace(
    'print("unlabelled:", missing, "extra:", extra)', ""
)
ns = {"__file__": str(HERE / "classify.py")}
exec(compile(head, "classify-head", "exec"), ns)
q2, discovery, Ln, items = ns["q2"], ns["discovery"], ns["Ln"], ns["items"]
D0, D1 = inflow.D0, inflow.D1
disc = collections.Counter()
found_i = []
for i in q2:
    d, why = discovery(i)
    disc[d] += 1
    if d == "i":
        found_i.append((i.identifier, str(i.added), i.status, why, i.title[:110]))
print(f"apparatus defects filed {D0}..{D1}: {len(q2)}; discovery {dict(sorted(disc.items()))}")
for row in found_i:
    print("  i:", *row, sep="\t")
sim_done = [
    i
    for i in items
    if i.closed and D0 <= i.closed <= D1 and Ln[i.identifier] == "simulator" and i.status == "done"
]
sim_any = [
    i
    for i in items
    if i.closed
    and D0 <= i.closed <= D1
    and Ln[i.identifier] == "simulator"
    and i.status in ("done", "dropped")
]
print(f"simulator items closed {D0}..{D1}: {len(sim_done)} done, {len(sim_any)} done or dropped")
```
