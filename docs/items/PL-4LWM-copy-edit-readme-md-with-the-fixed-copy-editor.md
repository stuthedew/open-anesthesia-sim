---
id: PL-4LWM
title: Copy edit README.md with the fixed copy editor: apply its structure read, then line-edit each section except the blind-test section 'What it is for'
status: untriaged
feature: repo-copy-edit
added: 2026-11-05
---

**Problem.** README.md had not been through the copy editor since its fix (`PL-HGZS`, #2038). The project owner asked on 2026-11-05 for every human-facing document to be copy edited, skipping text the copy editor had already edited (thread "Copy edit the entire repository"). README's § "What it is for" was used in the copy editor's blind test, so it is left as it is.

**How.** `python3 tools/copy_edit.py --structure README.md`, then the accepted findings applied by hand, then each section line-edited alone with the four-read audit. Runs and replies are in `/mnt/project-files/v0.7.0/repo-copy-edit/runs/README-md/`.

**Done when.** Every README section except § "What it is for" has been line-edited, the structure findings are applied or answered, and no command, link, value or citation was lost.
