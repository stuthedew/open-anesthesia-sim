---
id: PL-39ZK
title: Restructure docs/machine-abstraction.md as the copy editor's structure read proposes: answer the seven questions in order, state a machine's whole effect on the model once, and use one name for a machine module
status: untriaged
feature: machine-docs-structure
touches: docs/machine-abstraction.md, src/anesthesia_sim/core/circuit.py, docs/items/PL-37N4-docs-machine-abstraction-md-answer-the-close.md, docs/items/PL-D42Z-docs-machine-abstraction-md-s-b11-row-calls.md
added: 2026-11-07
---

**Problem.** Restructure docs/machine-abstraction.md as the copy editor's structure read proposes: answer the seven questions in order, state a machine's whole effect on the model once, and use one name for a machine module

**Where this comes from.** The copy editor's structure read of the document, run on 2026-11-05 under the owner's request of that day to copy edit every human-facing document. The owner chose to line edit each document first and restructure it later, so this item holds the read's outline findings, verbatim, for that later pass. The read's per-chapter findings are in the project's shared files under `v0.7.0/repo-copy-edit/runs/docs-machine-abstraction-md/structure/`, and the pass should read them too. Each "Query" below is a question the document could not answer for itself; answer it from the sources it names, or file it as its own item.

**The outline read, verbatim.**

Structure:

- **Section order.** Move § "Question 6: attributability" (rows 462-490) so that it comes after § "Question 5: naming a real machine in the interface" (rows 533-584). The order then becomes: the finding, Questions 3, 1, 2 and 4, the inlet-position decision, Questions 5, 6 and 7, the open matters, and Sources. Rows 485-490 say "the interface would attribute it to the trade name", but only Question 5 says where a trade name may appear. Question 3 stays before Question 1 because Question 1's strategy slots (rows 159-193) fill the two rates that Question 3 (rows 135-139) has the machine supply. After the move, the sections that follow Question 2 run in number order.
- **What the document covers (rows 5-11).** These rows say the document covers four things: "what a module is, what the base owns and what each machine supplies, where the parameter/strategy line falls, and what the second machine costs". The headings answer seven numbered questions and also cover the main finding, the inlet-position decision and the open matters. Replace the four-item list with the seven questions and the section that answers each. A reader who meets "Question 3" first will otherwise look for Questions 1 and 2.
- **Query: which item?** Several sections quote requirements from an item they never name:
  - Question 3, rows 125-128
  - Question 1, rows 222-226 ("the 'too permissive' failure that 'the item' names")
  - Question 2, rows 262-270
  - Question 4, rows 432-435 ("the item's requirement")
  - Question 6, rows 464-466
  - Question 7, rows 588-589 and 614-616
  - § "What this design does not decide", rows 620-621, which says "the milestone".

  Rows 5-11 name planned-milestone item 1, and rows 195-208 name `PL-439V`. The reader needs to know which item asks the seven questions, and the text does not say. Name it once in rows 5-11 and use that name everywhere.
- **Heading, row 25.** "The finding the whole design rests on" does not say what the finding is. Use "A machine changes only two rates and one volume". "The two rates above" in Question 3 and "the three quantities" in Questions 1 and 6 then have a heading to point at.
- **Heading, row 492.** In "The inlet-position decision, taken on the record", the words "taken on the record" describe the document, not the subject. Use "Fresh gas inlet position is not modelled". Question 5 (rows 561-563) calls this decision "the decline above", and Sources (rows 657-659) calls it "the decline recorded above". Both should point to it as § "Fresh gas inlet position is not modelled".
- **Heading, row 462.** "Question 6: attributability" uses a made-up word. Use "Question 6: every difference between machines traces to a named field".
- **Heading, row 228.** "Question 2: what keeps the machine profile small" fits rows 230-319 only. Rows 321-428 sit under the subheading "Three homes, and why the shipped constants move". They say which values belong to the machine, the run and the model, and record what was built in September 2026. Make them a section of their own, after Question 2, headed "Which values belong to the machine, the run and the model". Where another file cites a heading changed here, change that citation too.
- **"Machine module" and "machine profile".** "Machine module" appears in row 1 and rows 5-11, 105-111 and 432-435. "Machine profile" appears in Questions 1, 2, 4 and 7, and rows 432-435 use both terms in one paragraph. The title promises to say what a machine module is, and no section says. Query: is a module the JSON profile alone, as "one data file, and nothing else" (rows 591-599) suggests, or the profile together with its strategies? Use one name throughout. The same applies to "the base" (rows 5-11) and "the existing core" (row 117).
- **A machine's whole effect on the model is stated four times.**
  - The finding, rows 62-67: "a machine contributes exactly two rates and one volume to the circuit's row, and nothing else anywhere in the model".
  - Question 1, rows 150-155: "the machine's whole footprint".
  - Question 6, rows 468-470: "the machine's entire reach into the model".
  - Question 7, rows 591-599: "reaches it only through the two rates".

  It belongs in the finding. The others keep only the clause their argument needs, with a pointer, and use one name instead of "footprint" in one place and "reach" in another.
