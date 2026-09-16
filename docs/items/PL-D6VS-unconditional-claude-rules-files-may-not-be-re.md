---
id: PL-D6VS
title: Unconditional .claude/rules/ files may not be re-injected after a compaction while CLAUDE.md is, which would silently drop every format rule
status: dropped
closed: 2026-09-16
reason: Refuted by the documentation the day it was filed. Claude Code's context-window reference lists "Project-root CLAUDE.md and unscoped rules" as re-injected from disk after compaction, so the two resident rules files - both carrying no `paths:` frontmatter - come back exactly as CLAUDE.md does and the supposed asymmetry does not exist. The real asymmetry is in skill bodies, which return truncated to 5,000 tokens from the start of the file; that is PL-2XM2.
added: 2026-09-16
---

**Refuted the day it was filed, by the documentation.** Claude Code's context
window reference lists "Project-root CLAUDE.md **and unscoped rules** —
Re-injected from disk" after compaction
([context window](https://code.claude.com/docs/en/context-window),
§ "What survives compaction"). `.claude/rules/instruction-writing.md` and
`.claude/rules/expert-review.md` carry no `paths:` frontmatter and are
therefore unscoped, so both come back after a compaction exactly as
`CLAUDE.md` does. The asymmetry this item supposed does not exist.

Recorded rather than deleted because the reasoning was sound and the same
question will be asked again: what *is* asymmetric is skill bodies, which come
back truncated to 5,000 tokens per skill from the start of the file. That is
`PL-2XM2`.
