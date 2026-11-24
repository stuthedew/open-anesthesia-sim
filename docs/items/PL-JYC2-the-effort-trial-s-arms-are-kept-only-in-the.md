---
id: PL-JYC2
title: The effort trial's arms are kept only in the harness's session events, so every model review re-reads every trial session through subagents, which took four readers about 25 minutes each on 2026-11-24 with 8 of 139 sessions failing on the first try, and an arm is lost if the harness drops the session
status: done
feature: effort-trial
added: 2026-11-24
closed: 2026-11-24
pr: 2321
filed-pr: 2318
tests: tests/unit/test_effort_trial.py::test_record_writes_a_row_once_and_says_what_it_read, tests/unit/test_effort_trial.py::test_pending_lists_trial_sessions_with_no_recorded_arm, tests/unit/test_effort_trial.py::test_every_line_the_script_prints_reads_back_as_its_arm
---

**Problem.** The effort trial's arms are kept only in the harness's session events, so every model review re-reads every trial session through subagents, which took four readers about 25 minutes each on 2026-11-24 with 8 of 139 sessions failing on the first try, and an arm is lost if the harness drops the session

**Why it matters.** The arm a session drew is the trial's one randomized
fact, and the only copy is the "Effort trial:" line in the session's
session-start events, which `list_events` reads one session at a time. The
2026-11-24 run (`PL-JT1C`) needed four background readers for 139 cloud
sessions, and eight sessions failed on the first try. Each later run reads
every session again, and the count only grows. A session the harness stops
returning takes its arm with it, which the ledger exists to prevent for every
other session fact.

**A fix to weigh.** The review writes each arm it reads into a file in the
tree, such as an `arm` column in `docs/session-ledger.tsv`, and later runs
read only sessions that have no arm recorded yet. This is new workflow
machinery, so it waits on the workflow pause in `CLAUDE.md`.

**Built** (2026-11-24, with `PL-C38D`). The arms are kept in a file of their
own, `docs/effort-trial-arms.tsv`, rather than a ledger column, because the
review rewrites the ledger whole each run and a column it does not know about
would be lost. `python3 tools/effort_trial.py pending` prints the ledger's
trial sessions with no recorded arm, leaving out sessions from before the
trial and threads from before 2026-11-24, which are in neither arm by rule.
`python3 tools/effort_trial.py record SESSION FILE...` reads the "Effort
trial:" lines from the saved events with `read_lines`, the parser kept beside
the functions that write the lines, and appends one row. It refuses a session
already recorded, and a session whose files hold no line unless `--none` is
given after the review has checked every page was saved. The review still
writes the record, so no working session writes about itself (`PL-92ZN`). The
139 arms read on 2026-11-24 were not kept in the tree, so the next run reads
those sessions once more and records them.
