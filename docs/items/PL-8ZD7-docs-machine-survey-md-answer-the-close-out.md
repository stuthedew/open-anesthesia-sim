---
id: PL-8ZD7
title: docs/machine-survey.md: answer the close-out copy editor's queries (contradictions and unstated reading depth)
priority: P2
effort: L
status: done
classes: defect, docs
feature: machine-docs-structure
touches: docs/machine-survey.md, docs/items/PL-37N4-docs-machine-abstraction-md-answer-the-close.md
added: 2026-11-07
closed: 2026-11-11
pr: 2112
payoff: a clinician or contributor checking a machine value against the survey finds a source and a reading depth for each entry, and no choice asked for that was already made
verify: ! grep -qF 'Choose option 1 or 2' docs/machine-survey.md
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
not a defect, with the reason. In particular, the inlet-position entry no longer asks the reader to "Choose option 1 or 2": it points to the choice that `docs/machine-abstraction.md` § "Fresh gas inlet position is not modelled" records.

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
- Passage 42: § "Fresh gas inlet position is not modelled" in `docs/machine-abstraction.md` already records a choice. Inlet position is left out for now, the interface says so, and representing it belongs to item 39. This list still asks the reader to choose option 1 or 2, so say whether the choice is still open.
- Passage 42: "Each entry says how far its source was read" conflicts with four entries that give no reading depth: Bashraheel (rows 761-764), Jakobsson (rows 774-777), Leijonhufvud (rows 778-782) and Zumsande (rows 783-786).
- Passage 42: the Bashraheel and Jakobsson entries do not say how far each source was read, which row 648 promises for every entry. The reader needs "abstract read", "metadata only" or "full text read" for each.
- Passage 24: "was kept because it was ruled not critical" does not say who ruled it or where that ruling is recorded (step 5, say who does what). A reader checking the stored value needs that record.
- Passage 25: "the default-flow column of the accuracy table" does not say which table or where it is.
- Passage 33: "the fresh gas flows the literature now uses, such as 300 mL/min" has no source. A clinician checking this figure needs one.
- Passage 33: "a surveyed machine's integrated multi-gas module" does not name the machine.
- Passage 34: "the only survey entry that affects an equation" is contradicted by § "(b3)" (rows 294-302), which says delivery mode "changes the model's equation". It is also contradicted by the "Behavior" list, which has five entries.
- Passage 35: I cannot tell what "Features that need a longer explanation are ruled out in bucket (b), above" means. The visible (b) entries describe differences the survey keeps, and no visible row explains "bucket".
- Passage 35: "The absorption has been measured" gives no source.
- Passage 40: the claim "Each entry says how far its source was read" does not hold for six entries: Bashraheel (rows 759-762), Jakobsson (772-775), Leijonhufvud (776-780), Zumsande (781-784) and both ISO entries. A reader checking those sources needs to know how far each was read.
- Passage 19: the file contradicts this. "In this model, volume is the only machine parameter" disagrees with § "(b8)", where a machine profile has `deliverable_fresh_gas_flow_range`, and with § "(a2)", where the default fresh gas flow is "a setting of the machine". Does the sentence mean the only machine parameter that shapes the curve?
- Passage 25: the reader does not know which "accuracy table" has a default-flow column, or where to find it. The text does not say.
- Passage 26: a clinician checking the stored values needs the sources of the 8.0% sevoflurane and 5.0% isoflurane maxima. The section cites a source only for 18%.
- Passage 26: the paragraph contradicts itself. "The maximum belongs to the device, not to the agent" sits beside "has to depend on the machine as well as on the agent".
- Passage 37: "No machine publishes one" claims more than § "(a2)", which says "No source that the survey could obtain gives a default fresh gas flow for any surveyed machine". The survey reached no manual.
- Passage 18: the contributor needs to know where the design is written. `docs/machine-abstraction.md` says it is the design for planned-milestone item 1 and that it builds on this survey. If it is the design that the work item `PL-FG9D` names, give its path here.
- Passage 25: "every value in the default-flow column of the accuracy table". No row says which accuracy table this is, and neither reader can find it from this document.
- Passage 31: "The minimum total flow is the lower limit of that range, so it has no field of its own" conflicts with the Data table under § "What `PL-FG9D` needs: data, behavior, and what is neither" (row 567), which lists "Minimum total flow and minimum oxygen flow" as a field that belongs in each machine's file.
- Passage 34: "This is the only survey entry that affects an equation rather than a parameter" conflicts with entry (b3), which says that delivery mode "changes the model's equation". The "Behavior" list under § "What `PL-FG9D` needs: data, behavior, and what is neither" also gives five such entries: (b11), (b3), (b4), (b1) and (b5).
- Passage 37: "Choose option 1 or 2, and record the choice in the work item (`PL-FG9D`)" asks for a choice that `docs/machine-abstraction.md` § "Fresh gas inlet position is not modelled" has already made: the present model leaves inlet position out (option 2), and the interface says so where a machine is chosen. That section defers representing inlet position and the topology to planned-milestone item 39 (option 1). Is the choice still open? If not, should this entry record it, or point to it?

