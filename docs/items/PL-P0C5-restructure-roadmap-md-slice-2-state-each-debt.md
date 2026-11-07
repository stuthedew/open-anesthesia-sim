---
id: PL-P0C5
title: Restructure ROADMAP.md, slice 2: state each debt-gate and development rule once in its own section, with the milestone sections pointing there
priority: P2
effort: L
status: ready
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
deferred-from: v0.7.0 - filed after the gate froze; the roadmap's arrangement and wording, with no displayed value depending on it
added: 2026-11-07
payoff: a reader finds each debt-gate and development rule stated once, in its own section, and each milestone section points there instead of restating it
verify: grep -q '^### How gate work is released$' ROADMAP.md && grep -q '^### Writing a milestone entry$' ROADMAP.md
---

**Problem.** Restructure ROADMAP.md, slice 2: state each debt-gate and development rule once in its own section, with the milestone sections pointing there

**Source.** The copy editor's structure read of `ROADMAP.md`, run on the project owner's Mac on 2026-11-06: one read per chapter, then one read of all the chapters' outlines together. Row numbers are `ROADMAP.md` at `aff76df1`, the last commit to change it before slice 1 (`PL-W0TS`), so a later slice finds each passage by the words the finding quotes. The project owner chose to file the findings as items and apply them one slice per pull request (project owner, 2026-11-07, ratified, over one pull request for the whole restructure), because the release tools read the roadmap's gate sections and a small move is easier to check against them. The raw reads are in the project's shared folder, `/mnt/project-files/v0.7.0/repo-copy-edit/mac-structure-reads/ROADMAP-md/structure/`.

**Why it matters.** Each debt-gate rule is restated in up to eight milestone sections, and the copies already disagree. Gate 2's freeze is an exception in v0.4.26's section and no exception in § "The cadence" (`PL-XRZW`). One rule has five names. A later session cites these rules to admit work to a gate or refuse it, so each must say one thing in one place.

**The findings, as the outline read gave them** (numbered by their order in the read: 12, 13, 15, 16, 17, 18, 19, 20, 34, 48, 49).

