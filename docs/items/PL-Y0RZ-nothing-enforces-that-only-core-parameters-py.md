---
id: PL-Y0RZ
title: Nothing enforces that only core/parameters.py imports Pydantic
status: untriaged
added: 2026-09-02
---

**Problem.** The invariant holds today — `grep -rn pydantic src/anesthesia_sim/`
returns hits only in `core/parameters.py` — but nothing checks it. Any later
change could import `pydantic` into `core/circuit.py`, a compartment, or the
controller, and every gate would stay green.

**Why it matters.** That boundary is the entire reason the
`_...Payload`/public-dataclass pairs exist, which PL-007 has just written down
at each payload class and on `_StrictPayload`: a payload validates one JSON
document and is discarded, so what the rest of the core holds is a plain
frozen dataclass with no dependency on the validation library. If Pydantic
leaks into a compartment, the pairs stop buying anything and the
documentation asserting they do becomes false — the worse of the two
outcomes, because it reads as verified when it is not. `CLAUDE.md` names
exactly this shape: a claim answerable by reading the tree belongs in a
script rather than in prose that nobody re-measures.

**Where.** `src/anesthesia_sim/core/` and `src/anesthesia_sim/app/`;
`src/anesthesia_sim/core/parameters.py` is the one module allowed the import,
and `_StrictPayload`'s docstring is the prose this would keep honest.

**Approach.** A standard-library check, in the shape `tools/` already uses:
walk `src/anesthesia_sim/**/*.py` with `ast`, collect every `import` and
`from ... import`, and fail on a `pydantic` root outside the allowed module.
`tools/contrast_check.py` reads `app/` with `ast` rather than importing it and
is the model to follow, including staying importable by a bare `python3`.
Whether `app/` should also be forbidden the import is the judgment: the core
boundary is the one the pairs exist for, but the interface has no business
holding validation models either.

**Done when.** A Pydantic import outside the allowed module fails
`make check`, and the allowed module is named in one place a reader can find.
