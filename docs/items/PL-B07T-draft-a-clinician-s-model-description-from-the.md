---
id: PL-B07T
title: Draft a clinician's model description from the paragraphs the reverse outline labels Model description, as a separate file for the owner to read before docs/MODEL.md changes
priority: P2
effort: M
status: done
classes: docs
feature: model-md-structure
milestone: v0.6.17
touches: docs/prose-review/model-description-draft.md, docs/prose-review/README.md, docs/items/PL-P3GZ-decide-whether-to-split-docs-model-md-by-reader.md
deferred-from: v0.7.0 - a draft document for the owner to read; the schematic release does not depend on it
added: 2026-11-10
closed: 2026-11-11
pr: 2092
payoff: the owner can judge a clinician's model description of about an eighth of today's length before anything in docs/MODEL.md moves
verify: grep -qE '^[*][*]The owner read the draft' docs/items/PL-B07T-*.md
---

**Problem.** Draft a clinician's model description from the paragraphs the reverse outline labels Model description, as a separate file for the owner to read before docs/MODEL.md changes

**Why it matters.** `docs/MODEL.md` has two readers, a clinician and a
developer, and the reverse outline of 2026-11-10 found that 23% of its words
serve the clinician and 13% belong in a description of the model. A clinician
who wants to know whether to trust a displayed value has to read past test
descriptions, interface requirements and decision history to find it. The
owner agreed on 2026-11-10 to see a clinician's model description as a
separate draft before anything in `docs/MODEL.md` moves (project owner,
2026-11-10, ratified, over deciding the split from the outline's totals
alone). A draft changes nothing that the code's citations of `docs/MODEL.md`
sections depend on.

**How to do it.** Do not edit `docs/MODEL.md`.

1. Read `docs/prose-review/model-reverse-outline.tsv`, which `PL-9RLM`'s
   brief describes. Take the units whose `best_home` is "model description"
   (16,792 words). Take each unit's text by its line range from
   `git show 50af1a2e:docs/MODEL.md`, the commit the outline describes.
2. Check the units whose `reader` is "clinician" and whose `best_home` is
   something else, because a label is one model's judgement. Take any that a
   clinician needs in order to trust or interpret a displayed value.
3. Order the draft for the clinician: what the model represents, its
   compartments and equations, each parameter with its value and source, the
   assumptions, and each limitation that could change what a clinician
   concludes from a displayed value.
4. State each fact once. Where two units give one fact, keep the clearer
   statement. Keep every unit, value, equation, condition, exception and
   citation. Set no word target, which the owner refused on 2026-11-04
   (`PL-J1ZM`).
5. List in this item each fact that the draft leaves out and the home it
   would go to, so that the owner can see what the draft costs.
6. Commit the draft as `docs/prose-review/model-description-draft.md` and
   send the file to the owner to read.

The copy editor does not run on the draft. The owner asked the Projects
trial's coordinator on 2026-11-10 to hold copy editor runs and within-section
restructuring of `docs/MODEL.md` until the split is decided.

**The draft, 2026-11-11.** `docs/prose-review/model-description-draft.md` is
about 14,300 words, counting table cells and equations. It has ten sections,
in the order of step 3: what the simulator is for, what the model represents,
units and symbols, assumptions, equations, parameters and sources, controls
and their limits, reading the display, the comparisons with measurements in
people, and limitations. `docs/MODEL.md` had not changed between `50af1a2e`
and the draft's commit.

*What it takes.* It takes the 236 units whose `best_home` is "model
description". It also takes the facts of most of the 124 units whose
`reader` is "clinician" under another `best_home`, because a clinician needs
them to trust or interpret a displayed value. The list of what it leaves out,
below, names the ones it does not take. The ones it takes are:

