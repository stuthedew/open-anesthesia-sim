---
id: PL-8Q1P
title: Run the heuristic evaluation of the current interface: four learner tasks against the 14 heuristics in Zhang et al. 2005, by a session and by the owner independently
status: untriaged
feature: interface-pass-design-round
added: 2026-11-11
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
- Each violation gets a severity from 0 to 4. 2 is a "Minor usability
  problem", 3 is a "Major usability problem", and 4 is a "Usability
  catastrophe. Imperative to fix before product can be released."
- Evaluators work independently. Their lists are merged into one, each
  evaluator rates every violation on it, and the ratings are averaged.
- "Typically one evaluator can only catch 35 percent of the usability
  problems, but 3-5 evaluators can detect 60-75 percent."

**What to do.**

1. Run the application as the run-the-app skill says, and walk each task on
   the current build. For each violation record the task, what was seen, the
   heuristic and a severity.
2. The owner does the same on their Mac, before reading the session's list.
   The reply of 2026-11-10 gave them the tasks, the heuristic names and the
   scale.
3. Merge the two lists, collect both ratings for every violation, and
   average them.
4. Record the merged list in this item, sorted by severity. File each
   violation rated 3 or higher as an item, or name the open item that already
   holds it. `PL-CXYV`, `PL-571L`, `PL-4JCC`, `PL-9YPR` and `PL-CBYS` hold
   some already.

**Limits the chapter states.** A heuristic evaluation does not show what the
interface does well, and it does not reveal a missing function. Two
evaluators are fewer than the three to five the chapter asks for, so the
resident rounds in `PL-DSXJ` are the check on what this misses.
