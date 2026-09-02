---
id: PL-1MK1
title: Compute colour-contrast ratios in make check instead of asserting them in comments
priority: P2
effort: M
status: done
classes: infra
feature: presentation-safety
touches: tools/contrast_check.py, tests/unit/test_contrast_check.py, Makefile, .github/workflows/quality.yml, docs/ARCHITECTURE.md, README.md
added: 2026-09-02
closed: 2026-09-02
pr: 183
verify: uv run pytest tests/unit/test_contrast_check.py && grep -q 'def test_a_shortfall_that_starts_passing_is_an_error' tests/unit/test_contrast_check.py
---

**Problem.** Every contrast claim in the tree is prose. `app/theme.py:53-56`
asserts that each agent fill/foreground pair "exceeds WCAG 2.2's 4.5:1 minimum
for normal text"; nothing computes it. `docs/MODEL.md` records simulated
protanopia/deuteranopia/tritanopia contrasts for the three agent colours;
nothing recomputes them when a colour changes. `PL-GVXP` measured the six trace
colours at 1.01-2.93 by hand. A colour edit today can silently falsify a
documented safety claim, and the only thing standing between that and a reader
is whoever remembers to re-measure.

**Why it matters.** This is the decidable half of the whole accessibility goal.
WCAG 2.x relative luminance and contrast ratio are closed-form arithmetic over
two sRGB triples — no judgment, no ambiguity, identical answer every run. It is
exactly the case `CLAUDE.md`'s "Prefer deterministic tooling over repeated model
work" describes: work moved into a script is paid for once, work left to a
session is re-derived at full context every time a colour changes. Every future
UI item picks colours, so it genuinely runs again.

It also converts three documentation claims from "trust the comment" to
"checked on every `make check`", which is the auditability half of the
safety-critical standard rather than a tidiness win.

**Approach.** A `tools/contrast_check.py`, standard library only (per
`CLAUDE.md`, so a hook or bare checkout can run it), wired into `make check`
beside `tools/doc_check.py`. Three parts:

1. The WCAG 2.2 relative-luminance and contrast-ratio functions, with the
   specification linked in the docstring so a reviewer can check the arithmetic
   against the source rather than against the author.
2. A declared table of the pairs that must hold and the ratio each must meet,
   *with the reason* — foreground-on-fill for each agent at the text minimum,
   each trace against the panel at the graphical-object minimum, and the
   pairwise trace separations `PL-GVXP` establishes. The table is the
   specification; the script only evaluates it.
3. Failure output that names the pair, the required ratio, the measured ratio,
   and the constant to change.

**Do not script the judgment.** The script decides whether a ratio is met. It
must not decide whether a colour is "text" or a "graphical object", whether two
traces are adjacent enough to need separating, or whether a non-colour channel
is genuinely redundant. Those stay in the declared table, written by a person.

**Where.** New `tools/contrast_check.py`; `Makefile` (beside the `doc-check`
target); reads `src/anesthesia_sim/app/theme.py` and
`src/anesthesia_sim/app/simulation_view.py:110-113,255-256`.

**Depends on.** `PL-MMYM` for the ratios to assert, though the WCAG 2.2 AA floor
is enough to build against. `ROADMAP.md` item 24 (consolidate the scattered
UI/display constants) would give the script one place to read instead of two;
worth doing after it if item 24 is close, but not a blocker — the script can
read both files today.

**Done when.** `make check` fails on a colour edit that breaks a documented
contrast claim, the three agent-pair claims in `theme.py` are verified rather
than asserted, and the failure message names the constant to change.
