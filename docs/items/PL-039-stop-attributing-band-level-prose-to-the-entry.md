---
id: PL-039
title: Stop attributing band-level prose to the entry above it
status: dropped
added: 2026-08-24
closed: 2026-08-25
reason: obsolete: the single-file parser it described was deleted with docs/PUNCH_LIST.md
---

**Problem.** `tools/punch_list.py` ends an entry's body at the next `###` or
`##` heading, so any prose written between entries — a band-level note, a
running-order paragraph — is parsed as part of the preceding entry. This is
not theoretical: the P1 band's running-order note was silently counted into
PL-037's body, pushing it to 35 lines and firing a spurious
`MAX_ENTRY_LINES` advisory against an entry that was within its brief.
**Why it matters.** The line count is the visible symptom; `Entry.blockers`
is the real one. It reads `PL-` references out of the same body, so a band
note that mentions an item would be read as a dependency of whichever entry
happens to sit above it, and a `blocked` item could be promoted or held on a
reference nobody wrote about it.
**Where.** `tools/punch_list.py`, `parse()` and `Entry.blockers`;
`tests/unit/test_punch_list_tool.py`.
**First step.** Decide whether band notes are legal in the format at all. If
they are, end an entry's body at the first blank-line-separated block that
is not part of its brief, and give the file's "Entry format" section a line
saying where a band note may go. If they are not, make one an error.
**Done when.** A band-level note between two entries changes neither the
preceding entry's line count nor its blockers, with a test that fails on
today's parser.
**Context.** Found while grooming the P1 band on 2026-08-24; the stale note
that triggered it was rewritten in the same pass.
