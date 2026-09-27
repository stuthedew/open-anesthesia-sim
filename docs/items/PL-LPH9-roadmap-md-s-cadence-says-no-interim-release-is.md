---
id: PL-LPH9
title: ROADMAP.md's cadence says no interim release is cut partway through clearing a gate, but 159 of Gate 1's 175 frozen entries already shipped in v0.4.x patches, so the sentence a later session would cite to refuse a cut describes nothing this project has done since v0.4.5
priority: P2
effort: S
status: done
classes: docs, planning
touches: ROADMAP.md
added: 2026-09-19
closed: 2026-09-27
pr: 1189
payoff: stops a later session declining a release the project has cut twenty-seven times, on a cadence rule ROADMAP.md still states
verify: grep -q 'A gate does not get a version of its own' ROADMAP.md && ! grep -q 'decline it, or the gate work scatters' ROADMAP.md && ! grep -qF 'Later gates ship *inside*' ROADMAP.md
---

**Problem.** ROADMAP.md's cadence says no interim release is cut partway through clearing a gate, but 159 of Gate 1's 175 frozen entries already shipped in v0.4.x patches, so the sentence a later session would cite to refuse a cut describes nothing this project has done since v0.4.5

**The two sentences, read against the tree 2026-09-20.** `ROADMAP.md`
§ "The cadence" states the rule twice:

> **A gate does not get a version.** Cleared gate work ships inside the
> milestone it gates: it lands between that milestone's predecessor and its own
> release, so the milestone's release notes carry it, and no interim release is
> cut partway through clearing. `docket release` will offer one as soon as a
> few gate items are finished — decline it, or the gate work scatters across
> patch releases and the milestone ships carrying only its feature work.

and again where the Qt port reads it as the one open question about its own
number. `bin/docket wave` that day: Gate 1 holds 175 entries, **172 cleared,
3 open**, and the version is 0.4.32. Those 172 cleared across the v0.4.x patch
track - twenty-seven patch releases between v0.4.5 and v0.4.32 - which is
precisely "the gate work scatters across patch releases", done deliberately,
release after release, by sessions following the offer the sentence says to
decline.

**Why it matters.** This is a rule a later session would cite to refuse work,
and it is the only kind of sentence `.claude/rules/expert-review.md` singles
out for that reason - `ROADMAP.md` and `docs/MODEL.md` are the two documents
whose prose closes questions. A session reading it correctly declines a release
the project has cut twenty-seven times, and one reading the practice correctly
is contradicting the roadmap. Neither is wrong about what they read, which is
what makes it worth an item rather than an edit: whichever way it is
reconciled, the reconciliation is what stops the next session re-deriving it.

It also reaches `bin/docket release`, which offers the cut. The tool does what
the sentence says it will do; what the sentence says to do about the offer is
what no longer matches.

**Decision needed.** Which of the two is the record - and this is a release
train question rather than a wording one, which is why it is not being answered
at triage:

1. **The prose is stale.** Cutting patch releases while a gate drains is the
   working practice, the gated milestone still takes its own number, and the
   sentence is rewritten to say so. **Recommended**: 172 of 175 entries shipped
   this way with no observed harm, and the stated cost - "the milestone ships
   carrying only its feature work" - is what a milestone release *should*
   carry once its debt has been paid down continuously. It also matches
   § "Versioning decision", where the number marks the capability boundary
   crossed, and a gate crosses none.
2. **The practice is wrong.** The rule stands, and clearing the remaining gate
   entries happens without further patch cuts. Costs: work sits unreleased for
   the length of a gate, which at Gate 1's size was months, and the ephemeral
   container makes an unreleased finished item indistinguishable from an
   unfinished one to every session that follows.

Whichever is chosen, § "The cadence" and the Qt port's open-question paragraph
both change, and Gate 0's exemption paragraph should be re-read in the same
pass - it exists to explain why v0.3.0 was allowed a version, which option 1
would make unremarkable.

**Done when.** `ROADMAP.md` § "The cadence" states one rule about interim
releases during a gate that the last twenty-seven cuts satisfy, and the Qt
port's paragraph citing the old reading is brought into line with it.

## Answer 2026-09-27