- **The machine's volume.** Rows 62-67 give the machine "one volume", "that of the apparatus the circuit gas occupies", and rows 69-80 put that volume into the matrix as V_C. Question 2 (rows 302-319 and 350-352) is the first place to say that V_C is the apparatus plus a patient circuit that the run supplies. Question 6 (rows 472-473) repeats this. Say it once, in rows 62-67, where the volume is introduced. Question 2 keeps the decision (`PL-HGB6`) and its reasons, and Question 6 keeps a pointer.
- **The two refused proposals.** Question 1 (rows 222-226) states them. Question 6 (rows 477-483) repeats them, "which this paragraph repeats", and Question 4 (row 442) refuses an unregistered strategy when a profile loads. Question 1 keeps the rules and Question 4 keeps the load-time refusal. Question 6 keeps a pointer to Question 1 and its own conclusion, that the fields that differ between two profiles can be computed.
- **The steps for adding a field.** Question 2 (rows 242-247) gives them: "the survey gains an entry, then this document's closed set or schema gains the member, then the machine is added". Question 7 (rows 607-612) gives them again: "first into `docs/machine-survey.md` … then into the schema … last, into every existing profile". They belong in Question 7, case 3, where a contributor adding a machine looks. Question 2 keeps "a machine adds a row, not a column, and a machine that needs a new field is a design event", with a pointer to Question 7.
- **A machine with an `unknown` field cannot be added.** Four places say this:
  - Question 2, rows 257-260: "A machine with an unknown apparatus volume cannot be added yet".
  - Question 2, rows 333-345: "a machine with an unknown required field cannot be added".
  - Question 4, rows 440-441: "`unknown` in a field the model reads … most surveyed machines cannot be added yet".
  - § "What this design does not decide", rows 639-647: "a machine whose fields are `unknown` cannot be added yet".

  The rule belongs in Question 4, refusal 2. Rows 257-260 keep "never given a plausible volume" and a pointer. Rows 333-345 keep what the rule means for the opening flow. Rows 639-647 keep which machines and fields are unknown, and the 2026-09-20 decision to look for each manual when its profile is built. Query: Question 4 refuses `unknown` in "a field the model reads", but rows 362-377 say the refusal "applies only to required fields". `deliverable_fresh_gas_flow_range` is read by the model (row 289) and is optional, so the two wordings give different results for it. Which one is the rule?
- **Opening fresh gas flow.** Question 2 (rows 333-345) says: "It is a run's opening condition … `PL-NM7X` decides the value, independently". Rows 623-625 repeat it: "`PL-NM7X` holds it, and the project owner decides it. This document decides only that the value is an opening condition of a run, not a machine specification." The argument belongs in Question 2. Rows 623-625 keep the open value, who decides it and a pointer. Query: rows 379-395 say `default_fresh_gas_flow_l_min` "stays on the machine profile", which contradicts "not a machine specification".
- **Ambient pressure.** Question 1 (rows 195-208) says: "Until it lands, a profile naming `fixed_volume_percent` gets the same numbers as one naming `variable_bypass`". Rows 626-628 repeat this: "`variable_bypass` and `fixed_volume_percent` agree everywhere in the model's domain". It belongs in Question 1. Rows 626-628 keep the open question with `PL-5K5C` and a pointer. Their one new fact, "the discriminating test in `PL-439V` passes on paper only", moves to Question 1, beside `PL-439V`'s request.
- **Flow-dependent vaporizer output.** Question 1 (rows 210-216) covers it, and rows 629-630 repeat it: "Hendrickx et al. measured it … both mapping strategies declare it as a limitation". It belongs in Question 1, and rows 629-630 keep a pointer.
- **Automated end-tidal control.** Rows 113-115 say it "fails the first and the third". Rows 635-638 say it "fails two of this design's three admissibility conditions, which is why it is a milestone and not a strategy". It belongs in the finding, and rows 635-638 keep a one-line pointer. Cut "The reason is now recorded instead of assumed", because it describes the document.
- **What a profile does not model.** Question 4 (rows 446-452) lists "Fresh gas inlet position, ventilator drive, decoupling and the control loop". Question 5 (rows 553-560) lists "inlet position, decoupling, ventilator drive and delivery mode. All four are in the model's `not_modelled` list". Give the list once, in Question 4, and have Question 5 point to it. Query: the fourth item differs ("the control loop" against "delivery mode"). Also, Question 5 calls it "the model's" list, while row 296 and rows 443-452 make `not_modelled` a field of each profile.
- **The comparison table.** "`PL-WZVZ`'s comparison table" first appears in Question 2 (rows 235-240). What it is, the machine's own panel where the trade name sits beside its parameters, sources and `not_modelled` list, appears only in Question 5 (rows 543-549 and 578-584). Say what it is at rows 235-240. The failure the table "exists to prevent" is also described two ways:
  - rows 509-514: "a number that looks sourced but that no measurement supports";
  - rows 485-490: a machine that changes a result through something unnamed, which the interface then attributes to the trade name.

  State once what the table prevents, at its first mention, and have the later places point to it.
