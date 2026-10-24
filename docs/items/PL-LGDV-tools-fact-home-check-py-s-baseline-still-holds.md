---
id: PL-LGDV
title: tools/fact_home_check.py's baseline still holds 59 second readers (49 duplicate module-level names across docket and tools such as FENCE, MARKER, API, TIMEOUT_S and ITEM_ID, 6 git readers outside docket.vcs and 4 GitHub API readers) and no open item drains it since PL-5DZ8 closed
priority: P2
effort: L
status: done
classes: defect
feature: one-source-of-truth
touches: tools/fact_home_check.py, tools/, subprojects/docket/src/docket/, subprojects/docket/tests/, tests/unit/test_main_ci_status.py, tests/unit/test_open_pull_requests.py, tests/unit/test_dead_ends.py, tests/unit/test_item_read_log.py, docs/apparatus.md
added: 2026-10-19
closed: 2026-10-24
pr: 1740
payoff: each apparatus constant and git or GitHub reading has one home, so two copies cannot drift into two answers
verify: grep -qF 'BASELINE: dict[str, dict[tuple[str, str], int]] = {}' tools/fact_home_check.py
---

**Problem.** tools/fact_home_check.py's baseline still holds 59 second readers (49 duplicate module-level names across docket and tools such as FENCE, MARKER, API, TIMEOUT_S and ITEM_ID, 6 git readers outside docket.vcs and 4 GitHub API readers) and no open item drains it since PL-5DZ8 closed

**Why it matters.** Each entry is a fact read or defined in two places, for example `FENCE` in both `frontmatter.py` and `markdown.py`, or a git reader outside `docket.vcs`. `tools/fact_home_check.py` refuses new ones, but the 59 recorded when it landed can still drift apart. No open item was draining them.

**Class.** Each baseline entry is a second copy, which breaks a rule this repository states, so `CLAUDE.md`'s fix-in-place condition 1 counts it as a defect whether or not the copies disagree today (project owner raised this on 2026-10-24).

**Done when.** `BASELINE` in `tools/fact_home_check.py` is empty. Each duplicate name is imported from one home, and each git or GitHub API reader goes through the module that owns that reading. This is large, so a session may split it by module as it starts, filing the parts under `one-source-of-truth`.

**Checked 2026-10-24.** `BASELINE` is not empty. It lists, among others, `FENCE` twice in `markdown.py`, `ID` in `claiming.py` and `claims.py`, and `_git` readers in `claiming.py` and `tools/branch_sweep.py`.

**Generator check.** Bookkeeping. This is the baseline the check recorded when it landed, so it is not new inflow.

**Done 2026-10-24.** The baseline held 57 entries when the work started, where the title counts 59: 47 definitions, 6 git readers and 4 GitHub API readers. All 57 are gone and `BASELINE` is empty.

- **The same fact, now imported from one home.** `claims._ID` and `claiming._ID` read `vcs.ANY_ID_RE`. `notes._ID_RE`, `dead_ends.ITEM_ID` and `item_reads.ITEM_ID` read `store.CITED_ID_RE`, which was the private `_CITED_ID_RE`. `verify.UNPARSABLE` and `vcs._UNPARSABLE` moved to `docket.python.UNPARSABLE`, beside `UNTOKENIZABLE`. `contrast_check.APP` is imported from `agent_identity_check`. `REPO` in `dead_ends.py` and `item_reads.py` became `ROOT`, the one name every tool spells itself. Their `ITEMS` is read from `docket.toml` where it is used, so the tests now point `ROOT` at a temporary tree. `GITHUB_API`, a new `API_VERSION`, `PAGE` and a new `api_request`, which builds every request's headers, live in `open_pull_requests.py`, and `main_ci_status`, `pr_body_check`, `required_checks_check` and `update_armed` read them from there.
- **The body records directory.** `arming.RECORDS` was a deliberate copy of `vcs.RECORDS` (project owner, 2026-09-26, ratified, over `arming` importing it, `PL-F6MM`), kept so that widening what arms took an edit the gate held for a read. `PL-9JHM` ended that hold on 2026-10-19, so the copy no longer protected anything; the pinned arm tests in `test_cli.py` that name the directory are what hold a widening now. This branch reopens that ratified decision on that evidence: `arming` and `verify` import `vcs.RECORDS`, and the test that pinned the two copies equal is deleted.
- **Two facts that shared a name, now named apart.** `frontmatter.FENCE` became `DELIMITER`, since it is the front matter's `---` and not `markdown.FENCE`, a block kind; `markdown._FENCE` became `_FENCE_OPEN`, beside `_FENCE_CLOSE`. `markdown._MARKER` became `_LIST_MARKER` and `grep._MARKER` became `_COMMENT_MARKER`, leaving `fixture_id_check.MARKER`. `trend.UNPLACED` became `UNPLACED_PATH`, apart from `roadmap.UNPLACED`. `doc_check.APPARATUS` became `APPARATUS_MAP`, apart from `trend.APPARATUS`. `vcs._AHEAD`, `_BEHIND` and `_EQUAL` became `_COPY_AHEAD`, `_COPY_BEHIND` and `_COPY_EQUAL`, apart from `arming.BEHIND`. `arming.LANDED` became `ALREADY_MERGED`, apart from `vcs.LANDED`, a branch's disposition. `contrast_check.LINE_CITATION_RE` became `LINE_NUMBER_RE`, since it refuses any line number and `doc_check.LINE_CITATION_RE` reads a backticked citation. `literal_home_check.EXEMPT` became `EXEMPT_VALUES`, `tag_release.ABSENT` became `NO_MATCHING_REF`, `fixture_id_check.JSON_KEY_RE` became `NAME_SEPARATOR_RE`, and `pr_body_check.TIMEOUT_S` became `READ_TIMEOUT_S`, each a different fact from the name it shared.
- **Git readers.** `claiming._git`, `branch_sweep._git`, `tag_release._git` and `open_pull_requests._git` run git through `vcs.call_git`. `main_ci_status` and `required_checks_check` read `origin`'s repository through `open_pull_requests.repo_slug`, which now takes the root to read.

`PL-H5T9` records five more copies of one fact under two names that the check cannot see, and `PL-MM3Q` the gap in rule 2 that lets them pass.
