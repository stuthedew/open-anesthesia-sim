---
id: PL-R4Y2
title: Simulator defects per product item closed have stayed at about 0.7 to 0.8 a week while apparatus defects fell, and a recorded head explains only 16% of product defects: run the generator question over the open product defects, starting with stale state after a halt
priority: P2
effort: L
status: ready
classes: housekeeping
feature: defect-review-2026-10
touches: docs/items, ROADMAP.md
added: 2026-10-19
payoff: the stale-state defects a learner can see get their root cause fixed once, instead of each one being found and patched separately
verify: grep -qE '^\*\*Re-measured\.' docs/items/PL-R4Y2-*.md
---

**Problem.** Simulator defects per product item closed have stayed at about 0.7 to 0.8 a week while apparatus defects fell, and a recorded head explains only 16% of product defects: run the generator question over the open product defects, starting with stale state after a halt

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Scope** (project owner, 2026-10-19): every product defect, closed ones included (222 on 2026-10-19), not only the 28 open ones the review recommended. The closed ones carry most of the history of where defects come from.

**Evidence.** Organic workflow defects per workflow pull request fell from about 1.0 a week through 2026-09-20 to 0.41, 0.33, 0.60 and 0.20. Product defects per product item closed show no trend: 0.64, 0.14, 0.69, 0.26, 0.83, 0.79 and 0.77 for the weeks of 2026-08-31 to 10-12. A head explains 35 of 222 product defects (16%), against 44% in the workflow lane and 59% for items that cross lanes. By a keyword count of titles, about 36 of the 91 product defects filed since 2026-09-25 are stale state after a halt, a failed frame or a reset. Only 11 of them are members of `PL-X7D5` (the run screen's single writer) or `PL-5JTH` (dashboard panels restated on a halt). Stale state is a failure the safety-critical standard in `CLAUDE.md` names explicitly. A second cluster is a quantity's range checked by hand (about 15). A third is float extremes such as overflow, subnormal steps and rounding noise (about 10).

**What to do.** Ask every product defect triage's generator question (`.claude/skills/docket/modes/triage.md`): which fact did it misread? Record a head wherever three or more share one, open or closed. Delegate the reading to subagents and keep only their verdicts here. Start with stale state, because `PL-X7D5` and `PL-5JTH` landed only on 2026-10-17 and 2026-10-19.

**Done when.** Every product defect has an answer to the generator question, heads are recorded where they exist, and the product rate is re-measured two weeks after `PL-5JTH`.

**Why it matters.** Product defects are the ones a learner can see, and stale state after a halt is a failure the safety-critical standard names. While no head explains 84% of them, each is found and patched one at a time, and the rate does not fall.

**Generator check.** One-off. This item asks the generator question; it does not misread a fact itself. Record the re-measured rate under a `**Re-measured.**` heading here.

**Generator question answered, 2026-10-25.** The population was every product-lane item classed `defect` or `safety`, closed ones included: 245 on `main` at `07ac5e0c`, read with `docket.store.read_items` and placed with `Item.lane(workflow_paths)`. 35 were already members of a recorded head. Seven subagents each read 30 of the other 210 and answered the generator question for each one: which fact did it misread, and which cluster does that fact belong to. Their verdicts are leads, so this session checked each new head's members by title and closure before recording it.

Seven heads are recorded from this reading, 38 members in all, so heads now explain 73 of the 245 product defects (30%), up from 35 (14%):

- `PL-HJKN`, **live**: which slots that read or change a run must pass the halt gate. Six members, four of them filed on 2026-10-11 and 2026-10-12.
- `PL-N7MM`, **live**: whether a record's cross-field rule still holds after a later field write. Four members, from 2026-10-04 to 2026-10-18.
- `PL-58D7`, **live**: the floating-point input domain on which each operation in `core/` is correct. Nine members, seven of them from 2026-10-03 to 2026-10-17.
- `PL-GTH6`, spent: which run a displayed value belongs to once two runs are shown. Eight members, none since 2026-09-21.
- `PL-CMJ5`, spent: a test's expected value taken from the code under test. Four members, ended by `.claude/rules/test-oracles.md`.
- `PL-VDWT`, spent: a run opens at its own instant on the case axis. Three members from one review.
- `PL-R0BJ`, spent: what must fit at the 1366 by 700 reference window. Four members from the Qt port's compare mode.

Four clusters match the misread fact of a head that already exists, but their items are not recorded as its members. They are left unrecorded, because each match is one subagent's label and a closed head's member list is its own record:

- A document sentence diverged from the tree fact it restates, `PL-4FBP`'s fact, 27: `PL-01GY`, `PL-0SHZ`, `PL-11YF`, `PL-1QL6`, `PL-27H0`, `PL-2HTF`, `PL-3P2P`, `PL-8PZ1`, `PL-9KP5`, `PL-9PD6`, `PL-B875`, `PL-C1KK`, `PL-GJYL`, `PL-KF0T`, `PL-KGNF`, `PL-L7JB`, `PL-NBWP`, `PL-QM5P`, `PL-QYPX`, `PL-RBMK`, `PL-SR8F`, `PL-WSDY`, `PL-X9KD`, `PL-Y4Q4`, `PL-YD6X`, `PL-YYL2`, `PL-ZHSW`. About nine of these are queue or release state restated by hand in `ROADMAP.md` or `docs/MODEL.md`.
- A quantity's range checked by hand, or a checked type's construction contract, `PL-ZGYX`'s fact, 24: `PL-0MLQ`, `PL-1KQ9`, `PL-25D9`, `PL-3800`, `PL-391Y`, `PL-51B7`, `PL-5GVL`, `PL-629Z`, `PL-73ZN`, `PL-8JV2`, `PL-96SQ`, `PL-979Z`, `PL-BMY5`, `PL-CX2C`, `PL-F9TC`, `PL-GYH2`, `PL-HPKK`, `PL-VP7N`, `PL-Y5WR`, `PL-5D1Z`, `PL-7N8P`, `PL-848D`, `PL-SWD1`, `PL-W3Q5`.
- A second copy of a value, `PL-40SJ`'s fact, 12: `PL-1MGB`, `PL-6YKY`, `PL-7CRY`, `PL-84G1`, `PL-9PMV`, `PL-CLVM`, `PL-G84G`, `PL-Q3G9`, `PL-R1VD`, `PL-WG73`, `PL-XVCV`, `PL-YHWH`.
- Stale state after a halt, a reset or a failed frame, the fact of `PL-X7D5` and `PL-5JTH`, 15: `PL-026`, `PL-1ZQ4`, `PL-2N43`, `PL-3K9B`, `PL-5291`, `PL-BM6X`, `PL-J12Z`, `PL-LTKL`, `PL-N3N5`, `PL-P58M`, `PL-QRD1`, `PL-T2Q2`, `PL-VYXP`, `PL-WM5P`, `PL-X7D5`. Five of these share a different fact, how a mark's standing is evaluated (`PL-3K9B`, `PL-5291`, `PL-N3N5`, `PL-1ZQ4`, `PL-2N43`), but they split three ways on what was misread, so no head is recorded for it.

The rest have no shared fact that three items share closely enough to record:

- Displays and labels, 16: `PL-0S0V`, `PL-2K1R`, `PL-3355`, `PL-3PJZ`, `PL-74TX`, `PL-90Y6`, `PL-B396`, `PL-DHV7`, `PL-KCWD`, `PL-NV9W`, `PL-Q4VH`, `PL-QYBW`, `PL-TG60`, `PL-THXF`, `PL-YH6Z`, `PL-YVHK`. Three of these, `PL-74TX`, `PL-TG60` and `PL-3PJZ`, misread the precision a value's fidelity justifies. `PL-0S0V` is the open item that would fix that structurally, and it is blocked, so a head here would be a live head that nothing can start.
- Tests that could not fail, 16: `PL-042`, `PL-624C`, `PL-7YZH`, `PL-904Y`, `PL-B7ZV`, `PL-F5GN`, `PL-G5SX`, `PL-GZP6`, `PL-J0F7`, `PL-JFYT`, `PL-JS0X`, `PL-SLHS`, `PL-Y5BV`, `PL-Z3W6`, `PL-ZH1F`, `PL-ZVS7`. Each misread a different guarantee.
- Qt layout and sizing, 11: `PL-8GLZ`, `PL-J4NW`, `PL-JSY5`, `PL-K285`, `PL-KX97`, `PL-NC0D`, `PL-T91K`, `PL-TCR5`, `PL-TZNM`, `PL-VCF0`, `PL-YJ21`. Size hints and heightForWidth account for five, and they split on which widget's hint was misread.
- Model provenance and stated limits, 7: `PL-0NQ1`, `PL-8PS6`, `PL-B4P7`, `PL-VJZK`, `PL-W7H9`, `PL-WZVZ`, `PL-X35V`.
- Clusters of three or fewer, 37 items: `PL-4RBD`, `PL-GS3R`, `PL-K9Z5`, `PL-KRZW`, `PL-QW19`, `PL-TBMX`, `PL-VM40`, `PL-B32L`, `PL-BNPY`, `PL-V6M0`, `PL-NJPB`, `PL-P1Z3`, `PL-SM5V`, `PL-CTD7`, `PL-0RZ0`, `PL-1K9G`, `PL-HSP8`, `PL-DSMK`, `PL-W54S`, `PL-88MK`, `PL-CW51`, `PL-Q18P`, `PL-B1R9`, `PL-NC62`, `PL-2TZT`, `PL-LQ19`, `PL-SPN6`, `PL-K5NY`, `PL-MMWX`, `PL-QBX0`, `PL-KFNP`, `PL-QG52`, `PL-74R0`, `PL-W7H9`, `PL-WZVZ`, `PL-X35V`, `PL-FPLQ`.
- One-off defects, 8: `PL-2R2C`, `PL-5MT4`, `PL-BTSW`, `PL-GHMB`, `PL-KFTM`, `PL-Q197`, `PL-Y04W`, `PL-YBWT`. Two items, `PL-1P15`, `PL-2881`, are a planned feature and a specification rather than defects.

Of 2026-10-19's three named clusters, stale state is now mostly explained by `PL-X7D5`, `PL-5JTH` and `PL-HJKN`, a quantity's range checked by hand by `PL-ZGYX`, and float extremes by `PL-58D7`.

`PL-R4Y2` stays open for the re-measurement, due two weeks after `PL-5JTH` closed on 2026-10-19, which is 2026-11-02.

**Generator question for the product defects filed 2026-10-23 to 2026-10-25, asked 2026-10-26.** There were 56 such items, read with `docket.store.read_items` and placed with `Item.lane(workflow_paths)`. 43 of them are `PL-GTHP`'s reviewer-replay findings, filed at 21:59 UTC on 2026-10-25, after this item's pass on `07ac5e0c`. Product items are not asked the generator question at triage, so none of the 43 had been asked. Each verdict below was checked against the members' briefs, and the two new heads against the code.

- **`PL-ZR49`, new head, live**: which stretch an edit made while a run stands on an instant belongs to. Eight members: `PL-3K9B`, `PL-2N43` and `PL-1ZQ4` (closed), and `PL-HSP8`, `PL-TNYP`, `PL-NRR6`, `PL-K5BS` and `PL-XV0D` (open). The earlier pass on this item saw the first three as a mark-standing cluster that split three ways. One level up, the five new members share their fact.
- **`PL-J5GC`, new head, live**: three post-close instances of `PL-X7D5`'s fact, each recorded `reenters: PL-X7D5`. They are `PL-6RJ0`, `PL-3B34` and `PL-HF4B`, all filed against `main` after `PL-WM5P` merged. One writer per widget holds. Values shown together coming from one state does not.
- **Rounding a computed value just past a bound that a reader then tests exactly**: `PL-9SL5` (last column one rounding unit past `stop_s`), `PL-N559` (alveolar fraction a few units in the last place above the inspired fraction, classed as elimination) and `PL-PM67` (a fraction rounded just above 1). They are `PL-58D7`'s fact, the floating-point domain of an operation, and `PL-8H2R` is already its member. But they arise at ordinary inputs, and `PL-58D7`'s split items (`PL-QX2G`, `PL-YT3T`, `PL-06LS`) declare input envelopes, which will not reach them. They are not recorded as `PL-58D7`'s members here, because that head is blocked on its own design. The session that unblocks it should decide whether its scope takes them.
- **A `docs/MODEL.md` claim about the model's computed behaviour that no test computes**: `PL-39KH`, `PL-MLPT`, `PL-M8F6` and `PL-5RPD`. This is `PL-4FBP`'s fact, a document sentence diverged from the fact it restates, where the fact is the model's output rather than a file. Left unrecorded, as the earlier pass left that cluster.
- **Leads with fewer than three members**: `PL-YH6Z` and `PL-T5NJ` are hovers that derive their own answer instead of reading `read_wash_in` or the clock grid. `PL-97WX` and `PL-C9XP` derive an Area's size again instead of reading `settle`'s held sizes, and `PL-Y65Q` and `PL-QZ7Z` are `settle`'s own policy. `PL-0WFJ`, `PL-S11T` and `PL-WRVX` are `PL-ZGYX`'s fact, a way in that skips a quantity's check. They are listed with the earlier pass's 24 unrecorded `PL-ZGYX` matches.
- **Already attributed, or not defects of a shared fact**: the `floating-point-domain` items, `PL-HJKN`, `PL-N7MM`, `PL-58D7`, `PL-7FPD`, `PL-PNGQ`, `PL-2T6S`, `PL-G84G`, `PL-Q3G9` and `PL-6YKY` carry their own answer. The `mac-awake-reference-text` and `supported-run-length-text` items misread a source or the model's physiology, one each. `PL-1P15`, `PL-2881`, `PL-KFTM`, `PL-RNYV` and `PL-S79P` are planned work. `PL-88MK`, `PL-FPLQ`, `PL-DQL9`, `PL-QG52`, `PL-QBQX`, `PL-KDZW`, `PL-TPBH`, `PL-VHQX`, `PL-X4X2`, `PL-KHXB` and `PL-X9K0` are one-offs.

**Generator question for the product defects filed 2026-10-26 and 2026-10-27, asked 2026-10-27.** Every triaged product item classed `defect` or `safety` and filed up to 2026-10-27 now has an answer, either in this brief, in its own `**Generator check.**` line, or as a member or re-entry of a head. The two not yet answered by name are answered here. `PL-3HT2`, a stale docstring in `core/uptake_system.py`, is `PL-4FBP`'s fact, a document sentence diverged from the tree fact it restates, and is left unrecorded like the 27 listed above. `PL-T6P0` belongs to the `floating-point-domain` feature, which carries its own answer. Eight untriaged items filed on 2026-10-25 to 2026-10-27 look like product defects: `PL-9B1M`, `PL-PTDZ`, `PL-000W`, `PL-9Z74`, `PL-QVBR`, `PL-D88N`, `PL-D1LR` and `PL-93LV`. They are left to triage. From `PL-K5CX` (#1883, merged 2026-10-27), triage asks every product item that is not classed only as new work the generator question, so a sweep like this one is no longer the only way a product defect is asked.

**Interim reading, 2026-10-27, on `main` at `516b0ce22`.** This is not the re-measurement, which is still due on 2026-11-02. It checks the method and gives one full week after `PL-5JTH`. Organic product defects filed per product item closed, by week starting Monday:

| Week of | Organic defects | Of them, `PL-GTHP`'s replay batch | Items closed | Rate | Rate without the replay batch |
| --- | --- | --- | --- | --- | --- |
| 2026-08-31 | 44 | 0 | 69 | 0.64 | 0.64 |
| 2026-09-07 | 12 | 0 | 87 | 0.14 | 0.14 |
| 2026-09-14 | 52 | 0 | 80 | 0.65 | 0.65 |
| 2026-09-21 | 8 | 0 | 34 | 0.24 | 0.24 |
| 2026-09-28 | 25 | 0 | 30 | 0.83 | 0.83 |
| 2026-10-05 | 14 | 0 | 24 | 0.58 | 0.58 |
| 2026-10-12 | 36 | 0 | 52 | 0.69 | 0.69 |
| 2026-10-19 | 44 | 16 | 94 | 0.47 | 0.30 |
| 2026-10-26 (2 days) | 0 | 0 | 41 | 0.00 | 0.00 |

Three things limit this reading:

- **The earlier weeks have moved since 2026-10-19.** Recomputed today, 2026-10-05 reads 0.58 where the review read 0.79, and 2026-10-12 reads 0.69 where it read 0.77. The first two weeks reproduce exactly. Triage has since changed some items' `touches` and `classes`, which moves them between lanes and classes. So the 2026-11-02 re-measurement compares each week against the earlier weeks recomputed on the same day, never against the figures in § "Evidence".
- **The replay batch is a sweep of old faults.** `PL-GTHP` filed 45 items in `a4746bda7` on 2026-10-25, and 16 of them count as organic product defects in the week of 2026-10-19. Each describes a fault that was already present at an older merge, so the last column is the better measure of defects arising from current work.
- **The latest week is incomplete.** An untriaged item has no `touches`, so it is placed in no lane and is not counted. Triage the eight items named above before taking the 2026-11-02 reading.

On this reading the week after `PL-5JTH` closed is 0.30 without the replay batch, against 0.58 to 0.83 in the four weeks before it. One week is not a trend. Heads now explain 89 of 279 product defects (32%), 16 of them open, up from 73 of 245 (30%) on 2026-10-25.

**How to take the re-measurement.** Run this from the repository root, with the replay batch's ids written to a file first: `git show --diff-filter=A --name-only --format= a4746bda7 -- docs/items | sed -E 's#docs/items/(PL-[0-9A-Z]+)-.*#\1#' > replay.txt`. An organic defect is an item classed `defect` or `safety` with no `reenters:` that was filed before any head naming it in `root-cause-of:`. An item filed on the same day as the head that names it counts as that head's own filing.

```python
import sys, tomllib
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, "subprojects/docket/src")
from docket.store import read_items

paths = tuple(tomllib.loads(Path("docket.toml").read_text())["docket"]["workflow_paths"])
items = read_items(Path("docs/items"))
replay = set(Path("replay.txt").read_text().split())
named = {}
for head in items:
    for member in head.root_cause_of:
        if head.added and (member not in named or head.added < named[member]):
            named[member] = head.added

def organic(i):
    return not i.reenters and (i.identifier not in named or i.added < named[i.identifier])

def week(d):
    return d - timedelta(days=d.weekday())

filed, swept, closed = Counter(), Counter(), Counter()
for i in items:
    if i.lane(paths) != "product":
        continue
    if i.closed and i.status == "done":
        closed[week(i.closed)] += 1
    if i.added and {"defect", "safety"} & set(i.classes) and organic(i):
        filed[week(i.added)] += 1
        swept[week(i.added)] += i.identifier in replay
w = date(2026, 8, 31)
while w <= date.today():
    c = closed[w]
    print(w, filed[w], swept[w], c, f"{filed[w] / c:.2f}" if c else "-",
          f"{(filed[w] - swept[w]) / c:.2f}" if c else "-")
    w += timedelta(days=7)
```

**The eight untriaged product defects triaged, 2026-10-31,** ahead of the
2026-11-02 reading, as the interim reading asked. On `main` at `35892ff1`:

- `PL-9B1M` (a fraction rounded just past 1 from a full state): P1, `defect,
  safety`, `needs-decision`, recommending that the inputs be capped at a
  physically reachable fraction. `PL-58D7`'s own finding.
- `PL-D88N` (the mass-balance tolerance at the stiffest corners): P1, `defect,
  science`, `needs-decision`, recommending a tolerance that follows the
  propagator's bound. `PL-58D7`'s fact, filed while it was open.
- `PL-QVBR` (stepped and canonical readings disagree on a crossing): P1,
  `defect, safety`, `ready`. `PL-ZR49`'s own finding.
- `PL-PTDZ` (MAC-awake washout figures no test pins): P1, `defect, science`,
  `ready`, `reenters: PL-4FBP`.
- `PL-000W` (a control's settings field mapped twice): P1, `defect, safety`,
  `ready`. One-off.
- `PL-D1LR` (MODEL.md margins against a display resolution since changed): P1,
  `docs, science`, `ready`, `reenters: PL-4FBP`.
- `PL-9Z74` (a too-small Area's floor measured at the wrong width): P3,
  `defect, ux`, `ready`, deferred from v0.7.0. One-off.
- `PL-93LV` (a section name without its § mark): P3, `docs, defect`, `ready`,
  deferred from v0.7.0. One-off.

The six classed `safety` or `science` joined v0.7.0's frozen list, which
admits such a capture after the freeze. With `PL-PTDZ` and `PL-D1LR`,
`bin/docket inflow --lane product` names `PL-4FBP` as re-entered by three
filings (`PL-LNFG`, `PL-D1LR`, `PL-PTDZ`), a generator whose fix did not hold.
Its convention ties a sentence to a value held in a file. It does not reach a
figure the model computes or a display resolution restated in prose, and the
2026-10-26 pass above found four more items of the first shape. Recording that
head is work for a session of its own, not for this triage.
