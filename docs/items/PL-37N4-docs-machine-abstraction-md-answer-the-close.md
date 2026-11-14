---
id: PL-37N4
title: docs/machine-abstraction.md: answer the close-out copy editor's queries (contradictions, unnamed items, missing citations)
priority: P2
effort: L
status: done
classes: defect, docs
feature: machine-docs-structure
touches: docs/machine-abstraction.md
added: 2026-11-07
closed: 2026-11-11
pr: 2141
payoff: a contributor adding a second machine follows a design with no internal contradiction and a citation for every source, so the profile they write stores no second flow floor and meets every condition the solver needs
verify: grep -qE '^- Lerou' docs/machine-abstraction.md
---

**Problem.** The close-out copy edit of docs/machine-abstraction.md (`PL-3K13`, 2026-11-07) raised the
queries below. Each says that one sentence contradicts another part of the
document, the survey, or the code, or that a reader cannot follow it without a
fact the document does not give. The copy editor may not change a fact, so it
left each sentence as it found it. Row numbers are those of the file the copy
editor read, the branch head before its rewrite (`PL-3K13`'s branch, commit
`db2d3eb4`). The four reads of each passage overlap, so some queries repeat in
other words.

The full replies are in the project files folder at
`v0.7.0/repo-copy-edit/runs/close-out/md-ce.txt`.

**Fix.** Answer each query in the document: correct the sentence that is wrong,
name the item where the text says "the item", and add the missing citation.
Where the restructure in `PL-39ZK` would remove or move the sentence, do this
item with it or after it.

**Done when.** Each query below is either fixed in docs/machine-abstraction.md or answered here as
not a defect, with the reason. In particular, § "Sources" gains an entry, beginning "- Lerou", for Lerou and Booij's model, which the inlet-position entry cites.

## Queries

