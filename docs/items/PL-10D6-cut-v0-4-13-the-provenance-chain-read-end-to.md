---
id: PL-10D6
title: "Cut v0.4.13: the provenance chain read end to end, the Flet decision recorded, and doc-consistency-checks completed"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.14
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases
added: 2026-09-12
closed: 2026-09-12
pr: 495
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.13"' pyproject.toml && test -f docs/releases/v0.4.13.md
---

**Problem.** Cut v0.4.13: the provenance chain read end to end, the Flet decision recorded, and doc-consistency-checks completed

**Why it matters.** Eleven items had landed since v0.4.12 and `doc-consistency-checks`
had completed, which is past the point where release notes can be written from
memory rather than from the store.

**The version is 0.4.13, chosen rather than incremented** (this session, on the
project owner's delegation of 2026-09-12: "make a version. You decide").
`ROADMAP.md`'s "Versioning decision" says the number marks the capability
boundary a release crosses. **This one crosses none.** No equation, parameter,
unit, numerical method, solver step or interface element moved;
`src/anesthesia_sim/core/` is byte-identical to v0.4.12, and
`src/anesthesia_sim/data/` changes only in what its entries say about their own
numbers. All eleven items are provenance, documentation, tooling or a recorded
decision.

The one argument for going higher was the Flet decision, and it does not hold:
`PL-QXSB` *decided* to leave Flet and scoped the port as v0.5.1, and `PL-55DH`'s
spike is explicitly disposable and touches no shipped `app/` module. A decision
to change toolkits later is not a capability crossed now, and numbering it as
one would say a user-visible thing changed when none did - the same false
precision this project refuses for a displayed value. v0.5.0 was never a
candidate: it is scoped, gated, and its gate stands at 56 of 152.

**What was done.** `make release VERSION=0.4.13`, which bumped `pyproject.toml`,
relocked `uv.lock`, wrote `docs/releases/v0.4.13.md` and stamped the eleven
items. Then the three things it names as owed by hand: the version-table row,
moving the `current baseline` mark off v0.4.12, and the baseline section - the
prose saying what the release was *for*, which nothing generates.

**Preconditions checked before cutting**, both of which `bin/docket release`
refuses on: v0.4.12 is tagged on the remote (`git ls-remote --tags`), and no
other session is cutting - `list_sessions` showed one session running, this
one, with the rest archived. That check is `PL-66FP`'s, two sessions having cut
v0.3.7 within the hour.

**The tag is outstanding and is the project owner's to push**, `PL-N936` having
established that a session's tag push fails while reporting success.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.13 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> No displayed value moves and no stored value moves: no equation, parameter, unit, numerical method, solver step or interface element changed, and `src/anesthesia_sim/core/` is byte-identical to v0.4.12. `src/anesthesia_sim/data/` changes only in what its entries say about their own numbers. **What moved is how much of that provenance is known.** The Gas Man Workbook names Lowe and Ernst 1981 for seven of the reference patient's eleven values; that book cites four references on page 56 for its own figure 4.1b, and over one afternoon the project owner supplied all four by interlibrary loan and direct download. They are two documents one link apart: ICRP Committee II's 'standard man' table at page 151, which Mapleson 1963 also cites for his volumes, and which gives organ masses and **no blood flows at all**; and Mapleson himself, who compiles his flows from about twenty sources - some of them animal, one row an `Estimate`, and one 'chosen merely to complete cardiac output', which is 19.9% of his total. Lowe and Ernst's other two references are Mapleson's table lumped and relabelled, reproducing it in nine rows of nine. **The chain reaches tier 1 nowhere, and figure 4.1b's flow column reproduces from none of the four**: on Mapleson's own rows the vessel-rich share is 59.0-63.0% against Lowe's 76%. `reference_adult.json` gains five `sources` entries and its `provenance_gap` is rewritten to say that, stated as what was checked rather than as what exists - **it does not follow that no origin exists**, and the field says so. **Two other decisions are recorded rather than built.** The PySide6 spike was run on the project owner's own hardware and the interface will leave Flet, scoped as v0.5.1 and not started here. And `docs/MODEL.md`'s cardiac-output limitation stops setting Lowe's derived 4.84 L/min beside Cattermole's measured 5.51 L/min as though they were evidence of the same kind. `doc-consistency-checks` is complete, and `tools/doc_check.py` can now express a one-entry gate group without silently attributing it to the group above.