- the parameter table, the source tiers and the comparison of each stored
  value with the measurements beside it (labelled "parameter source
  register");
- the comparisons with published human data and their four caveats, the first
  25 minutes of wash-in, the first 24 hours of elimination, and Candries et
  al.'s study of Gas Man in patients (labelled "verification and validation
  report");
- the displayed precision of each readout (labelled "interface
  requirements").

It also takes three tables that the outline gives a developer and that a
taken paragraph points at: the six time constants (`U0204`), the fitted
fourth-compartment time constants (`U1625`) and the circuit materials'
partition coefficients (`U1603`). It takes the two closed-circuit points of
`U0181`, because `U0180` ends "Two other things change."

*How it uses the structure findings of `PL-YKKC`.* Each heading names what
its section holds. "Known limitations" has thirteen titled subsections where
`docs/MODEL.md` has a 41-item list and untitled essays. The draft states once
each fact that `PL-YKKC` counted several times: the closed circuit (§ 10.3),
$`F_a \equiv F_A`$ (§ 2), and trunk, branch and fork (§ 8.6). It defines each
term before it uses it.

*What it leaves out, and the home each would go to.*

1. The symbol table's Code column, and every code name in a taken paragraph
   (`AgentUptakeSystem.for_agent()`, `SimulationController`, `mac_percent`).
   Home: docstrings in the code.
2. The data file and key path of each stored value, and the hidden
   `provenance`, `derived` and `not-restated` markers. Home: the parameter
   source register. The draft is therefore not checked against the data
   files, and a stored value that changes will not fail a check there.
3. The numerical envelope of the two gas volumes, 0.01 to 10 000 L (`U0760`),
   and the sentence that an automatic check keeps the model's code from
   reading the clock (`U0068`). Home: the verification and validation report.
4. How each test works: the test that reads the default flows at run time
   (`U1434`), the 3.5 to 4.2 SD shift that a test requires (`U1442`), the
   test names in `U1627` and `U1556`, and the sentence that a test reruns the
   3-hour sevoflurane washout (`U0987`). The draft keeps each result. Home:
   the verification and validation report.
5. The table of control timing by playback rate (`U0340`) and its reading
   notes. The draft keeps the ratios of `U0346`. Home: the verification and
   validation report.
6. Which wash-in points set which limit of the published-data comparison
   (`U1525`, first, second and fourth bullets in part). The draft keeps what
   the comparison detects. Home: the verification and validation report.
7. Decision history: the dates on which values were adopted, the owner's
   rulings on the 6.0 L circuit and the 4.0 L/min default (`U0509`), why
   Mapleson's MAC was not adopted (`U0568`), why a non-rebreathing mode was
   not built (`U1440`), and every item id. Home: the item record.
8. Planned work: `ROADMAP.md` items 30 and 31, and the sentences saying that
   circuit absorption and a fourth compartment are not planned (`U1605`,
   `U1642`, `U1615`, `U0460`). Home: `ROADMAP.md`.
9. Source detail behind a value the draft does keep: Davis and Mapleson's
   blood volume, cardiac output and arterial pool, and the `GASMAN.INI`
   listing (`U0499`); Yasuda's heart, liver and kidney coefficients and their
   mean (`U0546`); Katoh's equation 1 and the flows and volumes of Katoh's
   brain model (`U0992`, `U0994`); the mean ages and awakening concentrations
   of Katoh's patients (`U1006`); the four fitted fourth-compartment
   amplitudes (`U1556`); the examples under each source tier (`U0441`,
   `U0445`); and the note on how each source was read. Home: the parameter
   source register.
10. Interface rules that do not change what a value means: where the readout
    row sits (`U1142`), how the MAC-awake band is drawn (`U0984`), the
    bookmarks a branch inherits (`U0793`), the agent-accounting panel's
    residual lines (`U1172`), and the schematic's fill heights (`U1327`). The
    draft keeps the fact that a compartment's concentration is not its
    amount. Home: the interface requirements.
11. The halt that can stop one or two display counts past a mark (`U0590`).
    Home: the interface requirements.
12. The purpose list's two entries on identical results and conservation of
    mass, which § 5.7 and § 5.9 of the draft state instead (`U0014`).

*One gap the owner should know of.* `docs/MODEL.md` cites about twenty
sources by author and year only, among them Mapleson 1996, Katoh 1993,
Chortkoff 1995, De Wolf 2012, Weber 2021, Esper 2015 and Cattermole. Their
full citations are in the data files' `sources` entries. The draft cites them
the same way and has no reference list. A model description that stands alone
would need one.

The copy editor did not run on the draft, as the brief says.

**Decision needed.** Is `docs/prose-review/model-description-draft.md` the
document a clinician should get? The owner decides, because the answer sets
what a clinician reads before trusting a displayed value, and `PL-P3GZ`
(decide whether to split `docs/MODEL.md` by reader) takes it.

**Recommendation (session, 2026-11-11):** yes to its contents and order, with
one addition before it could stand alone, a reference list with each source's
full citation. A clinician can read the draft from start to finish without
meeting a test, a code name or an item id, and every limitation has a heading
they can find. Its cost is the list above: the draft is checked against
nothing, so it would need the stored-value markers back before it replaced
any part of `docs/MODEL.md`.

**The owner read the draft** and answered on 2026-11-11: "Yes with
references" (project owner, 2026-11-11, ratified, over leaving the draft with
author-and-year citations and no list). The draft is the document a clinician
should get, in its contents and order, once it carries a reference list. The
owner also asked how to deal with the three weaknesses the session had named:
no reference list, numbers that nothing checks, and two sentences written from
the outline's summary and not from the paragraph.

**What changed after the verdict, 2026-11-11.**

1. *Reference list.* The draft now ends with § "References", 47 entries, and
   its text cites by author and year. Each citation is copied from
   `docs/MODEL.md`, `docs/machine-survey.md` or a `sources` entry under
   `src/anesthesia_sim/data/`. One is not: `docs/MODEL.md` gives the paper
   "Do distribution volumes and clearances relate to tissue volumes and blood
   flows?" by title and address only, and its authors, year and volume
   (Hendrickx, Lemmens and Shafer, *BMC Anesthesiol* 2006;6:7) come from its
   PubMed record, PMID 16772041, metadata and abstract read 2026-11-11.
2. *The two sentences.* § 3's statement about the 37 °C stores and the opening
   of § 10.8 on the fat group's blood flow are rewritten from the paragraphs
   of `docs/MODEL.md` they summarise ("One reference condition, where the
   model physically has two", and "The fat group's flow is twice a resting
   depot measurement"). Both of the earlier sentences were true. § 10.8 now
   gives the figures behind "about twice": 2.07 mL per 100 mL per minute
   stored, the fits' 2.1 to 2.4 as published and 2.3 to 2.6 at the model's
   solubilities.
3. *Seven wrong section pointers.* Sections 4, 6.3, 7.3 and 9.6 pointed at
   "§ 9.x" for limitations that are in § 10. Each now names the right section.
4. *The numbers, checked once.* A script compared every number in the draft
   with every number in `docs/MODEL.md` at `50af1a2e`. All are there. Five are
   written differently: `docs/MODEL.md` gives the effect of one standard
   deviation of a partition coefficient as 8.7×10⁻⁴ to 6.8×10⁻² percentage
   points, and the draft writes the same values as decimals. The comparison
   cannot tell that a number sits beside the right quantity, so it finds a
   mistyped value and not a misplaced one. It was a single run and no check
   repeats it.
5. *The tables, checked once.* A second script took each of the draft's 62
   table rows that hold two or more numbers. For 53 of them, `docs/MODEL.md`
   holds the same numbers together, in one table row or within twelve lines.
   The other nine are rows of two tables the draft rearranges. The agent
   table in § 6.2 matches the three agent data files value for value, and the
   elimination table in § 9.3 matches the two tables of `docs/MODEL.md` it
   joins. Running prose is not covered: a correct number beside the wrong
   quantity in a sentence would pass both scripts.

The draft is now about 15,500 words, of which the reference list is about
1,250.

**What `PL-P3GZ` takes from this.** The owner accepts this draft as the
clinician's document. Two things still stand between it and replacing any
part of `docs/MODEL.md`:

- *Nothing ties its values to the data files.* `tools/doc_check.py` checks
  the stored-value markers only in the documents that its
  `PROVENANCE_DOCUMENTS` names, which are `docs/MODEL.md` and `README.md`. A
  clinician's document that stands as specification needs its markers back
  and its path in that list, so that a stored value that changes fails the
  check there as it does in `docs/MODEL.md` today.
- *A value could sit beside the wrong quantity.* The one-off comparison above
  does not catch that. The markers do, for the 49 stored values. For the
  rest, the owner's read of the parameter tables and the validation tables
  (§ 6, § 9) is the check.

**Done when.** The owner has read the draft, and this item records in a
paragraph that opens "**The owner read the draft**" whether it is the
document a clinician should get. `PL-P3GZ` (decide whether to split
`docs/MODEL.md` by reader) then takes that answer.

**Generator check.** Work the owner asked for.
