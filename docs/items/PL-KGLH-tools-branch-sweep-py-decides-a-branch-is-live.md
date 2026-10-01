---
id: PL-KGLH
title: tools/branch_sweep.py decides a branch is live from 72 h of committer age (GRACE) although the claim record names the holding session, so a live session's branch past the grace reads as finished and a dead one inside it as live
priority: P3
effort: S
status: dropped
classes: defect
feature: recorded-not-inferred
touches: tools/branch_sweep.py
added: 2026-10-01
closed: 2026-10-01
reason: the claim record is already read (read_docket keeps every branch with unfinished work on it); the 72-hour grace covers only the window before any record exists, and the fact it stands for - whether a session that has recorded nothing is still alive - is one no session can record and the sweep's Action cannot ask; each swept tip is archived first, so the inference costs a restore
---

**Problem.** tools/branch_sweep.py decides a branch is live from 72 h of committer age (GRACE) although the claim record names the holding session, so a live session's branch past the grace reads as finished and a dead one inside it as live

**Recorded alternative, from the 2026-10-01 survey.** Read the session id the claim record holds, or a recorded branch-opened fact. The 72 h grace is documented in the module docstring as covering a first push, so triage should weigh whether the claim record now covers that case. Shape A.

**Why it matters.** Filed as shape A, liveness inferred from age where a record exists. Triage read the sweep: `read_docket` already keeps every branch the claim record holds unfinished work on, and the 72-hour grace is read beside it for the window before any record exists - a branch with pushed commits, no claim, no pull request and no item file only it holds. The fact that window stands for, whether a session that has recorded nothing is still alive, is one nothing can record: a session cannot write its own death, and the sweep runs in an Action that cannot ask the harness. The sweep also archives each tip before deleting it (`restore_command`), so the inference costs a restore, never a loss.

**Done when.** Not applicable: dropped at triage, 2026-10-01.

**Generator check.** Would have been an instance of `PL-MB2W`'s fact (who holds an item now, and whether that holder is still live), filed after that head drained on 2026-09-25 - one, not three. Dropped because the record the rule says to read is already read, and what remains infers a fact nothing can record.
