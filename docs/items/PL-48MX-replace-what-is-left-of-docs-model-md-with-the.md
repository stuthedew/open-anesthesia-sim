---
id: PL-48MX
title: Replace what is left of docs/MODEL.md with the clinician's model description the owner accepted, brought up to date and carrying its stored-value markers (stage 2 of the split PL-P3GZ decided)
priority: P1
owner-priority: P1, 2026-11-11, ratified
effort: L
status: done
classes: docs
feature: model-md-structure
touches: docs/, tools/, src/anesthesia_sim/, tests/, .claude/rules/, README.md, ROADMAP.md
blocked-by: PL-FWR6
added: 2026-11-11
closed: 2026-11-22
pr: 2222
payoff: a clinician who opens docs/MODEL.md reads the description of the model, its values and its limits, and nothing written for a developer
verify: grep -qF '## How this document is held to the tree' docs/VERIFICATION.md
---

**Problem.** Replace what is left of docs/MODEL.md with the clinician's model description the owner accepted, brought up to date and carrying its stored-value markers (stage 2 of the split PL-P3GZ decided)

**Why it matters.** The project owner read
`docs/prose-review/model-description-draft.md` on 2026-11-11 and accepted it
as the document a clinician should get (`PL-B07T`), then decided to split
`docs/MODEL.md` by reader (`PL-P3GZ`). After the three moves of stage 1
about 24,000 words remain in `docs/MODEL.md`: the status, purpose and
intended use, the model boundary, assumptions, conventions, symbols, tissue
groups, compartment capacities, governing equations and known limitations,
and the section on how the document is checked. The draft states the same
model in about 15,500 words for a clinician. While both exist, nothing
checks the draft, and a change to the model would have to edit both.
<!-- absent: docs/prose-review/model-description-draft.md -->

**What to do.**

1. Bring the draft up to date. It was written from `docs/MODEL.md` at
   `50af1a2e`. Apply to it every change `docs/MODEL.md` has taken since
   (`git log 50af1a2e.. -- docs/MODEL.md`, and the three documents that
   stage 1 moved text into).
2. Put the stored-value markers back in the draft, and add its path to the
   documents that `tools/doc_check.py` checks them in. `PL-B07T` § "What
   `PL-P3GZ` takes from this" names both, and the values that the draft
   states beside a different quantity.
3. Place each fact that `PL-B07T` lists as left out in the home it names:
   one of the three developer documents, a docstring or test, the item that
   took the decision, or `ROADMAP.md`. Cut a fact only after confirming that
   its home holds it, and record each cut in this item.
4. Make the draft `docs/MODEL.md`, and delete
   `docs/prose-review/model-description-draft.md` and its entry in
   `docs/prose-review/README.md`.
   <!-- absent: docs/prose-review/model-description-draft.md -->
5. In `.claude/rules/plain-writing.md`, leave `docs/MODEL.md` one reader, a
   clinician or educator, and remove the paragraph that keeps developer
   detail in notes opening "**For developers.**" (`PL-W8FL`), because the
   document then has no such notes. In `CLAUDE.md`, say which document is
   the home of which part of the specification.
6. Ask the owner to read only what differs from the draft they accepted,
   quoted before and after.

**What it must not do.** Change no value, unit, equation, condition or
citation except to bring it up to date with the tree. Set no word target
(`PL-J1ZM`).

**Done when.** `docs/MODEL.md` is the accepted description, up to date with
the tree and carrying its stored-value markers; the draft file is gone;
every fact of the replaced text is in `docs/MODEL.md`, in its named home, or
recorded here as cut; the owner has read the differences; and `make check`
passes.

**Generator check.** Part of the fix for the cause that `PL-P3GZ` records:
the repository named no home but `docs/MODEL.md` for a test's description,
an interface requirement or a value's source history, so each change added
them there. No new head.

**Two fact fixes landed in `docs/MODEL.md` after the draft was written, and the
draft still carries one of them (2026-11-14).** `PL-2BG1` and `PL-G0R3` merged
together, and step 1's `git log` picks both up. Neither is a restructure.

