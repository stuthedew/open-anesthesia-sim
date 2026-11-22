---
id: PL-WKKH
title: Decide which streamlining ideas from the one-shot rewrite of 2026-11-14 to take: fewer instructions at launch, developer documents written as a requirement and its test, the 13 checks on the workflow's own records, done-conditions as test names, and one rule for computing a run
priority: P2
effort: S
status: done
classes: housekeeping
feature: standing-weight
milestone: v0.6.19
touches: docs/items
added: 2026-11-20
closed: 2026-11-20
pr: 2173
payoff: the owner's five answers are on record, and each has an item or a line in an existing item that carries it
verify: grep -qF 'Answered 2026-11-20' docs/items/PL-WKKH-decide-which-streamlining-ideas-from-the-one.md
---

**Problem.** Decide which streamlining ideas from the one-shot rewrite of 2026-11-14 to take: fewer instructions at launch, developer documents written as a requirement and its test, the 13 checks on the workflow's own records, done-conditions as test names, and one rule for computing a run

**Checked 2026-11-20**, in a project thread, after the project owner wrote: "I feel like ours is bloated. I'm not saying theirs is perfect or adequate for our needs but maybe can give us some ideas where to streamline". The thread read the private repository `stuthedew/OAS-Sim-oneshot` at commit `2f37877`, the transcript of the session that built it, and this repository at `77b6958`. The full report is the Claude Doc "Lessons from the one-shot rewrite", at https://claude.ai/artifact/5e46Lyz7G8KPuZpNNVMaEa. This brief holds what a later session needs if it cannot open that link.

**What the one-shot is.** It is the project owner's own rewrite of the simulator from an empty repository, made in one session on 2026-11-14 (`session_01GnrHQvFFbhhjMv9dW8NpKG`, about 3.5 hours, $139 at list price). The session read this repository at `799ddd8` and the reference corpus. Its whole process is one instruction file of 149 lines, a status file, a backlog, a changelog and a decisions file. Each of the instruction file's eight rules names the test that enforces it, and a test fails when the file reaches 150 lines. Its checks pass in a clean container: 96 test functions in 12 seconds, with 98.6% branch coverage of its model code. Its status file says that nobody but its author has used it and that its window has not been drawn on a real display.

**What was measured in this repository at `77b6958`.**

| Measure | Value | Command or file |
| --- | --- | --- |
| Instructions loaded at launch | 1,332 lines and 99,951 characters. The instruction files alone are 92,660 characters, against 60,199 on 2026-09-19. | `python3 tools/doc_check.py check` |
| The two specifications | `docs/MODEL.md` is 70,200 words and `docs/INTERFACE.md` is 61,130. | `wc -w` |
| Commands in `make check` | 29. Twelve guard code, 3 guard documents, 13 guard the workflow's own records, and the check on regular expressions covers all Python. | The `check` target of the `Makefile`, and the first line of each tool's docstring |
| Done-conditions | 2,648 of 3,102 items carry a `verify:`. 1,766 of those run only `grep`, and 843 of them search for the name of a test. | The front matter of each file in `docs/items/` |
| Root causes still producing items | Two, both in the simulator: `PL-RF2S` (every widget keeps the last value written to it) and `PL-GJ1W` (each comparison of computed values picks its own tolerance). | `bin/docket generators` |
| The workflow's share of lines changed, with the queue left out | 44% over 13 weeks, then 13% and 14% in the last two full weeks. | `bin/docket trend` |
| Checks on one push | About 7 minutes, in 4 jobs. | GitHub Actions run 43941626719 |

**Why it matters.** The standing weight is paid again by every session and every push. Each session loads 1,332 lines of instructions before it reads anything, and each push runs 29 check commands. The specifications are the largest source of blind-review findings, and the two root causes still producing items are in the simulator.

**Decision needed.** Five questions follow, in the order the thread recommends taking them. Each is the owner's, because it changes how every session works or what a learner sees.

