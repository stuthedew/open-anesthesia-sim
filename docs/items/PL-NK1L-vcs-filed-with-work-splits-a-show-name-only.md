---
id: PL-NK1L
title: vcs.filed_with_work splits a show --name-only listing on whitespace, so a path holding a space is reported as two paths
status: untriaged
feature: one-answer
added: 2026-09-25
---

**Problem.** vcs.filed_with_work splits a show --name-only listing on whitespace, so a path holding a space is reported as two paths

Found 2026-09-25 by PL-8HSX. `vcs.filed_with_work` reads the filing commit's paths with `run(changed_path_args("show", "--format=", "--name-only", commit), root).split()`. `--name-only` does not quote a space, so `src/a b.py` arrives as the two words `src/a` and `b.py`, and both are reported as work filed beside the item. Every other `--name-only` reader in `vcs.py` splits on lines. An instance of PL-PVW2's "which files a branch changed", and a candidate member of its `root-cause-of:`.
