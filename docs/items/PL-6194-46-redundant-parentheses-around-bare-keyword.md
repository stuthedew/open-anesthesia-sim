---
id: PL-6194
title: 46 redundant parentheses around bare keyword-argument values across src/, from the initial build
priority: P3
effort: S
status: done
classes: refactor
milestone: v0.4.23
touches: src/anesthesia_sim/core/agent_simulation_validation.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/patient.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/test_controller.py, tests/reference/test_multi_agent.py, tests/reference/test_published_wash_in_and_elimination.py, tests/reference/test_sevo_patient.py, tests/unit/test_circuit.py, tests/unit/test_formatting.py, tests/unit/test_simulation_view.py, tests/unit/test_uptake_system_failure.py
added: 2026-09-03
closed: 2026-09-14
pr: 555
verify: uv run pytest tests/unit/test_uptake_system_failure.py tests/unit/test_simulation_view.py && ! grep -rEq '^ +[a-z_]+=[(][a-zA-Z_][a-zA-Z0-9_.]*[)],?$' src/ --include=*.py
---

**Problem.** Keyword arguments are passed with their value wrapped in
parentheses that do nothing:

```text
currently_stored_agent_l=(currently_stored_agent_l),
arterial_fraction=(self.alveoli.concentration_fraction),
delivered_agent_l=(fresh_gas_exchange.delivered_agent_l),
```

Measured 2026-09-03: **40 occurrences across seven files** under `src/`, plus
six more in `tests/`.

| File | Count |
| --- | --- |
| `src/anesthesia_sim/app/controller.py` | 16 |
| `src/anesthesia_sim/core/uptake_system.py` | 8 |
| `src/anesthesia_sim/core/patient.py` | 8 |
| `src/anesthesia_sim/app/simulation_view.py` | 5 |
| `src/anesthesia_sim/core/agent_simulation_validation.py` | 1 |
| `src/anesthesia_sim/core/circuit.py` | 1 |
| `src/anesthesia_sim/core/parameters.py` | 1 |

They date to `875ba08` (2026-08-22), the initial v0.1.0 build, and no
convention anywhere records them as deliberate — nothing in `CLAUDE.md`,
`.claude/rules/`, `docs/ARCHITECTURE.md` or `docs/MODEL.md` mentions them. They
are accumulation, not house style.

**Why it matters.** Small, and filed for one reason: `.claude/rules/core-domain.md`
sets the bar for `core/` at code where "a clinician who knows uptake and
distribution should recognize the physiology without a translation step", with
"the equation visible rather than buried". A reader held to that standard stops
on a redundant construct and looks for the reason there is not one, and the
inconsistency is what makes them stop — `agent_simulation_validation.py` carries
it on one of eight fields in a single call, while `uptake_system.py` carries it
on four fields of one call and not the rest.

Not a correctness problem, and nothing displayed changes. It is visual noise in
exactly the files that rule governs.

**Where.** The seven files in `touches`, at every line matching
`^ +[a-z_]+=[(][a-zA-Z_][a-zA-Z0-9_.]*[)],?$`. Sweep `tests/` in the same pass.

**Approach.** One mechanical pass, then the full suite. Do it by hand or with a
regex; either way `make check` is what proves it, since removing a redundant
parenthesis cannot change behaviour and the suite covers every file listed.

**No linter does this, and no check should be built for it.** Measured
2026-09-03 against a scratch file: `ruff check --isolated --select ALL --preview`
reports nothing for `f(alpha=(VALUE))`, `UP034` included — it covers
`print(("x"))`, not a keyword argument's value — and `ruff format --diff`
produces an empty diff. So nothing removes these on its own.

A `tools/` check enforcing it was considered and rejected against `CLAUDE.md`'s
own gate — "the gate is whether it will genuinely run again ... where the
benefit is unclear, the answer is no". Such a check would fire once, on this
sweep, and then never again unless somebody typed a new one. Recorded here so
the question is not re-opened each time this item surfaces.

**Done when.** No line under `src/` or `tests/` wraps a bare keyword-argument
value in parentheses, and `make check` is green.

**Found.** Reading the guard while writing `PL-B7ZV`'s boundary tests. Captured
that session as a single stray parenthesis in one file; the count and the
spread above were measured during triage, and the item is rewritten around
them.

**What v0.4.1 does to this (added 2026-09-03).** Re-measure the table. Counted today, 16
of the 40 sites in `src/` sit in `core/uptake_system.py` and `core/patient.py`,
which `PL-GS5X` restructures, and `PL-9SH6` then rewrites roughly 300 accessor
sites across `core/` and `app/` on top of that. The item survives at a smaller
size; sweeping now means sweeping twice. Do it last in the v0.4.1 sequence, or
fold it into the `PL-9SH6` rename only if that item's "this is a rename and
nothing else" rule can be squared with it - which it probably cannot, so
separately and after.

## Swept 2026-09-14, and proved rather than tested

**50 occurrences across 15 files**, and every file's `ast.dump` is byte-identical
before and after. That is the verification this change is entitled to:
parentheses around a single expression leave no trace in the AST, so a correct
sweep *cannot* change the dump, and an incorrect one cannot avoid changing it.
The sweep asserted the equality per file before writing, so a file whose AST
moved would have been left untouched and named. None was. `make check` is green
on top of that, but it is the weaker of the two statements.

**The table was re-measured first, as the v0.4.1 note required, and it had
moved in both directions:**

| File | 2026-09-03 | 2026-09-14 |
| --- | --- | --- |
| `src/anesthesia_sim/core/uptake_system.py` | 8 | 12 |
| `src/anesthesia_sim/app/controller.py` | 16 | 6 |
| `src/anesthesia_sim/core/patient.py` | 8 | 7 |
| `src/anesthesia_sim/app/simulation_view.py` | 5 | 7 |
| `src/anesthesia_sim/core/agent_simulation_validation.py` | 1 | 1 |
| `src/anesthesia_sim/core/circuit.py` | 1 | 1 |
| `src/anesthesia_sim/core/parameters.py` | 1 | 1 |
| **`src/` total** | **40** | **35** |
| **`tests/` total** | **6** | **15** |

Sweeping last in the sequence was the right call: `PL-GS5X` and `PL-9SH6` moved
five of these out of `src/` on their own, and `controller.py` fell by ten.

**One finding, filed as `PL-YNYK` rather than acted on here.** This brief
rejected a `tools/` check on the prediction that it "would fire once, on this
sweep, and then never again unless somebody typed a new one", and recorded that
so the question would not be re-opened each time the item surfaced. The
re-measurement is not a re-opening on the same grounds — it is the number that
prediction implied, and it disagrees with it: `tests/` went from 6 to 15 over
the eleven days the item sat open, so somebody typed nine new ones in that
window. Whether nine in eleven days clears `CLAUDE.md`'s "will it genuinely run
again" gate is a judgment, and it is the owner's; what has changed is that it
is no longer answerable by the premise written here.
