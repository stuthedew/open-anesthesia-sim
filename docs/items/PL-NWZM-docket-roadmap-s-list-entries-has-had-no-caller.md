---
id: PL-NWZM
title: docket roadmap's list_entries has had no caller since the Markdown batch of 2026-10-10, and its docstring and three others still describe it as the walker three readers share
priority: P3
effort: S
status: done
classes: refactor
milestone: v0.5.25
touches: subprojects/docket/src/docket/roadmap.py, tools/doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-17
pr: 1475
payoff: The list walker's docstrings point at the functions that run, with no dead walker beside them to fix by mistake.
verify: ! grep -q 'def list_entries(' subprojects/docket/src/docket/roadmap.py && ! grep -qF 'reason `list_entries` gives' tools/doc_check.py
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

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`: `git grep -n list_entries`
gives the definition, the docstrings of `list_entry_lines` and `_section_end`
in `roadmap.py` and of `doc_check._list_members` (twice), and no call under
`subprojects/`, `tools/`, `.claude/hooks/` or `tests/`. `_entry_text`, which it
calls, has two other callers and stays.

**Generator check.** Not a member of `PL-R417`: dead code and the prose that
describes it; nothing reads a format through it.

**Why it matters.** A docstring naming a dead function as the walker three
readers share sends the next reader of the list walker to code nothing runs,
and a fix to how list entries are read could be made there and change nothing.
Dead code also keeps `LITERAL_BLOCKS`' omission (`PL-KR6M`) in one more place a
fixer has to check.

**Done when.** `list_entries` is removed, or given a caller, and the four
docstrings name the reader each caller now takes.

**Decided at triage 2026-10-11.** Remove it rather than give it a caller: every
reader now takes `list_entry_lines` or `document_entry_lines` directly, and the
joined text it yields is what `_entry_text` already gives its two callers. The
`verify:` holds the removal and the stale doc_check sentence.
