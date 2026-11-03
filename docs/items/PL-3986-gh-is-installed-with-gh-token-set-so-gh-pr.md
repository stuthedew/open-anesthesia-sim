---
id: PL-3986
title: gh is installed with GH_TOKEN set, so gh pr merge, gh api .../merge and gh pr create --body reach every action the merge and email guards exist to stop, and no Bash guard reads them; direct-merge-guard.sh calls the gap safe because the base binds admins, which is the state the guard exists for losing
status: untriaged
feature: guards-keyed-on-the-action
added: 2026-11-03
---

**Problem.** gh is installed with GH_TOKEN set, so gh pr merge, gh api .../merge and gh pr create --body reach every action the merge and email guards exist to stop, and no Bash guard reads them; direct-merge-guard.sh calls the gap safe because the base binds admins, which is the state the guard exists for losing
