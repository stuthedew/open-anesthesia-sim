---
id: PL-8Q1P
title: Run the heuristic evaluation of the current interface: four learner tasks against the 14 heuristics in Zhang et al. 2005, by a session and by the owner independently
priority: P3
effort: M
status: blocked
classes: planning, ux
feature: interface-pass-design-round
blocked-by: PL-4JCC, PL-9YPR, PL-CBYS
added: 2026-11-11
payoff: the interface pass starts from a ranked list of what stops a resident completing the four tasks, rather than from taste
not-delegable: the owner is one of the two evaluators
---

**Problem.** Run the heuristic evaluation of the current interface: four learner tasks against the 14 heuristics in Zhang et al. 2005, by a session and by the owner independently

**Where this comes from.** `PL-HS9M` is the design round's record. The owner
agreed its order of work on 2026-11-10, and this is the second step. The
first step is settled: the learner is a resident early in training who works
through a case alone, and the tasks are:

1. Induction: set 8% sevoflurane at 6 L/min and say when the alveolar
   concentration reaches 1 MAC.
2. Fresh gas flow: compare wash-in at 1 L/min and at 6 L/min with the same dial
   setting.
3. Ventilation and cardiac output: show how changing each alters the rise of
   F_A/F_I.
4. Emergence: turn the vaporizer off after an hour and say when the alveolar
   concentration falls to MAC-awake, and what fat is doing.

**The method.** Zhang J, Patel VL, Johnson TR, Chung P, Turley JP. Evaluating
and Predicting Patient Safety for Medical Devices with Integral Information
Technology. In: Advances in Patient Safety, vol. 2. AHRQ; 2005. pp. 323-36.
PMID 21249841. The full text is in the private reference corpus, and pp.
327-28 were re-read on 2026-11-10.

- The 14 heuristics, by the chapter's short names: Consistency, Visibility,
  Match, Minimalist, Memory, Feedback, Flexibility, Message, Error, Closure,
  Undo, Language, Control, Document.
- Each violation gets a severity from 0 to 4. 0 is "Not a usability problem
  at all", 1 is a "Cosmetic problem only", 2 is a "Minor usability problem",
  3 is a "Major usability problem", and 4 is a "Usability catastrophe.
  Imperative to fix before product can be released."
- Evaluators work independently. Their lists are merged into one, each
  evaluator rates every violation on it, and the ratings are averaged.
- "Typically one evaluator can only catch 35 percent of the usability
  problems, but 3-5 evaluators can detect 60-75 percent."

**What to do.**

1. Run the application as the run-the-app skill says, and walk each task on
   the current build. For each violation record the task, what was seen, the
   heuristic and a severity.
2. The owner does the same on their Mac, before reading the session's list.
   The tasks are above, and the heuristics and the scale are in "What each
   heuristic asks" below.
3. Merge the two lists, collect both ratings for every violation, and
   average them.
4. Record the merged list in this item, sorted by severity. File each
   violation rated 3 or higher as an item, or name the open item that already
   holds it. `PL-CXYV`, `PL-571L`, `PL-4JCC`, `PL-9YPR` and `PL-CBYS` hold
   some already.

**Which build to evaluate (the session's decision, 2026-11-10).** Both
evaluators walk the same commit of `main`, taken after the three open items
of the `window-is-the-frame` feature have merged: `PL-4JCC`, `PL-9YPR` and
`PL-CBYS`. Those items change where every panel sits and remove the page
scroll, and another session was building them on 2026-11-10. Findings about
layout made on the build before them would describe a screen that no longer
exists. Record the commit in this item beside the merged list. The owner can
overrule this and evaluate today's build.

**What each heuristic asks.** These are one-line paraphrases of the chapter's
definitions on pp. 327-28, for the owner's independent pass.

1. Consistency: the same word, mark or action means the same thing
   everywhere, and conventions are followed.
2. Visibility: the screen always shows what state the simulation is in.
3. Match: what the screen shows fits the model the learner already holds.
4. Minimalist: nothing on screen that the task does not need.
5. Memory: the learner does not have to remember a value from one place to
   use it in another.
6. Feedback: each action gets a prompt, informative response.
7. Flexibility: shortcuts and customization exist for the practiced user.
8. Message: an error message says what went wrong and how to recover.
9. Error: the design prevents the mistake instead of reporting it.
10. Closure: the learner is told when a task has finished.
11. Undo: an action can be reversed.
12. Language: the words are the learner's own.
13. Control: the learner, not the program, decides what happens next.
14. Document: help is available where it is needed.

For each violation, note four things: the task, what was seen, the heuristic
or heuristics, and the severity. One problem can violate several heuristics.

**Limits the chapter states.** A heuristic evaluation does not show what the
interface does well, and it does not reveal a missing function. Two
evaluators are fewer than the three to five the chapter asks for, so the
resident rounds in `PL-DSXJ` are the check on what this misses.

**Why it matters.** This is the second step of the interface pass that the owner agreed on 2026-11-10 (`PL-HS9M`). Its findings say what the grey-box layouts (`PL-2V6V`) must fix, so every later step of the pass waits on it.

**Done when.** The merged list of violations, sorted by severity with both evaluators' ratings averaged, is recorded in this item beside the commit evaluated. Each violation rated 3 or higher is an item, or names the open item that holds it.
