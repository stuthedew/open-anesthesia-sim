---
id: PL-552M
title: bin/docket arm holds every change under tests/ for the owner's read, a test of the tooling that imports no anesthesia_sim included, so 16 of the 51 merges held for a read since 2026-10-03 had nothing to judge
priority: P2
effort: M
status: ready
classes: infra
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_portability.py, tools/workflow_paths_check.py, CLAUDE.md, docs/maintainer.md, docs/items/PL-WW0Q-bin-docket-arm-holds-a-change-to-arming-py-for.md
added: 2026-10-05
payoff: a pull request that changes only tests of the tooling merges on green CI instead of waiting on the owner's read with nothing to judge, while every change to a simulator test still waits on it
verify: grep -q 'def test_arm_arms_a_test_of_the_tooling_under_tests_on_green' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket arm holds every change under tests/ for the owner's read, a test of the tooling that imports no anesthesia_sim included, so 16 of the 51 merges held for a read since 2026-10-03 had nothing to judge

**Evidence, measured 2026-10-05 on `main` at 85b9c437.**

- `bin/docket arm --no-fetch`, on a scratch branch whose one commit adds a
  comment to `tests/unit/test_doc_check.py`, answers `hold - ...: it changes 1
  path on the owner's read list, so its pull request waits on a read` and exits
  1, with the ask for a read beneath it. `READ_PATHS` in
  `subprojects/docket/src/docket/arming.py` holds `tests/` whole, by prefix.
- Of the 94 first-parent commits on `main` since 2026-10-03, 51 changed a path
  on the read list, and 16 of those changed none but test files under `tests/`
  that import no `anesthesia_sim` on either side of the commit, every
  `PL-R417` slice among them. Each waited on the owner's read with nothing for
  the owner to judge. Counted with `arming.waits_on_read` and
  `tools/workflow_paths_check.py`'s `imports_product`, over each commit's
  `git show --no-renames --name-only`.
- 43 of the 93 test files under `tests/` import no `anesthesia_sim`, all 43 of
  them in `tests/unit/` (of 77 there), and `docket.toml`'s `workflow_paths`
  lists all 43, as `tools/workflow_paths_check.py` requires (`PL-JBZK`). The
  card that put the question said 31 of 77; 43 is the tree's count at
  85b9c437. Twelve of the 43 name `anesthesia_sim` in their text, and every
  such mention is fixture text or a path read by the tool under test, none an
  import the `ast` reading misses. The two support modules are
  `tests/conftest.py`, importing none, and `tests/benchmarks/frame_cost.py`,
  importing it; the only other files under `tests/` are two `.gitkeep`s.

**Decision.** The owner chose "Narrow it" at 2026-10-05 13:45Z, on the card the
`PL-R417` Python slice's thread put to the owner: "Stop holding tooling-only test
changes under tests/ for your read?", the option reading "Only tests that
import the simulator wait for your read; tooling tests merge on green CI, as
subprojects/docket/tests/ already do", recommended because a third of recent
read requests had nothing to read, the click-through that retired the
docket-wide hold (`PL-SQTR`). Recorded as (project owner, 2026-10-05,
ratified, over keeping every change under `tests/` on the read list).

**The pause on new workflow mechanisms.** `PL-R417` carries `generator: live`,
so `CLAUDE.md` § "What this project is" holds apparatus work unrelated to
fixing the generators, and a narrower rule in an existing gate is such work.
The owner's answer on the card is the request that lifts the pause for it:
"A request from the project owner lifts it for that request, and the session
says so" (`PL-6Q9L`), checked against that sentence and `PL-6Q9L` on
85b9c437.

**How.** The import rule moves into `subprojects/docket/src/docket/arming.py`:
`PRODUCT_PACKAGE`, `TEST_FILE_PATTERNS`, `imported_modules`, `imports_product`
and `is_test_file` are defined there, and `tools/workflow_paths_check.py`
imports them, so the lane check and the gate read one rule, and a change to it
waits on the owner's read. `arm` reads each changed test file under `tests/`
on both sides of the change, the merge base's and HEAD's, and arms it on green
only where neither side imports `anesthesia_sim`: a change that removes a
test's simulator import, or deletes a simulator test, still waits. So does a
support module such as `tests/conftest.py`, whose imports decide nothing about
its side (`PL-12P8`), a file that is not Python, and a file either side of
which git or the running interpreter's parser could not read, said with the
reason.

**Not `workflow_paths`, though the lane check holds it to the same rule.** The
gate would then widen on an edit to `docket.toml`, which arms on green, and
`PL-0JGZ` decided that "widening what arms still takes an edit the gate holds"
(2026-09-26, ratified). The lane check also reads HEAD alone, so a branch that
drops a simulator test's import and lists the file there passes it.

**Why it matters.** A hold that fires with nothing to judge trains the click it
exists to prevent, which is `PL-SQTR`'s finding and `CLAUDE.md`'s "being routed
around" test. Every remaining `PL-R417` slice changes
`tests/unit/test_doc_check.py`, and each would be held the same way.

**Done when.** `bin/docket arm` arms on green a branch whose only change outside
the store and the tooling is a test file under `tests/` importing no
`anesthesia_sim` on either side, and holds one whose test imports it on either
side, a support module, and a file it could not read, each pinned by a
`test_arm_` test in `subprojects/docket/tests/test_cli.py`;
`tools/workflow_paths_check.py` reads the import rule from `arming.py`; and
`CLAUDE.md` and `docs/maintainer.md` describe the narrowed list.

**Not a recurrence of `PL-WW0Q`.** `docket new` matched this capture to it on
`arming.py` and `test_cli.py`, and the match was withdrawn: `PL-WW0Q` asks
whether the hold reaches what `arm`'s answer is read through, and this narrows
which paths the hold names. It adds nothing to that question's surface, since
the rule stays in the module the gate holds and both sides are read through
the runner every other read in `arm` takes.

**Generator check.** Work the owner asked for, not a misread. The read list is
the owner's partition of what waits on a read, deliberately not the lane
boundary (`.github/workflows/` is on it and in the workflow lane), and
`tests/` was on it whole by the owner's wording of 2026-10-03 until their
answer of 2026-10-05. The fact the narrowed rule reads, whether a test file under
`tests/` is the simulator's, is the one `PL-8ZGY` states for lanes, and it is
read through the lane check's own import rule rather than a second spelling of
it, `PL-PVW2`'s fact; neither head is reopened.
