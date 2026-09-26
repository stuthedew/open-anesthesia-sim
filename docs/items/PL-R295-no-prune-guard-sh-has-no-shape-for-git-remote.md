---
id: PL-R295
title: no-prune-guard.sh has no shape for git remote remove or git remote rm, which delete every remote-tracking ref of the named remote at once - git remote remove origin leaves no origin/<branch> at all, a stranded item's only copy among them - so the one git spelling that deletes more refs than a prune runs unrefused
status: untriaged
feature: bash-guard-bound
added: 2026-09-26
---

**Problem.** no-prune-guard.sh has no shape for git remote remove or git remote rm, which delete every remote-tracking ref of the named remote at once - git remote remove origin leaves no origin/\<branch> at all, a stranded item's only copy among them - so the one git spelling that deletes more refs than a prune runs unrefused
