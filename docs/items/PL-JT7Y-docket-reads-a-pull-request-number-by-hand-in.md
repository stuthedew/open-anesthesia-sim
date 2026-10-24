---
id: PL-JT7Y
title: docket reads a pull request number by hand in four places (verify.py PR_VALUE_RE and RECORD_NAME_RE, cli.py's two isdigit checks) instead of model.pr_number, so 0 and leading zeros pass, the reading PL-4DK2 replaced
priority: P3
effort: S
status: ready
classes: defect
feature: one-source-of-truth
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/
added: 2026-10-19
payoff: docket verify and docket check give the same answer about a pr: value of 0 or 07
verify: ! grep -qE '(PR_VALUE_RE|RECORD_NAME_RE) = re.compile' subprojects/docket/src/docket/verify.py
reenters: PL-4DK2
---

**Problem.** docket reads a pull request number by hand in four places (verify.py PR_VALUE_RE and RECORD_NAME_RE, cli.py's two isdigit checks) instead of model.pr_number, so 0 and leading zeros pass, the reading PL-4DK2 replaced

**Why it matters.** `model.pr_number` is the one reading of a `pr:` value. It refuses `0` and leading zeros, because GitHub never gives those numbers. `verify.py`'s `PR_VALUE_RE` and `RECORD_NAME_RE` and the `isdigit()` checks in `cli.py` accept both. So `docket verify` can accept a `pr: 07` that `docket check` refuses, and the two commands disagree about the same item.

**Done when.** Every place in `subprojects/docket/src/docket/` that reads a pull request number calls `model.pr_number`. `PR_VALUE_RE` and `RECORD_NAME_RE` are gone, and a test shows `verify` refusing `pr: 0` and `pr: 07`.

**Checked 2026-10-24.** `verify.py` defines `PR_VALUE_RE = re.compile(r"[0-9]+")` and `RECORD_NAME_RE = re.compile(r"[0-9]+\.md")`. `cli.py` has three `isdigit()` calls, not two, and the work should check which of them read a pull request number.

**Generator check.** A re-entry of `PL-4DK2`, closed 2026-10-18. It replaced the hand readings of a `pr:` number in `vcs` and `tools/pr_body_check.py` with `model.pr_number`, and missed these sibling sites. The misread fact is the head `PL-5DZ8`'s: "which spelling of a repeated predicate is the answer". Recorded 2026-10-24 as a member of the head `PL-N4FP`, because `tools/fact_home_check.py` has no rule that sees this form.
