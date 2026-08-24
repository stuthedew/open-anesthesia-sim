---
id: PL-33CL
title: The listing-vs-file cost ratio is overstated in three places, and drifts
status: untriaged
touches: .claude/skills/punch-list/SKILL.md, tools/punch_list.py
added: 2026-08-24
---

`P3` · `S` · `docs`

**Problem.** `python3 tools/punch_list.py list` currently costs about a
seventeenth of reading `docs/PUNCH_LIST.md` (2,475 chars against 43,754).
`tools/punch_list.py` claims "roughly twenty-five times as much" in two
places, and `.claude/skills/punch-list/SKILL.md` claims "a fortieth". All
three disagree, and every one of them overstates the saving.
**Why it matters.** These numbers are the stated justification for reading
the listing instead of the file, so a session weighing the two is deciding
from a figure that is wrong. It is also self-inflicted drift: the ratio moves
every time an entry is added or completed, so any hardcoded multiplier is
wrong again within a few sessions.
**Where.** `tools/punch_list.py` (module docstring, `format_list` docstring),
`.claude/skills/punch-list/SKILL.md`.
**First step.** Decide whether to state the ratio qualitatively ("a fraction
of") in all three places, or to keep a number and have a test assert it. The
existing test `test_list_is_far_cheaper_than_the_file_it_summarizes` asserts
only `< len(document) / 4`, which is far weaker than any of the three claims
and is why the drift went unnoticed.
**Done when.** No document states a multiplier that the tool's own output
contradicts, and whatever claim remains is either qualitative or enforced by
a test.
**Context.** Found while writing CLAUDE.md's deterministic-tooling section,
which deliberately states no ratio at all rather than adding a fourth copy to
keep in sync.