- A gate takes no version: "Gate 1 and later gates ... take no version; their work ships in patch releases on the preceding milestone's track" (27-35) and "Its work ships as it clears, in patch releases on the previous milestone's track" (7832-7852); 445, 449 and 459-469 say it again. The rule belongs in § "The cadence" (7832-7858). § "Versioning decision" keeps one sentence and its pointer, and each gate's timeline row keeps "ships in v0.N.x patches". 7832-7852 now answers v0.4.26's "open question, this number" (1752-1764), so that passage can be cut to a pointer.
- The freeze day: "The freeze day is the later of the day the milestone is scoped and the day the milestone before it ships" (7729-7731) and "§ 'The cadence' now freezes a gate on the later of the two days" (449); 479-488, 502-511, 5687-5698 and 6973-6989 repeat it. The rule and the history of the Gate 1 and Gate 2 freezes belong in § "The cadence" (7729-7731, 7808-7823). The timeline rows and the gate sections keep their freeze dates.
- What counts as debt: "An open item is debt when it is classed defect, safety, science, refactor or perf ... also ... needs-decision" (7530-7533) and "Debt means classed defect, safety, science, refactor or perf, or at needs-decision" (2208-2218); 1168-1174, 5687-5698 and 6973-6989 repeat it. The definition belongs in § "What counts". Each gate section keeps "every open item that is debt by § 'What counts'".
- No closed count is recorded: 727-735, 1184-1189, 2208-2218, 3568-3572, 4829-4836, 5687-5698, 6973-6989 and 7907-7910 each say that a count of closed entries is not written, because it goes stale. This is a rule for writers. State it once, in § "Recording it", and the gate sections keep nothing. The version table ("Gate 2: 22 of 185", rows 102-160) and § "Current baseline" ("87 of 90 cleared", 288-291) do give counts, each dated to a release. The rule should say whether it forbids only an undated count, which is the owner's call. PL-WSDY (2604) was filed against a count in the baseline.
- Items captured after the cut: 6301-6315 and 7175-7182 both say that such an item is deferred to the next gate unless it is classed `safety` or `science`, or an entry waits on it. 7584-7605, 7763-7776 and 7885-7905 state the same rule. It belongs in § "The debt gate". Each milestone keeps its own cut (`e6cdfd93` at 07:04 on 2026-09-21 for v0.6.0; `0947408` for v0.7.0) and its own entries.
- The `anticipated` carve-out (7550-7555, 7656-7718) is restated at 2749-2759, 2945-2953, 4442-4491, 4548-4582 and 5842-5861. Those places keep their dispositions and a pointer. The rule's example, "a splitter handle can only resize an Area (AreaLayout ... live since PL-W9P6 on 2026-10-18)" (7656-7672), also appears in a record dated 2026-09-16 as "Since PL-W9P6 (2026-10-18) the handles are live" (4469-4481). It belongs only with the rule.
- Groups and the deferral field: "two kinds of group, and only the second is a precondition ... a written lane goes stale (PL-Z64T)" (5807-5829, 6997-7004) repeats § "Debt inside the milestone's own scope" (7860-7877). "A deferral is a per-entry field, not a group (PL-8QMD ...)" (5831-5840) repeats 7763-7769. Both belong in § "The debt gate", and the gate sections keep their group headings.
- The staleness sweep: "one measured pass found 12 of 134 items dead and 31 more overtaken" (6036-6044) and "found 12 of 134 open items dead and 31 more overtaken, 32% in all" (7732-7755). The figure belongs in § "The cadence". v0.6.0 keeps whether and when its own list was swept. Query: 6036-6044 says Gate 2's list "has not yet been checked for stale entries", but version row 102 (v0.5.1) says "Gate 2's 168 clearable entries swept".
- The frozen Goal: "A rule for writers says a Goal records the problem and is not rewritten" (1129-1136) and "A milestone's Goal is frozen and dated at scoping" (7428-7439). This belongs in § "Development rules for scientific milestones", and v0.4.0 keeps only its Goal's date.
- Terms: § "The cadence" calls its four stages "steps" (7722-7802), but 379-388, 3540-3546, 5517-5521, 5842-5903, 6036-6044, 6997-7004, 7067-7074 and version row 48 call them "beats". Use one word and define it at 7722-7724. Note that "step" also names the simulation step and the timeline's "Step" column (439-440).
- Terms: one rule has five names: "The gate is a snapshot, not a moving target" (7568), "the presence rule" (1242-1246), "the presence test" (2492-2502), "the snapshot rule" (4005-4010) and "the presumption" (1334-1343). Use the heading's name.

**Queries filed separately.** Finding 14 of the outline read is `PL-XRZW`, and the query inside the staleness-sweep finding is `PL-9857`. The undated-count question in the no-closed-count finding is decided in this slice, because both answers are defensible and its reach is one rule's wording: the rule forbids a count of closed entries that carries no date, and a count dated to a release, as the version table and § "Current baseline" give, stays. This is a placeholder the project owner can overrule.

**The findings inside each chapter, as the chapter reads gave them.** Each chapter read also ended with an outline of one line per paragraph, which is left out here and kept in the shared folder. Each read is quoted whole, as a block, so that its quotations of the roadmap are not taken for this item's own claims.

**Chapter read 42: § "Development rules for scientific milestones", rows 7413-7453.**

