# Contributing

Corrections, bug reports and pull requests are welcome, and none of them
require you to learn how this repository is run.

**The one thing worth knowing up front:** most changes here are made against an
internal development queue in [`docs/items/`](docs/items), which is why almost
every pull request is titled `PL-XXXX: …`. That is a maintainer's bookkeeping
convention. **You do not need an item, an id, or a particular branch name, and
nothing checks your pull request for one.** Open it the way you would anywhere
else.

## Reporting a problem, or asking a question

[GitHub issues](https://github.com/stuthedew/open-anesthesia-sim/issues) is the
place for all three — bugs, questions and suggestions. There is no separate
support channel and no template to fill in.

A report about the *science* is the most useful thing you can send, and the
more specific the better: name the value or curve that looks wrong, what you
expected, and the source you expect it from. [`docs/MODEL.md`](docs/MODEL.md)
cites its sources precisely so that a disagreement can be about a measurement
rather than about a recollection.

## Sending a change

Fork the repository or push a branch, open a pull request against `main`, and
describe what it does. That is the whole process.

If you would like to check your change before CI does, the project uses
[uv](https://docs.astral.sh/uv/) and pins its interpreter in
[`.python-version`](.python-version):

```bash
uv sync --locked --dev
make check                   # everything CI runs; a few minutes
make test                    # the test suite alone, no coverage gate
make fix                     # apply the formatter and the safe lint fixes
```

Running them is optional — CI runs the same commands and will tell you.

### What CI actually checks

One required job, `checks`, and it runs:

- `ruff format --check` and `ruff check` — formatting and linting;
- `mypy` — type checking over the paths named in `pyproject.toml`;
- the full test suite, with **100% statement and branch coverage of
  `anesthesia_sim.core`**. Coverage is measured on that package only, so a
  change to the interface or to a tool does not owe you tests for coverage's
  sake — though a behavior change owes you a test regardless (below);
- `tools/doc_check.py`, which refuses documentation naming a file, package,
  make target or citation the repository does not hold. If it fires, a
  reference in the docs went stale rather than your code being wrong.

A second job, `pr-title`, checks the pull request title **only when your branch
closes an item in `docs/items/`**. If it does not — and a contributor's branch
will not — it passes and asks nothing of you.

### What a change is held to

The full standards are in [`CLAUDE.md`](CLAUDE.md), and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) says where new code belongs. The
four that come up most often:

1. **Anything that could reach a displayed clinical value is treated as
   safety-critical** — dose and concentration arithmetic, unit conversion, PK/PD
   state, model selection, thresholds, and the labels and axes around them. Such
   a change is reviewed for correctness, explicit units, provenance and
   traceability rather than for elegance, and it wants a test that would have
   caught the bug.
2. **Add or update a test with every behavior change.** This is separate from
   the coverage gate and is not waived by it.
3. **Keep simulation code independent of the interface.** Nothing in
   `src/anesthesia_sim/core/` may import Flet, and no simulation arithmetic
   belongs in a UI callback.
4. **Keep results deterministic.** Identical inputs and model version produce
   identical outputs; simulation time is explicit state, never wall-clock time.

A change that shifts a number `docs/MODEL.md` specifies belongs with the source
it came from — a DOI or PMID is enough.

### Adding a source document

[`docs/references/`](docs/references) holds full texts a reader can open, and
**this repository is public, so a file placed there is redistributed to
everyone.** Only add one whose own licence permits that; check it before you
commit, since there is no directory-wide policy to inherit. Where the licence
does not permit it, add the citation without the file — that is the pattern
already in [`docs/references/README.md`](docs/references/README.md), which
carries the rule in full.

## Licence

The project is [Apache-2.0](LICENSE), and a contribution is offered under the
same licence.
