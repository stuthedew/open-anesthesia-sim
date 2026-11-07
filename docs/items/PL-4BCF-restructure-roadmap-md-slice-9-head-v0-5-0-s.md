---
id: PL-4BCF
title: Restructure ROADMAP.md, slice 9: head v0.5.0's gate dispositions by the ground each was decided on
priority: P2
effort: M
status: blocked
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
blocked-by: PL-V8SJ
deferred-from: v0.7.0 - filed after the gate froze; the roadmap's arrangement and wording, with no displayed value depending on it
added: 2026-11-07
---

**Problem.** Restructure ROADMAP.md, slice 9: head v0.5.0's gate dispositions by the ground each was decided on

**Source.** The copy editor's structure read of `ROADMAP.md`, run on the project owner's Mac on 2026-11-06: one read per chapter, then one read of all the chapters' outlines together. Row numbers are `ROADMAP.md` at `aff76df1`, the last commit to change it before slice 1 (`PL-W0TS`), so a later slice finds each passage by the words the finding quotes. The project owner chose to file the findings as items and apply them one slice per pull request (project owner, 2026-11-07, ratified, over one pull request for the whole restructure), because the release tools read the roadmap's gate sections and a small move is easier to check against them. The raw reads are in the project's shared folder, `/mnt/project-files/v0.7.0/repo-copy-edit/mac-structure-reads/ROADMAP-md/structure/`.

**Why it matters.** The heading "Declined to Gate 2 on the refilling-queue ground" holds dispositions on five other grounds, so a reader looking for why an entry was declined cannot trust the heading. The section is about 2,000 rows that the reader deciding a release does not act on.

**The findings, as the outline read gave them** (numbered by their order in the read: 6, 10).

- Heading (3548-5219): "Declined to Gate 2 on the refilling-queue ground" also holds dispositions on five other grounds:
  - the problem did not exist at the freeze (3890-3912, 4918-4927, 5088-5105);
  - the milestone's own work created the problem (4102-4110, 4160-4175);
  - the item was placed in a Required scope, v0.5.0's at 4382-4404 and v0.6.0's at 4432-4491;
  - the decision has been answered (4504-4514, 4807-4817);
  - nothing misleads in the meantime (4982-5044).
  The own-work passages belong in the sibling § "Declined to Gate 2, because this milestone's own work created them" (3221-3249). Give the rest a heading that says what it holds, such as "Declined to Gate 2, each on its stated ground", with a subheading for each triage pass. Keep the opening "Declined to Gate", because the checker reads it (4819-4827), and update citations such as 5718-5729.
- Written for another reader, an owner's decision (3221-5219): about 2,000 rows record Gate 1's dispositions item by item, and the reader deciding a release does not act on them. v0.6.0 moved its own 43 such records onto the items on 2026-09-23 (6409-6413). § "Recording it" says completed sections keep these subsections (7885-7905), so moving them to the items or to a history file is the project owner's call.

**Answered 2026-11-07 in `PL-LVN8`: the rows move to the items.** Each disposition moves to its item's brief as a dated paragraph, and the roadmap keeps one line per ground with the ids. The rest of this paragraph is the question as it was put.

The outline read leaves the 2,000 rows to the project owner: § "Recording it" says completed sections keep these subsections as the record of their period, while the writing rule puts decision history in the item. If the rows move to the items, this slice moves them and keeps one line per ground in the roadmap, and most of the chapter reads' findings below no longer apply. If they stay, this slice applies finding 6's headings and the chapter reads' findings. Keep the heading opening "Declined to Gate" either way, because older citations name it.

**The findings inside each chapter, as the chapter reads gave them.** Each chapter read also ended with an outline of one line per paragraph, which is left out here and kept in the shared folder. Each read is quoted whole, as a block, so that its quotations of the roadmap are not taken for this item's own claims.

**Chapter read 17: § "Declined to Gate 2, because this milestone's own work created them", rows 3221-3249.**

