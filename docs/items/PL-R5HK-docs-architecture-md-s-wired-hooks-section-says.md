---
id: PL-R5HK
title: docs/ARCHITECTURE.md's wired-hooks section says five scripts where settings.json wires six, so the count has been wrong since item_read_log.py was added
status: untriaged
added: 2026-09-19
---

**Problem.** docs/ARCHITECTURE.md's wired-hooks section says five scripts where settings.json wires six, so the count has been wrong since item_read_log.py was added

`docs/ARCHITECTURE.md:983` opens the wired-hooks section with "The five scripts
`.claude/settings.json` wires as hooks". Six are wired today, and six live in
`.claude/hooks/`: `stop_hook_patch.py`, `docket-digest.sh`,
`docket-branch-guard.sh`, `no-prune-guard.sh`, `floor-interpreter-guard.sh`,
`item_read_log.py`.

**The count has been one short since 2026-09-13, and the edit that should have
caught it carried the error forward instead.** `item_read_log.py` was wired in
`34c96e3` (`#527`, 2026-09-13) with the prose left at "four". `PL-JQJQ`
(`95f5d65`, `#630`, 2026-09-16) then added `floor-interpreter-guard.sh` as a
sixth and bumped the sentence four to five — incrementing the number it found
rather than recounting the file, so a correct-looking edit preserved the
off-by-one.

**Same mechanism as `PL-5N7T`** (nothing checks a prose enumeration of
`quality.yml`'s bare-interpreter commands, so it has drifted silently twice in
one day), and the same remedy would close both: that item proposes a
`tools/doc_check.py` rule holding a marked prose enumeration to the file it
enumerates. This is a second instance in the same document, so the rule is worth
pricing against two callers rather than one. They are filed separately because
`PL-5N7T` already carries `feature: project-introduction` and regrouping it
would mean editing an item this branch has no other business in.

**Found.** 2026-09-19, by `doc_check.py candidates --base origin/main` during
the close-out sweep on `#715`, which flagged `docs/ARCHITECTURE.md:983` for that
branch's one-line `.claude/settings.json` change. The finding is the base's, not
that branch's: `#715` adds `subagentPromptCacheTtl` and wires no hook. Not fixed
there because `docs/ARCHITECTURE.md` is outside its `touches`, which is the
fix-now door's second test.