- Passage 2: "to the breathing circuit's row ... and nothing else anywhere in the model" contradicts rows 45-47 and 74-75, which put both rates in the accounting rows too.
- Passage 2: "The volume V_C is the space that the circuit gas occupies in the apparatus" contradicts § "Question 6: every difference between machines traces to a named field" (rows 465-467). There, V_C is the apparatus volume plus the patient-circuit volume. Question 3 also says the machine supplies only the apparatus volume.
- Passage 2: "Everything the survey found falls under one of the three" contradicts the survey's "Neither data nor behavior" list (inlet position, ventilator drive). It also contradicts § "The inlet-position decision", which says the model cannot represent inlet position.
- Passage 3: "Every other machine that the survey found separates them" introduces a table of survey entries, not machines. The survey also records each machine's sampling configuration as unknown (machine-survey.md (b10), rows 486-487). The author should say whether "each survey entry below" is meant.
- Passage 5: the heading (row 87, "Two admissibility conditions, both structural") says two, but row 89 says three and the list has three. The heading must keep its text, so the author must decide which is wrong.
- Passage 6: "The item asks for this guarantee" (row 123) and "The item asks the design to avoid this" (rows 135-136) do not say which item. "The item" also appears at rows 165 and 461. The reader does not know this repository's history, and no visible row names the item.
- Passage 7: "so every difference is one or the other" contradicts the survey's "Neither data nor behavior" list (inlet position, ventilator drive). It also contradicts § "The inlet-position decision" in this file.
- Passage 8: "the failure that the item names" does not say which item (see Passage 6).
- Passage 11: I cannot tell how "Recording the model's sea-level assumption (`PL-5K5C`) will separate the two mappings". At sea level the factor stays one. The reader needs to know what `PL-5K5C` adds that makes the mappings differ.
- Passage 12: "seven categories, each with the condition that would bring it back" is contradicted by the survey's § "Ruled out". There, "Circuit component absorption of agent" and "Data export, record-keeping and network integration" give no such condition.
- Passage 13: "The item asks for this" does not say which item (see Passage 6).
- Passage 13: the inflow entry names only the delivery strategy. § "The closed set of behaviors" gives the dial mapping its own slot, and it sets F_D and so the inflow. The author should say whether the dial mapping belongs in this entry.
- Passage 14: the reader needs a citation for Lerou and Booij's model. Neither this file's § "Sources" nor the survey's lists it.
- Passage 16: the bold sentence says "one data file and nothing else", but rows 587-589 add a schema test, a table row and a test file.
- Passage 16: a table row added for each machine reads as hand-maintained, while § "Question 6" says the table is derived.
- Passage 16: "a machine affects it only through the two rates" leaves out the volume that rows 27-28 include.
- Passage 16: the condition names delivery and removal only, but row 585 gives three slots. The author should say whether a new dial mapping falls under the second case.
- Passage 17: Targ et al. 1989 is not in the survey's § "Sources" (rows 648-801), so rows 641-643 are not true of it. The reader needs Targ's retrieval route and read depth.
- Passage 1: the reader needs to know which data "the data migration" moves, and from where to where. The text does not say.
- Passage 1: later sections say "the item asks…" (Question 3, § "The closed set of behaviors", Question 6). The reader needs this introduction to name the work item whose questions the design answers. The survey calls the design's item `PL-FG9D`, but this file never says so.
- Passage 9: the reader adding a two-mode machine such as the Zeus IE needs to know which form the design uses: two profiles, or one profile with a mode selection. Alternatively, the text could say that either is allowed.
- Passage 14: the reader needs a citation for "a model such as Lerou and Booij's". Neither this file's § "Sources" nor the survey's lists it.
- Passage 16: the passage contradicts itself. "it needs one data file and nothing else" is followed by "Adding the machine also takes a schema test and a row for it in the comparison table" and "The diff touches the data file and one test file".
- Passage 16: "a row for it in the comparison table" disagrees with Question 6, "The comparison table between machines (`PL-WZVZ`) is therefore derived". Does anyone write this row, or is it derived?
- Passage 16: the condition names "delivery and removal strategies", but the next sentences say that the profile names a strategy for "each of the three slots". Should dial mapping be in the condition?
- Passage 16: "a machine affects it only through the two rates" leaves out the volume, which § "A machine changes only two rates and one volume" gives as the machine's third quantity.
- Passage 17: the file contradicts itself. "Each source below is cited in `docs/machine-survey.md`" does not hold for Targ AG et al. 1989, which the survey's § "Sources" does not list. The reader then has no record of how Targ was retrieved or read.
- Passage 2: "The volume $`V_C`$ is the space that the circuit gas occupies in the apparatus". Three other places say something different:
- Passage 12: "then add it to this document's closed set or to the schema". The closed set holds strategies, not fields. § "Question 7: what the second machine costs" also gives a different order for adding a new field: the survey, then the schema, then every existing profile. Which order applies?
- Passage 13: I cannot tell what "the run's patient-circuit volume, which today is the assembled circuit volume (`circuit_volume_l`)" means. The survey (rows 139-140) gives `circuit_volume_l` as the whole $`V_C`$, apparatus and patient circuit together. As written, this line makes it the patient-circuit part alone. Does it mean that today all of $`V_C`$ is `circuit_volume_l`?
- Passage 14: "Under a model such as Lerou and Booij's". The contributor does not know this outside model, and this document's § "Sources" has no entry for it. The sentence needs a citation.
- Passage 16: "When a machine's delivery and removal strategies are already in the closed set" names only two of the three slots that the next sentence mentions. Which case covers a machine that needs a new dial mapping?
- Passage 17: the Targ entry has two problems:

- From `PL-8ZD7`'s list (its "Passage 42", the same close-out copy edit), two queries this list did not hold. "Five entries of that matrix involve the fresh gas flow" does not match the equation: $`A_{F_I,F_A} = \dot V_A/V_C`$ contains no $`\dot V_F`$, and the text later rewrites only "four of the five entries". The same count appears twice more.
- From `PL-8ZD7`'s list: the reader needs to know what the 9.86 L measures, and where "the reference profile's provenance note" is.
- Passage 17's Targ query, updated 2026-11-11: `PL-8ZD7` added Targ, Yasuda and Eger 1989 to the survey's § "Sources", so "Each source below is cited in `docs/machine-survey.md`" now holds for it. Check the entry's other problems against the survey's new entry.

## Queries from the structure read (`PL-39ZK`, 2026-11-07)

The structure read of 2026-11-05 raised these. The document's restructure on 2026-11-07 (`PL-39ZK`) answered the queries it could. The rest are below, in the restructured document's terms. Where a query repeats one above, it says so.

