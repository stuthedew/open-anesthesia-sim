---
id: PL-JT7Y
title: docket reads a pull request number by hand in four places (verify.py PR_VALUE_RE and RECORD_NAME_RE, cli.py's two isdigit checks) instead of model.pr_number, so 0 and leading zeros pass, the reading PL-4DK2 replaced
status: untriaged
feature: one-source-of-truth
added: 2026-10-19
---

**Problem.** docket reads a pull request number by hand in four places (verify.py PR_VALUE_RE and RECORD_NAME_RE, cli.py's two isdigit checks) instead of model.pr_number, so 0 and leading zeros pass, the reading PL-4DK2 replaced
