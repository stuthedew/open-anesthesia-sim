---
id: PL-HS9M
title: The interface pass has no agreed order of work, first-pass learner or task list, and the design round's recommendations wait on the owner
status: untriaged
feature: interface-pass-design-round
added: 2026-11-11
---

**Problem.** The interface pass has no agreed order of work, first-pass learner or task list, and the design round's recommendations wait on the owner

**What the round was.** On 2026-11-10 the project owner said the interface's
look, theme, layout and colour scheme "seem like an afterthought or amateur
hour", and asked why it feels unpolished and what would make it look
professionally made. This is the design round that `ROADMAP.md`
planned-milestone item 33, the interface pass, places before its items. The
round changed nothing in the tree. This item holds what it found, what the
owner said, and the questions that are still open.

**What was measured.** The Default Workspace was rendered offscreen at 1600 by
1000 on `0.6.16+g0b1c8b65`, with sevoflurane at 2% after 300 s. The container
drew it with Qt's Fusion style and the Inter font, so the owner's Mac will
differ in both.

1. The two largest saturated regions on screen are the yellow agent selector
   and the yellow badge that holds the version and model name. They outweigh
   the readouts and the chart.
2. Start, Pause and Reset are three identical outlined buttons 25 px tall. The
   selector beside them is 27 px tall and the agent selector is taller again.
3. About 16 white rounded panels sit on one pale background, at 1.07:1 against
   it. Nothing separates the window's frame from its content.
4. Text starts at four left edges within 45 px of the window edge: 16, 30, 32
   and 45 px.
5. The concentration chart's heading and key take about 210 px of the Area's
   635 px before the plot begins. Each key entry names its dash in words
   beside a swatch that shows it.
6. The top tick label on both chart axes is cut off. `PL-571L` already holds
   this.
7. The four parameter sliders are 51, 85, 54 and 29 px wide, and each sits in
   its own panel inside the Parameters Area.
8. An Area draws no surface of its own. Its header is a separate strip, and the
   unused part of the Parameters Area shows the page background. `PL-4JCC`
   holds the size of that Area.
9. Seven text styles are on screen: the default size in regular and bold, 12 px
   regular and italic, 13 px, 14 px, and 22 px bold. Headings are the body size
   in bold. Readout digits are proportional, so a value's width changes as it
   updates.
10. `src/anesthesia_sim/app/main.py` sets neither the widget style nor the
    font, so each platform draws the unstyled parts its own way.

`PL-CXYV` holds one more finding: the run buttons do not change when pressed or
focused.

**Why it looks this way.** Each visual value was chosen to fix one defect.
No one has chosen the system that the values belong to: a type scale, a spacing
scale, a set of surfaces, and a set of controls with every state. The owner's
rule of 2026-10-18 makes look and placement placeholders until the interface
pass, and `src/anesthesia_sim/app/theme.py` calls six of its values
placeholders.

**Two mock-ups were shown, and neither was adopted.** Both were throwaway Qt
windows that reused the real chart, readout values, slider positions and trace
pens. The scripts are not in the repository. The owner has the pictures.

- The first used a grey window, white Areas with a hairline border, one
  teal accent and a 4 px grid. Type was 11, 13, 15 and 24 px in Inter with
  tabular digits. The readouts were one strip with each compartment's line
  sample beside its name. Each parameter was a full-width row. The agent was a
  small ISO-colour swatch with its name, and the version sat in a status line
  beside the disclaimer. The owner said: "mock ups a little better but still
  don't like it. I like their style", and linked the NCSA article below.
- The second followed that article's screenshots. It used a navy band across
  the top (`#16253A` to `#233F64`, sampled from the screenshots) that held the
  product name, the model and version, and the agent swatch. The page was
  white. Each Area was a card with a `#DFE2E7` hairline border, a `#F8F9FB`
  title strip and 4 px corners. Navy `#224063` was the one accent: a filled
  primary button, and outlined secondary buttons. The owner answered
  (2026-11-10): "I don't want a knee jerk reaction. Ok with mock ups in their
  style but I want us to learn to understand what makes good ui to inform our
  decisions as well (see paper)".

