---
id: PL-JYC2
title: The effort trial's arms are kept only in the harness's session events, so every model review re-reads every trial session through subagents, which took four readers about 25 minutes each on 2026-11-24 with 8 of 139 sessions failing on the first try, and an arm is lost if the harness drops the session
status: untriaged
feature: effort-trial
added: 2026-11-24
filed-pr: 2318
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