```text
- Rows 7413 and 7425: the heading "Development rules for scientific milestones" covers the bullets at 7415–7424, which are rules for building the simulation's scientific core. It does not cover the bullets at 7425–7453, which are rules for writing any milestone's entry in this file, scientific or not. Keep the heading over the first five bullets, because other files cite it. Add a subheading before row 7425, such as "### Writing a milestone entry", over the bullets on narrow milestones, frozen Goals and exclusions.
- Rows 7428–7439 and 7440–7453: each of these two bullets has grown into an essay, which is the writing rule's fifth pattern. Each mixes the rule, its reason and an incident, and the second also describes the tools that apply the rule. Cut each to the rule and the reason the reader acts on, and move the rest as the findings below say.
- Rows 7435–7436, "`PL-DXQC` is why this rule is written down rather than left to imitation", and rows 7446–7447, "`PL-NBCS` is why this rule is written down rather than left to imitation", are the same sentence twice. Each is narration about the text. Cut both. Each item id can follow its rule's reason as a pointer.
- Rows 7436–7439, "Two of v0.4.0's three Goal bullets were fixed … no convention to breach.", are decision history. They belong in `PL-DXQC`. The bullet keeps nothing beyond the id as a pointer.
- Rows 7447–7450, "The stage-3 exclusion in v0.4.0 put `PL-B9PY` into v0.4.0's `scope_ids` … and it named the milestone.", are decision history. They use terms this reader does not know: "stage-3", `scope_ids`, "the anchor" and "Gate-1". "Gate-1" also clashes with "release gates" at row 7423, which uses "gate" in a different sense. The rows belong in `PL-NBCS`. The bullet keeps the id as a pointer.
- Rows 7441–7446, on how `bin/docket next` reads `Required scope` and `Explicitly out of scope`, and rows 7451–7453, on what `tools/doc_check.py` fails or warns on, are written for whoever maintains those tools. They name tools this reader does not know. They belong in the workflow's files that the writing rule's last table row lists, or in a comment beside each tool. The bullet keeps what these rows guarantee the reader:
  - Every item id named in a `Required scope` bullet counts as part of that release, wherever the sentence names it, even when the sentence names it in order to exclude it.
  - An id named under both headings of one milestone is reported as an error.
  - A scope bullet worded as an exclusion draws a warning.
- Query: rows 7452–7453 say "exclusion language" but give no example of the wording that draws the warning. The reader needs one, and the text does not give it.
- Query: row 7425 sends a new idea to "the sections below" without naming them. A reader with an idea that is not yet scoped needs to know which sections hold it, and this chapter does not say.
- Query: this chapter names a milestone's subsections (Goal, Required scope, Definition of done, Explicitly out of scope) but does not say what each holds. A contributor writing a milestone needs that, unless another chapter gives it. The outline read can tell. If another chapter does describe a milestone entry's layout, the bullets at 7425–7453 belong there.
```

**Chapter read 44: § "The debt gate", rows 7515-7910.**

