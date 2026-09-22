---
id: PL-R5HK
title: docs/ARCHITECTURE.md's wired-hooks section says five scripts where settings.json wires six, so the count has been wrong since item_read_log.py was added
priority: P3
effort: S
status: done
classes: docs
feature: project-introduction
milestone: v0.5.3
touches: docs/ARCHITECTURE.md
added: 2026-09-19
closed: 2026-09-22
pr: 887
verify: ! grep -q 'The five scripts' docs/ARCHITECTURE.md
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

**Confirmed against the tree, 2026-09-19.** `.claude/settings.json` wires six:
`docket-branch-guard.sh`, `docket-digest.sh`, `floor-interpreter-guard.sh`,
`item_read_log.py`, `no-prune-guard.sh`, `stop_hook_patch.py`. The directory
holds those six plus `ruff.toml`, which is configuration rather than a hook.
`docs/ARCHITECTURE.md:983` still opens the section with "The five scripts".

**Why it matters.** `docs/ARCHITECTURE.md` is written for a reader of the
simulator, which is why `docket.toml`'s `workflow_paths` deliberately excludes
it - so this sits on the side `CLAUDE.md` holds to the specialist standard, and
a count a reader can falsify in one `ls` is the cheapest possible way to teach
them the document is not maintained. The concrete loss is the section's own
argument: it exists to explain *why* hooks live under `.claude/` rather than
`tools/`, and a reader who has just caught the opening clause being wrong
discounts the reasoning that follows it.

The mechanism is the one that matters more than this instance. The count has
been one short since `item_read_log.py` was wired in `34c96e3` (`#527`,
2026-09-13) with the prose left at "four", and `PL-JQJQ` (`95f5d65`, `#630`,
2026-09-16) then added a sixth hook and bumped the sentence four to five -
incrementing the number it found rather than recounting the directory, so a
correct-looking edit carried the off-by-one forward. Two independent edits and
neither caught it, which is what says no reader will.

**Done when.** The sentence agrees with `.claude/settings.json`, and the
agreement is either held there by a check or removed as a claim - `PL-5N7T`
carries the general rule for a marked prose enumeration and this is its second
caller in the same document.

**Closed by `PL-D0W8`'s docs sweep, 2026-09-22.** Found again independently,
from the other direction: that item wired a sixth Bash guard
(`.claude/hooks/gate-status-guard.sh`), which made this section's count wrong by
*two*, and its close-out sweep read the section and recounted the file rather
than incrementing what it found. The sentence now reads seven, and the
by-name list beside it - which had never picked up `item_read_log.py` either -
names every wired script but `stop_hook_patch.py`, which the next paragraph
covers on its own.

**The mechanism is not closed with it, and that is deliberate.** This brief
argued the durable remedy is `PL-5N7T`'s `tools/doc_check.py` rule holding a
marked prose enumeration to the file it enumerates, priced against two callers
rather than one. That rule is still unbuilt and `PL-5N7T` still carries it, so
nothing yet stops the count going wrong a fourth time - only this instance is
gone. The recount happened because a sweep was run, which is judgment rather
than a gate, and this is now the third time the same sentence has drifted.
