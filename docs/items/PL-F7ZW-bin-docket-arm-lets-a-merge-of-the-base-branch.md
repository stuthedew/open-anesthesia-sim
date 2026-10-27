---
id: PL-F7ZW
title: bin/docket arm lets a merge of the base branch cancel a branch's Owner-read record but not its Owner-ask record, so a routine update from main makes an armed housekeeping pull request answer hold and tells the session to disarm it
status: untriaged
touches: subprojects/docket/src/docket/arming.py
added: 2026-10-27
---

**Problem.** bin/docket arm lets a merge of the base branch cancel a branch's Owner-read record but not its Owner-ask record, so a routine update from main makes an armed housekeeping pull request answer hold and tells the session to disarm it

Found on 2026-10-27 while merging #1844 (`PL-ZR49`). `docket.arming._since_change` takes `merges`, and its docstring says that without merges "a merge does not count as a change, so bringing the base in, which the owner's *Update branch* does, leaves a record standing". `_owner_ask` passes `merges=False`, but `_owner_read` uses the default `merges=True`. So after `git merge origin/main`, which changed no line of the branch's own work, `bin/docket arm` answered "no Owner-read record on a commit since its newest change there says whether the owner must read it". The `Owner-ask` record still stood. For a `needed` record this costs a restated trailer. For a `not needed` record on an armed pull request, the same answer tells the session to disarm it before pushing a plain update from `main`. Decide whether the read record should survive a merge of the base, as the ask record does, or say why the two differ. Any fix keeps or adds the test that pins the answer.