- **Query: two admissibility conditions or three?** The subheading at row 88 says "Two admissibility conditions, both structural", and rows 105-111 then add a third. Rows 635-638 count three, but Question 7 (rows 601-605) has a new strategy prove only "the two admissibility conditions". Must a new strategy also show that it holds no state (rows 105-111)? Use the same count everywhere.
- **Survey labels.** Only rows 57-60 explain the labels (b1), (b3), (b10) and (b11) in words. Question 3 (rows 129-134) and Question 1 (rows 167, 179-180 and 193) use labels without saying what they stand for. Question 2 (rows 288-295) cites (a1), (b2), (b8) and (b9), which no section explains, and rows 631-634 rest a sentence on (b5) and (b6). Each use should say the finding in words and put the label after it. Query: what do (b5) and (b6) record?
- **Query: who measured?** Question 5 says "the survey measured the shortfall" (rows 553-560) and "the survey's measurement" (rows 569-576). Question 4 (rows 454-460) says Shin et al. "reports [the apparatus volumes] rather than measuring them". The survey is a document, so who measured what? Should Question 5 say that Shin et al. measured time to target and reported the volumes?
- **Query: is any of this built?** Rows 13-16 say "Nothing here changes `src/`", and rows 18-23 say "This design is not implemented". But rows 82-86 say "The reference tests in `tests/reference/` show this with their expected values unchanged". Rows 362-395 also record two built parts: the deliverable flow range (2026-09-20, `PL-8PS6`) and the opening-flow fallback (2026-09-27, `PL-QW19`). Which parts are built? By the reasoning in rows 18-23, built parts should be specified in `docs/MODEL.md`. Are they? Rows 13-23 should say which parts are built.
- **Query: does every survey finding fit the three quantities?** Rows 62-67 say "Every survey finding lands in one of the three". But rows 494-502 say the model has no place for inlet position, which is the survey's sharpest finding. Rows 631-634 also say (b5) and (b6) reach a number only once the machine owns the ventilator.
- **Query: does a Perseus A500 profile exist?** Rows 302-319 say "Today a Shin et al. profile for a Perseus A500 stores the with-circuit 3.3 L". Rows 639-647 say the design "runs on the reference profile in the meantime".
- **Inlet position missing from the open matters.** Rows 515-521 leave representing the inlet position to planned-milestone item 39. § "What this design does not decide" lists other matters left to a milestone, such as automated end-tidal control left to item 5, but not this one. Add a pointer line.
- **Sources.** The Fukuda entry (rows 657-659) and the Johnston entry (rows 662-663) point to where the document uses them only as "the decline recorded above" and "the 18". The Hendrickx entry (rows 660-661), the Meyer entry (rows 664-667) and the Shin entry (rows 668-670) give no pointer at all. Give each entry the section that uses it:
  - Fukuda: the inlet-position section.
  - Hendrickx: Question 1, rows 210-216.
  - Johnston: Question 2, rows 422-428.
  - Meyer: Question 1, rows 169-173 and 195-208.
  - Shin: Question 2, rows 302-319; Question 4, rows 454-460; and Question 5, rows 553-560.
  - Targ: Question 2, rows 397-420.

  Query: rows 210-216 say Hendrickx et al. measured "the same devices", just after a paragraph on the Tec 6, while rows 660-661 say they measured a cassette vaporizer. Which devices did they measure?

**Done when.** Each finding above is applied or recorded as declined with its reason, and each query is answered or filed.