```text
- **Section order (7554, 7588, 7589-7590, 7598, 7801):** the reader keeps getting sent to sections further down. Use this order:
  1. The opening rule and its reason (7517-7526).
  2. "What counts" (7528-7566).
  3. "Debt inside the milestone's own scope" (7860-7877), moved directly after "What counts" because it narrows what counts.
  4. "The cadence" (7720-7831), with its four steps kept short.
  5. "The gate is a snapshot, not a moving target" (7568-7654).
  6. One section on deferring an entry, merging 7757-7798 with 7885-7905.
  7. "Recording it".
  8. A section on how gate work is released (7832-7858).
- **Inside "The gate is a snapshot" (7570-7605):** 7597-7605 says what the freeze is and when a finding comes back in. It should open the section, ahead of 7570-7595, which only makes sense once the freeze is known.
- **Misplaced block (7656-7718):** the rule on `anticipated` findings says it decides "what it takes for a finding to count against the current gate at all" (7661-7663). That is a "What counts" question, so move it under "What counts". 7550-7555 then becomes its opening sentence, and 7651-7654 points to it.
- **Repeated fact, freeze day (7597-7599, 7730-7731, 7808-7823):** 7597-7599 says "the later of two events: the milestone's scoping, and the ship of the milestone before it", and 7730-7731 says "the later of two days: the day the milestone is scoped, and the day the milestone before it ships". 7808-7823 gives the reason again.
  - It belongs in step 2 (7729-7731), with the reason from 7810-7813 beside it.
  - 7597-7599 keeps only "at the freeze".
  - The history in 7813-7823 goes to `PL-KKRP`.
- **Repeated fact, empty gate heading (7727-7728, 7804-7806):** "Add the heading that its frozen list goes under, with no entries in it until the freeze" repeats "carries its gate heading from the day it is scoped, empty until the freeze". It belongs in step 1, which also takes "A milestone without one has not been scoped". 7804-7806 keeps nothing.
- **Repeated fact, where the list is written (7729-7730, 7881-7883):** "record the debt list in that milestone's own section, as item ids" repeats "Record the frozen list in the milestone's own section here, as the ids". It belongs in step 2, along with the reason in 7882-7883. "Recording it" keeps nothing of it, which leaves that section about deferrals only.
- **Repeated fact, `anticipated` (7551-7553, 7663-7664):** "describes a hazard that a later milestone will create" appears in both places. It belongs in the moved `anticipated` block. 7550-7555 keeps nothing beyond that block's opening.
- **Misquote (7539-7544, 7670-7672):** 7670-7672 quotes 7539-7544 and gets it wrong: it says "The distinction is state, not layer", but 7543-7544 reads "The distinction is about state, not layer". Once the block moves, keep "the same test as for process work" and cut the quote.
- **Repeated fact, `defect` not `infra` (7542, 7557-7562):** "It is classed `defect` like any other defect" repeats 7557-7562. Fold the example (`uv.lock` left stale is a defect, release tagging is not) into 7539-7548. Cut 7557's account of the first pass.
- **Repeated fact, how an item ends (7564-7566, 7733-7734):** "Clearing means `done` **or** `dropped`, with the reason recorded" repeats "Each item ends `done`, or `dropped` with its reason, or **deferred to a later gate**". It belongs in step 3, which also takes "deciding that something is not worth doing is a legitimate way to clear it". 7564-7566 keeps nothing.
- **Repeated fact, where a new finding goes (7603-7605, 7651-7652, 7799-7802):** findings made during the gate go to the next gate unless the problem was there at the freeze or the finding is `P0`, `safety` or `science`. This is stated in both places. It belongs in the snapshot section. Step 4 keeps a pointer in the full form, § "The gate is a snapshot, not a moving target". 7801's shortened § "The gate is a snapshot" is not the heading's text.
- **Repeated point in one section (7599-7602, 7612-7614):** "The gate tests when a problem was present, not when it was discovered" repeats 7599-7602. 7607-7617 keeps its reason and the case of a problem found again under a new id (`PL-64LS`).
- **Repeated fact, check on entries waiting on other work (7593-7595, 7897-7900):** "`bin/docket check` rejects an open frozen entry that waits on work none of the three homes covers" repeats "fails an open frozen entry that is waiting on work outside the plan". It belongs in the deferral section, in the 7897-7900 wording, which says what "outside the plan" means. 7593-7595 keeps nothing.
- **Repeated fact, the `deferred-from:` field (7590-7591, 7765-7766, 7774-7776, 7886-7888, 7893-7894):** "The field names the gate the entry leaves, not the one it reaches" repeats "It is never the gate that the item goes to". Give the field, its form and the version it names once, in the merged deferral section. 7590-7591 keeps "recorded as `deferred-from:`".
- **Repeated fact, the next freeze takes deferred entries (7771-7772, 7888, 7894-7896):** "The next gate's freeze carries every open entry that this list deferred, debt or not" repeats "The next freeze takes it whatever its classes". State it once, in the deferral section.
- **Repeated fact, the entry stays listed (7777-7778, 7894-7895):** "stays written on the frozen list" repeats "The entry stays on its list". Keep it once, with its reason.
- **Repeated fact, written grounds (7768-7769, 7900-7902):** "The gate section may also set out the decision behind the deferral" repeats "A section may state the grounds that its deferrals share". Keep it once, with "no tool reads that prose".
- **Repeated point, renegotiation (7647-7649, 7777-7778, 7813, 7882-7883):** the point that freezing prevents renegotiation is made four times. 7813, "Nothing in this rule is open to renegotiation", adds nothing to the others.
- **Repeated fact, release numbers (7832-7835, 7848-7850, 7857-7858):** "ships in patch releases" repeats "Ordinary maintenance ships in patches and takes no number of its own". "A session cuts one whenever it judges" and "Since 2026-09-27 the occasion for a cut is a feature finishing" both say when to cut.
  - Both belong in 7832-7839, with the date kept.
  - 7854-7858 keeps only the Gate 0 exception.
- **Repeated fact, Gate 0 (7845-7846, 7854):** "Gate 0 closed across the v0.2.6 to v0.3.0 patch series" overlaps "released as the *minor* v0.3.0". Keep 7854. 7845-7846 goes with its history to `PL-LPH9`.
- **List item grown into an essay (7732-7798):** step 3 runs 66 rows, the fifth machine-writing pattern.
  - Move the staleness sweep (7734-7755) to a subsection headed "Sweep the frozen list for staleness".
  - Move the third outcome (7757-7798) into the deferral section.
  - Step 3 keeps one sentence for each, with a pointer.
- **Long section, "The gate is a snapshot, not a moving target" (7568-7718, about 150 rows):** once the `anticipated` block moves, add subheadings before 7597 ("Which findings re-enter the gate") and before 7570 ("What a frozen entry may take in").
- **Long section, "The cadence" (7720-7858, about 140 rows):** once steps 3 and 4 shrink, give 7832-7858 a section of its own, "How gate work is released". It says what a release holds, which is this reader's job.
- **Decision history to move to items (cut whole tags only where the item holds the decision):**
  - 7557-7558: account of the first pass.
  - 7641-7642: `PL-SWFM`.
  - 7674-7682: why this option was chosen, to the item for the 2026-09-16 decision, which the text does not name (see queries). Keep the rule "placed in the milestone that creates the hazard, never deferred" and the ten findings in v0.6.0's `Required scope`.
  - 7741-7744: the rejected advisory that counted repeated changes, to `PL-LKGL`.
  - 7751-7754: `PL-6ZQY`, to `PL-D8KW`. Keep the rule and its one-sentence reason.
  - 7785-7798: to `PL-F0L8` and `PL-Y949`. Keep "completed milestones' bullets are left as written".
  - 7813-7823: to `PL-KKRP`.
  - 7841-7852: to `PL-LPH9`.
  - 7902-7904: to `PL-WD5Z`. Keep "Completed sections keep those subsections, because they are the record of that period".
- **Text written for another reader:** 7675-7679 (`tools/doc_check.py`), 7693-7696 (`checks.py`), 7706-7708 (`check_gate_reentries`, `make check`), 7895-7896 and 7908-7909 describe how the tools read fields.
  - They are for a later session, so they belong in the items they name or in code comments.
  - This reader keeps what each guarantees, such as "the check enforces this on every run".
- **Text about the text itself, which goes with the moves above:** 7518-7519, 7557, 7661-7663, 7710 ("recorded rather than waved past"), 7785, 7841-7843 and 7851-7852.
- **Out-of-date tense:** 7792 says "Gate 2 freezes the day v0.5.0 ships", but 7817 says "Gate 2 froze on 2026-09-21". 7834's "while Gate 2 does" carries no date.
- **Query:** the safety and science rule contradicts itself across rows.
  - 7651-7653 says these classes cannot be deferred ("This project's own standard does not allow those to be deferred"), and so do 7680 and 7874-7875.
  - 7780-7783 lets such an entry be deferred when its hazard is not live, and 7786 records `PL-WZVZ` deferred that way.
  - Only the author knows which is right.
- **Query:** 7566 says "Leaving it open and starting anyway is not legitimate". Step 3's deferral (7759-7760) leaves an entry open and ships without it.
- **Query:** "Phase 0" (7517-7518, 7644) and "Gate 0" (7845, 7854) may or may not be the same thing. 7517-7518 says Phase 0 applied this rule, but 7644 says the debt gate "replaced Phase 0".
- **Query:** 7689-7690 says the exemption "lapses when that wait ends". 7698 says it "lapses when the item is promoted, not when its blocker closes".
- **Query:** in 7586-7595, I cannot tell whether homes 2 and 3 split the remaining cases or are two choices for the same case, and so what 7591's "anything else" covers.
- **Query:** the reader needs these terms explained, and the chapter does not explain them:
  - "the store" (7896, 7909);
  - "release train" (7594, 7900);
  - "places" and "placement" (7679, 7886), and "takes" (7886);
  - "promoted" (7698), and "item blocker" against "milestone blocker" (7701-7702);
  - "grooming pass" (7703);
  - "capture rule" (7609);
  - "safety-band exemption" (7694) and "safety-class advisory" (7676);
  - "fails closed" (7715);
  - `partly` and `yes` (7744), and the `verify:` field (7735);
  - "Area" and "splitter handle" (7664-7665), and `status: blocked` and `blocked-by` (7687-7688);
  - what `bin/docket` is, and what each of its commands is for.
- **Query:** to move the decision history, the reader needs the items that hold these decisions. Their tags name no item:
  - 2026-08-30 (7570, 7577, 7619);
  - 2026-09-16 (7656, 7684);
  - 2026-09-17 (7734);
  - 2026-09-21 (7757).
- **Query:** these figures carry no date: the staleness pass's "12 of 134 open items dead and 31 more overtaken" (7741), "thirteen items in one session generated fourteen new ones" (7608), and "Gate 2's 190" (7848).
- **Query:** the field `deferred-from: vX.Y.Z` "naming this gate" (7765, 7887) needs the link between gate numbers and milestone versions. The chapter only implies it (Gate 1 for v0.5.0, Gate 2 for v0.6.0).
- **Query:** 7869-7870's "a heading that says so" does not say which heading, or whether it is the gate heading from step 1.
- **Query:** 7630-7631's "the saving the release exists to deliver" does not say which release or what saving.
```

