---
id: PL-5MYR
title: Generator identification reaches one level up and never clusters the heads: triage asks each item whether a head explains it, so one record read by several readers gets a head per reader, and both such generators found so far - PL-WD5Z's gate prose after three heads, and the claim family PL-MB2W names after four - surfaced only in a sweep the owner asked for
priority: P2
effort: S
status: needs-decision
classes: defect
feature: generator-identification
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, .claude/skills/docket/modes/triage.md, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a gap in how generators are found, held for the owner's decision on lifting the pause
added: 2026-09-23
impairs-generators: the triage mode's generator check and bin/docket generators (cli.cmd_generators, render) compare each new item with one head at a time and never compare heads with each other, so one record read by several readers gets a head per reader and its generator is found only by a sweep the owner asks for
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

**The owner's direction, 2026-09-23.** In their words: "I'd rather fix it right once, then fix it twice" (project owner, 2026-09-23). Of the two
outcomes above, that reads as the first: a pass that compares the heads every
time, rather than the owner asking "are we sure?". Building it is new workflow
mechanism, so it waits for the pause unless the owner lifts the pause for it.

**Decision needed - the project owner's.** Should the pause be lifted for this
item alone? `CLAUDE.md` § "What this project is" allows it: "A request from
the project owner lifts it for that request". **Recommendation: yes, and build the durable version rather
than a prose question alone** (revised 2026-09-23 by `PL-67SX`, under the
owner's "I'd rather fix it right once, then fix it twice"). The question on
its own would ask every pass to compare 35 heads by reading their briefs.
Doing that once took `PL-T7Y1` 262 agents. A question that expensive gets
skipped, which makes it the quick fix half done. The durable version leaves
the judgment with the session and makes the reading cheap:

1. **Each head states its record in one line**: the fact its members misread,
   the thing that, stored once, would have made them impossible. It goes in a
   front-matter field beside `generator:`, and `bin/docket check` asks any
   head that lacks one, as it already asks for a verdict. The seed is below.
2. **`bin/docket generators` prints those lines together, and flags any two
   heads whose `root-cause-of:` lists share a member.** The overlap is a fact,
   not a verdict. On 2026-09-23 it named 11 pairs. They include three of the
   five shared records the audit verified (`PL-G21K` with `PL-4W2L`, and
   `PL-8FJK` and `PL-7TVT` with `PL-MB2W`). They also include both
   misattributions the audit found: `PL-YZJD` under `PL-4W2L`, and `PL-8JQQ`
   under both `PL-MB2W` and `PL-R808`. A set intersection found what took
   262 agents. It missed `PL-J6HP` with `PL-WD5Z` and `PL-6TP8` with
   `PL-1P5V`, which is why the record lines, and not the overlap alone,
   carry the comparison.
3. **The triage generator check and the grooming pass ask against that
   one-screen list**: which record did this reader misread, and does a head
   already state it?

It is a defect in the machinery that finds generators, so it should carry
`impairs-generators:`, which ranks it with the heads. The work above reaches
`generator_paths` (`model.py`, the `generators` output, `checks.py`), so
that claim is sound. **Order:** before `PL-K046`, so the heads it records
start with a record line. **Cost:** one field on about 35 heads, one check,
one output change and two prose edits, all apparatus, effort M. Taking the
cheaper route and redoing it later would mean a second pass over every head
recorded in between. Waiting costs more again. Until the five live heads
close, the only way to find the next record read by several readers is
another sweep the owner asks for.

**Answered 2026-09-23: no lift is needed** (project owner, 2026-09-23). In the
owner's words: "The pause is on apparatus work unrelated to fixing these
generators (new features, housekeeping). 5MYR is exactly the type of thing that
should be in the pause". That is, it is work the pause exists for. The question
above asked for a lift because `CLAUDE.md`'s pause paragraph read as barring
any new field. The wording was wrong, not the rule, and `PL-8L9S` corrected
it. The durable version above is what gets built.

**Then the session's decision:** the field's name and the rule for its
wording, the format of the record listing and the overlap flag, and a rewrite
of the Done-when below to match. Check each seeded record against its head
before writing it.

**Generator check.** A one-off gap in the identification step itself, and not
an instance of a closed head. `PL-KVDK` built the per-item step. `PL-RX3H`
(recurrences never chain across items) and `PL-J870` (promotion declined on
severity) are other gaps in identification, but each is at item altitude. It
cannot carry `impairs-generators:`, because the step is prose in
`.claude/skills/docket/modes/triage.md`, outside `generator_paths`.

**Verified counts (PL-T7Y1, 2026-09-23).** Adversarial verification ran over
two rounds: three skeptics per claim, 262 agents in all. `PL-T7Y1` holds the
method. The counts below replace the unverified figures above wherever the two
differ.

- **Claim family: 20 verified members, 3 open.** Of the 19 instance members
  listed above, 15 survive (`PL-MB2W` is the head, not a member). The four
  that do not:
  - `PL-RY2R` and `PL-1X2C`: the file-edit mark kept one carrier per id before
    the landing test ran.
  - `PL-X3NY`: whether a pull request is open is a forge fact.
  - `PL-WM46`: the batch NOTE parses subjects by regex instead of calling
    `leading_ids`.

  So two of the five called open survive: `PL-MFM4` and `PL-J16N`. The four
  that `PL-MB2W`'s branch copy adds (`PL-X3WZ`, `PL-7790`, `PL-N1JK`,
  `PL-VFJ3`) survive, and so does `PL-8JQQ`, which no list names. The third
  open member is `PL-VFJ3`. `PL-X5PK`, `PL-QNQJ`, `PL-YFXG` and `PL-GJPD` were
  tested and refuted.