```text
- Rows 3221, 3231-3232 and 3249 make the same point three times. The heading says "because this milestone's own work created them". The opening paragraph says "That pull request was work done while implementing the milestone this gate protects, which is the case the rule names explicitly". The PL-624C entry says "the capability it fails to cover is this milestone's own". The point belongs once, in the opening paragraph, where it covers both entries. The heading keeps it as the section's subject, and the PL-624C entry keeps nothing.
- Rows 3226-3229 and 3240-3241 give two different reasons for leaving an entry out of the gate. The opening paragraph says "The difference comes from the rule, not from a judgment about severity. Neither is classed `safety` or `science`". The PL-WG73 entry says "it displays no wrong clinical value, which is why it sits at `P2` and outside this gate". The gate reason belongs in the opening paragraph. The entry keeps only its own fact: it shows no wrong clinical value, so it is `P2`.
- Rows 3223-3232 open with "**Recorded rather than silent**", which talks about the text itself. The paragraph's point comes only at rows 3227-3232. Use this order: (1) both entries are deferred from Gate 2; (2) neither is classed `safety` or `science`; (3) both were created by this milestone's own work, in the pull request that built the fork control on 2026-09-20; (4) only then, the contrast with PL-25DD and PL-LHBY, if it stays. The duty to record each decision can follow as a pointer to § "The gate is a snapshot, not a moving target".
- Rows 3224-3226 and 3229-3230 are history for another reader: which review found the entries ("The same adversarial review of `#784` found both ...") and how their origin was dated (`git log -S` ... `d048aca`). This detail belongs in items PL-WG73 and PL-624C. The opening paragraph keeps the result: the pull request that built the fork control created both, on 2026-09-20.
- Rows 3234-3235 and 3243-3245 are written for a developer. They give a constant (`COMPARING_FORK_LOCK_TEXT`), a folder (`app/`), a test name (`test_the_branch_is_drawn_beside_the_trunk_on_one_time_axis`) and a call (`view.present(False)`). This reader does not know the internal names of tests, and the writing rule forbids those names in prose for the owner. These details belong in items PL-WG73 and PL-624C. The entries should keep two things in plain words. For PL-WG73: the notice tells the learner to "Reset the case", but the button is labelled "Reset". For PL-624C: the check that the branch is drawn beside the trunk triggers the redraw itself, so it would pass even if a fork failed to redraw.
- Rows 3221, 3226 and 3234/3243 use two names for one decision. The heading says "Declined"; the paragraph and both entries say "deferred". A better heading is "Deferred from Gate 2, because this milestone's own work created them". Other files may cite the old heading, so update those citations along with it.
- Query: rows 3224, 3228, 3229 and 3247-3248 name rules without saying what they ask: "either disposition", "the unconditional re-entry", "the presence test", "compounding friction" and "the arithmetic that rule asks for". The reader needs each in plain words, and this chapter does not give them.
- Query: rows 3226-3227 and 3240-3241 conflict. The paragraph says the decision did not rest on severity. The PL-WG73 entry puts the entry outside the gate because it shows no wrong clinical value. Only the author knows which reason applies.
- Query: the reader needs to know where the two deferred entries go, such as which later milestone or release. The chapter does not say.
- Query: PL-WG73 gives a priority (`P2`), but PL-624C gives none. The reader deciding what a release holds needs both.
- Query: rows 3234 and 3243 give the deferral date (2026-09-21) but not who deferred the entries or whether the owner ratified it. This reader does not know decisions taken in sessions they did not see.
```

**Chapter read 18: § "Deferred to v0.4.26, because the port dissolves the defect", rows 3251-3280.**

```text
- **Repeated fact.** Rows 3262-3263 say "Qt supplies no such theme, so the port's `theme.py` declares those colours itself, and the tool can reach them". Rows 3276-3278 say it again: "Qt supplies no disabled-state theme, so the ported `app/theme.py` declares those colours as constants. That gave `tools/contrast_check.py` something to be pointed *at*." The fact belongs at 3262-3263, as a reason for the deferral. The outcome paragraph needs nothing beyond "right about the mechanism" (3275-3276). The two places also give one file two names, "the port's `theme.py`" and "`app/theme.py`". Use one name in both places.
- **Repeated fact within 3255-3257.** "`PL-NGF7` stays written in its ... block above" and "It does not delete it" say the same thing. Keep the first as the pointer to the block. Cut the second, along with "This section records its disposition", which only describes the text.
- **Lighter repeat.** Three places say that the port resolves the defect: the heading (3251), 3262-3263, and "the port resolves the item" (3270-3271). At 3270-3271, keep only what the prediction adds: closing the item would need no work on the item itself.
- **Written for another reader (3253-3257).** This paragraph tells writers why the deferral is recorded here and how the record keeps the item. It is narration about the text. The owner needs one sentence from it: `PL-NGF7` is on the frozen gate list, in its block "Added 2026-09-08 under the presence rule" above, and was deferred to v0.4.26, which § "The gate is a snapshot, not a moving target" allows. Cut the rest.
- **Internal names (3259, 3265-3267, 3278).** "the unconditional `safety`/`science`/`P0` re-entry in `check_gate_reentries`" and `tools/contrast_check.py` are internal names this reader does not know. Keep the facts in plain words. The tool that checks colour contrast cannot see disabled-state colours. Items classed safety, science or P0 must stay in the gate no matter what. This item is classed infra/test, so no rule keeps it there. Move the code names to item `PL-NGF7`.
- **Written for another reader (3271-3273).** "This expectation is recorded now, so that a later session does not mistake a dropped item for one that was skipped" speaks to later sessions about the record. Move it to item `PL-NGF7`, or cut it.
- **Narration about the text (3278-3280).** "The expectation above is left as written rather than edited, because what it got wrong is the useful part of the record" describes the record, not the item. Cut it, and state directly in the outcome paragraph what the prediction got wrong.
- **Paragraph that makes two points (3259-3268).** Rows 3259-3261, up to "a defect *of Flet*", say what the defect is. Rows 3261-3268 say why it could wait: the port makes the colours reachable, clearing it now would build a tool for an interface about to be replaced, its class does not keep it in the gate, and its problem does not outlast the change of toolkit. Split the paragraph after "a defect *of Flet*". Its bold opening "**`PL-NGF7`**" is an id, not a point, so open with the defect in words.
- **Order.** A reader deciding what a release holds needs the outcome first, but the outcome comes last (3275), after a prediction (3270-3273) that it overturns. Use this order:
  1. What the item is, and that it was deferred from the frozen list to v0.4.26 and closed `done` there (#621).
  2. Why it was deferred (3261-3268).
  3. One paragraph that merges 3270-3273 with 3275-3278: the item was expected to close `dropped`, because the port would resolve it with no work on the item itself, and it closed `done` because of the work it actually needed. This keeps what the prediction got wrong, which 3279-3280 calls the useful part, without the narration.
- **Heading (3251).** It names neither the item nor the outcome. "The port" does not say which port, and "dissolves" is used in a private sense. Suggested heading: "Disabled-state colour contrast, deferred to the Qt port and closed in v0.4.26". If another file cites the old heading by its text, change that citation too.
- **Query (3251, 3253, 3263-3265, 3275):** the heading and 3275 put the deferral and the closure in v0.4.26. Rows 3263-3265 say that clearing the item "before v0.5.0" would mean building something for an interface about to be replaced. The reader needs to know which release's gate "this list" (3253) is, and which release holds the port, and the text does not say.
- **Query (3275-3278):** "wrong about the work" never says what work closing the item `done` took. "Something to be pointed *at*" suggests that someone pointed the contrast tool at the new constants. The reader needs that work stated, and the text does not give it.
- **Query (3267-3268):** "Its problem also does not predate the freeze in any sense that survives the toolkit changing underneath it" answers a gate rule the section never states, presumably that an item whose problem predates the freeze stays in the gate. To follow the sentence, the reader needs that rule or a pointer to it, and the text gives neither.
```

**Chapter read 19: § "Sequenced past v0.5.0, so not clearable before it begins", rows 3282-3546.**

```text
- Repeats, the entries staying as frozen. Four places say it: "The entry stays written as the freeze put it ... It does not delete the entry" (3292-3295), "The heading and every entry below stay as the freeze wrote them ... does not delete them. `PL-NGF7` already had the same treatment" (3304-3307), "Every entry below stays where the freeze wrote it, exactly as `PL-NGF7` does ... does not delete them" (3374-3376), and "The entry stays on Gate 1's frozen list above ... What moves is the disposition, recorded here" (3516-3520). Say it once, in a new first paragraph under the heading, together with "Those headings record what the list said on 2026-09-06, not a claim about today" (3377-3378). The other three places keep nothing.
- Repeats, the rule for deferring an entry. Two places give it: "allows a deferral only where this section 'says so and says why' ... renegotiation by frontmatter (`PL-9S30`)" (3367-3372) and "permits a deferral only where this section says so and says why. `PL-9S30` shows what it already cost" (3500-3505). Give the rule once, in the same opening paragraph. 3500-3505 keeps nothing, because the `PL-WZVZ` entry is the record itself.
- Repeats, the safety rule, under three names. "A `safety` entry re-enters the current gate whenever it is found, per § "The cadence"" (3330-3332), "The presence rule assigns a `safety`-classed finding to the *current* gate" (3397-3400) and "the unconditional safety exception" (3527-3528) are one rule. State it once, at the first entry added after the freeze, with the § "The cadence" pointer and one name. The other two places keep only that name.
- Repeats, the planning tool's count. Three places explain it: "`bin/docket wave` still prints all thirteen ... Do not "fix" the count" (3334-3342), "The two readings agree. `bin/docket wave` reports ..." (3520-3524) and "`bin/docket wave` arrives at the same eleven ... visible on the next run" (3540-3546). Merge them into one paragraph at the end of the section. The other two places keep nothing. The counts and the claims disagree; see the queries.
- Repeats, the split of `PL-8PS6` and `PL-WZVZ`. "The two that do not move ... `PL-8PS6` can be started and `PL-WZVZ` cannot" (3353-3358) repeats 3454-3470. It belongs in the design-round group. 3353-3358 goes, along with its § pointer to a bold opening phrase.
- Repeats, the "written once, in the port" rule. "Text on a dashboard that is rewritten from scratch is written once, in the port" (3327-3328) repeats "Each defect lives in code that milestone rewrites from scratch. Fixing it on Flet would mean writing the same lines twice" (3385-3387). Keep the rule under "Carried by the Qt port — 5", and move the `PL-2K1R` paragraph (3323-3332) after that group, keeping "follows the same rule". As placed now, 3326-3327 makes the reader read ahead to a rule that is explained only at 3382.
- Repeats, the move from version numbers to port items. "Each now names the port item that does the work" (3360-3362) and "Each entry now carries a `blocked-by:` field naming the port item that does the work" (3387-3388) say the same thing. Keep one sentence, in the opening paragraph after the table.
- Repeats, the `PL-YLKR` split. "(project owner, 2026-09-14, splitting `PL-YLKR`)" (3397-3398), "It is the same split taken over `PL-YLKR` on 2026-09-14 ..." (3438-3440) and "`PL-YLKR`'s design is toolkit-independent" (3449-3450) all give it. Keep the dated split at `PL-YVHK`. 3438-3440 keeps "the same split as `PL-YLKR`'s". 3449-3450 moves out with the account of how this was found.
- Repeats, what blocks `PL-WZVZ`. "one profile exists, and there is nothing to compare" (3489-3490), "one machine profile exists and there is nothing to compare" (3497-3498) and "a second profile, or a surface that names a machine" (3537-3538) state one condition three times. "the paragraph below" (3489) points into the same list item. State the condition once, where `PL-TBMK` and `PL-4TWW` are named.
- Repeats, `PL-TH35` and `PL-R1WQ` arriving by v0.6.0. "Both are placed by v0.6.0" (3486) and "v0.6.0. That is the same release that carries `PL-TH35` and `PL-R1WQ`" (3511-3512) give it. Keep it in the Gate 2 paragraph.
- Repeats, `PL-NGF7`. "`PL-NGF7` already had the same treatment" (3306-3307) and "exactly as `PL-NGF7` does" (3375) repeat the group paragraph (3413-3414), which keeps it.
- Another reader's: decision and editing history belongs in the items it names. 3344-3351 goes to `PL-D143`; the reader keeps one sentence, that the gate can now reach zero before v0.5.0. "Until 2026-09-13 it was not recorded ... The other eight said so in a `blocked-by:` field and nowhere else" (3367-3372) goes to `PL-9S30`. "This paragraph used to say that item 1 did not exist ... disagreed about whether the intent was recorded at all" (3458-3461) goes to `PL-Z4WL`. The statuses of `PL-005` and `PL-LPLD` (3362-3365) and "what its own `verify:` command tested for" (3388-3389) go to `PL-D143`. "Each is argued where it was taken. This section is the index, not the argument" (3379-3380) is narration about the text and goes.
- Another reader's: "How this was found is worth one line" (3442-3451) is decision history. The owner needs one sentence of it in the `PL-16ZC` group: of the Flet-related entries, only `PL-16ZC` waits for the port, and the rest survive it or feed it. The count and the examples go to the item that records the 2026-09-14 question (see the queries).
- Another reader's: code and tool names this reader does not know belong in the items. "`ScatterPlotItem` ships with `hoverable` set to `False`" (3410-3411) and the 1 870 strings, 71.9 ms and 90 KiB (3405-3407) go to `PL-YVHK`. The `MilestoneStates.ships_with` reasoning (3428-3431) and `app/simulation_view.py` with its line count (3424-3425) go to `PL-16ZC`. The file paths, `deliverable_flow_range_l_min` and `core/supported_ranges.py` (3472-3477) go to `PL-8PS6`. "`verify_required_from`", "grandfathered set" and "`bin/docket gate`" (3287-3292) go to `PL-Z34C`. Each place keeps the sentence the owner needs, in words.
- Placement: `PL-WZVZ`'s `safety` class first appears at 3527, 47 rows after the entry is introduced at 3480. State the class in the entry's first sentence.
- Order: the section opens with the thirteenth entry (3284-3299) before the reader has met "these eleven" (3301) or "the twelfth" (3323). Use this order:
  1. The frozen heading.
  2. An opening paragraph: the heading and entries record the 2026-09-06 list; the rule for deferring an entry.
  3. What changed, with the table (3301-3302, 3309-3321).
  4. The groups in table order: carried (3382-3389), then `PL-2K1R` (3323-3332); sequenced behind (3391-3411); dissolved (3413-3414); deferred past (3416-3440); the design round (3454-3538).
  5. `PL-Z34C` and its entry (3284-3299), because it waits on something other than the port.
  6. One paragraph on the planning tool's count.
- Too long: at 2880 words the reader cannot find a given entry. Turn the bold opening phrases at 3382, 3391, 3413, 3416 and 3454 into `####` subheadings. Give `PL-WZVZ` (3480-3538) a subheading of its own, because its five paragraphs make one list item into an essay. Add subheadings for `PL-Z34C` and for the count paragraph.
- Pointers: § "Behind a design round no milestone section places" (3357) and § "What reads this, and what reads past it" (3524) point at bold opening phrases, not headings, so the documentation check cannot find them. Make them headings, or write "below".
- Pointers: § "Completed: v0.4.26 - the interface moves to Qt" (3303) uses a hyphen and 3384 uses an em dash. 3394, 3404 and 3421 shorten it to § "Completed: v0.4.26". Use the heading's exact text in every place.
- Heading: "Sequenced past v0.5.0, so not clearable before it begins" no longer describes the section. Nine of the eleven now clear before v0.5.0, and `PL-Z34C` is not sequenced behind anything. The snapshot rule keeps the heading's text, so the new opening paragraph must say that the heading records the 2026-09-06 list. Optionally, add a subheading such as "Where these entries stand since the port moved" above 3301.
- Heading: the bold phrase "What reads this, and what reads past it" (3540) does not say what its paragraph holds. Use, for example, "Why the planning tool's count can differ from this section", and update the pointer at 3524.
- Heading: the bold phrase "Behind a design round no milestone section places" (3454) is out of date, because that design round has happened (3467). Use, for example, "Waiting on the machine abstraction, now closed".
- Query: the planning tool's output is given three ways: "all thirteen" as waiting (3334), "the same eleven" (3540-3541) and "`0 this gate can clear, 1 waiting on 3 open items outside it`" (3521-3522). None is dated. "3 open items" does not match the four blockers of `PL-WZVZ`: `PL-TH35`, `PL-R1WQ`, `PL-TBMK` and `PL-4TWW`.
- Query: "The two readings answer different questions, and both are true ... Do not "fix" the count" (3339-3342) contradicts "If the prose and the count disagree, one of them is wrong" (3544-3546).
- Query: "the gate waits on `PL-FG9D` alone" (3297) contradicts "`PL-FG9D` closed on 2026-09-20 (`#748`)" (3355). The reader needs to know what the gate waits on now.
- Query: `PL-YVHK` "arrived after the freeze rather than at it" (3397), yet it is counted among "these eleven" (3301), while `PL-2K1R` is "the twelfth, added after the freeze" (3323). The reader needs to know which entries the freeze held. Also, "unlike the seven above" (3463) does not match the nine.
- Query: "Each sequencing decision was the project owner's, taken on 2026-09-10" (3378-3379) contradicts the 2026-09-14 decisions on `PL-YVHK` (3397), `PL-16ZC` (3418) and `PL-2K1R` (3323).
- Query: `PL-005` and `PL-LPLD` (3362-3363) are counted among "All nine" but are missing from the table, and "five of the six" (3364-3365) does not say six of what.
- Query: "Every entry below" (3304, 3374) finds only the `PL-Z34C` entry below it. The text does not say where the eleven entries stand, or which five sit under "Cleared before v0.5.0 begins" (3376-3377).
- Query: the table row "behind a design round the roadmap places nowhere | unchanged" (3320) contradicts 3472, where `PL-8PS6` clears inside this gate, and 3507, where `PL-WZVZ` clears in Gate 2. 3454-3465 likewise says in the present tense that both wait on `PL-FG9D`.
- Query: the port's section is titled "Completed: v0.4.26 — the interface moves to Qt", but this chapter treats the port as still to come ("now lands before v0.5.0", "waits for the port *landing*"). The reader needs to know whether the port has shipped and whether the five carried entries are done.
- Query: the decision to clear `PL-WZVZ` in Gate 2 (2026-09-20) rests on v0.6.0 carrying `PL-TH35` and `PL-R1WQ`. On 2026-09-21 two more blockers were added, and "No milestone section schedules either new item" (3492). The owner must decide whether Gate 2 still holds.
- Query: three figures carry no date. "`PL-KP7H` measured that frame at 71.9 ms and 90 KiB" (3406-3407), "all 4 321 lines" (3424) and "the 13 prerequisites ... that `PL-FCM3` measured" (3295-3296) each need the date they were measured.
- Query: "no longer counts as debt" (3289) contradicts "were never debt classes" (3291). Separately, "over keeping it on the frozen list" (3285) contradicts "The entry stays written as the freeze put it" (3292-3293).
- Query: `PL-YVHK` is "`safety`-classed for the same reason" (3396), but `PL-GS3R`'s paragraph gives no reason for its class.
- Query: the text calls the safety exception "unconditional" (3528) and then defers a `safety` entry. The reader needs to know which decision allows that.
- Query: the chapter uses terms that this reader does not know and it does not explain: "grandfathered set" and what `verify_required_from` does (3287-3288, 3299), "debt" and "debt classes" (3289-3291), "the beat" (3348, 3543), "the `anticipated` exemption" (3478), "its band" (3537), "parity claim" (3330), "carrier" (3472), "renegotiation by frontmatter" (3372), "promotable" (3491) and "Done-when" (3436).
- Query: the text names no item for the history at 3442-3451, the owner's 2026-09-14 question. `PL-NR2K` may be it.
- I cannot tell what this sentence means: "The field shipped naming the port item alone" (3389), when the sentence before it says that the field names the port item.
```

**Chapter read 20: § "Declined to Gate 2 on the refilling-queue ground", rows 3548-3912.**

```text
- **Heading (3548).** "Declined to Gate 2 on the refilling-queue ground" names only one of the grounds this section uses. Entries are also declined because:
  - they wait on the Qt port (3620-3653, 3797-3808);
  - a decision belongs to `PL-L9RD` (3641-3646, 3702-3710);
  - they change only how a fact is recorded (3672-3683, 3810-3820, 3841-3853);
  - § "The gate is a snapshot, not a moving target" defers them (3712-3717);
  - their problem did not exist at the freeze (3890-3912).

  Use "Declined to Gate 2, and the ground for each entry". Any file that cites the old heading must change with it.
- **Length and order (3548-3912).** The section runs 3925 words under one heading, in the order the batches arrived. A reader looking for one entry, or for every entry on one ground, has to read all of it. Pointers send them back up the page: "the four paragraphs above" (3606, 3668), "the first thirty" and "the first twenty-nine" (both used for the same group), "the paragraph above" (3873). Replace the batch paragraphs with one table of declined entries. Columns: item, date captured, priority, class, lane, ground, and one line on what it does. Then add subheadings by ground:
  - opening: 3550-3558, plus 3609-3610 and 3774-3776
  - "The refilling-queue ground": 3560-3581
  - "Where an entry stands now": 3583-3599
  - the table, which replaces 3601-3618, 3655-3670, 3685-3700, 3762-3795, 3822-3839 and 3877-3884
  - "Waiting on the Qt port": 3620-3653, 3702-3710, 3755-3760, 3797-3808
  - "Changes to how a fact is recorded": 3672-3683, 3810-3820, 3841-3853, 3885-3888
  - "Ranked ahead of the gate anyway": 3855-3875
  - "Filed after the freeze": 3712-3753, 3890-3912
- **Repeat: the same four tests in nearly every batch.** "found after the 2026-09-06 freeze, it is `P2`, it is neither `safety` nor `science`, and it lies wholly in the workflow lane" (3606-3608) appears again, nearly word for word, at 3665-3668, 3714-3717, 3781-3783, 3790-3793, 3826-3827, 3846-3847, 3869-3871, 3883-3884, 3897-3898 and 3906-3907. State the tests once in the opening. Each entry keeps its own values in its table row.
- **Repeat: the refilling-queue reason.** "The refilling-queue arithmetic above is unchanged and is still the reason" (3613-3614) appears again at 3668-3669 and 3793. "admitting them would grow a gate that is not draining" (3615-3616) appears again at 3669 and 3693. Both belong in 3560-3566. The other places keep nothing, because the table's ground column says it.
- **Repeat: "rather than … being stretched to cover them".** It appears at 3617-3618, 3673-3674, 3797-3799, 3850, 3886 and 3893. Subheadings by ground do this work, so these keep nothing.
- **Repeat: cannot affect a reader of the simulator.** "None of them can affect a reader of the simulator. So deferring them costs the gate nothing that it exists to protect" (3577-3578) appears again at 3679-3680, 3694-3695, 3785-3786, 3816 and 3852-3853. It belongs in 3574-3581, and the other places keep nothing.
- **Repeat: the lower bar.** "held to `.claude/rules/apparatus-standard.md`'s deliberately lower bar" (3575-3576) appears again at 3667-3668 and 3792-3793. Keep it at 3575-3576.
- **Repeat: the disposition rule.** "either way it must say so and say why" (3553-3554) is restated as "the disposition rule asks for a sentence either way" (3899-3901) and "what the disposition rule exists to force" (3910-3912). Keep it in the opening and cut the restatements.
- **Repeat: where to see the current state.** "`bin/docket wave` reports where the gate stands now" (3572) and "`bin/docket wave` prints every deferral of the current gate with its state" (3592-3599). Keep the second; 3572 keeps nothing.
- **Repeat: the ranking argument.** "all four are offered ahead of this gate's own entries … The gate decides whether v0.5.0 *waits* on them" (3857-3860) and "The ranking already offers it ahead of this gate's own entries. The only thing declined is whether v0.5.0 waits on it" (3873-3875). Keep 3855-3861; under one subheading, 3873-3875 keeps nothing.
- **Repeat: decide once with `PL-L9RD`.** "Pulling them into Gate 1 would mean deciding them twice" (3645) and "answering it against the Flet chart would mean answering it twice. That is the same reason `PL-3JP0` and `PL-HKTB` wait for `PL-L9RD`" (3709-3710). Merge `PL-5B1N` into 3641-3646 as a third decision the port makes once.
- **Admitted entries counted here.** `PL-DZFJ` (3681-3683) and `PL-V6M0` (3794-3795) are admitted entries. They belong in the admitted list, and this section keeps nothing about them.
- **Misplaced: 3755-3760** ("No preview is drawn today … this item would be admitted above"). It is about `PL-5B1N`, the committed run against the uncommitted preview (3702-3710). Where it stands, after `PL-TBMX`, "this item" reads as `PL-TBMX`. Move it to follow 3710.
- **Misplaced: 3774-3777** ("They enter Gate 2 when it freezes at v0.5.0's ship"). It applies to every entry, but it stands after `PL-CY8B`, where "They" reads as that group. Move it to the opening, with the release each gate holds: Gate 1 holds v0.5.0's debt (the chapter says this only in passing, at 3820, 3860 and 3875). The parenthetical history ("written 'when v0.6.0 is scoped' until 2026-09-16") belongs in the item that changed the trigger, which the chapter does not name.
- **Misplaced: 3609-3610** ("Later additions belong in this list … Whether the audit found an entry is a note of provenance, not the test"). This rule covers the whole list, so it belongs in the opening.
- **Misplaced and mixed: 3583-3599.** It covers the whole list but sits between the twenty-nine and the thirtieth. Move it to follow the opening. The reader keeps four facts: the state is not written here; `bin/docket wave` gives it for the current gate; `bin/docket show` gives it for an earlier gate; and a release name already written is still correct. The history goes to `PL-0VFF`, `PL-B60Q` and `PL-J6HP`: the marks once written, 48 that matched, and 36 of 84 closed entries unmarked (counted 2026-09-23).
- **Writers' rule: 3568-3572.** "never recomputed … must not be treated as one" is a rule for writers, and it belongs in the item that keeps the gate's rules. The reader keeps only that the four figures date from 2026-09-08.
- **Written for a later session, not the owner.** Each piece goes to the item it names, leaving one line on what the entry does:
  - 3601-3605: how `PL-HX5C` turned `main` red, to `PL-33WM`
  - 3636-3639: the Flet and Qt harness measurement, to `PL-ZG5J`
  - 3676-3678: `_landing_split`, to `PL-880Z`
  - 3689-3693: the same-commit rule, the test fake and the git subprocesses, to `PL-QNYF`, `PL-3LLZ` and `PL-7XNX`
  - 3697-3700: the spawn count and the capture rule, to `PL-CSHL`
  - 3763-3772: `_shallow_pair`, `ID_PATTERN` and the assertion, to `PL-CY8B`; keep "the guard it tests is covered by other assertions"
  - 3864-3868: how `PL-2T03` was split, to `PL-2T03`
  - 3878-3882 and 3887-3888: rule 14's history and the rule's length, to `PL-QSGX` and `PL-CM40`
  - 3894-3895: `verify:` and the discriminator, to `PL-09G9`
  - 3904-3910: `_carried_work`, `pr` and `make check`, to `PL-YFXG`
- **Decision history: 3733-3753.** The `PL-TBMX` story (filed, refuted, reopened) belongs in `PL-TBMX` and `PL-HGB6`. The section keeps the current state: `PL-HGB6` keeps the assembled-total meaning in `docs/machine-abstraction.md`, and `PL-TBMX` is on v0.6.0's frozen list as a `safety` entry (project owner, 2026-09-27, ratified, over building `PL-HGB6` as written).
- **Narration about the text: cut.** "This paragraph applies that rule to the gate's own membership" (3580-3581). "This is worth stating because the batch was measured" (3697). "A later reader who meets the dropped item is owed the reason" (3741-3742). "This asymmetry is named here so that it does not look like an omission" (3836-3837). "It is stated rather than left out because …" (3898-3901).
- **A decision for the owner, buried.** `PL-N32Y` waits on a question only the project owner can answer: is a frozen Required scope line corrected or annotated when it turns out to be wrong (3817-3820)? It sits mid-section. Put waiting decisions where the owner looks, as a table column or a line in the opening.
- **Query:** Do 132 + 42 make 173? 3560-3563 gives 132 entries and forty-two admitted, which is 174. The 31% matches 173.
- **Query:** Eleven, or twelve? 3612-3616 says eleven, with "six of them are not in the workflow lane" and "the six that are apparatus", which makes twelve. 3620-3653 then names seven non-workflow entries: four port, two decisions and `PL-CNCF`.
- **Query:** Where is the eighth member? 3864-3868 says `PL-HWW1` had eight members: four moved and three were kept.
- **Query:** Where is the fourteenth capture? 3788-3795 says the pass covered fourteen captures: twelve declined, one admitted (`PL-V6M0`).
- **Query:** When was Gate 1 at 52 open entries? "Gate 1 remains at 52 open entries that it can clear" (3830-3831) has no date. 3598-3599 says the number still open is not written down, and 3562 gives 89 open on 2026-09-08.
- **Query:** Is v0.6.0's list frozen, and which gate holds which release? 3591 ("v0.6.0's deferrals") and 3753 ("v0.6.0's frozen list as a post-freeze `safety` entry") disagree with 3776-3777 ("v0.6.0 was scoped without freezing it") and with Gate 2 freezing at v0.5.0's ship.
- **Query:** Does 3674-3675 still hold? It says "nothing marks a closed entry apart from an open one", but 3592-3596 says `bin/docket wave` prints each deferral's state. Is 3674-3675 a statement as of 2026-09-12?
- **Query:** Does "none of the three can affect a reader of the simulator today" (3719-3720) still hold for `PL-HGB6`? 3725-3729 calls the stored value correct, but 3744-3753 says that reading was the misreading. `PL-TBMX`, which says a real profile would understate the circuit time constant by about 40%, is now a `safety` entry.
- **Query:** What is the "presence test"? 3552, 3555, 3828 and 3892 use it without explaining it. 3828-3830 says `PL-DG84` passes it "squarely" yet "fails the arithmetic that the presence rule asks for".
- **Query:** What sets 3714-3716 apart? It defers three post-freeze entries under the snapshot rule "on its own terms, not on the refilling-queue ground". Every other entry captured after the freeze (3606-3608, 3781-3782, 3790-3791) is declined on the refilling-queue ground.
- **Query:** Where are the first twenty-nine, and where is the admitted list? "these twenty-nine" (3555) and "the workflow-lane list above" (3676) name no entries in these rows, and "admitted above" (3554, 3578, 3682, 3759, 3794) names no section. The reader needs the list, or § pointers to it.
```

**Chapter read 21: § "Declined to Gate 2 on the refilling-queue ground", rows 3914-4293.**

```text
- **Heading.** "Declined to Gate 2 on the refilling-queue ground" does not say what the subsection holds. Its paragraphs also decline findings on other grounds:
  - the problem is new (4102-4110, 4160-4175, 4260-4264);
  - the item cannot be worked yet (4012-4020);
  - the finding is not apparatus (4038-4055, 4083-4093).

  They also record product-lane items that are not deferred at all (4190-4211). 4252-4254 says "the refilling-queue argument no longer fits the facts". Use "Findings deferred from Gate 1 to Gate 2". The item titles at 3916 ("'Declined to Gate 2' list") and 3945 ("declined-to-Gate-2 argument"), and any file that cites the heading, need the new text.
- **Order: the current ground comes too late.** 4248-4258 ("The arithmetic has changed under this section…") gives the ground that now applies to the whole subsection, with the gate's current count. It stands after some twenty paragraphs that argue the old ground. Move it to the subsection's opening, ahead of the list that ends at 4003. Each group below then needs only its own ground.
- **Repeated: the old ground.** Four places restate a ground that 4252-4254 withdraws:
  - 4035-4036: "The refilling-queue arithmetic in the four paragraphs above is unchanged and is still the reason"
  - 4068-4069: "The refilling-queue arithmetic above is unchanged and is still the reason"
  - 4113-4116: "The arithmetic is the argument here … just as it is finally draining"
  - 4232-4235: "because of the arithmetic this section rests on … Admitting it would grow a gate that is not draining"

  State the ground once, in the moved 4248-4258. The four places keep nothing.
- **Repeated: the gate's size.** Three places give the size, the last two in the present tense:
  - 3945: "'Gate 1 stands at 132 entries ... with 89 still open' … now 159 with 94 open"
  - 4114: "This gate stands at 166 entries with 15 open"
  - 4250-4251: "**170 entries, 165 cleared, 5 open - and 0 that this gate can clear**"

  Keep one dated count in the opening paragraph. 4114 keeps nothing, and 3945 stays as an item title.
- **Repeated: the snapshot-rule quotation.** 4104-4106 and 4161-4164 both quote, word for word, '"The gate is a snapshot" says that a finding "defers to the next gate only when the problem itself is new: introduced by work done while clearing this gate or implementing the milestone it protects"'. Quote it once, in the opening paragraph, with § "The gate is a snapshot". Each of 4104 and 4161 keeps only "defers because the problem is new".
- **Repeated: why post-freeze debt items are listed at all.** Five places give the reason:
  - 4009-4010: "Without this note, a reader who found it open would have to work out why it is absent"
  - 4139-4140: "…found one open would have to work out why it is absent"
  - 4218-4219: "…why a `P2` CI defect is absent from a gate this large"
  - 4244-4245: "…why it is absent from a gate this size"
  - 4229-4230: "A gate this large owes a reader a reason for every open debt item it does not include"

  Say it once in the opening paragraph. The groups keep nothing.
- **Repeated: what makes an item workflow-lane debt.** The description (found after the 2026-09-06 freeze, `P2` or `P3`, neither `safety` nor `science`, apparatus held to `.claude/rules/apparatus-standard.md`'s lower bar) appears at 4024-4027, 4063-4066, 4075-4077, 4128-4131, 4142-4143, 4226-4227, 4235-4237 and 4269-4271. "cannot affect a reader of the simulator" also appears at 4087-4088 and 4116. State the description once in the opening paragraph. Each group keeps only "wholly in the workflow lane".
- **Repeated: captured after the freeze.** "so the snapshot rule … places it/them in the next gate" appears at 4006-4008, 4136-4137, 4215-4217, 4224-4226 and 4240-4242. State the rule once in the opening paragraph, and let each group keep its capture dates (but see the first query).
- **Scattered: which item to take off first.** Four recommendations stand in four places:
  - 4124-4125: "It is recommended as the first item taken off this list" (`PL-0MLZ`)
  - 4154: `PL-RWBV`
  - 4171-4172: `PL-FPY2`
  - 4283-4284: `PL-Q8RQ`

  This is the decision the reader acts on. Gather the four in one short list in the opening paragraph. Each group keeps the item's description and drops "is the one to watch, and it is deferred with that said".
- **Repeated: v0.4.26 comes before this gate.** 4195-4197 says "the v0.4.26 port beat, which comes before this gate on the timeline rather than after it". 4257-4258 says "The timeline also puts v0.4.26 ahead of v0.5.0". Keep the fact in the moved 4248-4258. 4195 keeps "belong to v0.4.26" (but see the v0.4.26 query).
- **Split: `PL-SMN4`.** 4213-4219 records its capture and debt. 4232-4237 gives its ground, after the unrelated 4221-4230. Merge 4232-4237 into 4213-4219.
- **Repeated: `PL-2M4X` and `PL-SYG4`.** They are disposed of at 4221-4230, and 4290-4293 explains "so they are not disposed of a second time here". Move 4221-4230 into the evening-pass paragraph at 4286, where those two were triaged, and cut the explanation at 4290-4293.
- **Out of date: `PL-QRD1`.** 4197-4199 gives an expectation ("was `blocked` on `PL-8PSW`. That item was expected to decide…"). 4201-4211 corrects it ("the expectation in the sentence above was wrong"). Put the outcome in 4197-4199: closed 2026-09-20, once `PL-VKJW` made the defect reachable and locked the trunk's selector. Cut the correction.
- **Out of date: `PL-RWBV`.** 4151-4153 says the stale path makes `PL-CNCF` "look delegable when it is not". The bracketed note at 4155-4158 ("Corrected 2026-09-30") says the delegation guard never failed open. State the corrected fact in place of the claim, keeping 2026-09-30 and `PL-RWBV`'s 2026-09-21 narrowing as its source.
- **Order: dates.** Two groups stand out of date order:
  - 4060-4069 (`PL-ZMGR`, captured 2026-09-19) stands between the two 2026-09-13 passes (4022-4058 and 4071-4093).
  - 4160-4188 (`PL-LHBY` close-out, 2026-09-20) splits the 2026-09-15 pass. That pass's twelve are the nine at 4142-4158 and the three at 4190-4211.

  Use this order:
  1. 2026-09-13: 4005-4058, then 4071-4093.
  2. 2026-09-14: 4095-4132.
  3. 2026-09-15: 4134-4158, 4190-4211, then 4213-4219 with 4232-4237 merged in.
  4. 2026-09-16: 4239-4284, then 4286 onward with 4221-4230 moved in.
  5. 2026-09-19 and 2026-09-20: 4060-4069, then 4160-4188.
- **Subheadings.** At 5969 words with no subheading in these rows, the subsection is too long for a reader to find one item's ground. Put subheadings at these boundaries:
  - "Why these findings wait for Gate 2" over the moved opening;
  - "Declined findings, by item" over the list that ends at 4003;
  - "From the 2026-09-13 triage passes";
  - "From the 2026-09-14 triage pass";
  - "From the 2026-09-15 triage pass";
  - "From the 2026-09-16 triage passes";
  - "Found later, 2026-09-19 and 2026-09-20".
- **The list mixes open and closed entries.** 3914-4003 puts open entries among ones marked "closed in v0.4.x" or "dropped 2026-09-xx", and 4001-4003 break the id order. A reader deciding what a release leaves out needs the open ones. Split the list into "still open" and "closed or dropped", each in id order.
- **Written for another reader.** Some detail is written for a later session, and belongs in the item it describes:
  - 4012-4020 belongs in `PL-VV6N`: the expert-review rule, the `PL-YVV4` count, and the `PL-LKGL` precedent with its 67% figure.
  - 4147-4158 belongs in `PL-RWBV`: the three mechanisms, `protected_paths`, `docket.toml` and the correction.
  - 4177-4188 belongs in `PL-RBMK`: `_apply_to_every_run`, `BookmarkSet`, and the roughly 24,000 fuzzed gestures.
  - 4201-4211 belongs in `PL-QRD1` and `PL-VKJW`: the selector lock, `set_agent` and the agent chip.
  - 4271-4277 belongs in `PL-1RTM`: `workflow_paths`.
  - Triage history belongs in `PL-6FJ5`, `PL-0C6W`, `PL-Q0J1` and the 2026-09-13 pass: 4071-4073 ("folded in…"), 4096-4097 ("checked each finding against the tree…") and 4286-4289 ("arrived during the day from four sessions").

  `ROADMAP.md` keeps each item's id, what it affects in plain words, its ground, and whether it can affect a reader of the simulator.
- **Query:** 3914-4003 repeat item titles written for a later session. They are full of tool names the reader does not know, such as `bin/docket`, `doc_check`, `_section_text` and `verify:`. The reader needs each entry's effect in plain words, and the text does not give it. Should the list give that, or only ids with a pointer to the items?
- **Query:** The file contradicts itself on the snapshot rule.
  - 4006-4008, 4136-4137, 4215-4217, 4224-4226 and 4240-4242 say that a capture date after the 2026-09-06 freeze is enough for the snapshot rule to place a finding in the next gate.
  - 4104-4106 and 4161-4164 quote the rule as deferring a finding "only when the problem itself is new". 4112-4113 and 4265-4267 decline pre-freeze problems found after the freeze on another ground.
  - Some items get both grounds: the nine at 4142-4143 against 4136-4137; `PL-ZMGR` at 4067-4068 ("on its own terms rather than by exception") against 4068-4069 ("is still the reason"); and `PL-SMN4` at 4215-4217 against 4232.

  Which reading is right?
- **Query:** Do "the presence rule" (4103, 4161), "the snapshot rule" (4008, 4068, 4216, 4225, 4257, 4261) and "the presence test" (4266) name one rule? If so, it needs one name.
- **Query:** How many entries were declined first? 4024 and 4075 say "the first thirty", and 4142 says "the thirty before them". 4089 and 4113 say "the first twenty-nine". The list in these rows alone has 90 entries.
- **Query:** When were the gate counts taken?
  - 4114 ("166 entries with 15 open") and 4250 ("Today … 170 entries, 165 cleared, 5 open") carry no date.
  - At 4115, "would take it past 180" does not follow from the nine findings it discusses, since 166 + 9 = 175. Which findings does "these findings" mean?
  - 4255 calls the gate "a cleared gate" while 4251 counts 5 open entries.
- **Query:** Is 4078-4081 still true? It says `PL-Z34C` "keeps Gate 1 open because no status records" its decision. `PL-TGFY` (4002, closed in v0.4.32) says `PL-Z34C` has moved to `blocked`, carries no debt class, and is no longer counted as debt.
- **Query:** Is v0.4.26 still ahead? 4195-4197 and 4257-4258 put v0.4.26 ahead of this gate and call it "the beat that is due". The list records closures up to v0.4.34 (4001). Are `PL-J0F7` and `PL-TCR5` still open?
- **Query:** Is `PL-RWBV` still the one to take off first? The 2026-09-30 correction (4155-4158) removes "the expensive instance" that the recommendation at 4151-4154 rests on.
- **Query:** What do "all of the above" at 4000 (`PL-ZG5J`, "the headless frame-cost harness that measured all of the above") refer to? The entry has no referent in an id-ordered list.
- **Query:** What is the third group's ground? 4099-4100 says the thirty-four are declined "on two different grounds", but 4128-4131 never names the ground of the sixteen.
- **Query:** The chapter uses terms it never explains: "refilling queue" (4035 places its arithmetic in "the four paragraphs above", outside these rows), "apparatus", "workflow lane", "product lane", "debt", "frozen list", "beat", "Required scope" and "the unconditional science exception" (4058). The outline read should confirm that an earlier chapter defines each.
```

**Chapter read 22: § "Declined to Gate 2 on the refilling-queue ground", rows 4295-4846.**

```text
- Repeats: almost every entry restates the same three facts behind the refilling-queue ground. Examples are "captured after this freeze, neither `safety` nor `science`, and wholly in the workflow lane" (4715-4716) and "They were captured after the 2026-09-06 freeze. They are `P2` or `P3` and neither `safety` nor `science`. They sit wholly in the workflow lane" (4753-4755). The same facts appear at 4296-4297, 4312-4313, 4324-4325, 4344-4346, 4422-4424, 4498-4499, 4518-4519, 4527-4528, 4546, 4657-4659, 4676-4681, 4701-4703, 4733-4735, 4774-4778, 4815-4817 and 4845-4846. State the ground once, where the subsection first states it (before this chapter, per "the reason this subsection already states", 4414-4415). Give the routine entries as a table with these columns: item, its subject in plain words, capture date, priority, class. An entry keeps prose only where it differs from the ground.
- Repeats: the time since the freeze appears as "ten days after this gate was frozen" (4344-4345, 4361, 4384-4385, 4407), "eleven days after this freeze" (4677-4678) and "after the 2026-09-06 freeze" (4296, 4733, 4753, 4775). Give the freeze date once at the head of the subsection, and let each entry keep only its capture date.
- Repeats: "Without this record, a reader who found them open would have to work out why" appears twice (4363-4364, 4411-4412). It is narration about the text. Cut both.
- Repeats: the rule for `anticipated` findings is given twice in full: "not debt until the hazard it describes exists" and "A gate that clears debt *before* a milestone cannot clear a hazard that the milestone introduces" (4460-4464 and 4555-4557). Parts of it come back at 4401-4404, 4476-4477 and 4572-4578. It belongs in the section that states the rule in full (see the first query). Here, keep a pointer to that section and each item's placement.
- Repeats: "Today the splitter handles can only resize an Area" (4461-4462) and "Since `PL-W9P6` (2026-10-18) the handles are live. But they only resize an Area" (4478-4481). Keep 4478-4481, which carries the date. Rows 4461-4462 keep nothing.
- Repeats: three places say that nothing checks this subsection's own entry count: `PL-4RHP` (4597), `PL-HCTF`'s "Nothing validates that count" (4795-4796), and "`check_gate_counts` checks a frozen list's count-carrying group headings ... and this is a body paragraph" (4832-4834). The fact belongs in those items. Each entry keeps its subject in one line, and 4829-4836 keeps none of it.
- Repeats: the "66 dispositions" figure is discussed at 4534-4539 and again at 4829-4831. Keep it in one place once the query below is answered.
- Repeats: the gate's size is given four ways: "the largest this project has held, and it is not draining" (4630-4631), "173 entries with five open" (4685-4686), "168 cleared of 175, with four entries left" (4760-4761) and "170 cleared of 175, with two entries it can clear" (4780). Put one dated count at the head of the gate's section and point to it from the entries (see query).
- Repeats: two forecasts are later restated as dispositions. For `PL-73P0`, "it reaches this gate only if a triage pass classes it" (4667-4668) is quoted again at 4689-4693. For `PL-RY2R` and `PL-61MD`, the forecast is restated at 4712-4714. Write each disposition where its forecast stands (4665-4668, 4712-4714). Rows 4689-4693 then keep nothing.
- Repeats: the owner's decision to un-absorb the interface pass appears at 4321-4322 and again at 4543-4544. Keep it at 4543-4544, where the owner must decide what follows from it. Rows 4321-4322 keep a pointer.
- Repeats: rows 4391-4392 say `PL-MN4J`'s reason "is carried across to the bullet in § "Required scope" below", yet 4393-4404 argues it again. § "Required scope" keeps the reason. This chapter keeps one sentence saying the item is in v0.5.0's `Required scope`, with its tag whole: "(`PL-R7XK`, project owner, 2026-09-16, ratified - chosen over leaving it deferred here)". The argument for `Required scope` over a deferral is decision history and goes to `PL-R7XK`.
- Repeats: the four `safety` area-model items are argued out here (4469-4491), yet 4560-4561 says "the v0.6.0 section argues out" the same four. Keep the argument in one place.
- Another reader's: each entry's mechanism detail is written for the session that will work the item, not for the owner deciding a release. It uses internal names: `bin/docket verify` (4297), `setStyleSheet` (4310), `assemble_chart_frame` and `QT_QPA_PLATFORM=offscreen` (4342-4350), `TraceLegend` (4359), `_superseded` (4523, 4662), `GitRunner` (4654), `branches_in_flight` and `_taken_on_base` (4696), `walk.edited` and `own_edits` (4709-4710), `ast` and `with (` (4727-4738), and `clusters()` and `STORE_PATHS` (4841-4842). It also names the branches `keen-cannon` and `eager-brown` (4700). Move this detail into each item's brief. Here, each entry keeps what the item is about in plain words, and whether it could change what a simulator user sees.
- Another reader's: decision history belongs in the item it names. How `PL-Y4YX`'s ground was rewritten (4316-4323) goes to `PL-Y4YX`. What the `safety` class "used to mean here", and how the subsection argued items back off the gate (4469-4476), go to `PL-83LS`.
- Another reader's: several passages explain how the documentation check finds dispositions: 4485-4488 (`check_gate_reentries`), 4590-4592, 4769-4770, 4819-4827 (`_declined_ids`, `PL-82B0`) and 4832-4834 (`check_gate_counts`). This is for whoever maintains the check. Move it to `PL-82B0` and the check's code comments. The reader keeps what it guarantees: a finding whose problem predates the freeze goes back on the list, whatever this text says.
- Another reader's: closing `feature: carrier-collapse` (4721-4725) is a record about the feature's work, not a release decision. Move it to that feature's items.
- Narration about the text (pattern 3 of the writing rule): "This paragraph is their disposition" (4439-4440), "So these paragraphs record the reasoning, not the mechanism" (4487-4488), "The entry stays as the record of why it sat here" (4513-4514), "The paragraph remains as this gate's reasoning for declining it" (4643-4644), "The disposition is written because the presence rule asks for an answer in writing" (4717-4719), "It is left named here rather than removed, because this subsection records the disposition taken" (4748-4750), and "The entry stays for the record, not as a deferral" (4811-4812). Replace each with a status such as "closed", given in the subsection for closed findings.
- Order: the nine area-model findings are introduced at 4426-4440 and listed at 4469-4502. The scoping round's eight (4442-4467) stand between them, so "Four of the nine" (4469) reads as four of the eight. Use this order: 4426-4440, 4469-4491, 4493-4502, then 4442-4467.
- Order: `PL-TH35` and `PL-VN6M` (4357-4380) wait on item 34 for the same reason as the nine, as 4426-4428 says. Move them into the area-model group.
- Order: `PL-KZ99` (4572-4582) takes the same disposition, against the same planned-milestone item 28, as `PL-0S0V` and `PL-VJZK` (4548-4567). Merge them into one group, and follow it with the pointer to `PL-H4N8` and `PL-QBX0` on the frozen list (4584-4592).
- Order: `PL-LSR0` (4839-4846) stands after the subsection's closing paragraphs (4819-4836). Move it up with the other 2026-09-19 workflow-lane entries, or into the table.
- Order: the arithmetic for why the ground still applies is restated three times (4685-4693, 4758-4770, 4778-4782). Give it once, dated, before the entries it governs (see the counts query).
- Subheadings: the subsection is a 5,894-word log in the order findings were captured. A reader deciding what a release holds cannot find any item's current status. Group the entries by disposition under level-4 headings. Rows 4824-4826 say the check still reads every entry until the next `##` heading. Suggested groups:
  - "Workflow-lane findings declined to the next gate", as a table: 4295-4326, 4414-4424, 4516-4528, 4594-4615, 4653-4719, 4727-4791, 4839-4846.
  - "Findings outside the workflow lane, each on its own ground": 4328-4355, 4617-4636, 4793-4805.
  - "Findings placed in v0.6.0 or v0.7.0 with the area system": 4357-4380, 4426-4502.
  - "Findings with no milestone yet (planned-milestone items 24 and 28)": 4548-4592.
  - "Findings that wait on the project owner": 4302-4307, 4530-4546.
  - "Findings closed or moved since they were recorded" (`PL-MN4J`, `PL-KQHN`, `PL-KRZW`, `PL-J4NW`, `PL-QMC0`, `PL-RY2R`, `PL-61MD`, `PL-TQFB`): 4382-4404, 4504-4514, 4638-4650, 4708-4719, 4742-4750, 4807-4817.
- Heading: "Declined to Gate 2 on the refilling-queue ground" does not say what the subsection holds. Many entries rest on other grounds: the snapshot rule alone (4344), item 33 (4331-4338), "a narrower ground" (4800), an owner's decision (4530-4545). Others are not declined at all: `Required scope` (4389), placements (4432-4467), closed items. A heading that fits is "Declined to Gate 2: findings after the 2026-09-06 freeze, and where each one goes". Keep the opening "Declined to Gate", because the documentation check finds these subsections by it (4820-4825). Update every citation of the old heading in other files. I read "(run 3 of 4)" as this chapter's label, not part of the heading.
- Query: 4460 puts the `anticipated` rule in § "The gate is a snapshot, not a moving target", but 4554 says "That rule is stated in full in the v0.6.0 section, not here". Which section states it?
- Query: 4434-4438 says eight of the nine area-model findings are in v0.6.0's `Required scope` and the ninth, `PL-J4NW`, closed. But 4493-4499 says `PL-9PD6`, `PL-D584` and `PL-J4NW` "can be started today" and are deferred, and 4500-4502 defers `PL-L8RN`. 4438-4439 says the entries below are "left as the freeze wrote them", yet 4478 cites a change from 2026-10-18. The reader needs the current disposition of each of the nine.
- Query: 4486 and 4489 speak of "all ten `anticipated` findings". This chapter names four (4469-4474) and eight (4457-4458), twelve in all. It also says "All ten are blocked on item 34", although two of the eight belong to no milestone (4453-4457). Which ten?
- Query: 4366 and 4379-4380 say `PL-TH35` and `PL-VN6M` are not deferred, but 4427-4428 says they "are already deferred, two paragraphs up". They actually stand five and six paragraphs up.
- Query: 4538-4539 says the "66 dispositions" figure "is left as it stands here", but 4829-4831 says the subsection "deliberately does not record how many dispositions it holds" and that a sentence "carried" 66, in the past tense. Is the figure still in the text, and where?
- Query: 4836 says "The open count is not recorded here". Yet 4685-4686, 4760-4761 and 4780 give open counts that carry no dates and disagree: 173 entries with five open; 168 of 175 cleared, four clearable; 170 of 175 cleared, two clearable. The reader needs one count with its date, or none.
- Query: the eighteen findings (4406) and the six (4516, `PL-554Q`) both come from "the 2026-09-16 triage pass". Was that one pass or two?
- Query: 4530 says `PL-7RYB` and `PL-NLP4` "wait on answers ... as `PL-KQHN` does", but 4510-4513 says `PL-KQHN` was answered and "no longer waits on anything".
- Query: 4641-4642 says `PL-KRZW` was "built 2026-09-22, as a Gate 2 entry", in a paragraph that declines it to Gate 2. Was it admitted to Gate 2 after all?
- Query: 4324 calls `PL-Y4YX` "wholly in the workflow lane", but its subject is the application's styling layer in `app/theme.py` (4310-4311). The text does not show why that lies in the workflow lane.
- Query: `PL-4RHP` (4597) and `PL-HCTF` (4795-4796) both concern this subsection's unchecked entry count. Does one duplicate the other?
- Query: 4307 recommends `PL-L4KX` "as the first of these taken off the list". The owner makes this decision, so they need to know which list "these" are on and what taking the item off it does, for example whether it admits the item to Gate 2.
- Query: this chapter does not explain several terms the reader needs: "the first thirty" (4732-4733, 4752, 4774, 4814), "the presence rule" or "presence test" (4474, 4626, 4646, 4718), "beat" (4688, 4764, 4781), "the carve-out" for an item that is both `anticipated` and `status: blocked` (4402, 4577-4578), "the unconditional exception" (4590, 4679), "the `PL-X9T3` shape" (4353), "the refilling-queue arithmetic" itself (4299, 4423, 4628) and "route 1" (4812). The outline read will show whether an earlier chapter explains them.
- Query: these figures carry no date of when they were measured or counted: 8.4 ms and 15.4 ms (4343), 18-28 ms (4351), 97,687 lines (4737), and 22 items carrying 1,127 lines (4810).
- Query: in "It is inside this section rather than beside it" (4819), I cannot tell what "It" refers to: the `PL-TQFB` entry, the 2026-09-19 entries, or this whole subsection.
- Query: "The entries below are the record" (4834) stands after nearly every entry in this chapter. Which entries does it mean?
```

**Chapter read 23: § "Declined to Gate 2 on the refilling-queue ground", rows 4848-5219.**

```text
- **Heading.** "Declined to Gate 2 on the refilling-queue ground" does not cover everything in this chapter. Several entries are declined on other grounds:
  - PL-ZM48 (4901-4916) and PL-WFFX (5088-5105): the problem arose after the freeze.
  - PL-LPH9 (4970-4980): it cannot affect a reader of the simulator.
  - PL-JQY1 (4982-4993): it is correct whichever way it is decided.
  - PL-QYBW (4995-5007) and PL-7CRY (5029-5044): nothing misleads anyone in the meantime.
  - PL-1K9G (5154-5164): the snapshot rule alone.
  
  Rows 4918-4927 exist only to explain this mismatch. Other files cite this heading, so keep it for the workflow-only entries. Move the others under sibling headings that name their grounds, such as "Declined to Gate 2: items that could change what a learner sees" and "Declined to Gate 2: problems that arose after the freeze". Rows 4918-4927 then go.
- **Subheadings.** The chapter runs about 370 rows in the order the triage passes happened, with no subheading. A reader looking for one item, or for the items that could reach a learner, has to read all of it. Add subheadings by ground, as above. Within the workflow-only entries, add subheadings by the tool each item concerns:
  - `verify`'s suppression and assertion checks: PL-5MFL, PL-BHBZ, PL-G21K and its five close-out items, PL-087W, PL-7NKD and PL-RR1N.
  - `bin/docket release`: PL-MFM4 and PL-W7WL.
  - The in-flight guards: PL-8JQQ, PL-7TVT, PL-N2PP and PL-1X2C.
  - The git reads behind a printed count: PL-NGBM and PL-T441.
  - The restart hook: PL-J3TV.
  - The model-choice reference: PL-13PB and PL-V8QG.
- **Order.** The only deferrals that could affect a learner are PL-JQY1, PL-QYBW, PL-7CRY and PL-1K9G (4982-5007, 5029-5044, 5154-5164). They are scattered among workflow items. Put them first, because they are what this reader weighs when deciding what a release leaves out.
- **Owner's decisions are buried.** These decisions wait on the project owner but sit inside deferral paragraphs:
  - PL-2FQ5: delete the ref (4934-4936).
  - PL-QYBW: choose among four options (5005-5007).
  - PL-WFFX: say which merge client sends the empty message (5098-5100).
  - PL-4W2L: the design round (5082).
  - PL-J870 (5172-5174), and PL-TDBT and PL-W80S (5114-5115): all at `needs-decision`.
  
  Collect them in one list of the owner's decisions at the head of the section.
- **Repeat: the refilling-queue argument.** "the refilling shape that Phase 0 was retired for" appears at 4857-4858, 4898-4899, 5070-5071 and 5125-5126, and as "the refilling shape twice over" at 5104-5105. "The refilling-queue arithmetic … is unchanged" appears at 4895-4896, 4950-4951, 5124, 5177-5178, 5193-5194 and 5213-5214. State the argument once, where the subsection's opening sets it out (an earlier chapter). Each group then keeps nothing, or a § pointer. Also, "the four paragraphs above" (4950-4951) points at rows 4889-4936, which do not contain the arithmetic.
- **Repeat: workflow only.** Three phrases recur throughout: "wholly inside `docket.toml`'s `workflow_paths`" or "wholly in the workflow lane", "cannot affect a reader of the simulator", and "apparatus held to `.claude/rules/apparatus-standard.md`'s deliberately lower bar". They appear at 4869-4870, 4894-4895, 4912, 4939-4943, 4953, 5065-5067, 5100-5101, 5121-5123, 5175-5177, 5191-5192 and 5211-5212. Say it once at the opening of the workflow-only group, and drop it from each entry.
- **Repeat: captured after the freeze.** The point appears at 4940-4941, 5091, 5115-5116, 5157-5158, 5177, 5192 and 5213. Rows 5116-5117 already say that "The gate is a snapshot" places every capture after the freeze in the next gate. State that rule once at the group's opening.
- **Repeat: entry lines restated in prose.** Each group paragraph repeats the entry lines under it:
  - 4943-4950 restates 5016-5027.
  - 5029-5032 restates 5046.
  - 5048-5054 restates 5073.
  - 5186-5190 restates 5199.
  - 5205-5211 restates 5218-5219.
  
  PL-HJZW and PL-VJPJ each appear three times (4943-4944, 4950, 4957-4963, 5018, 5025). The paragraph should give the ground and the entry line the defect.
- **Repeat: PL-5MFL and PL-G21K.** They give the same reasons: the failure is loud, `--self` does not relax it, the code sits in `workflow_paths`, and admitting one more refills the queue (4890-4899 and 5064-5071). PL-G21K is the root cause of PL-5MFL (5049-5052), so put PL-5MFL under PL-G21K and give the reasons once.
- **Repeat: PL-ZM48's date after the freeze.** It is given at 4908-4910 and again at 4923-4924. Keep it at 4908-4910. Rows 4918-4927 talk about the text itself, and their decision history belongs in `PL-QNQJ`.
- **Another reader's: how the paragraph was stranded (4929-4936).** This history belongs in `PL-T2YR` and `PL-BYMX`. Only PL-2FQ5, the owner's deletion of the ref, stays, in the list of the owner's decisions.
- **Another reader's: the triage session's story (4956-4965).** Rows 4956-4965 tell which items fired during the triage pass and why this subsection has its shape. That is the session's story, and it belongs in PL-HJZW and PL-VJPJ.
- **Another reader's: PL-0RZ0 closing by measurement (5009-5014).** This concerns an admitted entry, not a declined one, and is written for a later session. It belongs with PL-0RZ0's entry in the gate, or in PL-0RZ0's item.
- **Another reader's: how the check counts ids (5143-5152).** This is for a developer of the workflow tool, and it belongs in PL-H6VQ. The reader needs two things:
  - PL-H6VQ is recommended first of the fourteen.
  - The reason: the documentation check may count an item as disposed when the text only cites it.
- **Another reader's: internal function names (5205-5212).** These belong in PL-NGBM and PL-T441. Keep two facts for the reader: PL-T441 gives a wrong answer silently, and so it goes first.
- **Decision history to move to the items.**
  - "The observation that prompted them…" (4878-4880) goes to PL-13PB and PL-V8QG.
  - "filed after two sessions read…" (5172-5174) goes to PL-J870.
  - "`PL-PT7M` dropped `PL-8T3Z`…" (5184-5186) goes to PL-J3TV.
  - The transcript detail at 4904-4908 repeats what PL-ZM48 already holds (4916).
- **Missing blank line.** There is no blank line between rows 4880 and 4881, so the PL-5MFL paragraph shows as part of the PL-13PB/PL-V8QG paragraph.
- **PL-8JQQ is misplaced.** Its entry (5108) sits under PL-WFFX, which is declined on the after-the-freeze ground. PL-8JQQ's own entry line declares the refilling-queue ground, and it has no paragraph. Move it to the in-flight guards group.
- **Query: gate counts.** The chapter gives five counts, none dated:
  - "173 of 175 cleared" (4856)
  - "170 of 175 closed … three of the five still open are blocked" (4897-4898)
  - "three open entries" (4951-4952)
  - "177 of 178 … one open entry is blocked" (5068-5069, repeated at 5079-5080)
  - "178 cleared of 181" (5118)
  
  The reader needs the current count, given once with its date where they look for it. The text does not say which count is current.
- **Query: PL-LPH9.** The note at 4974-4975 settles it ("Settled 2026-09-27"), but the paragraph (4971-4974) and its entry (5020) still describe an open conflict. Is PL-LPH9 closed? If it is, its paragraph and entry leave the list.
- **Query: PL-BHBZ.** Rows 4943-4944 call it a check "whose stated severity does not match what they do". Its entry (5016) and row 5050 describe instead the prose-`xfail` defect of PL-5MFL (4881-4884). Which is right? If both describe the same defect, one item duplicates the other.
- **Query: the first thirty or twenty-nine.** Rows 4939 and 5121 say "the first thirty", and row 4977 says "the first twenty-nine". Which is right?
- **Query: a missing capture.** The pass "folded in 30 of the 37 captures open that day" and left six to PL-HZ1B (5111-5113). One capture is unaccounted for.
- **Query: PL-QYBW's options.** The owner's decision needs the "four options" (5006), and the text does not name them.
- **Query: the safe direction.** "The error runs in the safe direction, because the check goes quiet rather than red" (5147-5148). A check that goes quiet misses an item nobody disposed of. In what sense is that safe?
- **Query: the hook file.** The comment `<!-- absent: .claude/hooks/no-prune-guard.sh -->` (5197, 5201) marks the hook as absent. Rows 5187-5190 say the hook "still prints" the recipe. Which is right?
- **Query: entries with no entry line.** These items are declined only in prose, with no entry line in this chapter: PL-13PB, PL-V8QG, PL-5MFL, PL-ZM48, PL-STC4, PL-4FD2 and PL-0KQP. Row 4918 also refers to a list entry for PL-ZM48 that this chapter does not show. A reader scanning the list cannot find these items. Do they have entry lines elsewhere?
- **Query: undefined terms.** The reader needs these terms, and this chapter does not explain them: "generator" and "generator tier", "debt", "apparatus", "workflow lane" and "product-lane", "Phase 0", "the refilling shape", "the presence test", "the altitude item", "count-input-addressing" and "the unconditional safety exception". The outline read should check whether an earlier chapter defines them.
```

**How to apply.** Move and deduplicate only. No sentence is reworded, except a pointer that replaces a restatement, a word such as "above" or "below" that a move made wrong, and a heading. The line edit of what this slice changes follows in `PL-YRY3`, once the copy editor no longer drops requirements (`PL-F0Q2`). Each finding is applied, or recorded here with the reason it was not. A query that the tree answers is answered in the pull request, and one that needs the author is filed as its own item under `roadmap-structure`. Whether a finding that moves decision history out of the roadmap and into an item is applied is decided by the project owner's answer in `PL-LVN8`. Before the pull request is marked ready, two reviewers compare the old and new text passage by passage for any change of meaning. The move-only restructures of the machine documents and of `docs/interface-provenance.md` each changed 10 or 11 meanings that only such a comparison found.

**Done when.** Each finding below is applied, or recorded here with the reason it was not. No statement is lost: every sentence that leaves its place is kept at its one home, or replaced by a pointer that names that home. `bin/docket wave`, `bin/docket gate` and `bin/docket check` give the same answers before and after the slice, and `make check` passes.

**Generator check.** The repeats came from accretion. Each change that touched a topic stated its own record in the section it was working in, instead of pointing to the section that already held it. The structure read found the same shape in every document it read (`PL-BSMF`, `PL-SVGH`, `PL-T8RL`, `PL-39ZK`, `PL-3MTS`), so these are one sweep's findings. No check can decide whether two sentences state one fact. The structure read, which the project owner put ahead of every line edit on 2026-11-07, is the procedure that catches the shape. Not recorded as a generator.
