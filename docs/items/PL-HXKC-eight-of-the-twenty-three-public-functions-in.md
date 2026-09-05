---
id: PL-HXKC
title: Eight of the twenty-three public functions in src/ that raise say nothing about the failure in their docstring, including all three shared guards in core/validation.py
priority: P2
effort: S
status: ready
classes: docs
feature: documentation-standard
touches: src/anesthesia_sim/core/validation.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/uptake_system.py
added: 2026-09-05
verify: uv run python -c 'import ast,pathlib,sys; sys.exit(any(not any(w in (ast.get_docstring(f) or "").lower() for w in ("raise","reject","refus")) for p in pathlib.Path("src").rglob("*.py") for f in ast.walk(ast.parse(p.read_text())) if isinstance(f,ast.FunctionDef) and not f.name.startswith("_") and any(isinstance(n,ast.Raise) for n in ast.walk(f))))'
---

**Problem.** Lee 2018 rule 7 asks that a documented function name its inputs
and their types, its output and its type, and the errors it can raise. Strict
mypy over `src/` settles the first two structurally; the third is prose and is
missing in eight places. Measured 2026-09-05 by walking `src/` with `ast`:
23 public functions contain a `raise`, 15 name the failure in the docstring,
and these 8 do not —

- `core/validation.py:22` `require_positive_finite`
- `core/validation.py:29` `require_nonnegative_finite`
- `core/validation.py:36` `require_concentration_fraction`
- `core/alveolar.py:68` `apply_blood_uptake`
- `core/circuit.py:180` `set_agent_amount`
- `core/parameters.py:427` `parse_agent_parameters`
- `core/parameters.py:456` `parse_reference_adult_parameters`
- `core/parameters.py:501` `load_agent_parameters`

Separately, 13 `__post_init__` and `_validate_*` functions raise and carry no
docstring at all. Those are a different question — a dataclass validator's
contract can reasonably live on the class — and are out of scope here unless
the class docstring is silent too.

**Why it matters.** The three `validation.py` guards are the ones every
compartment constructor and setter funnels through, so the file where the
refusal contract is least visible is the file that defines it for the whole
core. `core/exceptions.py` already documents what each exception branch means
to a caller; what is missing is which call sites can produce one. A caller
that cannot see which guard a value will meet writes the wrong `except`, or
none.

**A ninth, found at triage 2026-09-05.**
`core/uptake_system.py:65` `require_supported_simulation_step` refuses a step
above `MAXIMUM_SIMULATION_STEP_S` and its docstring says only what the guard is
for, never that it rejects anything. It is the same defect and belongs in this
item rather than a new one, because `PL-GZPX` (hold a raising function to naming
the failure, as a check) cannot land while any instance is open - a nine-instance
tree with eight fixed still fails the check that item exists to add.

**The `verify:` command is that walk**, as a one-liner under the project
interpreter, which it needs because `src/` uses PEP 695 syntax the bare
`python3` cannot parse. Its predicate is `raise`, `reject` or `refus` appearing
anywhere in the docstring - the decidable half; whether the sentence is *true*
stays the reviewer's, exactly as `PL-GZPX` specifies. It reports nine today and
exits 1.

**Where.** The eight functions above. Follow the shape already used by
`AlveolarCompartment.set_alveolar_ventilation`, which states what it rejects
and points at `core/supported_ranges.py` rather than restating the range.

**Done when.** Each of the eight names, in its docstring, the condition it
refuses and the exception it raises; the walk above reports 23 of 23.
`PL-GZPX` is the check that holds the line afterwards and is blocked on this.
