---
id: PL-HWZK
title: Adopt the lessons from the owner's machine-control dashboard project that he approved on 2026-11-27: closest analog first, sourced look and wording, error messages that say what to do next, and four interface-pass method changes
priority: P2
effort: S
status: done
classes: docs, ux
touches: .claude/rules/instruction-writing.md, .claude/rules/expert-review.md, .claude/rules/sources-and-docstrings.md
added: 2026-11-27
closed: 2026-11-27
pr: 2330
payoff: sessions choose look and wording from cited sources, error messages say what to do next, and the interface pass starts from user stories the owner corrected
verify: grep -qF 'they are decided from a source' .claude/rules/instruction-writing.md
---

**Problem.** Adopt the lessons from the owner's machine-control dashboard project that he approved on 2026-11-27: closest analog first, sourced look and wording, error messages that say what to do next, and four interface-pass method changes

**Where this comes from.** On 2026-11-27 the owner pasted 43 UI and UX
lessons, and then a 44th, from another of his projects: the control dashboard
for a hobby robot. He asked what this project could use. The thread compared
each lesson with the rules, `docs/INTERFACE.md`, `docs/interface-provenance.md`
and the interface-pass items, read the source behind each lesson it
recommended, and put seven adoptions and one rule change to him. He answered
"Agree with all rec" and "Implement all of this in this session" (project
owner, 2026-11-27, ratified, over leaving the lessons unrecorded).

**What was adopted, and where.**

1. Search the closest analog first: same quantity or signal, then the same
   class of product, then the same pattern of use. This is the owner's own
   rule from the other project, with no published source. It goes in
   `.claude/rules/expert-review.md`.
2. Look, wording and placement are decided from a cited source. When no
   source settles a choice, the session says what it searched and asks. This
   replaces the placeholder clause of rule 14 in
   `.claude/rules/instruction-writing.md`, which said "Decide one yourself"
   (owner's rule of 2026-11-27, "You don't make choices. Look up best
   practice.").
3. A refusal says what to do next. NUREG-0700 Rev. 3 (O'Hara, Brookhaven
   National Laboratory, July 2020; full text from
   https://www.osti.gov/servlets/purl/1644018), guideline 2.7.3-1: "an error
   message should state the error and possible subsequent operations." Siemens
   iX, error messages
   (https://ix.siemens.io/docs/guidelines/language/messaging/error-messages):
   "Explain how users can move forward, resolve issues, or take action". It
   goes in `.claude/rules/sources-and-docstrings.md`.
4. Interview the owner with a prototype in hand. This is the owner's rule. It
   goes in `PL-TJM4`, the user-story step.
5. Write user stories before any screen, each with a check that shows the
   need is met. Mountain Goat Software
   (https://www.mountaingoatsoftware.com/agile/user-stories) gives the form "As
   a [type of user], I [need/want/am required] to [do something], so that
   [reason or benefit]". Gibbons, NN/g, 2019
   (https://www.nngroup.com/articles/user-need-statements/): the need "should
   not be phrased as a solution", and "Stay away from features, interface
   components, and specific technology." Jeffries, 2001
   (https://ronjeffries.com/xprog/articles/expcardconversationconfirmation/), on
   the confirmation: "This component is the acceptance test." It is `PL-TJM4`.
6. Ask residents to think aloud. Nielsen, NN/g, 2012
   (https://www.nngroup.com/articles/thinking-aloud-the-1-usability-tool/): "ask
   test participants to use the system while continuously thinking out loud".
   It goes in `PL-DSXJ`.
7. Walk the owner through a clickable mock-up built from the real components
   before the resident rounds, and keep the layout open until then. Whitenton
   and Gibbons, NN/g, 2018
   (https://www.nngroup.com/articles/case-study-iterative-design-prototyping/):
   users "said they liked this grid", and "people unanimously gravitated
   towards the list version" once both were shown as visual designs. It goes in
   `PL-MF90`.
8. Two entries for the design language. Labels are nouns of 1 to 3 words in
   sentence case, from Siemens iX, form-field labels
   (https://ix.siemens.io/docs/guidelines/language/forms-and-form-fields/form-field-labels):
   "Use short labels, ideally 1-3 words", "Use nouns, not verbs", and "Use
   sentence casing for all labels". Every control is either a setting or an
   action, the owner's rule. They go in `PL-9WDN`.

All sources were read on 2026-11-27. The NN/g, Siemens iX, Mountain Goat and
Jeffries pages were read through a fetch tool that returns the page's text.
Five NUREG-0700 guidelines were read in the full PDF: 1.2.1-6, 1.3.3-2,
2.7.3-1, 2.7.5-1 and 2.7.6-9. The ISO 9241-210 extract that the lessons cite
was not read, and nothing here rests on it.

**What was already followed, and needed no change.** The agreed order of work
(`PL-HS9M`) matches lesson 8. Grey for normal states (ISA-101) is already the
first rule of the `PL-9WDN` draft. The unconditional values sit in a fixed
region (`PL-NWTM`). A halt leaves the run paused until the user resumes it.
Discarding a run asks first, and removing a mark offers Undo. The wording rules
in `.claude/rules/ui-reader.md` and `.claude/rules/plain-writing.md` cover the
lessons on screen text.

**What does not fit.** A settings gear is wrong for a Mac app. Apple's Human
Interface Guidelines, Settings, say "Include a settings item in the App menu",
opened with Command-Comma, and "Avoid adding settings buttons to a window's
toolbar". The button colours under IEC 60073, the PackML state names and the
emergency stop are for physical machines. Setting layers and editable profiles
fit scenario save and load (`ROADMAP.md` planned-milestone item 9).
Keyboard access to the hover readout and the run controls is planned-milestone
item 20. Rendering at a device pixel ratio of 2 has no published source and is
`PL-QCFC`.

**Why it matters.** The interface pass is about to turn placeholder looks into
permanent rules, so those rules should rest on sources. Its order of work began
from tasks written for a learner, a framing the owner retired on 2026-11-27.

**Done when.** The three rule files carry the changes above, `PL-TJM4` and
`PL-QCFC` are filed, and `PL-8Q1P`, `PL-DSXJ`, `PL-MF90`, `PL-9WDN` and
`PL-2V6V` carry what each adoption gives them.

**Generator check.** One-off: the owner asked for these lessons to be adopted, and no earlier item records the same gap.

**Done 2026-11-27.** Rule 14's placeholder clause now says to decide look,
wording and placement from a cited source and to ask where none settles it.
The coordinator's line on styling calls says the same. Docs swept for another
live copy of the old rule: `CLAUDE.md`, `docs/maintainer.md`, `docs/worker.md`,
every `.claude/skills/*/SKILL.md`, every file in
`.claude/skills/docket/modes/` and every file in `.claude/rules/`. The only
other copy is the dated history in `docs/resident-instructions.md` § "The sort
of 2026-11-21, and the history it moved here", which is a record and was left
as written. `PL-VT87` checks the existing refusal messages against the new
error-message rule.
