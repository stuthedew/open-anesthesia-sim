---
id: PL-8XPQ
title: Nothing checks that an interface string uses glyphs the Flutter client can actually draw
priority: P2
effort: M
status: ready
classes: defect, infra
feature: presentation-safety
touches: tools/glyph_check.py, tests/unit/test_glyph_check.py, Makefile
added: 2026-09-04
verify: uv run pytest tests/unit/test_tools_portability.py && python3 tools/glyph_check.py
---

**Problem.** `→` (U+2192) has no glyph in the Flutter client this interface
renders in, and drew as a replacement box in the control-change list on
2026-09-04. Nothing in the repository could have caught it: every string
assertion here compares text the same font-less Python process produced, so
the test suite is blind to whether the client can draw what it is given.

**Why it matters.** The character that failed was the arrow in
`5.60% -> 0.95%` - the direction of a setting change, which is the one thing
that line exists to state. `CLAUDE.md` treats presentation correctness as
part of the safety standard, and a displayed value whose meaning arrives as
a missing character is a presentation failure whatever the number beside it
says. The failure mode is silent, it is invisible to the whole test suite,
and the next non-ASCII character somebody reaches for will hit it again.
`·`, `–`, `—`, `×`, `±` and `%` are confirmed to render; the confirmed set
is small and nobody has written it down outside one test's docstring.

**Where.** A new `tools/` check, wired into `make check`, plus wherever the
confirmed set is recorded.

**Approach.** The decidable half is cheap: parse `src/anesthesia_sim/app/`
with `ast` (as `tools/contrast_check.py` already does, and for the same
reason - these tools run under a bare `python3` and the app imports Flet),
collect every string literal that reaches a display, and fail on any
character outside a declared allowlist. Adding a character to the allowlist
is then a deliberate act that says "I rendered this and saw it". What the
tool must *not* try to decide is whether an unlisted character would in
fact render: that needs a real client, and a tool guessing at it would be
worse than none.

**Not yet decided.** Whether the allowlist is per-character or a named
Unicode-block set, and whether the check covers `docs/` strings that never
reach the client (it should not).

**Done when.** A non-renderable character added to a displayed string fails
`make check` rather than reaching a reader as a box.