## Queries from the structure read (`PL-3MTS`, 2026-11-07)

The structure read of 2026-11-05 raised queries, and the restructure of 2026-11-07 (`PL-3MTS`) answered those it could. The rest are below, in the restructured document's terms.

- Shin et al.'s volumes: the headline says Shin et al. "computed each one's circuit volume" (Perseus A500 3.3 L, Zeus IE 3.2 L) and calls circuit volume "this model's only machine parameter". Rule 2 and the Shin entry say that Shin et al. printed apparatus volumes taken from other sources, and another item (`PL-H47Y`) already records that those sources were Dräger's instructions-for-use manuals (Shin et al.'s refs 12-14). The (a1) table defines apparatus volume as excluding the patient circuit. Are 3.3 L and 3.2 L the tier-2 apparatus volumes plus the 1.2 L circuit? Did Shin et al. compute them or copy them? Does the model take the circuit volume or the apparatus volume? The headline should state the volumes' tier and use one name for the quantity.
- Fukuda et al.'s machines: the headline says "on fixed machines", the machine table names the Dräger Fabius as "the fresh-gas-inlet experiment's platform", and (b7) says "two decoupling-style machines". The headline should name the machines, which needs the paper.
- The comparison table (`PL-WZVZ`): none of the four places that name it says what it shows or who sees it. Say both where it is first mentioned. The four are § "(b7) Fresh gas inlet position", § "Ruled out", the (b7) entry of § "What `PL-FG9D` needs: data, behavior, and what is neither", and § "What is missing, and how the next session gets it".
- "This session": § "The machines surveyed" says "No installed-base or market-share source was reachable from this session" and "whose current US presence this session could not evidence", and the Shin entry says "this session could not reach". Only § "How a value gets into this document" dates its search (2026-09-19). Each sentence should give the date of its own search.
- Biro 1997 and the Fabius: the table lists "Biro 1997 (decoupling)" as a study of the Dräger Fabius, but Biro's title names the Dräger Sulla 808V ventilator. The inclusion rule admits a machine on a study published 2006-2025, yet the "In because" column also lists Biro 1997 and Hendrickx 2001. Does Biro's study apply to the Fabius? Are the pre-2006 studies evidence for an axis rather than for inclusion?
- US presence: § "The machines surveyed" leaves out Mindray's A-series, Penlon and Spacelabs for lack of evidence of "their current US presence". The inclusion rule asks for a peer-reviewed study published 2006-2025 and an axis no other row covers, with no US condition. Is the survey limited to machines in US use? If so, the inclusion rule should say so. If not, the exclusion should give its reason in the rule's terms.
- Circuit component absorption: § "Ruled out" says it has been measured, and no entry in § "Sources" covers it. What is the source? A clinician checking the claim needs it.
- Inlet position and topology: the (b7) entry of § "What `PL-FG9D` needs: data, behavior, and what is neither" says both "measurably change" $`F_I/F_D`$. Fukuda et al. measured the effect of inlet position only, and § "(b7) Fresh gas inlet position" says Shin et al. inferred the effect of topology. The entry should cite Fukuda 2006 for the inlet and say that the topology effect is inferred.
- Tier 1: rule 1 under § "How a value gets into this document" names no tier. § "Sources" gives tier 1 to "measurements of quantities this model computes" and lists Kalmar et al. under tier 2, although § "(b4)" cites their measured agent consumption (6.0 to 7.3 mL over 45 min). Should rule 1 say that a cited measurement is tier 1, and which tier does Kalmar's consumption figure take?
- Biro 1997's tier: § "Sources" lists Biro under "Measurements of quantities this model computes (tier 1)". Biro measured minute volume with and without fresh gas decoupling, and § "(b5)" says that effect changes no simulated value, because ventilation is a patient setting in this model. Should the entry move to the device-description group? (Raised by the restructure's blind review, 2026-11-07.)

The structure read's other per-chapter queries are in the project's shared files, under `v0.7.0/repo-copy-edit/runs/docs-machine-survey-md/structure/chapter-*.txt`, on the lines that begin "Query". Most ask for a term to be explained where it is first used, or for a citation beside a value. Read each one against the restructured text: some no longer apply.

