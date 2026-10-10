---
id: PL-NWZM
title: docket roadmap's list_entries has had no caller since the Markdown batch of 2026-10-10, and its docstring and three others still describe it as the walker three readers share
status: untriaged
added: 2026-10-10
---

**Problem.** docket roadmap's list_entries has had no caller since the Markdown batch of 2026-10-10, and its docstring and three others still describe it as the walker three readers share

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`docket.roadmap`. `a5f2df42` (`#1388`) removed the last two calls of
`roadmap.list_entries`, and nothing in `subprojects/docket/`, `tools/`,
`.claude/hooks/` or the tests calls it now. Its docstring still calls it "One
walker and three readers", and three more cite it as a live reader: the
docstrings of `list_entry_lines` and `_section_end` beside it, and that of
`doc_check._list_members`, twice.

**Reproduced 2026-10-10** on `main` at `75e1700d`: `git grep -n list_entries`
gives the definition and those four docstrings, and no call.

**Generator check.** Not a member of `PL-R417`: dead code and the prose that
describes it; nothing reads a format through it.

**Done when.** `list_entries` is removed, or given a caller, and the four
docstrings name the reader each caller now takes.
