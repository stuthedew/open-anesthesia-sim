---
id: PL-LFJZ
title: Count how many of the 35 items about verify: commands and shell commands a done-condition written as a test name would have prevented, and what the 923 other grep conditions check
priority: P2
effort: S
status: done
classes: planning
feature: standing-weight
milestone: v0.6.19
touches: docs/items
deferred-from: v0.7.0 - captured after the freeze, and not safety or science; a count the owner asked for on 2026-11-20 about the workflow, which no v0.7.0 feature needs
added: 2026-11-20
closed: 2026-11-21
pr: 2174
payoff: the owner chose the form of a done-condition for each kind of item on two counts, and four items carry the build
verify: grep -qF 'chose the four-part form' docs/items/PL-LFJZ-*.md
---

**Problem.** Count how many of the 35 items about verify: commands and shell commands a done-condition written as a test name would have prevented, and what the 923 other grep conditions check

**Why it matters.** 2,648 of the 3,102 items carry a `verify:` written as a shell command. 1,766 of those run only `grep`, and 843 of them search for the name of a test. The code that runs and interprets these commands, `subprojects/docket/src/docket/verify.py` and `subprojects/docket/src/docket/shell.py`, is 5,905 lines. `bin/docket generators` lists 35 items under the two root causes named "What a verify: command's exit status proves about its own item's work" and "What a shell command does when run". `PL-WKKH` (the streamlining questions from the study of the one-shot rewrite) holds the measurements and the sources.

**Answered 2026-11-20.** The owner agreed to count before deciding (project owner, 2026-11-20, ratified, "Agree with recs", over changing the form of the done-condition now).

**What to do.** Count how many of the 35 items would not have happened if the done-condition of an item that changes code had been the name of a test. Sort the 923 `grep` conditions that name no test by what they check. Then recommend whether to change the form, and what an item that changes only a document would use.

**Done when.** The owner has the two counts and a recommendation.

**Counted 2026-11-21**, on `main` at `2b17061c` with `PL-WKKH`'s branch merged in. The scripts are in `/mnt/project-files/v0.7.0/pl-lfjz/`: `count.py` reads every item's `verify:` with `docket.shell`, and `sort.py` reads each `grep` clause with `docket.grep.read_grep`.

The form counted is the one `PL-WKKH`'s fourth question describes: an item that changes code names a test, docket confirms that the test exists, and CI runs it. The one-shot rewrite states the same condition as "the change has a test that fails without it".