**Checked 2026-11-09:** after the restructure (`PL-3MTS`, done), a sample of the queries still applies to `docs/machine-survey.md`. "Choose option 1 or 2, and record the choice in the work item (`PL-FG9D`)" is still at row 623, though `docs/machine-abstraction.md` § "Fresh gas inlet position is not modelled" records that choice. "This is the only survey entry that affects an equation" is still at row 536. Rows 190 and 135 still name "the accuracy table" and "bucket" without saying where or what. § "(b2)" still gives the sevoflurane 8.0% and isoflurane 5.0% maxima with no source in the survey (the data files cite one, as a manufacturer specification). The Bashraheel, Jakobsson, Leijonhufvud and Zumsande entries still give no reading depth. One query no longer applies: `grep -n 'how far' docs/machine-survey.md` finds no sentence claiming every entry says how far its source was read. So the item still holds, and the session that works it reads each query against the current text.

**Why it matters.** A clinician or a contributor checks a stored machine value against this survey. An entry with no reading depth, a value with no source, or a choice the document asks for that was already made sends that reader to the wrong conclusion or to no source at all.

**Generator check.** One-off: queries from the `docs/machine-survey.md` copy edit and structure read (`PL-3K13`, `PL-3MTS`).

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** `git show 817a4d88:docs/machine-survey.md` already has "the one entry that reaches an equation" (row 545), "bucket" with no definition (row 134), "the accuracy table's default-flow" column with no location (row 189), "No machine publishes one" (row 596), and the Bashraheel entry with no reading depth (row 791). Some individual queries may concern wording added after the freeze; the item as a whole was present. So the problem was present at the freeze, commit `817a4d88` (2026-10-24), and this finding belongs on v0.7.0's frozen list rather than deferred.

## Done (2026-11-11)

Each query above, and each chapter query of the structure read, was read against the survey as it stood after `PL-KZ60`. The sources were read again where a fix rested on them: Shin et al. 2017 at full text (Tables 1-3, through NCBI efetch), and the abstracts of Fukuda et al. 2006, Targ et al. 1989, Bashraheel et al., Jakobsson et al., Leijonhufvud et al. and Zumsande et al. through the PubMed MCP server.

**The copy edit's queries, fixed in `docs/machine-survey.md`:**

- "Choose option 1 or 2" (Passages 37 and 42). The (b7) entry under § "What `PL-FG9D` needs" now points to `docs/machine-abstraction.md` § "Fresh gas inlet position is not modelled", which records the choice: leave inlet position and topology out, and say so where a machine is chosen.
- "The only survey entry that affects an equation" (Passages 34 and 42). (b11) now says that, like delivery mode (b3), it changes an equation rather than a parameter.
- "The accuracy table" (Passages 25 and 42). The phrase came from `PL-4DCG`'s brief, which called it "`docs/MODEL.md`'s accuracy table". No table in `docs/MODEL.md` now has a default-flow column, so (a2) now says what the default flow sets: $`\tau_C`$ at the start, and for the whole of a run in which the flow is not changed.
- "Bucket" (Passage 35). § "Ruled out" now says its lines are bucket (c), and that an item needing more than a line has its own entry under § "The variables".
- 300 mL/min (Passage 33). No source gave it as practice, and § "(a2)" says a study's chosen flow is not a report of practice. (b10) now uses Shin et al.'s own case: their 200 mL/min sample was 40% of their lowest flow, 0.5 L/min.
- The multi-gas module (Passage 33). Meyer et al. describe Dräger's ILCA, and they do not say which machine carries it, so (b10) names the module and no longer says that a surveyed machine has it.
- The absorption source (Passages 35 and 42, and the structure read). Targ, Yasuda and Eger 1989 is now cited and listed in § "Sources". Its abstract names bellows among the parts measured, so the line no longer calls the absorption a property of the disposable circuit alone, and it now gives its condition for coming back.
- Reading depth (Passages 40 and 42). Bashraheel, Jakobsson, Leijonhufvud and Zumsande now each say "Abstract read 2026-11-11", and each abstract confirms the machine the table names for it. The two ISO entries already say that neither standard was read.
- The "not critical" ruling (Passage 24). (a1) now says the project owner ruled on 2026-09-01, and that the reference circle system's data file records the ruling in its note on the Gas Man source (`PL-4YY1`).
- The 8.0% and 5.0% maxima (Passage 26). (b2) now points to `docs/MODEL.md` § "Delivery-limit and MAC parameters", which names the vaporizers behind each maximum, and to the agent data files. "The maximum belongs to the device, not to the agent" became "set by the delivery device, not by the agent alone", which no longer contradicts the sentence after it.
- "No machine publishes one" (Passage 37). The data table and (a2) now say that no source found gives a default fresh gas flow.
- Where the design is written (Passages 18 and 42). The introduction names `docs/machine-abstraction.md`.
- "Every run" (Passage 42). (a1) now says the difference shows in the first two minutes at the default 4 L/min.
- "This model's only machine parameter" (Passage 19). The headline now says that circuit volume is the only property of the machine in the circuit equation.
- The minimum total flow (Passage 31). The data table no longer lists it as a field of its own: it is the lower limit of the deliverable range, as (b8) says.

