---
id: PL-LLWN
title: No check holds a .claude/rules/ paths: entry to the repository root, so every glob silently matches the same name at any depth
status: ready
priority: P2
effort: S
classes: defect, infra
feature: worker-instructions
touches: tools/rules_paths_check.py, tests/unit/test_rules_paths_check.py, Makefile, .github/workflows/quality.yml, .claude/rules/apparatus-standard.md, .claude/rules/citing-sources.md, .claude/rules/core-domain.md, .claude/rules/ui-color.md
added: 2026-09-05
verify: python3 tools/rules_paths_check.py && grep -q 'def test_an_unanchored_entry_is_refused' tests/unit/test_rules_paths_check.py
---

**Problem.** Every `paths:` entry across `.claude/rules/` is written as if it
were relative to the repository root, and none of them is. Measured against
this harness on 2026-09-05, an unanchored entry matches the same name at any
depth, and a leading `/` is what anchors it:

| `paths:` entry | root | `subprojects/docket/…` |
| --- | --- | --- |
| `"zzp.md"` (bare file) | fires | fires |
| `"/zzp.md"` | fires | does not fire |
| `"./zzp.md"` | does not fire | does not fire |
| `"zzdir/**"` (bare directory) | fires | fires |
| `"/zzdir/**"` | fires | does not fire |

`PL-ZQ35` fixed the one entry where the collision was already real
(`readme-hold.md`'s `README.md`, against three files of that name).
`PL-H588` carried a second live instance (`expert-review.md` reaching
`subprojects/docket/src/` and `tests/`) and was dropped when `PL-WWDT` made
that file resident, deleting its `paths:` outright. The rest are latent: they
match one file today and would silently widen the moment a second file of that
name appears anywhere in the tree. `.claude/rules/sources-and-docstrings.md`,
added by `PL-WWDT`, is the first rule written anchored from the start.

**Why it matters.** Both failure directions are silent, and a rule is trusted
in a way a check is not. A rule that fires where it should not is read as
in force by everyone who wrote it (`PL-3V4N` makes the same argument about
delivery), and a rule that fires nowhere — the `./` row above — leaves no trace
at all. This is also a growth problem rather than a fixed one: `subprojects/`
exists precisely so a second tree can live here, so every unanchored glob is a
collision waiting for a directory nobody has created yet.

**Where.** A new check under `tools/`, wired into `make check` and so into CI's
`floor` job. `.claude/rules/*.md` are the inputs.

**Approach.** The rule is exact and needs no judgment, which is what
`CLAUDE.md` § "Prefer deterministic tooling over repeated model work" asks
for: **every `paths:` entry in `.claude/rules/*.md` starts with `/`**. Parse
the YAML frontmatter with the standard library only (these run from a bare
checkout), and hard-fail with the offending file, the entry, and the anchored
spelling to replace it with. A `./` entry is worth naming separately in the
message, since it is the spelling that matches nothing.

Anchoring every entry is the other half, and it is mechanical: seven rule
files, of which `instruction-writing.md` carries no `paths:` at all — it is
resident by necessity. `PL-ZQ35`'s brief listed it as path-scoped; that was
corrected while closing `PL-ZQ35`.

Deliberately not attempted: deciding whether a rule's glob describes the right
set of files. That is the judgment half, it differs per rule, and a check that
guessed at it would be the "worse than no tool" case `CLAUDE.md` names.
`PL-H588` is that judgment for one rule.

**Done when.** `make check` fails on a `.claude/rules/*.md` `paths:` entry that
does not begin with `/`, every current entry is anchored, and the check names
the replacement spelling rather than only the offence.