**Option 1, in the project owner's own words** (project owner, 2026-09-27):
"Also, make sure to cut versions when appropriate on our way to v0.6.0",
written in the project's thread as an instruction rather than as an answer to
the two options above - so it is a decision he specified, recorded in the
plain form `CLAUDE.md` § "Working with the project owner" keeps for one, and
it reopens only on a compelling argument. It coincides with option 1: patch
releases are cut while a gate drains, and the gated milestone still takes its
own number. The project's standing instructions of the same day say what
"when appropriate" currently means - when a feature finishes, a thread cuts a
release with what is in it, none while another session holds the release
train, and the owner pushes the tag from his own machine with the one-line
command the thread gives him - and name this item as where the ask is
recorded.

**The count, refreshed against the tree the day the answer landed.** The
brief above was written at v0.4.32 with Gate 1 at 172 of 175 cleared across
twenty-seven patch releases. On 2026-09-27 the version is 0.5.14; Gate 2 froze
on 2026-09-21, the day v0.5.0 shipped, with 190 entries; `git tag` lists
`v0.5.1` through `v0.5.14`, fourteen patch releases cut in the six days since,
stamping 323 items between them; and `bin/docket wave` reads 92 of the 190
cleared. Forty-one interim releases across two gates, every one cut
deliberately by a session that read the offer the sentence says to decline.

**What the answer settles, and what it leaves to rules that already exist.**
Three consequences, decided here under `.claude/rules/instruction-writing.md`
rule 14 because each is one document's phrasing or a reading of a rule the
roadmap already states:

1. **The number of an interim cut is a patch on the preceding milestone's
   track** - `v0.5.x` until v0.6.0 is cut - and needs no new sentence.
   § "Versioning decision" already chooses a number for the capability
   boundary it crosses, gate work crosses none, and `docket release` reads
   the versions the roadmap has spent ahead of the current one
   (`release_offer`'s `RESERVED` answer in
   `subprojects/docket/src/docket/release.py`; `bin/docket wave` prints them
   as `Reserved 0.6.0, 0.7.0, 0.8.0`), so it cannot offer 0.6.0 for a patch's
   worth of work. v0.6.0 is cut when its Definition of done holds, which the
   project's instructions have a thread check first. Interim cuts during
   beat 4, the build, are outside this item - the cadence sentence is about
   gate work - and rest on the same capability-boundary test, with the same
   reserved number keeping them patches; the `v0.4.35` row of § "Versioning
   decision" records that shape already, "a patch on one half of the test
   rather than on both - stated rather than smoothed over".
2. **The trigger is a session's judgment that finished work is worth a
   release, and "a feature finishing" is the instance that judgment currently
   turns on**, dated 2026-09-27. The roadmap records the instance with its
   date rather than a per-feature rule, per `.claude/rules/expert-review.md`
   § "Say what would falsify it, then record the instance rather than the
   rule": what would falsify a per-feature rule is already on the roadmap -
   a session with finished items and no feature among them - and the
   project's own cadence before 2026-09-27 was `docket release`'s offer,
   taken when a session judged the work worth it.
3. **The rewrite keeps the clause that is still true and replaces the one
   that is not.** "A gate does not get a version" survives as "a gate does
   not get a version *of its own*": the gate as a whole has no number, and
   Gate 0 stays the single exception because it was given the *minor*
   v0.3.0. What goes is "no interim release is cut partway through clearing"
   and the instruction to decline `docket release`'s offer. The old rule's
   stated cost - "the milestone ships carrying only its feature work" - is
   what a milestone whose debt was paid down continuously should carry, as
   the recommendation above already argued.

**Four passages state the old rule, not the two the brief counted.** The
build thread brings them into line in one commit on this item's id; they are
named by heading and quoted string rather than line, per
`.claude/rules/citation-drift.md`:

- § "The debt gate" -> "The cadence": the paragraph opening "**A gate does not
  get a version.**" and the one after it opening "Gate 0 is the single
  exception". The draft below replaces both.
- § "Versioning decision": the paragraph opening "**This is an exception and
  not a precedent.**", whose sentence "Later gates ship *inside* the
  milestone they gate and take no version of their own" is the rule's third
  statement. One sentence changes; the draft below has it.
- § "Completed: v0.4.26 - the interface moves to Qt": the paragraph opening
  "**The one question the reorder leaves open is this number**", which
  quotes "no interim release is cut partway through clearing one" as the
  rule. Its reading - that the port is a milestone carrying gate fixes, per
  § "Debt inside the milestone's own scope" - stands; the quoted clause is
  the only part to change, and a bracketed note dated 2026-09-27 naming this
  item is enough, since the section is a completed milestone's record.
