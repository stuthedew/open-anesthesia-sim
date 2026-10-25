---
id: PL-R4Y2
title: Simulator defects per product item closed have stayed at about 0.7 to 0.8 a week while apparatus defects fell, and a recorded head explains only 16% of product defects: run the generator question over the open product defects, starting with stale state after a halt
priority: P2
effort: L
status: ready
classes: housekeeping
feature: defect-review-2026-10
touches: docs/items
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
