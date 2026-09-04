---
id: PL-L17Q
title: tools/contrast_check.py runs in the CI floor job but reads 3.14 source, so one PEP 695 generic in app/ turns it red
status: untriaged
added: 2026-09-04
---

**Problem.** `.github/workflows/quality.yml`'s `floor` job runs `python3
tools/contrast_check.py` under the 3.11 floor to prove the tools need no
virtualenv. That tool reads `app/theme.py` and `app/simulation_view.py` with
`ast.parse`, and `src/` targets 3.14. It works today only because those two
files happen to contain no 3.12+ syntax. Measured 2026-09-04 on the bare
`python3` (3.11): `theme.py` and `simulation_view.py` parse;
`app/chart_downsampling.py` raises `SyntaxError: expected '('` on its PEP 695
`def first_index_at_or_after[SampleT](`.

**Why it matters.** Adding a PEP 695 generic - or any 3.12+ syntax - to
`simulation_view.py` turns the `floor` job red, in a job about tool
portability, for a reason that has nothing to do with the change and nothing
to do with the tool. The author of that change has no path from the failure to
its cause: the traceback names `contrast_check.py`, which they did not touch.
`ast.parse`'s `feature_version` cannot help - it only ever narrows the accepted
syntax; it cannot teach a 3.11 parser a 3.14 language.

This is latent rather than live: nothing is failing today, and the exposure was
found while building `PL-Y0RZ`'s import-boundary check, which hit it
immediately because it reads *every* module under `src/anesthesia_sim/`.

**Where.** `.github/workflows/quality.yml` (`floor` job), `Makefile` (`check`
target), `tools/contrast_check.py`.

**Approach.** `PL-Y0RZ` took the answer that generalizes: a tool whose *input*
is 3.14 source runs under `uv run python`, in the `checks` job and not in
`floor`, with the reason on both lines. The tool itself stays
standard-library-only and parses at the floor, so
`tests/unit/test_tools_portability.py` still holds. Applying the same move to
`contrast_check.py` is a two-line change.

The tempting alternative - hold `src/` to what a bare `python3` can parse - is
the wrong one, and is recorded here so it is not re-proposed: it would pin the
application to a three-year-old interpreter to satisfy a promise made by the
tooling, which is the tail wagging the dog. `src/` should be free to use the
language `.python-version` pins.

**The general rule worth writing down.** The bare-`python3` promise is about
what the tools *depend on*, not about what they can *read*. A tool that parses
repository source can only run under an interpreter that understands that
source. Nothing states this today, which is why the exposure was inherited
rather than decided; a sentence in `tools/ruff.toml`'s comment block or in
`tests/unit/test_tools_portability.py`'s docstring is probably where it goes.

**Done when.** No tool in the `floor` job parses a file that `src/` is free to
write in 3.14 syntax, and the rule above is stated where the next tool author
will read it.