**The structure read's queries (`PL-3MTS`):**

- Shin et al.'s volumes. The headline now says that Shin et al. added the apparatus volume from Dräger's manual to their 1.2 L circuit and computed the time constant from the sum (their Table 3), that the apparatus volumes are tier 2, and what the times to target were (their Table 2).
- Fukuda et al.'s machines were named by `PL-KZ60`. The headline now also says that the abstract gives no fresh gas flow and no values of the ratio.
- The comparison table (`PL-WZVZ`) is defined at its first mention, in (b7).
- "This session" is now dated 2026-09-19 and names the survey's item, `PL-4DCG`.
- Biro 1997 studied the Dräger Sulla 808V, so it left the Fabius row. The rule now says that a study before 2006 is listed for the axis it shows and does not count toward inclusion, which covers Hendrickx 2001 in the GE row.
- US presence. `PL-4DCG`'s brief sets no US condition, so the exclusion of Mindray, Penlon and Spacelabs is now stated in the rule's terms: the survey cites no study of them.
- The (b7) entry now cites Fukuda et al. for the inlet, and says that no study here measured the effect of the rest of the topology.
- Tier 1. Rule 1 now names tier 1 and `docs/MODEL.md` § "Source hierarchy: what may be cited as the authority for a value". Kalmar et al. stay in the second group of § "Sources", whose heading no longer claims a tier: § "(a2)" cites them for the authors' conclusion, and § "(b4)" for consumption that rises with the speed setting, and neither backs a stored value.
- Biro's tier. Biro stays with the measurements. That group's heading no longer says "of quantities this model computes", so it fits Biro and Targ, whose measured quantities the model does not compute.

**The structure read's chapter queries.** Of those still standing after the restructure, these were fixed: the introduction's pointers to the machines and the source rules; one name for the machine milestone and its design; planned-milestone item 6 for the multi-substance state; a gloss of "interlock" and of "machine profile"; examples of data and of behavior; "a set of bounds"; Shin's third workstation and the size of the Perseus-Zeus difference; the rule now admitting a direct comparison as well as an axis, which the Apollo, Fabius and Avance rows needed; a pointer from the machines table to the sources of each axis; "Three routes"; the "gap" wording of rule 4; the bucket (b) definition; the ambient-pressure question, which `PL-5K5C` already settled by recording that the model holds at sea level; the FLOW-i named in (a2); the agent named in (b4); (b9)'s misfilling hazard tied to agent-specific filling, which is what it explains; "model selection" in (b9); one pair of names for the Zeus's two modes; the condition for each ruled-out line; a pointer from § "What `PL-FG9D` needs" to the variables' codes and sources; the machine profile named as the data file; $`\dot V_F`$ defined; the volume reflector, which no source read here describes, now said to be unknown; and the dates and group headings in § "Sources", including Candries et al.'s "reference implementation".

**Answered as not a defect.** No item tracks getting the manufacturers' data or the standards' texts, because the project owner decided on 2026-09-20 to seek each value only when a machine profile needs it, and § "What is missing" says so. Kern et al., Lerman and Correa, and Morimoto et al. are cited only in the machines table, and they are measurements, so they stay in that group.

**Filed and moved.** The 2006 start of the inclusion window has no recorded reason. The survey now says so, and `PL-VJNQ` holds it. Two of this item's Passage 42 queries concern `docs/machine-abstraction.md` and were missing from `PL-37N4`, so they were added there; the rest of Passage 42 is already in `PL-37N4`, or no longer applies ("Hendrickx et al. measured it for both device classes" is no longer in that file).

**After the blind review.** Both passes found that the survey had withdrawn "no machine publishes" a default fresh gas flow while `docs/MODEL.md` and the reference circle system's data file still say it; `PL-Z843` holds both copies, and the survey's paragraph on adopted claims now names it. Pass 1 found that (b3)'s opening still called the Zeus's fresh gas mode the equation the model already has, against Shin et al.'s times; the opening now says so.

**Not done.** The page in Meyer et al. for each quotation, which an outline query asked for and which is outside this item's list. The Meyer entry says that the page of each passage can be recovered from the corpus dump.