1. `PL-2BG1`: the stored MAC is a single adult value whose source, De Wolf et
   al. 2012, states no age for it. `docs/MODEL.md` no longer calls it "1 MAC
   for a 40-year-old adult" or "at age 40", and its 22% comparison is now
   against Mapleson's confidence limits only. The draft still has the old
   wording in four places: the symbol row for $`\mathrm{MAC}_\%`$ ("at age
   40"), the parameter table row "1 MAC, 40-year-old adult (percent)", the
   paragraph that opens "**MAC.** The stored MAC is 1 MAC for a 40-year-old
   adult", and the 22% paragraph's "That is larger than either source's
   confidence limits, so by the primary literature", which `docs/MODEL.md`
   now gives as Mapleson's confidence limits and "by Mapleson's meta-analysis".
   Change all four when the draft is brought up to date. The draft has no
   "band drawn for age 40": its MAC-awake band paragraph already compares
   only with Mapleson's and Katoh's age-40 figures. Checked again on
   2026-11-14 with a search for "40", "forty", "either source" and "primary
   literature". The sentence that compares the
   stored MAC with Katoh's MAC "at age 40" is a comparison and stays.
2. `PL-G0R3`: `docs/MODEL.md` now says "simulated", "computed" or "come from
   runs on" where it reported a result of this simulator, and keeps
   "measured" for patients, tissue and equipment. The draft's own uses of
   "measured" were read on 2026-11-14 and all describe real measurements. One
   use of the verb does not: "This comparison measures an omission and claims
   no agreement", which `docs/VERIFICATION.md` now words as "shows an omission".

**Checked 2026-11-22** against `d4e8200`: still applies, and step 1 has grown. `docs/prose-review/model-description-draft.md` is still a separate draft, and `docs/MODEL.md` still holds the developer sections. Its one blocker, `PL-FWR6` (the parameter move), is still open and still blocked, so nothing about the order has changed. Since the note of 2026-11-14, `docs/MODEL.md` has taken 14 more commits that step 1 must carry into the draft. The largest are #2183 (62 statements the code contradicted, corrected), #2180 (a run now steps in whole seconds, and every shown value is read from stored states) and #2121 (the rounding bounds in `core/rounding.py`). #2181 (the interface documents corrected) also changed two lines of the draft, so the draft is no longer exactly as written at `50af1a2e`.
<!-- absent: docs/prose-review/model-description-draft.md -->

**Built 2026-11-22**, on a branch that starts from `PL-FWR6`'s. The draft is
now `docs/MODEL.md`, brought up to date with the tree.

*Choices made while building.* These are wording and placement, decided as
placeholders:

1. Headings carry no numbers, and a reference names a heading in quotes, as
   `§ "Altitude"`. A number would change each time a section is added.
2. The draft's § 10, "Limitations that can change what a displayed value
   means", is titled "Known limitations", and opens with the sentence "Each
   limitation in this section can change what a displayed value means." The
   code, the tests and the rules cite § "Known limitations".
3. The draft's § 8.1, "Concentrations", is titled "Reading a concentration".
   `docs/VERIFICATION.md` § "Concentrations" holds the conventions for
   developers, and two sections with one title would make a citation
   ambiguous.

*Where the developer text went.*

1. The conventions, the symbol table with its code column, the notes for
   developers and § "How this document is held to the tree" went to
   `docs/VERIFICATION.md`, under "Notes for developers on the model
   description" and "How this document is held to the tree".
2. § "Agent amount", the evidence behind the known limitations, the
   provenance table and the format of a `sources` entry went to
   `docs/PARAMETERS.md`.
3. `tests/reference/test_known_limitations_figures.py` and the bound family in
   `tools/doc_check.py` now read `docs/PARAMETERS.md` § "The evidence behind
   the known limitations", because `docs/MODEL.md` names no test. The test
   reads both documents and requires every copy of a figure to agree. Two
   other routes were refused. Comments naming the tests, hidden in
   `docs/MODEL.md`, would be a new mechanism while a generator is live.
   Dropping the family would lose the tie from each figure to its test.

*Stored-value markers.* 62 blocks of the draft carry a marker again, each
matched to the markers that the replaced text carried for the same figures.

*Code.* The three refusals in `core/validation.py` of an agent amount that does
not fit a compartment's capacity cited a section that each caller passed. The
replaced sections are now one, "How much agent each compartment holds", so the
argument is gone and the section is the constant `CAPACITY_SECTION`. The
refusal of a circuit volume cited "Breathing circuit" before. It now cites the
capacity section, which defines $`M_C = V_C F_I`$.

*Facts compared.* `python3 tools/model_rewrite.py lost` against `74da8b79`
listed 88 equations, code spans, citations and numbers held fewer times than
before. Each was searched for in the four specification documents, with
spacing ignored. Each is still stated at least once, except three:

1. Three `derived` markers for the 15.8 s time constant were missing. They are
   restored under the table of time constants.
2. Desflurane's five-minute elimination ratio with the circuit removed is
   0.0934, where the replaced text gave 0.0935. 0.0934 is the result with
   whole-second steps (#2180), and
   `tests/reference/test_published_wash_in_and_elimination.py` holds it.
3. The PubMed Central address of Hendrickx, Lemmens and Shafer (2006) is
   replaced by the paper's full reference in § "References".

*The draft's twelve left-out facts* (`PL-B07T`). Each was found in the home
that `PL-B07T` names, except the sentence that absorption by the circuit's
walls is not planned. That sentence is now in `ROADMAP.md` § "Planned
milestones".


*Step 5's second half.* `CLAUDE.md` § "Safety-critical clinical-output
standard" already names the home of each part of the specification, from the
three moves: the model in `docs/MODEL.md`, the method, tests and hazards in
`docs/VERIFICATION.md`, each stored value's source in `docs/PARAMETERS.md`, and
the interface in `docs/INTERFACE.md`. Nothing was added there.

*Items this unblocks.* `PL-N83Z`, `PL-4H8Q`, `PL-SY7G` (the three sorting
items) and `PL-XLDN` (the pointer to the second sourcing rule) move to ready.
`PL-1VXY` and `PL-YKKC` now wait on the three sorting items, which apply
their findings document by document.

*Blind review, two passes.* Each finding and what was done:

1. The control-delay paragraph said a one-second-late control change moves a
   reading less than one SD of any coefficient. The table beside it shows the
   vessel-rich and fat shifts are smaller than the timing error. The paragraph
   now states the comparison as the numbers give it. `docs/VERIFICATION.md`
   has the same two wrong sentences, and `PL-3MMJ` corrects them.
2. The precision table gave one row for every agent amount. It now gives the
   run totals, a compartment's amount in the schematic and the cost view's
   totals as three rows, each at the precision the code formats.
3. About 84 citations in 21 files still named a section that moved. Each now
   names the section that holds the text. Pass 2 named this again.
4. The test of the known-limitation figures did not compare its two copies.
   Three of its patterns now match both, so a copy that changes alone fails.
5. The "common gas outlet" line under the fresh gas flow control lost its
   stated reason with the replaced text. `docs/INTERFACE.md` § "Minimum
   displayed outputs" now states it, and `docs/MODEL.md` § "Breathing
   circuit" says why the label is worded so. The same review found that no
   specification states the circuit readout's "inspired" line, and
   `PL-NMZS` records that.
6. Passages in `docs/PARAMETERS.md` § "The evidence behind the known
   limitations" still read as the end of a section they no longer follow.
   Their opening sentences now name what they are about. The subheadings
   that section needs are part of `PL-N83Z`, which sorts that document.

*Step 6, decided 2026-11-22.* What differs from the draft the owner accepted
is of three kinds:

1. Facts that `docs/MODEL.md` took from the 21 commits merged after the draft
   was written, which step 1 carried in. Examples are the stored MAC as one
   adult value with no stated age (`PL-2BG1`), whole-second steps (#2180) and
   the rounding bounds (#2121). Each merged after its own review.
2. The three heading choices listed above.
3. The corrections the blind reviews found, listed above.

One of these changes what a stated limitation tells a learner. The draft's
§ 7.2 said a control change was timed to a tenth of a second, and that only an
abrupt ventilator start moved a reading more than one standard deviation of a
coefficient does. With whole-second steps, an ordinary control change moves a
displayed concentration by up to 0.066 percentage points for desflurane. That
is more than one standard deviation of the vessel-rich or fat coefficient
moves one, and less than one of the blood:gas or muscle coefficient. The
owner is asked about that paragraph alone, quoted before and after. The rest
is not put to the owner, who said on 2026-11-02 that a reply cannot let them
re-check a rewording that reviews already checked (`PL-BGN1`), and on
2026-11-22 asked threads to put to them only what needs a clinician.

*The owner's answer, 2026-11-22.* The owner answered "do best practice
approach", then "research best practice approach". The control-delay
paragraph keeps the comparison with each coefficient's spread (project owner,
2026-11-22, ratified, over giving the timing figures alone). ASME V&V 20-2009
splits a simulation's error into the model's error, the numerical error and the
error from uncertain inputs, estimates each separately, and combines the
numerical and input uncertainties into one validation uncertainty. This was
read in NIST's summary of the standard, NISTIR 8298 (Yeo 2020, pp. 13-15),
because only the standard's contents pages could be fetched. The National
Research Council's *Assessing the Reliability of Complex Models* (2012,
chapter 5, § 5.1) says a solution error that could matter to a prediction
"must also be captured in some way". A timing error stated without the input
uncertainty beside it gives a reader half of that budget.