- § "Completed: v0.5.0 - the case you can branch" -> "Debt gate: the frozen
  list": the paragraph opening "**Three groups, and only the third is a
  precondition.**", which quotes "A gate does not get a version" by its first
  six words. Keeping those words at the head of the rewritten sentence keeps
  this passage true as written, so it needs no edit; the build thread reads
  it to confirm.

**Draft wording for § "The cadence"**, a draft rather than the text - the
build thread's judgment on wording is its own:

> **A gate does not get a version of its own; its work ships as it clears.**
> Cleared gate work ships in patch releases on the preceding milestone's
> track - `v0.4.x` while Gate 1 drained, `v0.5.x` while Gate 2 does - cut
> whenever a session judges finished work worth releasing, and the gated
> milestone's own number is reserved for the capability boundary its scope
> crosses, per § "Versioning decision". Its release notes then carry its own
> scope, which is what a milestone whose debt was paid down continuously
> should carry. **This records the practice rather than changing it**
> (project owner, 2026-09-27, `PL-LPH9`): the sentence that stood here said
> no interim release is cut partway through clearing and told sessions to
> decline `docket release`'s offer, while twenty-seven patch releases between
> v0.4.5 and v0.4.32 shipped 172 of Gate 1's 175 entries and fourteen more,
> v0.5.1 through v0.5.14, shipped Gate 2's first 92 of 190 - none of them
> declined. Since 2026-09-27 the occasion for a cut is a feature finishing: a
> thread cuts a release with what is in it, and the project owner pushes the
> tag. That is the instance the judgment currently turns on, dated so a later
> reader can tell it from the rule.
>
> Gate 0 is the single exception, released as the *minor* v0.3.0 for the
> reason recorded under § "Versioning decision". It is exempt because it holds
> the backlog inherited from before this mechanism existed; every later gate
> holds one milestone's findings and is ordinary maintenance, which ships in
> patches and takes no number of its own.

And for § "Versioning decision", the one sentence: "Later gates take no
version of their own: their work ships in patch releases on the preceding
milestone's track as it clears, and the milestone's own number marks the
boundary its scope crosses - see § "The cadence" under § "The debt gate"."

[superseded 2026-09-27] **Status is left at `needs-decision` here.** This record was written by a
design thread that pushes item files only; the thread that rewrites
`ROADMAP.md` sets the status first and closes the item on that commit. Its
`touches:` already names the one file, and its effort stays `S`: the
passages are located and the wording is drafted above.

## Built 2026-09-27

`ROADMAP.md` now states the practice, on the draft above with its counts
re-read. The four named passages are handled as planned: § "The cadence"'s two
paragraphs are rewritten, § "Versioning decision"'s sentence is replaced, the
v0.4.26 paragraph carries a dated note beside the clause it quoted, and the
v0.5.0 "Three groups" paragraph was read and needed nothing. The draft's "v0.5.1
through v0.5.14 shipped Gate 2's first 92 of 190" was corrected: 92 was the
count *cleared*, which includes drops and closures not yet released, and the
Gate 2 entries stamped with a `v0.5.1`-`v0.5.14` milestone number 67. The Gate 1
figure is kept as the dated `bin/docket wave` reading it was - 172 of the 175
entries the list held on 2026-09-20 - since the list closed at 185.

**Five more passages stated or quoted the old rule, and the sweep found them**:
the timeline rows for Gate 2 ("Ships inside v0.6.0."), Gate 3 and Gate 4
("ships inside v0.7.0" / "v0.8.0") are rewritten, since each is a live
sentence a later session could cite to decline a cut; the Gate 1 row and the
v0.5.0 record of this item's own decline to Gate 2 are completed records, so
each carries a dated note instead. One more, the `PL-WZVZ` deferral paragraph
under v0.5.0 ("Gate 2 freezes when v0.5.0 ships and ships inside v0.6.0"), was
read and left: it is a dated decision's reasoning, and its point - that the
entry is workable only once v0.6.0's scope lands - does not rest on where gate
work ships. `subprojects/docket/src/docket/plan.py` argues from the old rule in
a comment and is outside this item's `touches`, so it is filed as `PL-QVSN`.