- "Machine module" and "machine profile": the title and the introduction say module, and Questions 1, 2, 4 and 7 say profile. Question 4's opening uses both. Is a module the JSON profile alone, as Question 7's "one data file, and nothing else" suggests, or the profile together with its strategies? Use one name throughout. The same applies to "the base" in the introduction and "the existing core" in Question 3's heading.
- Question 4's refusal 2 rejects `unknown` in "a field the model reads". § "What is built so far" says that refusal applies only to required fields. The model reads the optional field `deliverable_fresh_gas_flow_range`, so the two wordings give different results for it. Which one is the rule?
- § "Which values belong to the machine, the run and the model" says the opening fresh gas flow is "an opening condition of a run" and "not a machine specification". § "What is built so far" says `default_fresh_gas_flow_l_min` "stays on the machine profile". Which design must a contributor keep? Should that field be in Question 2's schema table, which admits only fields with a declared consumer?
- What a profile does not model: Question 4 lists "fresh gas inlet position, ventilator drive, decoupling and the control loop". Question 5 says Shin et al. attributed the residue to "inlet position, decoupling, ventilator drive and delivery mode" and that "every one of those is in this model's `not_modelled` list". Question 4 has "the control loop" where Question 5 has "delivery mode". Question 5 also calls `not_modelled` "the model's" list, while Question 2's schema makes it a field of each profile.
- Survey labels: Question 3 and Question 1 use (b1), (b3), (b10) and (b11) without saying what each records, and Question 2's schema table cites (a1), (b2), (b8) and (b9). Each use should give the finding in words with the label after it. The labels are the headings of `docs/machine-survey.md` § "The variables". (b5) is fresh gas decoupling, and (b6) is ventilator drive.
- Who measured: Question 5 says "the survey measured the shortfall" and calls the comparison "the survey's measurement". Question 4 says Shin et al.'s apparatus volumes are carried "rather than measured". Should Question 5 say that Shin et al. measured time to target and reported the volumes?
- Which parts are built: the introduction says "Nothing here changes `src/`" and "This design is not implemented". The finding says the reference tests in `tests/reference/` "prove it, with their expected values unchanged", and § "What is built so far" records the deliverable flow range (2026-09-20, `PL-8PS6`) and the opening-flow fallback (2026-09-27, `PL-QW19`). The introduction should say which parts are built, and those parts should be specified in `docs/MODEL.md`. Are they?
- Hendrickx et al.: Question 1's § "Dial mapping" says they measured "the same devices", right after a paragraph on the Tec 6. § "Sources" says they measured a cassette vaporizer. `docs/machine-survey.md` § "(b1)" says the device was GE's ADU cassette vaporizer. The sentence in Question 1 should name it.
- Fields that were not built: Question 2's schema table lists `minimum_total_flow_l_min` and `minimum_oxygen_flow_l_min` as fields the model reads. § "What is built so far" says neither was built: the minimum total flow is the floor of `deliverable_fresh_gas_flow_range` under a second name, and nothing the model computes would read the minimum oxygen flow until there is a hypoxic guard. A profile author who follows the table would store a second flow floor that can disagree with the range. Should the two rows leave the table, or say why they are not built? (Raised by the restructure's blind review, 2026-11-07.)
- The route for a new strategy: Question 2 gives one route for a new closed-set member and for a new schema field. In that route, the survey gains an entry first, then the document, then the machine. Question 7 repeats that order only for a new field, and its new-strategy case does not say that the survey comes first. Should Question 7 state the order for both, so that Question 2 can point there?

The remaining per-chapter queries are in the project's shared files, under `v0.7.0/repo-copy-edit/runs/docs-machine-abstraction-md/structure/chapter-*.txt`, on the lines that begin "Query". Most ask for a term to be explained where it is first used, or for an item, a milestone or a source to be named. Read each one against the restructured text: some no longer apply. In particular, the document now names the design's item, `PL-FG9D`, and the pointer to § "The run owns its opening conditions" resolves, because the documentation check (`tools/doc_check.py`) treats a bold opening phrase as a section.

**Checked 2026-11-09:** after the restructure (`PL-39ZK`, closed 2026-11-09), a sample of the queries still applies to `docs/machine-abstraction.md`. Row 42 still says a machine adds two rates and one volume "and nothing else anywhere in the model". Row 46 still says "Everything the survey found falls under one of the three", though § "Fresh gas inlet position is not modelled" says the model cannot represent inlet position. The heading "Two admissibility conditions, both structural" still sits over "The three conditions below" and a list of three, and no file cites the heading. Lerou and Booij are still cited in the inlet-position entry with no entry in § "Sources". § "Sources" still opens "Every source below is cited in `docs/machine-survey.md`", and `grep -n Targ docs/machine-survey.md` finds nothing. The schema table still lists `minimum_total_flow_l_min` and `minimum_oxygen_flow_l_min`, which § "What is built so far" says were not built. Some queries no longer apply: the document now names its item, `PL-FG9D`, and no "The item asks" sentence remains. So the item still holds, and the session that works it reads each query against the current text.

**Why it matters.** This document is the design a contributor follows to add a second machine. A contradiction in it leads to a profile that stores a second flow floor, or to a machine admitted on two conditions when the solver needs three. A source with no citation cannot be checked.

