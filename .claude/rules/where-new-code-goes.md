---
paths:
  - "/src/**"
  - "/tests/**"
---

# Before writing new code, read where it goes and one instance of the pattern

`docs/ARCHITECTURE.md` answers both questions and nothing loaded at launch points
at it. Its § "Where new code belongs" routes each pattern — a compartment, an
agent or patient profile, a panel or control, a rendering of an interpreted
value, a chart series — and its § "Tests (`tests/`)" says which of the three test
trees a new test belongs in, including why a case under `tests/reference/` may
import the parameter loaders but must not reach a solver in `core/`. `README.md`
and `CONTRIBUTING.md` carry the same pointer for a human contributor, and neither
is auto-loaded, which is the gap this rule closes (`PL-39K7`).

**Read those sections for the answer; they are deliberately not restated here.**
A rule that paraphrases the document it cites goes stale while still reading as
current, and then two places disagree about where a compartment goes. One of them
is the map `tools/doc_check.py` already holds to the tree on disk in both
directions. This file only says to go and read it.

## Then read one existing instance end-to-end before writing yours

Not a survey — one canonical instance, read whole, and yours written to match.
The instances are named where each pattern is written rather than listed here:
`.claude/rules/core-domain.md` names the compartment,
`.claude/rules/sources-and-docstrings.md` names the shape of a function that
refuses and of an error message that names what it refused, and
`.claude/rules/ui-reader.md` names the in-source pattern for a reference value on
screen.

Where no instance is named for the pattern you are about to reproduce, the
codebase is silent on it, and saying so is more useful than picking whichever of
several near-misses looks closest. That silence is a finding worth capturing, not
a gap to fill by guessing.