**What the paper says.** Arneson K, Fu L, Gatzke L. Toward More Usable,
Reproducible, and Sustainable Scientific Software: The Impact of User-Centered
Design in Research Software Development. PASC '25.
https://doi.org/10.1145/3732775.3733576. The owner supplied the PDF, and all
eleven pages and eight figures were read.

- Good interface design is a process, and the look comes late in it. Figure 1
  orders the design phase as information hierarchy, wireframing, prototyping,
  look-and-feel exploration, design system, then usability testing.
  High-fidelity mock-ups belong to the implementation phase. Both mock-ups
  above were made before any of the earlier steps.
- Discovery comes first: study the domain, interview users, and write the
  workflows down as task diagrams and user need statements.
- Usability has five parts, from Nielsen: learnability, efficiency,
  memorability, error recovery and satisfaction.
- The first release serves one user group and one core workflow.
- The figures show seven patterns:
  1. Restate the inputs beside the outputs (Figures 2 and 4).
  2. Put a headline answer above the detail (Figure 2, "Top Predictions").
  3. Reuse one encoding in every chart, table and card (Figures 2 and 4).
  4. Set labels small and grey, and values bold with small units (Figures 4
     and 6).
  5. Move secondary information behind hover (Figures 3 and 4).
  6. Give a term's definition on demand, marked by a dotted underline
     (Figure 7).
  7. Give each parameter a number field, a slider with its range printed at
     both ends, and a reset (Figure 8).
- Consistency comes from one design system. The team adopted an existing
  component library and added its own domain components, such as a standard
  molecule card.
- The evidence is case studies. The paper reports no task times, error rates or
  satisfaction scores, and the authors say their feedback came mainly from
  their own institute.

**Sources read on 2026-11-10.**

- Nielsen's ten usability heuristics, dated 1994:
  https://www.nngroup.com/articles/ten-usability-heuristics/
- Five test users find about 85% of problems on average, at a 31% detection
  rate per user, and the advice is three rounds of five:
  https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/
- Faulkner L. Beyond the five-user assumption. Behav Res Methods Instrum
  Comput. 2003;35(3):379-83. https://doi.org/10.3758/bf03195514. Random groups
  of five found between 55% and 99% of problems. With ten users the worst group
  found 80%.
- A heuristic evaluation wants three to five independent evaluators:
  https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/
- The System Usability Scale has ten questions, scores 0 to 100, averages 68,
  and needs "typically at least 20-30 users":
  https://www.nngroup.com/articles/measuring-perceived-usability/
- Zhang J, et al. Using usability heuristics to evaluate patient safety of
  medical devices. J Biomed Inform. 2003;36(1-2):23-30.
  https://doi.org/10.1016/s1532-0464(03)00060-1. Only the abstract was read, so
  its list of heuristics is still needed.
- Apple Human Interface Guidelines, Typography: macOS default 13 pt, minimum
  10 pt, and "Minimize the number of typefaces you use".
  https://developer.apple.com/design/human-interface-guidelines/typography
- The NCSA article and its screenshots:
  https://www.ncsa.illinois.edu/2025/08/26/designed-for-better-scientific-software/
- Not confirmed: the line recalled from Tufte's *The Visual Display of
  Quantitative Information* about labelling a chart directly. No source for it
  could be reached, so labels inside the plot are an option to test and not a
  recommendation.

**Recommendation (session, 2026-11-10, not yet answered by the owner).** Run
the paper's order here, and treat the NCSA look as the styling choice at the
fourth step.

1. Tasks. Name the first-pass learner and four or five things they do.
   `.claude/rules/ui-reader.md` names the reader as an anesthesia clinician
   with the resident as the teaching target. The project has no task list.
2. Heuristic evaluation of the current build against Nielsen's ten heuristics,
   task by task, with a severity for each finding. Use at least two independent
   evaluators: a session and the owner.
3. Wireframes of the Default Workspace's hierarchy for each task, with no
   colour or styling. Try patterns 1 to 7 above, each as a hypothesis.
4. One token set and one component set, including the domain components: a
   compartment readout, an agent chip, a parameter row and a reference mark.
5. Tests with residents in rounds of five, at least two rounds. Judge them by
   the tasks completed and the values misread. Collect the usability score as
   an impression only.