- **Head comparison, run once over all 28 heads.** Five pairs share one record
  and survived three skeptics each. The dates below are merge times on main.
  - Who holds an item: `PL-8FJK` and `PL-7TVT`, with the record named by
    `PL-MB2W`. `PL-4Q9B` (clone freshness) and `PL-BHVM` (landing) do not
    belong. Filed after `PL-7TVT` closed spent (ae9f7f6e, 00:16Z 09-23):
    `PL-QP9Z`, `PL-1MCK`, `PL-KWCY` and `PL-VFJ3`.
  - Whether the base holds a branch's work: `PL-BHVM` and `PL-R808`. Filed
    after `PL-R808` closed spent (c03ae7a3, 00:58Z): `PL-PXZ3` (01:18Z) and
    `PL-GHHW` (01:48Z).
  - Gate dispositions held as prose: `PL-J6HP` and `PL-WD5Z`. `PL-HWW1`'s
    record is Required-scope membership, which is a different fact. `PL-2T03`
    and `PL-8YXJ` do not belong either. `PL-WD5Z` is open, so no last close
    exists. Filed after `PL-J6HP` closed: `PL-59QW`, `PL-58JD` and `PL-VFJ3`.
    `PL-16HD` and `PL-694Q` are unlisted members that the lane filter hid,
    because `ROADMAP.md` sits outside `workflow_paths`.
  - verify's test-weakening verdict: `PL-G21K` and `PL-4W2L`. They share
    `PL-XQGH`, `PL-CNJH` and `PL-2DTK`. None filed after.
  - What a `verify:` command proves: `PL-6TP8` and `PL-1P5V`. None filed
    after.

  Refuted pairs: `PL-XYQW` with `PL-8FJK` (they share only
  `_annotates_only`), `PL-9RFP` with `PL-BHVM`, and `PL-HWW1` with `PL-J6HP`.
  So the gate-prose instance above holds with `PL-J6HP`, not with `PL-HWW1` or
  `PL-2T03`. The claim instance holds with `PL-8FJK` and `PL-7TVT`, not with
  `PL-4Q9B` or `PL-BHVM`.
- **Not generators, rechecked.**
  - Hook tokenising (`PL-1SFZ`, `PL-GVFC`) holds at two instances, 0 of 3.
  - Merge skew holds at two instances, `PL-33WM` and `PL-KH3Q`, 0 of 3.
  - Verify's contract copies is a generator by count (3 of 3) and is now head
    `PL-B8HZ` (live). It has six members; `PL-TKFD` is the open one that the
    entry above leaves out.
  - Landed elsewhere is a generator by count (`PL-XLQ5`, `PL-MBTZ`,
    `PL-GHHW`, `PL-PXZ3`), but it is `PL-BHVM`'s and `PL-R808`'s record, not
    a new one.
- **Inflow sweep, 321 items.** Four families no head covered are now recorded:
  - `PL-QHCW`: no record of the commit a release was cut on. Live, 6 members.
  - `PL-HMZZ`: the carrying pull request is inferred after the merge. Live,
    10 members. Three of three skeptics found that `PL-XYQW` does not cover it.
  - `PL-ZJ6X`: the id grammar was restated by hand. Spent, 7 members.
  - `PL-KRZW`: Qt palette roles inherited from the host. Spent, 4 members.

  Existing heads carry unlisted tails:
  - `PL-L4YG` (slug from the title): 9 unlisted, no verdict, judged live 3
    of 3.
  - `PL-9RFP`: `PL-73P0`, `PL-ZPDM`, `PL-1PBV`, `PL-Q9Z1`.
  - `PL-TZ7T` (near-duplicate capture) and `PL-G424` (apparatus prose
    drift).

  Nine more candidates got contradictory verdicts across the two rounds. They
  are held on `PL-K046` rather than recorded.
