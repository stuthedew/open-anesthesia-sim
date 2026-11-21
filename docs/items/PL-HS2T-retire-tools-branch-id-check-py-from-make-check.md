---
id: PL-HS2T
title: Retire tools/branch_id_check.py from make check, CI and the push hook
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** Retire tools/branch_id_check.py from make check, CI and the push hook

**Why it matters.** `PL-LY24` counted what each workflow-record check refused in CI from 2026-08-22 to 2026-11-21, and the owner agreed in `PL-KGPR` to retire this one (project owner, 2026-11-21, ratified, "Agree with recs"). Its 12 refusals caught no mistake: 10 asked for a claim on a branch whose commit subjects already named its item, and 2 were the owner's own edit on GitHub's web page. It has cost 21 items. `bin/docket claim` still writes claims.

**What to do.** Remove the check from `make check`, `.github/workflows/quality.yml` and the push guard hook, then delete the tool and its test. Leave the claim record alone.

**Done when.** No command, workflow or hook runs `tools/branch_id_check.py`, and the file and its test are gone.