**Generator check.** The owner asked for this work: the copy edit of every human-facing document (2026-11-05), with each document's structure applied before any more line editing (2026-11-07). The edits to `PL-37N4`, `PL-D42Z` and `src/anesthesia_sim/core/circuit.py` update citations of headings this restructure renamed.

## What the restructure did (2026-11-07)

The restructure moved and de-duplicated text and renamed headings. It did no line editing then, because the copy editor was paused until `PL-F0Q2` merged (project owner, 2026-11-07). The line edit of the passages that the restructure changed ran on 2026-11-09, after `PL-F0Q2` merged, and pull request `#2055` gives its counts. Two reviewers then compared each section's old and new text for statements lost or added, and the change had two blind reviews.

**Outline findings, in the order above.**

1. Section order: applied. The order is now the finding, Questions 3, 1 and 2, § "Which values belong to the machine, the run and the model", Question 4, § "Fresh gas inlet position is not modelled", Questions 5, 6 and 7, § "What this design does not decide", and § "Sources".
2. What the document covers: applied. The introduction lists the seven questions and each other section in the order they appear, and keeps "what a module *is*".
3. Which item: answered, `PL-FG9D`. Its brief asks the seven design questions and names the "too permissive" and "one field per line of the manual" failures. The introduction names it, and `PL-FG9D` replaces "the item" in Questions 3, 1, 2, 4, 6 and 7. "The item behind the comparison table" in Question 6 already names `PL-WZVZ` and stays.
4. Heading at row 25: applied, "A machine changes only two rates and one volume". `PL-D42Z` and `PL-37N4` cite it under its new name.
5. Heading at row 492: applied, "Fresh gas inlet position is not modelled". Question 5, the Fukuda source entry and `PL-8ZD7`'s citations point to it.
6. Heading at row 462: applied, "Question 6: every difference between machines traces to a named field".
7. Heading at row 228: applied. The subheading "Three homes, and why the shipped constants move" is now the section "Which values belong to the machine, the run and the model", after Question 2. The docstring of `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN` in `src/anesthesia_sim/core/circuit.py` cites the new heading. Closed items that cite the old heading are history and keep it.
8. "Machine module" against "machine profile": filed in `PL-37N4`. Choosing one name needs the design to say what a module is, and the document does not.
9. A machine's whole effect stated four times: applied. The finding states it. Question 1 and Question 6 keep the clause their argument needs, with a pointer to the finding. Question 7's "only through the two rates" is unchanged, because `PL-37N4` (passage 16) already asks whether it leaves out the volume.
10. The machine's volume: declined. A first draft rewrote the finding to say that the machine's volume is the apparatus part of $`V_C`$. The comparison found that this changed what the finding says, so the finding and Question 6 keep their original sentences. `PL-37N4` (passage 2) and `PL-8ZD7` (passage 42) already hold the query. Question 2's `PL-HGB6` paragraph keeps the decision and its reasons, and moved into the new section beside the patient-circuit bullet.
11. The two refused proposals: no change needed. Since the line edit, Question 6 already says "Question 1 explains both", and Question 4 keeps the load-time refusal.
12. The steps for adding a field: applied in part. Question 7, case 3, now ends "only then is the machine added. Never the other way." Question 2 keeps its own statement of the route, because it covers a new strategy as well as a new field, and Question 7 gives the order only for a field. The query is filed in `PL-37N4`.
13. A machine with an `unknown` field: applied. Question 4's refusal 2 now states the rule. Question 2 keeps a pointer and its statement that an unknown apparatus volume is never given a plausible one. The opening-flow bullet now says "under Question 4's refusal 2" in place of "under the rule directly above", which pointed at the wrong paragraph. The open-matters entry points to refusal 2. The query on optional against required fields is filed in `PL-37N4`.
14. Opening fresh gas flow: applied. The open-matters entry keeps `PL-NM7X`, the owner's decision, and a pointer. The query on `default_fresh_gas_flow_l_min` staying on the machine profile is filed in `PL-37N4`.
15. Ambient pressure: applied. "`PL-439V`'s discriminating test passes on paper only" moved into Question 1 beside `PL-439V`'s request. The open-matters entry keeps `PL-5K5C` and a pointer.
16. Flow-dependent vaporizer output: applied, as a pointer to Question 1.
17. Automated end-tidal control: applied. The open-matters entry points to the finding, and "that reason is now recorded rather than assumed" is cut, because it describes the document.
18. What a profile does not model: declined. Question 5's list reports what Shin et al. attributed the residual difference to, and a pointer to Question 4 would lose what the paper says. The outline finding's two queries are filed in `PL-37N4`.
19. The comparison table: applied in part. Its first mention, in Question 2, now says it is the machine's own panel that Question 5 describes. Declined: stating once what it prevents. The inlet section and Question 6 describe two different failures: a fitted volume shown as if measured, and a difference from an unnamed default shown under a trade name. Merging them is a rewrite for the line edit.
20. Two admissibility conditions or three: filed. `PL-37N4` (passage 5) already holds it, so the subheading at row 88 stays until the query is answered.
21. Survey labels: declined for this pass, because describing each finding before its label is new wording for the line edit. That wording change is filed in `PL-37N4`. The query is answered: (a1), (a2) and (b1) to (b11) are the headings of `docs/machine-survey.md` § "The variables", and (b5) and (b6) are § "(b5) Fresh gas decoupling" and § "(b6) Ventilator drive".
22. Who measured: filed in `PL-37N4`.
23. Which parts are built: filed in `PL-37N4`.
24. Whether every survey finding fits the three quantities: `PL-37N4` (passage 2) already holds it.
25. Whether a Perseus A500 profile exists: answered, none does. `src/anesthesia_sim/data/machines/` holds only `reference_circle_system.json`. Since the line edit, the sentence reads "a profile written today ... stores", which describes what such a profile would hold.
26. Inlet position missing from the open matters: declined. § "Fresh gas inlet position is not modelled" records a decision, and listing inlet position among the matters this design does not decide would contradict it. Representing it is planned-milestone item 39, which that section names.
27. Sources: applied. Each entry names the section that uses it. The query on which devices Hendrickx et al. measured is filed in `PL-37N4`.

