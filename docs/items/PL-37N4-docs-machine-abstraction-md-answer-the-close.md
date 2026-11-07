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
- Passage 2: "The volume V_C is the space that the circuit gas occupies in the apparatus" contradicts § "Question 6: attributability" (rows 465-467). There, V_C is the apparatus volume plus the patient-circuit volume. Question 3 also says the machine supplies only the apparatus volume.
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
- Passage 16: "a row for it in the comparison table" disagrees with Question 6, "The comparison table between machines (`PL-WZVZ`) is therefore derived". Does anyone write this row, or does it appear without work?
- Passage 16: the condition names "delivery and removal strategies", but the next sentences have the profile name a strategy for "each of the three slots". Should dial mapping be in the condition? Also, "a machine affects it only through the two rates" leaves out the volume, which § "The finding the whole design rests on" gives as the machine's third quantity.
- Passage 17: the file contradicts itself. "Each source below is cited in `docs/machine-survey.md`" does not hold for Targ AG et al. 1989, which the survey's § "Sources" does not list. The reader then has no record of how Targ was retrieved or read.
- Passage 2: "The volume $`V_C`$ is the space that the circuit gas occupies in the apparatus". Three other places say something different:
- Passage 12: "then add it to this document's closed set or to the schema". The closed set holds strategies, not fields. § "Question 7: what the second machine costs" also gives a different order for adding a new field: the survey, then the schema, then every existing profile. Which order applies?
- Passage 13: I cannot tell what "the run's patient-circuit volume, which today is the assembled circuit volume (`circuit_volume_l`)" means. The survey (rows 139-140) gives `circuit_volume_l` as the whole $`V_C`$, apparatus and patient circuit together. As written, this line makes it the patient-circuit part alone. Does it mean that today all of $`V_C`$ is `circuit_volume_l`?
- Passage 14: "Under a model such as Lerou and Booij's". The contributor does not know this outside model, and this document's § "Sources" has no entry for it. The sentence needs a citation.
- Passage 16: "When a machine's delivery and removal strategies are already in the closed set" names only two of the three slots that the next sentence mentions. Which case covers a machine that needs a new dial mapping?
- Passage 17: the Targ entry has two problems:
