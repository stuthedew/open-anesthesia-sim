---
id: PL-5MYR
title: Generator identification reaches one level up and never clusters the heads: triage asks each item whether a head explains it, so one record read by several readers gets a head per reader, and both such generators found so far - PL-WD5Z's gate prose after three heads, and the claim family PL-MB2W names after four - surfaced only in a sweep the owner asked for
status: untriaged
feature: generator-identification
added: 2026-09-23
---

**Problem.** Generator identification reaches one level up and never clusters the heads: triage asks each item whether a head explains it, so one record read by several readers gets a head per reader, and both such generators found so far - PL-WD5Z's gate prose after three heads, and the claim family PL-MB2W names after four - surfaced only in a sweep the owner asked for

**Found 2026-09-23**, in a second sweep for unrecorded generators the owner
asked for, at higher effort than `PL-02C4`'s, across the 321 workflow,
crossing and unplaced items filed 2026-09-19 to 09-23.

**The step works one level up.** The triage mode's generator check (§ "Ask
every workflow-lane item where it came from") asks each new item whether a
head explains it, then says to "grep for whether any one function or check
already encodes that fact", and to "prefer the one-off over a weak cluster".
Nothing compares heads with each other. So when one record is read by several
readers, each reader's failures get a head of their own, each head is fixed,
and each new failure is judged against one head at a time. The written checks
are each correct at the altitude they were asked at: `PL-WM46` "One-off",
`PL-J16N` "a defect inside an existing shape's test, not a new unclaimed
shape", `PL-KWCY` "Not a generator", `PL-GHHW` "two items in two tools with no
shared function, so not a generator".

**Two instances, both found by a sweep rather than by triage.**

- **Gate dispositions in `ROADMAP.md` prose.** `PL-HWW1`, `PL-2T03` and
  `PL-J6HP` each fixed a reader. `PL-WD5Z` named the record on 2026-09-23.
- **Who holds an item, derived by each reader from commit subjects, touched
  paths and ref age.** Twenty items filed 2026-09-19 to 09-23 are one reader
  getting this wrong. By day: 7, 3, 1, 4 and 5 (`PL-3CTW`, `PL-VYSP`,
  `PL-2BZY`, `PL-61MD`, `PL-RY2R`, `PL-X3NY`, `PL-MFM4`; `PL-1X2C`,
  `PL-7TVT`, `PL-N2PP`; `PL-3QM9`; `PL-3W3P`, `PL-8FJK`, `PL-8GV1`,
  `PL-J16N`; `PL-QP9Z`, `PL-1MCK`, `PL-KWCY`, `PL-WM46`, `PL-MB2W`). The seven
  readers are flight's `branches_in_flight`, `show`, `stranded`, the digest,
  verify's batch NOTE, release's collision guard, and `CLAUDE.md`'s auto-merge
  rule. Four heads each fixed one part of it: `PL-4Q9B` and `PL-BHVM` (both closed
  2026-09-19), `PL-8FJK` (closed 09-22, `live`) and `PL-7TVT` (closed 09-23,
  `spent`). Five more members were filed the day `PL-7TVT` closed as spent.
  Five are open: `PL-X3NY`, `PL-MFM4`, `PL-1X2C`, `PL-J16N` and `PL-WM46`.
  This is `PL-MB2W`'s candidate at family altitude. `PL-MB2W` is claimed on
  `claude/beautiful-lamport-8a9emq`, so this evidence is left here for that
  session rather than written onto it.

**For `PL-MB2W`'s verdict, leads to verify rather than findings.**
`PL-BHVM`'s round refused to record claims. That refusal was ratified
(project owner, 2026-09-19, ratified), so its own text says ordinary evidence
reopens it. The twenty items above are a cost the round did not carry. The
refusal rested on `vcs.py`'s module docstring: a stored claim is left "marked
in-progress forever" by a session that crashes. The established answer to
that objection is a lease, a claim that expires unless its holder renews it
(Gray CG, Cheriton DR, "Leases: an efficient fault-tolerant mechanism for
distributed file cache consistency", SOSP 1989,
https://dl.acm.org/doi/10.1145/74851.74870), and the round did not weigh it.
The landing half of that refusal stands on a different ground and is
untouched here: the merge authors that fact, so no session can record it
(`PL-R808`, `PL-LF2C`).

**Checked in the same sweep and not generators, so nobody re-derives them.**

- **Which copy of an item's contract `verify --self` reads.** `PL-KSV2`
  (`not-delegable:`), `PL-PZ6T` (`verify:`), `PL-BX1C` (status) and
  `PL-ZMGR`, `PL-K4R5` and `PL-YZJD` (`falsifies:`) each decided one field.
  That is a bounded tail and not a generator: the fields are four, three are
  decided, and the base's copy is already read in one place
  (`commissioned_falsification`). `PL-PZ6T` is the last field.
- **Each Bash hook tokenises a command by its own rules.** `PL-1SFZ` and
  `PL-GVFC` are two instances. A third makes it a generator.
- **A change landed through another pull request.** `PL-GHHW` and `PL-PXZ3`
  are two, as their own checks say.
- **Merge skew.** `PL-Z0SM` is held until a third instance, as the owner
  ratified.

**Inflow, for `PL-04KR`'s reading.** Non-product filings by UTC date ran 97,
75, 69, 44 and 36; the last is a partial day, to 04:00Z. Of the 321, 57 have
bookkeeping-shaped titles: 18 release cuts and one tag, 11 triage passes, 10
stranded-work recoveries, and 17 sweeps, deletions, backfills and records.
Those are filed by rule, not found as defects, and 54 of the 57 are closed.
The claim family's share of the daily filings rose on the last two days, from
1% on 09-21 to 9% and then 14%.

**Why it matters.** A head fixed at reader altitude closes, sometimes with a
`spent` verdict, while the record keeps producing. `PL-02C4`'s re-entry
reading (14 of 37 checked filings named a closed fix that had not reached
them) is what that looks like from the item side. Each such generator has so
far been found only when the owner asked "are we sure?".

**Pause.** Any remedy that adds a step or a check is a new workflow mechanism.
Under `CLAUDE.md` § "What this project is", it is captured and not built while
an open item carries `generator: live`, which `PL-WD5Z` does.

**Done when.** One of two outcomes. Either one existing pass (grooming, or the
generator sweep) asks whether two or more heads share one record, and that
question has been run once over `bin/docket generators`. Or the owner decides
the owner-requested sweep stays the mechanism, and this item is dropped with
that decision recorded. Comparing heads is judgment, so the remedy is a
question a session asks, not a script (`CLAUDE.md` § "Prefer deterministic
tooling", "Do not script the judgment").

**Generator check.** A one-off gap in the identification step itself, and not
an instance of a closed head. `PL-KVDK` built the per-item step. `PL-RX3H`
(recurrences never chain across items) and `PL-J870` (promotion declined on
severity) are other gaps in identification, but each is at item altitude. It
cannot carry `impairs-generators:`, because the step is prose in
`.claude/skills/docket/modes/triage.md`, outside `generator_paths`.