1. **Instructions loaded at launch.** Should one session sort every paragraph loaded at launch into four groups, for the owner's approval before any text moves? The groups are: enforced by a named check, procedure that belongs in a skill, history, and judgment that no check can carry. A line cap in `make check` would follow. **Recommendation: yes.** Claude Code's documentation asks for under 200 lines per file and says that longer files reduce adherence. `CLAUDE.md` records that a ceiling on its size was refused earlier. The growth since 2026-09-19 is the new evidence.
2. **Developer documents.** Should `PL-SY7G`, `PL-4H8Q` and `PL-N83Z` (sort the interface, verification and parameter documents by reader) write each developer document as a requirement followed by the test that checks it? Each parameter table would be compared with its data file by a test, and history would stay in the item. **Recommendation: yes.** 60 items sit under the three root causes named "The link between a document sentence and the tree fact it restates", and 42 of the 133 blind-review findings were a document claiming something the code does not do.
3. **Checks on the workflow's own records.** Should one session count, for each of the 13, how many of its refusals caught a real mistake? `CLAUDE.md` § "Prefer deterministic tooling over repeated model work" retires a check that changes no decision, and this is the count that rule needs. **Recommendation: yes.**
4. **Done-conditions.** Should the `verify:` of an item that changes code become the name of a test? **Recommendation: count first.** The count is how many of the 35 items under the two root causes about `verify:` commands and shell commands would not have happened, and what the other 923 `grep` conditions check.
5. **One rule for computing a run.** Should a design round open on computing a run by one rule? The one-shot's rule is one exact step per whole second, with every state stored, charts and readouts reading the stored states, a branch copying its parent's states, and time held as a whole number of seconds. **Recommendation: open the round.** It would remove the comparisons that `PL-GJ1W` gives tolerances to, and that item's planned pull requests are the work one rule would make unnecessary. A learner would see a control change land on a whole second, where today it lands on a tenth. Both versions stop a run at 24 hours. In the one-shot a 24-hour run with a control change every hour computed in 0.6 seconds and held 6.9 MB. The round first counts the closed items that came from two paths disagreeing or from a floating-point instant.

The report's sixth idea needs no answer now. Agents, patients and machines could be offered from the data folder, in place of the hand lists `AGENT_DATA_FILENAMES` in `core/parameters.py` and `AGENT_COLOR_SCHEMES` in `app/theme.py`. It belongs to the milestone that adds an agent, a patient or a machine.

**Routes weighed and refused.**

- Taking the one-shot as the base. The owner said that it is not adequate for the project's needs.
- One backlog file in place of `docs/items/`. With 12 to 14 threads at once, every thread would edit the same file.
- Arguing for a shorter instruction file because it would be followed more often. McMillan found no effect of length between 25 and 500 lines, and 1,332 lines are outside the range he tested. His result supports giving a rule a check.

**Sources, each read on 2026-11-20.**

- Claude Code documentation, memory page, https://code.claude.com/docs/en/memory. Read in full.
- McMillan D. "Instruction Adherence in Coding Agent Configuration Files: A Factorial Study of Four File-Structure Variables." arXiv:2605.10039. The abstract was read in full, and the first part of the body.
- Gloaguen T, et al. "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?" arXiv:2602.11988, version 3. The abstract was read in full, and the body in part.
- Young J. "Effective harnesses for long-running agents." Anthropic, 2025-11-26, https://www.anthropic.com/research/effective-harnesses-for-long-running-agents. Read in full.

**One figure in the one-shot's appraisal does not reproduce.** It counts "15 faults in simulator code" in the blind reviews. `docs/blind-review-findings.tsv` has 35 rows coded `code-bug`, against 42 coded `doc-claim-wrong`.

**Done when.** The owner has answered each of the five questions, and each yes has become an item of its own or a line in an existing item.

**Answered 2026-11-20.** The owner wrote "Agree with recs" in the project thread at 5:58 PM CST. That ratifies the recommendation under each of the five questions (project owner, 2026-11-20, ratified, over the alternative that each follow-up item names).

1. Instructions loaded at launch: yes. `PL-MR85` (sort every loaded paragraph into four groups, and bring the table to the owner) holds the work.
2. Developer documents: yes. `PL-SY7G`, `PL-4H8Q` and `PL-N83Z` (sort the interface, verification and parameter documents by reader) each carry a paragraph dated 2026-11-20 with the form.
3. Checks on the workflow's own records: count first. `PL-LY24` (count what each of the 13 checks caught) holds the count.
4. Done-conditions: count first. `PL-LFJZ` (count what a done-condition written as a test name would have prevented) holds the count.
5. One rule for computing a run: open the round. `PL-7CY5` (the design round on computing a run by one rule) holds it, and it comes before more work on `PL-GJ1W` (each comparison of computed values picks its own tolerance).

The four new items carry the feature `standing-weight`, so `bin/docket feature standing-weight` says whether they are dealt with.

**Generator check.** None: one instance. The item records a study that the owner asked for and the owner's answers, and no misread fact produced it.
