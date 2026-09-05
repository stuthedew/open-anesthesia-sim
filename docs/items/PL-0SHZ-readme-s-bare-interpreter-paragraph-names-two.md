---
id: PL-0SHZ
title: README's bare-interpreter paragraph names two ruff.toml pins and there are now three, since .claude/hooks/ carries one too
priority: P3
effort: S
status: blocked
classes: docs, defect
feature: project-introduction
touches: README.md
blocked-by: PL-N092
added: 2026-09-05
---

**Problem.** `README.md:185-192` says that running in a bare checkout means
running under whatever `python3` is on PATH, and that `tools/ruff.toml` and
`subprojects/docket/ruff.toml` "therefore pin the formatter to that floor".
There are three such trees now. `#340` (`PL-W4H9`) moved the stop-hook patch
under `.claude/hooks/`, which is invoked as bare
`python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/stop_hook_patch.py"` at session start
and carries its own `ruff.toml` for exactly the reason the paragraph gives.

**Sharper than the title, measured at triage 2026-09-05.** There are three
`ruff.toml` files and two pins: `.claude/hooks/ruff.toml` is one line,
`extend = "../../tools/ruff.toml"`, deliberately, so the floor is declared once.
So the sentence is not wrong about the pins - it is incomplete about the trees,
which is what a reader is counting when they read it.

**Why it matters.** The paragraph is the map of which trees run outside the
project virtualenv, and the guard it describes is what stops a formatter aimed
at 3.14 rewriting them into syntax the older interpreter cannot parse - which
has happened once in this tree. A reader who counts two trees does not look for
the third, and a hook added to `.claude/hooks/` inherits that guard by being put
where hooks go, which is the property the README stops short of stating.
`tests/unit/test_tools_portability.py` already covers both directories, so
nothing is unguarded today; only the description is short.

**Where.** `README.md`, the bare-interpreter paragraph, lines 185-192.

**Not fixed here because.** `.claude/rules/readme-hold.md` freezes `README.md`
until the owner has settled what the document is for (`PL-RM83`), and that rule
names this exact case - a correct fact found in passing - and says to file it
rather than fix it.

**Done when.** The paragraph names all three trees that run under the bare
interpreter and says that the third inherits the pin rather than restating it.
Fold it into `PL-N092` (rewrite README as a human-readable introduction) if that
lands first, alongside `PL-BTSW` (the wrapping defect in the neighbouring
sentences) and `PL-QM5P` (the stale `candidates` gloss).