**First count: the 35 items.** `bin/docket generators` lists 16 under `PL-61FT` (what a shell command does when run) and 19 under `PL-6TP8` and `PL-1P5V` (what a `verify:` command's exit status proves).

1. **None of `PL-61FT`'s 16 would have been prevented.** Every one is a Bash guard hook misreading a command a session runs, such as `timeout 600 make check | tail`. None is about a `verify:` field. The shell reader in `subprojects/docket/src/docket/shell.py` serves those hooks, `tools/doc_check.py`'s reading of workflow scripts and `tools/fixture_id_check.py`, so it stays whatever form the done-condition takes.
2. **9 of the 19 would not have happened.** `PL-6YWK` (a whole suite killed at the 120-second limit), `PL-H9GV` (a change shipped with no test), `PL-Q8RQ` (a bare `pytest -k`), `PL-Y4YX` (a condition that asked for a spelling the file's own rule forbids), `PL-0QRP` (counting a symbol), `PL-J3WK` (a literal `true`), `PL-09G9` (rerunning a file `make check` already runs), `PL-CWD4` (a condition that read output the tool stopped printing) and `PL-R812` (what a pytest node id exits before and after the work). Each is a property of a shell command that a named test does not have.
3. **2 would not have happened only if the test is named at close.** `PL-0M32` (the test shipped as `..._against_...` where the item asked for `..._matches_...`) and `PL-6TN8` (the behaviour already existed under three other names) are both a name guessed before the work. A name written at triage has the same fault.
4. **4 are prevented in part.** `PL-6YL1` and `PL-2M4X` named a test file in the wrong suite, and `PL-LBW5` named a file outside the item's `touches`. A test name can still point at the wrong file, though the clause that ran the wrong suite disappears. In `PL-3DXV`, one item's condition was satisfied by its neighbour's work. A test each item owns ends that, but two of the three items removed a dependency and a directory, which no new test can show.
5. **4 depend on what a non-code item uses.** `PL-T7VS` and `PL-D0K3` are about the conditions that ran `doc_check.py check`, which documentation items carried, `PL-RR1N` is a phrase split by the document's line-wrapping, and `PL-205P` is a branch-deletion item whose condition read the remote.

So the form prevents 9 of the 35, and 11 if the test is named at close. With a document form that is checked once at close and never replayed, it prevents 15, and 4 more in part.

**Second count: the `grep` conditions that name no test.** Today 2,648 of 3,103 items carry a `verify:`, 1,773 of those run only `grep`, and 845 search for `def test_`. That leaves 928, where `PL-WKKH` counted 923 at `77b6958`. But 134 of the 928 name a test without `def`, so 794 name none. `read_grep` reads 780 of the 794. The other 14 use `-l`, `-x` or `-c`, which it refuses, and were not sorted. Only 38 of the 780 belong to open items.

| What the `grep` reads | Conditions | Text present | Text absent | Both |
| --- | --- | --- | --- | --- |
| Workflow code, its tests, CI files and hooks | 127 | 59 | 44 | 24 |
| Simulator code under `src/` | 68 | 28 | 33 | 7 |
| Configuration, mostly `pyproject.toml` | 53 | 51 | 1 | 1 |
| Test files, for text other than a test name | 5 | 4 | 1 | 0 |
| Workflow documents and rules | 168 | 123 | 26 | 19 |
| `docs/MODEL.md`, `docs/INTERFACE.md`, `README.md` and `docs/references/` | 102 | 40 | 43 | 19 |
| `ROADMAP.md` and release notes | 95 | 69 | 16 | 10 |
| Other documents under `docs/` | 42 | 28 | 11 | 3 |
| The item's own file, recording a result or an answer | 79 | 79 | 0 | 0 |
| Another item's file | 41 | 34 | 4 | 3 |

An item whose condition reads several kinds of file is counted once, under the first row it reaches. 47 of the 794 are a release's version line in `pyproject.toml`, and 24 more read a release's baseline line or notes.

1. **253 check code by its text.** These are the conditions the form would replace with a test. 79 of them check only that text is gone, and 32 more check both. A deletion has no new test to name: the honest condition is that the text is gone and the suite still passes.
2. **407 check a document.** Most add or remove a sentence. 96 check only that text is gone.
3. **120 read an item file.** 79 confirm that the item's own brief records its result. 41 confirm an edit to another item.

**Three further measurements bear on the design.**

1. **A test named at close decays afterwards.** Of the 1,060 `done` items whose condition searches for `def test_`, 948 name a test that `main` still defines, and 109 name one later renamed or removed. 3 name a test that no commit on `main` ever defined. So a condition checked once at close holds, and one replayed across the store for good would turn red about one time in ten.
2. **The code that reads `verify:` commands is about 1,640 lines, not 5,905.** It is about 828 lines of `verify.py` (running the commands, reading their shapes, the replay's report), about 421 of `checks.py` (the shape rules and the replay) and the 393 of `grep.py`. These are the functions whose names concern the command, measured with `ast`, so the figure is approximate. The rest of `verify.py`, about 2,680 lines, checks that delegated work stayed inside `touches` and added no suppression, and it stays. So does `shell.py`.
3. **The replay of `verify:` commands has turned `main` or a branch red on its own.** `PL-32Z9`, `PL-KND7`, `PL-X7VY`, `PL-Y1W6`, `PL-PLSJ` and `PL-WJJ8` are each such a red, and none is among the 35. The `Makefile` comment above `bin/docket check --verify` records that 20 of 56 red pull-request runs from 2026-09-10 to 2026-09-22 failed on it. Whether those reds caught real unfinished closures is the count `PL-LY24` (what each of the 13 checks on the workflow's own records caught) takes for `bin/docket check`.

**Decision needed.** Should an item's done-condition change form by the kind of work it does?

**Recommendation:** yes, in four parts, each checked once when the item closes and never replayed.

1. **Code that adds or changes behaviour.** At triage the item says in words what will be true. At close it records the tests that show it, as pytest node ids. docket confirms that each test is defined in the tree and that the closing branch added or changed it. CI already runs every test. Naming the test at close prevents `PL-0M32` and `PL-6TN8`, and checking once prevents the decay above.
2. **Code that deletes something, and documents.** Keep one `grep -qF` for a few words the work adds, or `! grep -qF` for what it removes. The sentence in a developer document that restates a fact of the tree takes the form agreed under `PL-WKKH`'s second question: the requirement, then the test that checks it.
3. **An item that records a result in its own brief.** It needs no command: the closed status and the dated paragraph are the record.
4. **Release items.** No change. `bin/docket release` already writes the version and the notes.

[superseded 2026-11-21: `PL-LY24` closed with its count before the answer, and the build items below record the wait that remains.] This removes the shape rules and the replay's reading of commands, about 1,640 lines with their tests, and the 9 to 15 kinds of fault counted above. It costs the replay's catch of work merged with its item still open, for every item that no longer carries a command. That catch is worth keeping only if `PL-LY24` finds it caught real mistakes more often than it turned `main` red. So the build items filed on a yes would each carry `blocked-by` on `PL-LY24`, whose count covers `bin/docket check`. If that count says the catch is worth keeping, the replay can stay for the document conditions in part 2 and nothing else.

**Answered 2026-11-20.** The project owner chose the four-part form on the decision card at 7:50 PM CST (project owner, 2026-11-20, ratified, over changing the form for code items only, and over keeping today's form). `PL-LY24` closed before the answer. It counted 9 episodes in which the replay of `verify:` commands caught a real mistake, all before 2026-09-23, and recommended retiring the replay together with the commands. `PL-KGPR` (which of the 13 workflow-record checks to retire) holds that decision.

The build is four items under the feature `standing-weight`:

1. `PL-FN11`: an item that changes code records its tests when it closes, and docket checks them once.
2. `PL-N046`: an item that deletes code or changes only a document keeps one `grep`, checked once when it closes.
3. `PL-NY7Q`: an item whose result is recorded in its own brief closes with no command.
4. `PL-QTZG`: remove the shape rules and the replay's reading of commands once the first three land.

**Generator check.** None: one instance. The item is a count the project owner asked for, and no misread fact produced it.
