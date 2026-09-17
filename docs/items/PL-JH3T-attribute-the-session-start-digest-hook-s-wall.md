---
id: PL-JH3T
title: Attribute the session-start digest hook's wall-clock cost to a stage: the only number on record is 20.7s median and the hook measures 3.0s in a session container
priority: P2
effort: S
status: done
classes: session-cost
feature: session-start-cost
touches: docs/items
added: 2026-09-16
closed: 2026-09-17
not-delegable: the deliverable was a measurement taken on the project owner's own machine, which is the only place the 20.7s reproduces; no command in this checkout can re-run it
---

**Problem.** Attribute the session-start digest hook's wall-clock cost to a stage: the only number on record is 20.7s median and the hook measures 3.0s in a session container

**Where this came from.** A `/doctor` run on the project owner's machine
(2026-09-16) reported `.claude/hooks/docket-digest.sh` at a **median 20.7 s,
max 25.3 s across 13 recorded runs**, and flagged it against its own ">10 s for
SessionStart" heuristic. That heuristic is not documented policy: the hooks
reference gives `command` hooks a **600 s default timeout** on `SessionStart`,
and lowers it only on `UserPromptSubmit`, `PreModelSwitch` and `PostModelSwitch`
(https://code.claude.com/docs/en/hooks, read 2026-09-16). So the number is worth
attributing, but nothing is in violation.

**The number does not reproduce here.** Measured in a session container on
2026-09-16, same commit:

| stage | seconds |
| --- | --- |
| `bin/docket branch --brief` | 0.81 |
| `bin/docket digest` | 1.50 |
| `python3 tools/dead_ends.py emit` | 0.03 |
| `python3 tools/main_ci_status.py` | 0.85 |
| **hook end to end, warm** | **3.20, 2.93, 2.97** |
| `git fetch --unshallow origin` (once per container) | 3.40 |

So a cold container pays about **6.4 s**, and every session after that about
**3.0 s** - a seventh of the reported median. The `--unshallow` is not the
gap: 3.40 s here against the 3.4 s recorded in the hook's own comment on
2026-09-02, unchanged across 952 commits and a 16 MB `.git`.

**What the gap most likely is, and what would settle it.** Every stage that can
be slow is a network round trip, and each is separately bounded: the deepen by
`timeout 60`; `docket branch`'s `git fetch origin` by `_run_git`'s
`subprocess.run(..., timeout=10)`; `main_ci_status.py` by `TIMEOUT_S = 8`, which
it can spend twice because it makes two requests. Bounded, those sum to roughly
the reported median on a link slower than this container's. That is a
hypothesis, not a finding - it is the owner's machine that produces 20.7 s, so
the attribution has to be measured there:

```
cd <repo> && for s in "bin/docket branch --brief" "bin/docket digest" \
  "python3 tools/dead_ends.py emit" "python3 tools/main_ci_status.py"; do \
  printf '%-38s ' "$s"; /usr/bin/time -f '%es' sh -c "$s >/dev/null 2>&1"; done
```

**Done when** the 20.7 s is attributed to named stages by a measurement taken
where it occurs, and either the cause is fixed or this item records why the cost
is accepted. `PL-RC86` is the fix worth considering if the attribution lands on
the network stages.

---

**Answered 2026-09-16, same day.** The owner ran the attribution on their
machine. `bin/docket digest` is **17.64 s of the 20.01 s**, 88%, against 1.50 s
in a session container. The network hypothesis above is wrong and is refuted in
`PL-RC86`: `digest` touches no network at all.

The cause is git process spawns - 192 per `digest`, at ~92 ms each on that
machine against 2.1 ms in a container, a 44x spread. Neither the store nor the
item count is involved: 1,073 files and 5.1 MB parse in 0.019 s. `PL-MMVF`
carries the repo-side half (82 of the 192 calls are exact duplicates); the
per-spawn price is the machine's and is the larger of the two levers.

This item's question is answered and it should close at triage.

**Final attribution, 2026-09-16 - and it is the call count, not the clock.**
The three-way split was run on both machines. `bin/docket digest` makes **1,107
git calls on the owner's clone against 220 in a session container**, from
identical code against an identical store. Per call that machine is 2.8x
slower, which is unremarkable; 5x the calls is the finding. Neither the store
(1,089 files, 0.17 s) nor python startup (0.15 s) nor the network (`digest`
touches none) is involved.

Where the 17.25 s of replay sits: `diff` 570 calls / 8.90 s, `show` 389 / 5.77 s,
`merge-base` 78 / 1.19 s. The driver is the number of unmerged refs `digest`
walks - 18 in a container, inferred ~90 on a clone that has held every session's
branch since the project began.

Three items carry what follows, and the order matters: **`PL-XD3C`** (digest is
O(unmerged refs), which grows without bound and which pruning may not fix -
verify the ref count first), **`PL-0J9K`** (batch the 389 blob reads into one
`cat-file`, 24% and mechanical), **`PL-MMVF`** (memoize the runner, now measured
at 10% on the machine that pays). This item is answered and should close at
triage.

Two figures this item carried and got wrong are retracted above: ~92 ms per
spawn, and the network hypothesis. Both came from dividing a wall time by a
count instead of measuring the parts.

**Why it matters.** The hook runs before every session's first turn, and the
only number on record was a `/doctor` median that did not reproduce anywhere a
session could look. An unattributed cost cannot be fixed or accepted - it can
only be guessed at, which is what the two refuted hypotheses in this brief were.

**Closed at triage, 2026-09-17**, on the brief's own instruction ("This item's
question is answered and it should close at triage"). The attribution is
recorded above: `bin/docket digest` is 17.64s of 20.01s, 88%, and the driver is
git call count rather than per-call cost or the network. Its three successors
carry what follows - `PL-XD3C` (digest is O(unmerged refs)), `PL-0J9K` (batch
the blob reads) and `PL-MMVF` (memoize the runner), the last two now closed with
their work on `main`.