- **Verdicts a later member contradicts.** These are for `PL-TH9K`'s session,
  which holds the closed-head verdicts on #967; this item does not edit them.
  - `PL-7TVT` spent, which the owner accepted: `PL-QP9Z` (auto-merge erased a
    live start claim).
  - `PL-R808` spent: `PL-PXZ3` and `PL-GHHW`.
  - `PL-J6HP` spent: `PL-59QW` and `PL-58JD`.
  - `PL-4W2L` spent covers only the assertion half, and `PL-G21K` records no
    verdict: `PL-DNZ0` (suppression) is open.
  - `PL-XYQW` spent covers the timing half only.
  - `PL-L4YG` records no verdict.

**What this changes here.** The head comparison this item's Done-when asks
for has now run once. The other half of Done-when, a pass that asks the
question every time, is new workflow mechanism, so it stays captured and
unbuilt while any open item carries `generator: live`. Four live heads are now
open: `PL-WD5Z`, `PL-B8HZ`, `PL-QHCW` and `PL-HMZZ`.

**Head records seeded by PL-T7Y1, 2026-09-23.** One line per head, from the
first round's merged head comparison, with each head's record cut to its first
sentence. They are a seed, not a verdict: the session that builds the field
checks each one against its head before writing it.

- `PL-0HPV`: The list of checks the merge gate runs, held twice as hand-kept
  step lists:
- `PL-1P5V`: What a verify: command proves about its item: the shape half. The
  field is an opaque shell string whose exit status is the only meaning stored,
  so which command shapes ...
- `PL-2T03`: The release train's arrangement: the row order of ROADMAP.md §
  'The timeline', a table parse_timeline already parses and grammar-checks.
  Readers re-derived that order by ...
- `PL-4FBP`: No single record. Each member restates a different tree fact in a
  simulator-facing document sentence whose link to the tree lives only in the
  reader's head: a test name ...
- `PL-4Q9B`: Two facts, per its own answer: 'this cluster is not one mechanism'
  (PL-4Q9B:94). Fact 1, the cache half (PL-4Q9B:64): the remote's refs and tags
  as mirrored by the ...
- `PL-4W2L`: Whether a branch's diff removed or loosened an existing test
  assertion, or added a construct that disables a test, relative to the base.
- `PL-6T44`: Whether all of an item's blockers have closed, derived from
  blocked-by and each blocker's status.
- `PL-6TP8`: What a verify: command's exit status proves: the reading half. The
  field was specified only as a command that fails before the work and passes
  after, so 'every consumer ...
- `PL-7TVT`: Who holds an item now, and whether that holder is still live:
- `PL-8FJK`: Who holds an item, inferred from where a branch's commits wrote
  rather than from what they did to the item.
- `PL-8YXJ`: An item's own queue state (status, blocked-by, sequencing) as its
  front matter holds it, told a second time in the brief's prose, which no
  status or blocked-by write ...
- `PL-9HD1`: The item front-matter grammar as model.FIELD_RE reads it, one line
  at a time.
- `PL-9RFP`: Whether a git subprocess answered or failed:
- `PL-BHVM`: Mixed. Six of its eight members read whether a branch's work has
  reached the base, the fact the merge authors ('"Did this ref's work land" is
  authored by the merge', ...
- `PL-G21K`: Whether a branch's diff weakens the tests that measure it, by
  adding suppression markers or by removing or loosening assertions.
- `PL-G424`: No single record. It is PL-4FBP's docs-drift mechanism on the
  apparatus side ('PL-4FBP's adopted scope reaches only docs/MODEL.md and
  README.md'; 'the same mechanism ...
- `PL-HWW1`: Which ids a milestone's Required scope holds and which it
  explicitly excludes.
- `PL-J6HP`: Mixed, cut at document altitude ('Gate facts ...
- `PL-L4YG`: An item file's canonical serialized form:
- `PL-LN69`: Whether each resident instruction changes session behaviour.
- `PL-NGBM`: A command invocation's resolved context:
- `PL-R808`: Whether a merged pull request left a branch's work behind, that
  is, whether the base holds the branch's work.
- `PL-TZ7T`: Whether an open item already describes the mechanism a new capture
  names:
- `PL-WD5Z`: A debt item's gate disposition ('declined to a later gate,
  deferred, or cleared by the milestone itself', PL-WD5Z:16-17), recorded as
  the item's id appearing in a ...
- `PL-WFFX`: The squash commit's subject and body as the merge client sends
  them (commit_title / commit_message).
- `PL-WNCT`: Pushed work that no open pull request carries to main when the
  session ends.
- `PL-XYQW`: An item's pr: number, meaning the merged pull request that carried
  it. bin/docket record backfills it only after the merge, but bin/docket
  release's notes writer and ...
- `PL-YRYR`: What the docket suite's git-backed test fixtures cost.