**Per-chapter findings.** The restructure applied these:

- The closed-set rules ("A strategy is a pure function" and the two refusals) moved ahead of the slot tables, which became the subheadings "Delivery", "Removal" and "Dial mapping".
- Question 2's paragraphs were reordered as admission rule, two consumers, what the rule is wrong about, testable form, the check, unknown values.
- The desflurane maximum moved beside `agent_limits`.
- The document now has the subheadings "What is built so far" and "The reference breathing system".
- The reference profile's three grounds became a numbered list, and the second ground's two halves were joined.
- Question 4's tier paragraph moved after the list, and "Item 4" was renamed "Refusal 4", because "item" means a work item elsewhere.
- The inlet section was reordered as decision, when it stops applying, evidence, then alternatives, and "Taking the remaining choice on the record" was cut.
- Question 5's "What this binds" moved after the decision.

The restructure declined these, each for the reason given:

- Cuts of a sentence stated only once, and moves of decision history out of the document. Deciding what each reader needs is the line edit's work, and `CLAUDE.md` keeps a decision's tag with the decision.
- Repetitions inside one paragraph, renamed terms ("behaviors" to "strategies", the Question 7 heading), and a definition at the first use of a term. These are wording changes for the line edit.
- Stating "optional, defaulting to `None`" once. Each of the two paragraphs gives its own field's meaning.
- The three mentions of `PL-TBMX`. Each names a different edit.
- The inlet section's restatement of `docs/MODEL.md` § "Model boundary". The restatement stays until the restructure of `docs/MODEL.md` (`PL-BSMF`) settles what that document keeps.
- Replacing the list of what a machine owns with a pointer to Question 2's schema table. The table lists two fields that were never built, so the pointer would change what a machine owns. The query is filed in `PL-37N4`.
- Replacing "the option the survey's measurement argues directly against" in Question 5 with "(fact 1 above)". The pointer kept only part of the claim.
- The § "Sources" introduction's repeat. `PL-37N4` (passage 17) queries whether the claim holds for Targ et al., so it stays until that is answered.

The chapter reads' queries that this restructure did not answer are filed in `PL-37N4`.

**What the comparison of old and new text found.** It reported six changes:

1. `PL-FG9D` named where the old text said "the item": kept, because `PL-FG9D`'s brief shows that it is the item the text meant (outline finding 3). The reviewer saw only the two versions of the document.
2. The finding's new account of the machine's volume: restored to the original sentence (outline finding 10).
3. Question 2's route for a new strategy, cut to a pointer to Question 7: restored (outline finding 12).
4. Inlet position listed as undecided: removed (outline finding 26).
5. "Why declining is not merely the cheap option" placed before the options it refers to: moved back after them.
6. Question 5's "argues directly against" cut to a pointer: restored.

The first blind review reported nothing. The second reported that the pointer from "the machine owns" to the schema table took in two fields that were never built, so the list was restored.
