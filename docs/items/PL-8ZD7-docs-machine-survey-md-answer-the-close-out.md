---
id: PL-8ZD7
title: docs/machine-survey.md: answer the close-out copy editor's queries (contradictions and unstated reading depth)
status: untriaged
feature: machine-docs-structure
added: 2026-11-07
---

**Problem.** The close-out copy edit of docs/machine-survey.md (`PL-3K13`, 2026-11-07) raised the
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
Where the restructure in `PL-3MTS` would remove or move the sentence, do this
item with it or after it.

**Done when.** Each query below is either fixed in docs/machine-survey.md or answered here as
not a defect, with the reason.

## Queries

- Passage 42: the reader needs to know which data "the data migration" moves, and the rows shown do not say.
- Passage 42: "and nothing else anywhere in the model" conflicts with rows 45-47 and 74-75. There, both rates also enter the accounting rows (A_{M_delivered,1} and A_{M_exhausted,F_I}).
- Passage 42: "The volume V_C is the space that the circuit gas occupies in the apparatus" conflicts with two other rows. Rows 467-469 make V_C the apparatus volume plus the run's patient-circuit volume. `docs/machine-survey.md` rows 171-173 say that a machine supplies only the apparatus part.
- Passage 42: "Everything the survey found falls under one of the three" conflicts with `docs/machine-survey.md` rows 597-611. They list inlet position and ventilator drive as "Neither data nor behavior", which the model has no place for.
- Passage 42: "Five entries of that matrix involve the fresh gas flow" conflicts with the equation. A_{F_I,F_A} = V̇_A/V_C contains no V̇_F, and row 69 rewrites only "four of the five entries". Rows 49 and 69 use the same count.
- Passage 42: "Every other machine that the survey found separates them" introduces a table of survey entries, not machines. Its (b1) row changes only F_D and leaves removal unchanged, so that row does not separate delivery from removal. Say whether "every other machine" is meant.
- Passage 42: the heading (row 87) says "Two admissibility conditions, both structural", but rows 89-112 set out three conditions. Only the author can decide whether to rename the heading, and update the files that cite it, or reword the text.
- Passage 42: "The item" (rows 123 and 135) names no item. The reader needs its id to check the requirement.
- Passage 42: "Hendrickx et al. measured it for both device classes" conflicts with two other rows. Row 649 describes that source as "cassette-vaporizer output", and the survey's row 75 lists the GE cassette vaporizer as a separate axis. Say which device classes the study measured.
- Passage 42: "seven categories, each with the condition that would bring it back" conflicts with the survey's rows 548-553. Two of the seven ruled-out categories give no such condition: circuit component absorption and data export.
- Passage 42: Lerou and Booij are cited without an entry in § "Sources" (rows 641-661). A contributor who does not know that design needs the citation.
- Passage 42: "it needs one data file and nothing else" conflicts with rows 588-590, which add a schema test, a comparison row and one test file.
- Passage 42: the condition names only delivery and removal strategies, but the profile "names one strategy for each of the three slots". Say whether the dial-mapping strategy must also be in the closed set.
- Passage 42: "a machine affects it only through the two rates" leaves out the volume V_C, which rows 27-31 count as the machine's third quantity.
- Passage 42: the reader needs to know what the 9.86 L measures, and where "the reference profile's provenance note" is.
- Passage 42: the reader needs to know which document holds `PL-FG9D`'s design. If it is `docs/machine-abstraction.md`, name it here.
- Passage 42: "The difference shows in the first two minutes of every run" holds at 4 L/min, where the table gives τ_C of 48–89 s. Row 210 gives τ_C of about 12 minutes at 0.5 L/min, so say whether "every run" means every run at the default flow.
- Passage 42: "the accuracy table" names no document or section. The reader needs to know where the table is.
- Passage 42: "the only survey entry that affects an equation rather than a parameter" conflicts with the (b3) entry. Rows 294-302 say that delivery mode "changes the model's equation", and rows 573-595 list five behaviors that need different equations or code. Say which claim is right.
- Passage 42: "The absorption has been measured" gives no source. A clinician checking the claim needs the citation, and § "Sources" lists none for it.
- Passage 42: § "The inlet-position decision, taken on the record" in `docs/machine-abstraction.md` already records a choice. Inlet position is left out for now, the interface says so, and representing it belongs to item 39. This list still asks the reader to choose option 1 or 2, so say whether the choice is still open.
- Passage 42: "Each entry says how far its source was read" conflicts with four entries that give no reading depth: Bashraheel (rows 761-764), Jakobsson (rows 774-777), Leijonhufvud (rows 778-782) and Zumsande (rows 783-786).
- Passage 42: the Bashraheel and Jakobsson entries do not say how far each source was read, which row 648 promises for every entry. The reader needs "abstract read", "metadata only" or "full text read" for each.
- Passage 24: "was kept because it was ruled not critical" does not say who ruled it or where that ruling is recorded (step 5, say who does what). A reader checking the stored value needs that record.
- Passage 25: "the default-flow column of the accuracy table" does not say which table or where it is.
- Passage 33: "the fresh gas flows the literature now uses, such as 300 mL/min" has no source. A clinician checking this figure needs one.
- Passage 33: "a surveyed machine's integrated multi-gas module" does not name the machine.
- Passage 34: "the only survey entry that affects an equation" is contradicted by § "(b3)" (rows 294-302), which says delivery mode "changes the model's equation". It is also contradicted by the "Behavior" list, which has five entries.
- Passage 35: I cannot tell what "Features that need a longer explanation are ruled out in bucket (b), above" means. The visible (b) entries describe differences the survey keeps, and no visible row explains "bucket".
- Passage 35: "The absorption has been measured" gives no source.
- Passage 37: the reader needs to know that docs/machine-abstraction.md § "The inlet-position decision, taken on the record" has already made this choice for the present model (leave them out, option 2). This list still asks for it.
- Passage 40: "Each entry says how far its source was read" is contradicted by Bashraheel (rows 759-762), Jakobsson (772-775), Leijonhufvud (776-780), Zumsande (781-784) and both ISO entries, which do not say. The reader checking those sources needs to know.
- Passage 19: the file contradicts this. "In this model, volume is the only machine parameter" disagrees with § "(b8)", where a machine profile has `deliverable_fresh_gas_flow_range`, and with § "(a2)", where the default fresh gas flow is "a setting of the machine". Does the sentence mean the only machine parameter that shapes the curve?
- Passage 25: the reader does not know which "accuracy table" has a default-flow column, or where to find it. The text does not say.
- Passage 26: a clinician checking the stored values needs the sources of the 8.0% sevoflurane and 5.0% isoflurane maxima. The section cites a source only for 18%.
- Passage 26: the paragraph contradicts itself. "The maximum belongs to the device, not to the agent" sits beside "has to depend on the machine as well as on the agent".
- Passage 37: "No machine publishes one" claims more than § "(a2)", which says "No source that the survey could obtain gives a default fresh gas flow for any surveyed machine". The survey reached no manual.
- Passage 37: the reader needs to know whether "Choose option 1 or 2" is still open. `docs/machine-abstraction.md` § "The inlet-position decision, taken on the record" records option 2 for the present model and option 1 for item 39.
- Passage 18: the contributor needs to know where the design is written. `docs/machine-abstraction.md` says it is the design for planned-milestone item 1 and that it builds on this survey. If it is the design that `PL-FG9D` names, give its path here.
- Passage 25: "every value in the default-flow column of the accuracy table". No row says which accuracy table this is or where to find it, and neither reader can find it from this document.
- Passage 31: "The minimum total flow is the lower limit of that range, so it has no field of its own." The Data table under § "What `PL-FG9D` needs: data against behavior" (row 567) lists "Minimum total flow and minimum oxygen flow" as a field that belongs in each machine's file.
- Passage 34: "This is the only survey entry that affects an equation rather than a parameter". Entry (b3) says that delivery mode "changes the model's equation". The "Behavior" list under § "What `PL-FG9D` needs: data against behavior" also gives five such entries: (b11), (b3), (b4), (b1) and (b5).
- Passage 37: "Choose option 1 or 2, and record the choice in the work item (`PL-FG9D`)". `docs/machine-abstraction.md` § "The inlet-position decision, taken on the record" has already made this choice: inlet position is left out, and the interface says so where a machine is chosen. It also sends representing the topology to planned-milestone item 39. Should this entry record that choice, or point to it?
