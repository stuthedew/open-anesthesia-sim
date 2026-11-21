---
id: PL-LFJZ
title: Count how many of the 35 items about verify: commands and shell commands a done-condition written as a test name would have prevented, and what the 923 other grep conditions check
status: untriaged
feature: standing-weight
added: 2026-11-20
---

**Problem.** Count how many of the 35 items about verify: commands and shell commands a done-condition written as a test name would have prevented, and what the 923 other grep conditions check

**Why it matters.** 2,648 of the 3,102 items carry a `verify:` written as a shell command. 1,766 of those run only `grep`, and 843 of them search for the name of a test. The code that runs and interprets these commands, `subprojects/docket/src/docket/verify.py` and `subprojects/docket/src/docket/shell.py`, is 5,905 lines. `bin/docket generators` lists 35 items under the two root causes named "What a verify: command's exit status proves about its own item's work" and "What a shell command does when run". `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**Answered 2026-11-20.** The owner agreed to count before deciding (project owner, 2026-11-20, ratified, "Agree with recs", over changing the form of the done-condition now).

**What to do.** Count how many of the 35 items would not have happened if the done-condition of an item that changes code had been the name of a test. Sort the 923 `grep` conditions that name no test by what they check. Then recommend whether to change the form, and what an item that changes only a document would use.

**Done when.** The owner has the two counts and a recommendation.