Candidate tasks, drawn from what the simulator already does:

1. Induction: set 8% sevoflurane at 6 L/min and say when the alveolar
   concentration reaches 1 MAC.
2. Fresh gas flow: compare wash-in at 1 L/min and at 6 L/min with the same dial
   setting.
3. Ventilation and cardiac output: show how changing each alters the rise of
   F_A/F_I.
4. Emergence: turn the vaporizer off after an hour and say when the alveolar
   concentration falls to MAC-awake, and what fat is doing.

**Questions for the owner.**

1. Is this order agreed?
2. Who is the first-pass learner, and which tasks are right? These decide what
   the simulator is for, so they are the owner's.
3. Can the owner supply the full text of Zhang et al. 2003? **Answered
   2026-11-10:** the owner supplied the AHRQ chapter below, which gives the
   heuristic list.

**What follows an answer.** Once the order and the tasks are agreed, file the
heuristic evaluation, the wireframes, the token and component set, and the
resident rounds as items in this feature. A headline answer such as the time to
reach 1 MAC would be a new computed value. It needs the owner's approval as a
feature, and `core/` would compute it.

**What the pass keeps.** `ROADMAP.md` planned-milestone item 33 lists the
constraints: the contrast minimums, the fixed ISO 5360 agent colours, dash
pattern as the channel that separates the traces, and no dark mode in this
pass.

**Related open items.** `PL-BVC5` holds how the controls are built. `PL-CXYV`
holds the buttons' missing pressed and focus states. `PL-571L` holds the cut-off
tick labels. `PL-4JCC`, `PL-9YPR` and `PL-CBYS` are the `window-is-the-frame`
feature, which decides the window's frame and so the surface that the
wireframes start from.


**Added 2026-11-10: the clinical heuristic set.** The owner supplied Zhang J,
Patel VL, Johnson TR, Chung P, Turley JP. Evaluating and predicting patient
safety for medical devices with integral information technology. In: Advances
in Patient Safety: From Research to Implementation, volume 2. Agency for
Healthcare Research and Quality; 2005.
https://www.ahrq.gov/sites/default/files/wysiwyg/professionals/quality-patient-safety/patient-safety-resources/resources/advances-in-patient-safety/vol2/Zhang.pdf.
Its section on heuristic evaluation was read in full. It supersedes Nielsen's
ten heuristics as the set to use in step 2 of the recommendation.

- The chapter gives 14 heuristics, built from Nielsen's ten and Shneiderman's
  eight rules "with a focus on medical devices": consistency and standards,
  visibility of system state, match between system and world, minimalist,
  minimize memory load, informative feedback, flexibility and efficiency, good
  error messages, prevent errors, clear closure, reversible actions, use users'
  language, users in control, and help and documentation.
- Each violation gets a severity from 0 to 4: 0 is not a usability problem, 1
  is cosmetic, 2 is minor, 3 is major and "important to fix", and 4 is a
  "usability catastrophe" that is "imperative to fix before product can be
  released".
- Evaluators work independently, their lists are merged into one, and each
  then rates every violation. The ratings are averaged.
- "Typically one evaluator can only catch 35 percent of the usability
  problems, but 3-5 evaluators can detect 60-75 percent."
- "Ideally, double experts trained in both usability and the target clinical
  domain should be the evaluators." The owner is the clinical expert here.
- Its stated limit: a heuristic evaluation does not show what an interface does
  well, and it does not reveal missing functions. The chapter's second method,
  an extended hierarchical task analysis, covers that gap, and it starts from
  the same task list that step 1 asks for.

**Added 2026-11-10: both supplied papers are in the private reference corpus.**
The owner asked for the two papers they supplied to be added to
`stuthedew/open-anesthesia-sim-references`. Zhang et al. 2005 (PMID 21249841,
pp. 323-36) and Arneson, Fu and Gatzke 2025 are there as PDFs with text
dumps. Each has an entry in the corpus's `README.md` with its verified
citation. `INDEX.md` there has a heading for interface design and usability
evaluation, whose rows give the page of each passage quoted above. A session
that runs the heuristic evaluation reads the chapter there.
