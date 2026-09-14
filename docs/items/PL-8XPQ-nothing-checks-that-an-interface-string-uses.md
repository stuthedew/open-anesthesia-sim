---
id: PL-8XPQ
title: Nothing checks that an interface string uses glyphs the Flutter client can actually draw
priority: P2
effort: M
status: done
classes: defect, infra
feature: presentation-safety
touches: tools/glyph_check.py, tests/unit/test_glyph_check.py, Makefile, .github/workflows/quality.yml, docs/ARCHITECTURE.md, docket.toml, tests/unit/test_tools_portability.py
added: 2026-09-04
closed: 2026-09-14
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

## Built 2026-09-14, with both open questions answered on evidence

`tools/glyph_check.py`, wired into `make check` and CI. A non-renderable
character added to a displayed string now fails the build, which is the
Done-when.

**"Whether the allowlist is per-character or a named Unicode-block set" —
per character.** A block defeats the point of the list. Latin-1 Supplement
admits `¤`, `þ` and `ð` alongside the `·`, `±` and `×` this interface has
actually shown, so a block set would admit thousands of characters on the
evidence of three, and "adding a character is a deliberate act that says I
rendered this and saw it" would stop being true the moment the first block went
in. Each entry carries its evidence, and a test asserts that it does.

**"Whether the check covers `docs/` strings that never reach the client (it
should not)" — it does not, and the scope question turned out to be the other
way round.** The brief's Approach names `app/`; measured against the code,
that is not the whole set of displayed strings:

- **`core/` is covered**, because the view prints its text verbatim.
  `SimulationView._apply_setting` renders `f"Setting refused — {error}"` from a
  `SimulationConfigurationError`, and `_halt_run` passes `str(error)` into the
  halted-run banner. A validation message is a displayed string with one more
  step in front of it.
- **`data/` is covered**, because `display_name` reaches the readouts through
  `AgentParameters`, and a data file is the one place an edit lands without
  touching Python.
- **`docs/` is not**, as the brief says.

Measured 2026-09-14: `core/` and `data/` hold no character this check refuses
today, so covering them cost nothing now and closed the two routes by which one
could have arrived unseen. **This widens the brief's stated `app/` scope**, and
is flagged as such rather than folded in quietly - the brief left the scope
question open, which is what made it the implementer's to decide.

**What the scan found in the shipped tree.** Seven distinct non-ASCII
characters in `app/` string literals. Five are the confirmed set. The other two
were the useful part:

- **`§`** appeared only in *attribute docstrings* - `app/controller.py`, and two
  `core/` modules - which a first-statement-of-a-scope docstring test would
  have missed, putting a prose character into a list that means *this was
  rendered*. So documentation is excluded by the structural test instead: a
  string that is a bare expression statement. That covers module, class,
  function and attribute docstrings, and nothing else is one.
- **U+00A0 NO-BREAK SPACE** is genuinely displayed and load-bearing.
  `EMPTY_METRIC_QUALIFIER` and `EMPTY_METRIC_SECONDARY_VALUE` in
  `app/simulation_view.py` draw a full line of the qualifier's size where a
  blank string collapses to zero height in Flutter, which is what keeps every
  reading in the readout row on one baseline. It has shipped rendered and
  observed, so it is in `CONFIRMED` with that reasoning.

**`CONFIRMED` is keyed by code point rather than by the character**, because
`ruff format` rewrites a `\uXXXX` escape into the literal character, and a
literal U+00A0 in the source would be invisible to a reader and
indistinguishable from the space beside it. Found by running the formatter,
not by reasoning about it.

**No rot guard, unlike `KNOWN_SHORTFALLS` in `tools/contrast_check.py`**, and
the asymmetry is deliberate and stated in the docstring. A listed shortfall
that starts passing is an error there because the entry is an expired excuse.
An entry here is a record of something somebody rendered and looked at, which
stays true after the last use of the character is deleted; dropping it would
throw the observation away and make the next person repeat it.

**It joins the `uv run python` group**, sixth of six, because it parses `src/`
with `ast` and `src/` targets 3.14 - the rule
`tests/unit/test_tools_portability.py` states, whose docstring, the `Makefile`
note and the CI note are all updated from five to six. It stays
standard-library-only and floor-parseable, so it remains in that suite's scope.

**What it must never decide**, stated in the tool: whether an *unlisted*
character would render. That needs a real client, and a tool guessing at it
would be worse than none. It refuses, and never approves.
