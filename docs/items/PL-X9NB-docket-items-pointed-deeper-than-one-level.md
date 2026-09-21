---
id: PL-X9NB
title: docket --items pointed deeper than one level below the repository root makes cli root the store's parent, so ls-tree prints cwd-relative paths that git show cannot resolve and stranded reports every title as unreadable
status: dropped
added: 2026-09-21
closed: 2026-09-21
reason: duplicate of PL-P757, which names the same args.items.parent derivation in cli._tracked and _load; filed by the recurrence signal on 2026-09-21 and recorded there as a recurrence. The new symptom it carried - ls-tree's cwd-relative paths breaking every git show, so stranded prints every title as unreadable - is appended to PL-P757's brief as evidence.
---

**Problem.** docket --items pointed deeper than one level below the repository root makes cli root the store's parent, so ls-tree prints cwd-relative paths that git show cannot resolve and stranded reports every title as unreadable