**Generator check.** One-off: queries from the `docs/machine-abstraction.md` copy edit and structure read (`PL-3K13`, `PL-39ZK`).

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/machine-abstraction.md` already has the heading "Two admissibility conditions, both structural" (row 88) beside "this design's three admissibility conditions" (row 636), Lerou and Booij cited with no source entry (row 517), and "Every source below is cited in `docs/machine-survey.md`" (row 651) over a Targ entry (row 671) that the survey of that tree does not list. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.

## Answers, 2026-11-11

Every query above was read against `docs/machine-abstraction.md` on `origin/main` at `73c55c9`, and against `docs/machine-survey.md` as `PL-8ZD7` leaves it on #2112. Each is fixed in the document, answered here as not a defect, or left to the item that owns the sentence. Several queries are one problem in different words, so they are answered by problem.

**Fixed in the document.**

- What a machine contributes. It now says a machine reaches the breathing circuit's row and the two accounting rows, and nothing else. $`V_C`$ is defined as apparatus plus patient circuit, with the machine supplying the apparatus part. "Everything the survey found" is now "every difference this model can represent", with inlet position (b7) and ventilator drive (b6) named as the two it cannot, in § "A machine changes only two rates and one volume" and in Question 1's decidability sentence.
- The table of survey departures is introduced as four ways a machine departs, not as machines, and says which three separate the two rates. (b1) does not separate them; it changes the delivery formula only.
- Terms. The matrix section defines the nine states, the accounting rows, the unit state, the patient rows and the symbols, pointing to `docs/MODEL.md` § "Symbols". The introduction defines a machine profile as what `ROADMAP.md` calls a module, uses "profile" throughout, says the survey's labels are the headings of its § "The variables", and gives each label its finding in words where the tables cite it. $`\dot V_S`$ is defined under § "Removal". Planned-milestone items 1, 4, 5, 39 and 40 are named with their `ROADMAP.md` titles.
- Admissibility. The heading is now "Three admissibility conditions", which no file cited. The propagator needs the first two and rollback the third, and Question 7's new-strategy case now names all three. The volume needs no condition of its own, because `CompartmentVolume` in `core/numerical_envelope.py` already refuses a volume that is not finite or lies outside its range. The end-tidal sentence now says why it fails the first and third, from the survey's (b4).
- Which parts are built. The introduction says the design is mostly unbuilt, names the two built parts (`PL-8PS6`, `PL-QW19`) and where `docs/MODEL.md` specifies them (§ "Runtime controls", § "Parameter provenance"), and says which roadmap item builds the rest. `ROADMAP.md` split the work on 2026-09-20: item 40 builds loading and refusing a profile, item 1 the interlocks and the solver work. The document's sentences that said item 1 builds the loader or the column check now say item 40. The reference-test sentence is now in the future tense.
- The registry does not exist yet; § "The closed set of behaviors" now says item 1 builds it.
- The Zeus IE's two modes. **Decided: two profiles, one per mode**, because a profile names one strategy per slot. A mode selection would be a run control that changes a strategy mid-run, which the design does not have. This is the only reading the design's own rule allows, so it was decided rather than asked.
- Dial mapping. `PL-5K5C` is done: it recorded the 760 mmHg assumption in `docs/MODEL.md` § "Assumptions" and does not separate the mappings. Only a model whose ambient pressure can vary would, and no item or roadmap entry plans one. The paragraph and § "What this design does not decide" now say so.
- Hendrickx et al. The sentence now names the device, the vaporizer of the Datex-Ohmeda ADU, and gives the sevoflurane range too. All figures were checked against the abstract through the PubMed MCP server on 2026-11-11 (PMID 11473867, DOI 10.1097/00000539-200108000-00031). "Every validated wash-in ratio" now points to `docs/MODEL.md` § "Published wash-in and elimination validation test". No item or roadmap entry plans flow-dependent output, and the text says so.
- The schema table. **Decided:** `minimum_total_flow_l_min` and `minimum_oxygen_flow_l_min` leave the table, with a paragraph giving why neither is a field: the first is the range's floor, which `CLAUDE.md`'s one-source-of-truth rule forbids storing twice (the query was right that the admission rule alone did not say this), and the second has no consumer. `default_fresh_gas_flow_l_min` joins the table as optional, consumed by the run builder, so the table and § "What is built so far" agree. Optional fields are marked, and `consumer: "attribution"` is glossed as the comparison table.
- Refusal 2. **Decided:** it applies to required fields, and an optional field says "declares nothing" with `null`. This is what the built code does (`PL-8PS6`, `PL-QW19`) and what § "What is built so far" already said, so the refusal was brought into line with it.
- The opening flow. The design keeps the opening flow as a run condition. A machine that publishes a startup flow may state it in the optional field, and the run opens at it. § "The run owns its opening conditions" now says this, so it no longer reads as forbidding the field that § "What is built so far" keeps.
- The desflurane maximum. "The intersection rule ... holds the two together" was wrong: that rule is built for the fresh gas flow only. The text now says the maximum is a field of each agent's data file today, no machine limits the dial, and moving it is the data migration. The introduction names the migration too.
- Question 6's volume line now says that today all of $`V_C`$ is `circuit_volume_l`, and the split comes with item 1. The inflow line now includes the dial mapping, which produces the $`F_D`$ that delivery reads.
- Question 7. **Decided:** a machine whose three strategies already exist costs one data file and its provenance rows in `docs/MODEL.md`, which `ROADMAP.md` item 1's cost target and the documentation check already require and the document had left out. The schema test and the comparison row are gone from the list: the loader's refusals and the column check run over every profile, and Question 6 says the comparison table is derived. A new strategy in any of the three slots, a new dial mapping included, is the second case, which now gives the order (survey, closed-set row and registry entry, then the machine) and says that it changes `core/` by that entry. Question 2 now points to Question 7 for both orders.
- The inlet-position section. The decision not to represent inlet position expires with item 39, which `ROADMAP.md` names as where the circuit's topology would go, or with a multi-limb circuit entering the model by another route; the text now says the two are distinct. The interface statement outlives the decision for any machine whose inlet position is unknown. Those two claims no longer contradict each other, because the text now separates the decision from the statement. It also says that no interface states the decision yet, and which work builds the statement and its test.
- Lerou and Booij. § "Sources" gains an entry beginning "- Lerou", read at abstract depth through the PubMed MCP server on 2026-11-11 (PMID 11575385, DOI 10.1093/bja/86.1.12; PubMed Central holds no full text). The abstract supports the narrower sentence the document now uses, that their model represents an actual circle-absorber system with a standing bellows ventilator. The claim that their breathing system has three parts rests on `docs/MODEL.md`'s full-text reading of 2026-09-06, which § "Model boundary" carries. The § "Sources" preamble now exempts this entry from "cited in `docs/machine-survey.md`" and gives its route instead.
- Targ et al. The 9.86 L is now described as their water-filled volume of an assembled circle system with a reservoir bag standing in for the lungs, and "the reference profile's provenance note" is now the note on the Targ entry in `reference_circle_system.json`, which is where it is. `PL-8ZD7` adds Targ to the survey's § "Sources" on #2112, so the preamble holds for Targ once #2112 merges.
- Smaller points. Question 5's decision now names `PL-FG9D`, whose brief records it under "Promoted 2026-09-20". "The base" became the simulator's existing code. "Agent-milestone work" became the milestone that adds the agent. "The column check" is defined where Question 2 introduces it, and Question 7 gives that section's heading. The survey's last section is cited by heading. "The row above" names the paragraph. Shin et al., not the survey, measured the shortfall in Question 5. The Sources entries say what "the 18" and "the Zeus" are.

**Not a defect.**

- "Five entries of that matrix involve the fresh gas flow" (from `PL-8ZD7`'s list). The text on `main` already reads "Five entries of that matrix belong to the breathing circuit" and "$`\dot V_F`$ appears in four of those five". That matches `build_system_matrix` in `core/governing_equations.py`: three entries in the circuit's row, one each in the two accounting rows, and $`A_{F_I,F_A}`$ carries no $`\dot V_F`$.
- "Seven categories, each with the condition that would bring it back". On #2112 every one of the survey's seven ruled-out categories gives such a condition, circuit component absorption and data export included.
- "The item asks", and naming `PL-FG9D`. The 2026-11-09 check already found these answered by the restructure.


**Left to `PL-4G3N`** (untriaged, on #2112). That item owns what `docs/machine-abstraction.md` says Fukuda et al. and Shin et al. found, and the coordinator holds it for the owner's triage. Three queries here fall inside it and are not changed on this branch. The first is § "Fresh gas inlet position is not modelled"'s "with volume held fixed". The second is "except the two that Fukuda et al. instrumented", where the abstract names three machines. The third is Question 5's list of Shin et al.'s reasons and "every one of those is in this model's `not_modelled` list". That third sentence is also where Question 4's list (inlet position, ventilator drive, decoupling, control loop) and Question 5's list (adding delivery mode) disagree. The `PL-4G3N` fix should make the two lists agree and call `not_modelled` a field of each profile. § "Sources"'s Fukuda entry, "inlet position changes $`F_I/F_D`$ at fixed volume", repeats the same claim and belongs to the same fix.
