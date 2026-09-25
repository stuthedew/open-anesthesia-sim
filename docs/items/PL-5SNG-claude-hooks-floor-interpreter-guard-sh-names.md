---
id: PL-5SNG
title: .claude/hooks/floor-interpreter-guard.sh names one 3.11 collision (app_metadata.py) and six uv-run tools, where app/bookmarks.py:451 is a second collision and seven ast tools run under uv, and neither its comments nor its deny message say doc_check and possessive_section_check also parse source and decline at the floor
priority: P3
effort: S
status: ready
classes: docs
touches: .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_floor_interpreter_guard.py
added: 2026-09-24
payoff: a session that hits the 3.11 floor is told the true set of collisions and uv-run tools, so it does not re-derive a second SyntaxError on main as a defect
verify: grep -qF 'app/bookmarks.py' .claude/hooks/floor-interpreter-guard.sh && grep -qF 'fixture_id_check.py' .claude/hooks/floor-interpreter-guard.sh && ! grep -qF 'The collision is one line' .claude/hooks/floor-interpreter-guard.sh && ! grep -qF 'the CI floor section run these bare on purpose' tests/unit/test_floor_interpreter_guard.py
---

**Problem.** .claude/hooks/floor-interpreter-guard.sh names one 3.11 collision (app_metadata.py) and six uv-run tools, where app/bookmarks.py:451 is a second collision and seven ast tools run under uv, and neither its comments nor its deny message say doc_check and possessive_section_check also parse source and decline at the floor

**Found 2026-09-24, closing `PL-MB3F`.** Read against the tree at that close:

- Line 15 says "The collision is one line", naming `app_metadata.py:92`
  (PEP 758). `app/bookmarks.py:451` (PEP 695, `def _looked_up[Mark: ...]`)
  has also failed under 3.11 since 2026-09-20.
- Line 40 says `make check` runs "six of them under `uv run python`". It runs
  seven ast-parsing tools there, and since `PL-MB3F` also `doc_check.py` and
  `possessive_section_check.py`.
- The deny message (lines 137-141) lists six tools, missing
  `fixture_id_check.py`, and names only `app_metadata.py`.
- `tests/unit/test_floor_interpreter_guard.py:86-88` allows
  `python3 tools/doc_check.py check` on the ground that "`make check` and the
  CI floor section run these bare on purpose". Only the CI floor section does
  now. The allowance itself is still right: bare `doc_check` names what it
  cannot parse rather than failing.

Wording only. What the hook refuses is unchanged.

**Re-confirmed 2026-09-25 against 46954a81.** Bare `python3` (3.11.15) fails
`ast.parse` on `src/anesthesia_sim/app/bookmarks.py` at `def _looked_up[Mark:
...]` with `SyntaxError: expected '('`. The hook still says "The collision is
one line" and "runs six of them under `uv run python`", and its deny message
still ends its six-tool list at `glyph_check.py`. The `Makefile` runs seven
ast-parsing tools under `uv run python` (the six plus `fixture_id_check.py`),
and `doc_check.py` and `possessive_section_check.py` too. Only
`.github/workflows/quality.yml`'s floor section still runs `python3
tools/doc_check.py check` bare.

**Why it matters.** The comments and the deny message are what a session or a
subagent reads when it hits the 3.11 floor. They say there is one collision.
A session that reproduces the floor on purpose, as the hook's own comment
teaches (`/usr/bin/python3.11 -m compileall src/`), then meets a second
SyntaxError the hook says does not exist. It is set up to re-derive that as a
defect on `main`, which is the round `PL-JQJQ` built the hook to save. Nothing
is let through, because the refusal itself is unchanged, so this is wording
and not a gap.

**Done when.** The hook's comments and deny message are true of today's tree
about the collisions the floor hits and the tools `make check` runs under
`uv run`. That means either listing them in full or wording them so the list
cannot drift. They also say that `doc_check.py` and
`possessive_section_check.py` decline at the floor rather than fail. The
comment above `ALLOWED` in `tests/unit/test_floor_interpreter_guard.py` says
only the CI floor section runs `doc_check` bare. The `verify:` below pins the
list-in-full reading, and a worker who takes the other reading corrects it.

**Generator check.** An instance of `PL-G424`'s fact, the link between a
document sentence and the tree fact it restates. It was filed 2026-09-24,
after that head closed on 2026-09-19. The hook's comments and deny message
restate the `Makefile`'s `uv run` list and the set of 3.14-only files, and
nothing links them. The head's recorded fix, `.claude/rules/citation-drift.md`,
is path-scoped to `docs/items/**`, `docs/WORKING_NOTES.md` and
`.claude/skills/**`, so it never loads on `.claude/hooks/`. That is the reason
this was filed rather than repaired in place. It is the only post-close
instance of that head recorded so far, so there is no new head. It is not
`PL-PVW2`'s, even though that head's `PL-GVFC` and `PL-BBV7` share this hook.
The hook evaluates nothing from these lists; they are prose.