**How to apply.** Move and deduplicate only. No sentence is reworded, except a pointer that replaces a restatement, a word such as "above" or "below" that a move made wrong, and a heading. The line edit of what this slice changes follows in `PL-YRY3`, once the copy editor no longer drops requirements (`PL-F0Q2`). Each finding is applied, or recorded here with the reason it was not. A query that the tree answers is answered in the pull request, and one that needs the author is filed as its own item under `roadmap-structure`. Whether a finding that moves decision history out of the roadmap and into an item is applied is decided by the project owner's answer in `PL-LVN8`. Before the pull request is marked ready, two reviewers compare the old and new text passage by passage for any change of meaning. The move-only restructures of the machine documents and of `docs/interface-provenance.md` each changed 10 or 11 meanings that only such a comparison found.

**Done when.** Each finding below is applied, or recorded here with the reason it was not. No statement is lost: every sentence that leaves its place is kept at its one home, or replaced by a pointer that names that home. `bin/docket wave`, `bin/docket gate` and `bin/docket check` give the same answers before and after the slice, and `make check` passes.

**Generator check.** The repeats came from accretion. Each change that touched a topic stated its own record in the section it was working in, instead of pointing to the section that already held it. The structure read found the same shape in every document it read (`PL-BSMF`, `PL-SVGH`, `PL-T8RL`, `PL-39ZK`, `PL-3MTS`), so these are one sweep's findings. No check can decide whether two sentences state one fact. The structure read, which the project owner put ahead of every line edit on 2026-11-07, is the procedure that catches the shape. Not recorded as a generator.

