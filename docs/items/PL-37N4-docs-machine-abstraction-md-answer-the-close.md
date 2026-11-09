---
id: PL-37N4
title: docs/machine-abstraction.md: answer the close-out copy editor's queries (contradictions, unnamed items, missing citations)
status: untriaged
feature: machine-docs-structure
added: 2026-11-07
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
not a defect, with the reason.

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
