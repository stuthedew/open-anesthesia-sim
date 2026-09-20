---
id: PL-H71N
title: Thirteen open items declare touches: .claude/skills/docket/SKILL.md, but the docket skill's modes now live in .claude/skills/docket/modes/, so bin/docket concurrent under-reports contention between items whose work lands in the same mode file
status: untriaged
added: 2026-09-20
---

**Problem.** Thirteen open items declare touches: .claude/skills/docket/SKILL.md, but the docket skill's modes now live in .claude/skills/docket/modes/, so bin/docket concurrent under-reports contention between items whose work lands in the same mode file

**Found 2026-09-20**, while splitting the skill under `PL-2XM2`.
`bin/docket concurrent PL-2XM2` named thirteen open items declaring that one
path: `PL-0QRP`, `PL-6YYR`, `PL-CPLX`, `PL-G8TR`, `PL-HX5C`, `PL-KKRP`,
`PL-M21Q`, `PL-NGLM`, `PL-PNW6`, `PL-SY1J`, `PL-VYK1`, `PL-WVJ0`, `PL-WXX8`.

**Why it matters.** `SKILL.md` is now a 5,101-character front page; the prose
those items are about moved into `.claude/skills/docket/modes/`. Two items
whose work lands in the same mode file now share a file that neither declares,
so `concurrent` reports no overlap where there is one - and it reports overlap
on `SKILL.md` for two items that will never touch the same line of it. Both
directions are wrong, and the second trains a reader to discount the answer.

**Not urgent, and deliberately not done inside `PL-2XM2`.** Re-pointing each
one means deciding which mode file its work lands in, which is scoping thirteen
items this session has not read. Declaring the directory - `touches:
.claude/skills/docket` - is the cheap answer and `concurrent` already handles a
coarser declaration against a finer one ("Same area only"), but it is still a
judgment per item rather than a rewrite, so it wants a pass of its own.

**Done when.** Each of the thirteen declares a `touches` that names where its
work actually lands, and `bin/docket concurrent` on any two of them reports the
overlap they really have.