**Next steps, written when slice 1 closed (2026-11-07).** The thread that filed this feature stopped after slice 1 for length, not for the work, so a fresh session picks this item up.

1. Start from `main` once slice 1 (`PL-W0TS`, #2058) has merged, and claim this item.
2. The row numbers in the findings above are `ROADMAP.md` at `aff76df1`. Slice 1 moved whole sections: § "The debt gate" and § "Development rules for scientific milestones" now sit after § "The plan", and the completed milestones sit last. Inside each section the rows kept their order, so find each passage by the words a finding quotes.
3. Whether the findings that move decision history into an item are applied is decided by the project owner's answer in `PL-LVN8`, which was put to him on a card on 2026-11-07. If that question is still open, apply the rest and record here which findings it leaves unapplied.
4. Before marking the pull request ready: compare the output of `bin/docket wave --no-fetch`, `bin/docket gate --no-fetch`, `bin/docket check` and `tools/doc_check.py check` before and after the change. Check every § citation that sits beside "above" or "below" against where its heading now is, because a move can turn a pointer around (slice 1 found 15). Then give two reviewers the old and new file: one checks every word whose meaning depends on position, and the other checks every changed line and every new heading. Slice 1's two reviewers found 11 changes of meaning between them, with little overlap.
5. `ROADMAP.md` is not on the owner's read list, so `bin/docket arm` answers "arm" and the pull request merges on green.
