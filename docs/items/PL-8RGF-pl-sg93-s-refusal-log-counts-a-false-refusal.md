---
id: PL-8RGF
title: PL-SG93's refusal log counts a false refusal and each retry as a block, and its brief says Projects threads run no guard though thread files hold 45 of 118 logged lines, so the keep-or-retire verdicts due 2026-11-23 would read friction as value
status: untriaged
feature: defect-review-2026-10
added: 2026-11-03
---

**Problem.** PL-SG93's refusal log counts a false refusal and each retry as a block, and its brief says Projects threads run no guard though thread files hold 45 of 118 logged lines, so the keep-or-retire verdicts due 2026-11-23 would read friction as value

**Evidence, 2026-11-03.** A guard review in one session had three of its own commands refused as `gate-status-guard status-swallowed`, and none of them was a gate. They were `python3 -X importtime tools/pr_body_check.py --screen ... | tail`, `python3 tools/branch_id_check.py --hint ... | cut`, and a timing of `tools/doc_check.py` with its output sent to `/dev/null`. All three went into the real log. Of the 118 tracked lines, 23 repeat the same guard and rule in the same session within 2 minutes, and one session holds 13. The owner-ask guard logged 2 refusals, while 4 of its false refusals were filed on 2026-11-02 and 2026-11-03. The log records no matched pattern and nothing about what the session did next. So a count cannot separate a refusal that prevented an error from one that blocked correct work.

**What to fix before 2026-11-23.** Correct `PL-SG93`'s sentence about Projects threads, since `PL-X6VN` gave them the hooks. Have the verdict session judge a sample of refusals as true or false, rather than read the count as value. Logging which pattern refused would make that sample possible.
