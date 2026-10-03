---
id: PL-40SJ
title: A simulator number has no enforced single home: nothing refuses a second literal copy of a value src/ already names, so the copies drift (PL-T5J5, PL-TCW5, PL-QRBB, PL-DJYF, PL-4YY1, PL-8DJ7, PL-017) and the rule lives only in prose; extend the colours' one-home check to numeric literals, ratcheted from today's count
status: untriaged
feature: one-home-for-constants
touches: tools, Makefile, .github/workflows/quality.yml, tests/unit, src/anesthesia_sim
added: 2026-10-03
root-cause-of: PL-T5J5, PL-TCW5, PL-QRBB, PL-DJYF, PL-4YY1, PL-8DJ7, PL-017
generator: live - three of its members were filed on 2026-10-03 alone (PL-T5J5 and its two derived-state siblings PL-8H2R and PL-5291), and nothing in make check yet refuses a second literal copy of a named value
misread: the value of a named constant, read from its one definition rather than typed again at the use
---

**Problem.** A simulator number has no enforced single home: nothing refuses a second literal copy of a value src/ already names, so the copies drift (PL-T5J5, PL-TCW5, PL-QRBB, PL-DJYF, PL-4YY1, PL-8DJ7, PL-017) and the rule lives only in prose; extend the colours' one-home check to numeric literals, ratcheted from today's count

**Why it matters.** Seven closed or open items are one mechanism: a value `src/` already names was typed again somewhere else, and nothing held the two equal until they disagreed. The rule against it is resident prose in `CLAUDE.md` § "Architecture and development discipline", and prose is applied at a session's discretion at the moment of writing; a check in `make check` is applied at every commit. The three architecture bullets that have a check today (toolkit independence, no wall clock in `core/`, determinism) hold with zero violations in the tree; the two without one recur. The project owner asked on 2026-10-03 how to make best practice hold rather than be asked for again.

**Mechanism, measured 2026-10-03.** An `ast` walk over `src/anesthesia_sim/` (run with `uv run python`, since the package uses 3.14 syntax) counting numeric `Constant` nodes outside a module-level assignment, excluding 0, 1 and -1: 80 literals, 68 in `app/` and 12 in `core/`, 16 distinct values. `2` is 27 of them; `3600.0` is 7 (PL-06M7); `12`, `6`, `4` and `8` are display geometry in `app/qt_widgets.py` (25) and `app/qt_chart.py` (13). So the retrofit is small, and the ratchet starts from a baseline of at most 80, every entry named in the tool with its file.

**Shape.** `tools/literal_home_check.py`, standard library only, wired beside the `import_boundary_check` line of `Makefile` and `.github/workflows/quality.yml`. Rule: in `src/anesthesia_sim/`, a numeric literal other than 0, 1 and -1 may appear only as the value of a module-level named constant, in a data file under `data/`, or in the tool's own baseline; any other occurrence fails with the file, the line and the name it should read. The baseline may only shrink: an entry that no longer matches fails too, so the count is a ratchet, as `tools/ignore_check.py` is for `type: ignore`. Precedent: `check_colors_live_in_the_theme` at `tools/contrast_check.py:1343` is this rule for colours. Whether `2` joins the exempt set is the one judgment: 27 sites, almost all halving a width or a span; recommend exempting it and saying why in the tool.

**What it does not catch, deliberately.** A derived value computed twice (PL-8H2R: step count and time bound as two calculations of one limit; PL-5291: a latch beside the state it could be derived from) has no literal to find; that is design judgment and types, which PL-0GJC's `SimulationStep` carries. Prose restating a number (`docs/MODEL.md:1758`, `:1800` and `:4166` restate the 24 h run length; PL-4FBP and PL-G424 are the heads) belongs to the prose-provenance family, not to this tool. Tests restating a constant are PL-0Z0F.

**Considered and refused.** Ruff `PLR2004` (`magic-value-comparison`) flags a literal only in a comparison, so none of the seven `3600` sites, none of PL-4YY1's assignments and neither of PL-TCW5's two definitions would have fired (`uv run ruff rule PLR2004`, ruff 0.16.4, read 2026-10-03). Pylint's `duplicate-code` finds repeated blocks, not one repeated value. Neither replaces the one-home rule; `PLR2004` could still be enabled for `app/` comparisons in a few lines of configuration, but that is not this item.

**Done when.** `make check` fails on a new bare numeric literal in `src/anesthesia_sim/` outside a module-level constant and the baseline; the baseline cannot grow; the seven items above are named in the tool's docstring as what it would have caught; `docs/ARCHITECTURE.md`'s single-source paragraph points at the tool.

**Generator check.** It is one, recorded in the fields above: seven members by literal copy, three of the family filed on 2026-10-03, and the store will hand more while nothing refuses the copy. The fix is the check; the item alone changes nothing.

**Sources.** Anthropic, *Best practices for Claude Code*, § "Set up hooks": "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens" (https://code.claude.com/docs/en/best-practices, read 2026-10-03). ISMP's hierarchy of effectiveness places education and policy as the least effective risk-reduction strategies and forcing functions at the top; Crozier N, Robinson E, Murtagh NC, Coyne BD, *Hosp Pharm* 2023;59(2):210-216, https://doi.org/10.1177/00185787231207995, found that errors limited to education interventions repeated while those addressed by systematic change did not recur.
