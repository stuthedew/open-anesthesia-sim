.PHONY: sync check fix test run prebuild docket doc-check pr-title release

sync:
	uv sync --locked --dev

check: sync
	uv run ruff format --check .
	uv run ruff check .
# No paths: `[tool.mypy] files` in pyproject.toml names what the gate covers,
# and says why `tests/` is not in it.
	uv run mypy
# Under `uv run`, unlike `doc_check.py` below: this one shells out to mypy, so
# it needs the virtualenv the gate above runs in. It reads `warn_unused_ignores`
# over the two test trees `files` excludes, which nothing else evaluates.
	uv run python tools/ignore_check.py
# `--cov=` takes the dotted module, never a path, and the run is the whole
# suite: coverage of `core/` is the union of everything that exercises it, so
# the threshold is only reachable from a whole-suite run. Deliberately not in
# `[tool.pytest.ini_options] addopts` nor in a `[tool.coverage]` table - either
# would apply the threshold to the scoped `uv run pytest tests/unit/test_x.py`
# a session runs while iterating, which would fail for a reason unrelated to
# the change under it. Measured 2026-09-03: 92.8 s with the flag against
# 92.4 s without, so the gate is free. `PL-22Z3`.
#
# The parallelism is off `addopts` for exactly the same reason, and it is the
# reason that argument generalizes: a session iterating on one test file would
# pay worker startup for a handful of tests and lose. Here it is the largest
# item in this target, and the suite otherwise runs on one core of however many
# the box has - measured 2026-09-03, 1230 tests: 78 s serially against 27 s at
# `-n auto` (`PL-WCZV`).
#
# `-n auto` gives one worker per CPU, which is right for a CPU-bound suite, and
# a large part of this one is not: `subprojects/docket/tests` shells out to git
# and `test_verify.py` runs literal `sleep` commands, so a blocked worker holds
# a core it is not using. Measured 2026-09-05, four cores, 1577 tests, `--cov`
# on:
#
#     -n auto                  34.2 s  (34.5 / 34.0 / 34.1)
#     -n auto --dist worksteal 25.6 s
#     -n 8                     27.5 s
#     -n 8 --dist worksteal    26.3 s  (26.0 / 27.0 / 26.0)
#     -n 16 --dist worksteal   24.3 s
#
# Neither change helps alone; the pair does. Oversubscribing gives the scheduler
# somewhere to go while a worker waits on a subprocess, and `worksteal` is what
# stops the extra workers idling on an unlucky static split. Past about 2.5x
# cores it degrades again.
#
# Coverage holding is what makes either flag admissible rather than the wall
# clock - identical at 730 statements / 92 branches / 100% here, as it was at
# 691 / 78 / 100% for `-n auto` before it - which is why the threshold stays on
# this line and is not relaxed to pay for the parallelism (`PL-WCZV`,
# `PL-VZ8P`).
#
# The width is computed rather than pinned, for the reason `-n auto` was chosen
# in the first place: it has to read the runner rather than carry this box's
# core count, so the same line is right on a machine of a different size.
# Spelled through `python3` rather than `nproc`, which is GNU coreutils and
# absent on macOS; `os.cpu_count()` is also precisely what xdist's own `auto`
# falls back to here, so this is literally twice what `auto` would have picked.
# `tools/doc_check.py`'s `check_coverage_gate` already held this line and the
# one in `.github/workflows/quality.yml` to the same string; it now collapses
# Make's `$$` first, so the escape below is not read as a drift (`PL-D3M2`,
# `PL-VZ8P`).
	uv run pytest -n $$(python3 -c 'import os; print(os.cpu_count() * 2)') --dist worksteal --cov=anesthesia_sim.core --cov-branch --cov-fail-under=100
# Bare, deliberately: no `--verify`. That flag replays every open item's own
# `verify:` command, which was half this target's wall clock and is the wrong
# question to ask here - it finds work that *merged* without its item being
# closed, and a pre-commit gate on a feature branch cannot have changed that.
# `.github/workflows/quality.yml` passes it on both the events it ran on
# before (`PL-P3B6`), and since `PL-SDHR` it narrows the pull-request one with
# `--verify-base` to the items that branch changed - the same argument as this
# comment's, applied to the event that inherited the bill. The whole-store
# sweep runs on every push to `main`, where its answer is a fact about `main`.
# What is left on this line is the store validation, measured at 0.28 s.
# Measured 2026-09-05, four cores: this target 60.0 s with the replay against
# 29.5 s without.
	bin/docket check
# Bare `python3` for the reason the next line uses it, and placed with the
# provenance checks rather than earlier because that is what it is: `docket
# check` asks whether the store is sound, this asks whether this branch's work
# is visible to the guards that read the store. It answers from `git log`
# alone, so it costs milliseconds wherever it lands. `PL-CP74`.
	python3 tools/branch_id_check.py
# Beside the guard above, and the same category one level out: that one asks
# whether this branch's work is visible in the store, this asks whether it is
# visible in the subject a squash merge will land on `main`. It was the only
# gate a session could not run before pushing, because CI reads the title from
# `PR_TITLE` and nothing sets that locally, so every failure was found by CI
# and cost a cycle. `--discover` reads the title from this branch's own open
# pull request instead, and skips silently on every way that can fail - no
# token, no network, no pull request open yet - so this target stays green
# offline. `make pr-title` runs it alone. `PL-J3BB`.
	python3 tools/pr_title_check.py --discover
# Beside the guard above because it is the same category one level down: that
# one asks whether this branch's work is visible, this asks whether a rule's
# declared scope is the one it will actually get. Reads only the frontmatter of
# `.claude/rules/*.md`, so it costs nothing. `PL-LLWN`.
	python3 tools/rules_paths_check.py
	python3 tools/doc_check.py check
# Under `uv run`, both of them, unlike the bare-`python3` lines above, and for
# a reason about the *input* rather than about the tool. These two read `app/`
# and every module under `src/anesthesia_sim/` with `ast`, and that source
# targets 3.14. PEP 695 (3.12) type parameters in `app/chart_downsampling.py`
# are a `SyntaxError` to the 3.11 parser these tools promise to run under, and
# `ast.parse`'s `feature_version` only ever narrows the accepted syntax - it
# cannot teach an older parser a newer language. So the parser has to be the
# one the source is written for.
#
# `contrast_check.py` was bare until `PL-L17Q`, and passed only because
# `app/theme.py` and `app/simulation_view.py` happened to carry no 3.12+ syntax
# - one PEP 695 generic added to either turned the CI floor section red for a
# reason having nothing to do with the change. It still reads those constants
# with `ast` rather than importing them, because `app/simulation_view.py`
# imports Flet.
#
# `workflow_paths_check.py` joined them under `PL-JBZK` for the same reason
# about its input: it reads every file under `tests/` with `ast` to decide
# whether that file imports the simulator, and `tests/` targets 3.14 like the
# rest of the tree.
#
# `agent_identity_check.py` is here for the narrowest version of the same
# reason: `app/simulation_view.py` is its only input. It refuses a control
# that carries the agent colour and can be rendered disabled, which is the
# colour Material substitutes and `contrast_check.py` above cannot reach
# because it is declared in no source file (`PL-97VB`).
#
# `tools/ignore_check.py` above is the same category for a different reason.
# All four tools here stay standard-library-only and parse at the floor
# themselves, which is what `tests/unit/test_tools_portability.py` holds them
# to; that suite's docstring states the rule this group is an instance of.
# `PL-Y0RZ`, `PL-L17Q`, `PL-JBZK`, `PL-97VB`.
	uv run python tools/contrast_check.py
	uv run python tools/agent_identity_check.py
	uv run python tools/import_boundary_check.py
	uv run python tools/workflow_paths_check.py

fix:
	uv run ruff format .
	uv run ruff check --fix .
# The mutating half of `bin/docket check`'s missing-`pr` advisory. `check`
# reports which landed closures owe a pull request number and which number the
# base names for each; this writes them, so the field rides the commit the
# session is about to make instead of costing one of its own (`PL-N5WZ`).
# Here rather than in `check` for the reason `ruff format` is: `check` runs in
# CI, where mutating the tree is not the job.
	bin/docket record

# `-n auto` for the reason the `check` line above gives, which transfers
# unchanged: what keeps the flag off `addopts` is the scoped
# `uv run pytest tests/unit/test_x.py` a session runs while iterating, and this
# target is always the whole suite. Measured 2026-09-04, four cores, 1230
# tests: 88.5 s serially against 31.8 s, both passing. `PL-FX3N`.
#
# It costs neither `-x` nor the debugger, which is what made this not
# automatic. The recipe takes no arguments, so a run wanting either is already
# a direct `uv run pytest -x tests/unit/test_x.py` that never came through here
# - and `-n auto` is safe to copy into one anyway: given `--pdb` it sets
# `numprocesses = 0` and distribution off rather than erroring
# (`xdist/plugin.py`, `pytest_cmdline_main`), where a pinned `-n 4` raises
# `--pdb is incompatible with distributing tests`. `-x` stops the run under
# both; under `-n` the in-flight workers finish first, so more tests run before
# it stops.
#
# **That is why this line keeps `-n auto` where the `check` line above does
# not.** The computed width up there resolves to an integer, and an integer is
# what `--pdb` rejects - verified 2026-09-05, `-n auto --pdb` passes and
# `-n 8 --pdb` errors with exactly that message. `check` is a gate, takes no
# arguments and is never run under a debugger, so it can spend the property for
# the wall clock; this target is the one a session copies from, so it cannot.
# `--dist worksteal` is taken here regardless: it is the half of the pair that
# `--pdb` tolerates, and it is worth having on its own (`PL-VZ8P`).
#
# This is not the coverage gate. `.github/workflows/quality.yml`'s pytest step
# has to stay identical to the `check` line above, and deliberately not to this
# one, which now shares neither the width nor the threshold (`PL-D3M2`).
test:
	uv run pytest -n auto --dist worksteal

# Named for the store it validates. `make check` runs `bin/docket check` too;
# this target exists so a session can validate the store on its own, after
# editing an item and before committing it.
docket:
	bin/docket check

doc-check:
	python3 tools/doc_check.py check

# The title half of `make check`, on its own, for the moment a session has just
# closed a rider and wants to know what the pull request has to be renamed to
# before it pushes. Prints nothing when there is no open pull request to read.
pr-title:
	python3 tools/pr_title_check.py --discover

# The documented way to cut a release: everything about one that a command can
# do, and nothing that it cannot. `bin/docket release` writes the new version
# into pyproject.toml and stops, but uv.lock records the project's own version
# too, so a `uv sync --locked` afterwards fails with "the lockfile needs to be
# updated". That fired on both releases before the relock was sequenced here;
# `5e9a8f6` and `3ed704a` each carry a hand-run one-line uv.lock bump.
#
# The sequencing lives here rather than in docket because a lockfile is a
# generated artifact and the tool that generates it is a toolchain fact, which
# is what this file is for. docket stays standard-library-only and
# package-manager-agnostic.
#
# It deliberately stops short of `make check`. ROADMAP.md's version-table row
# and baseline section are release prose - what the release was *for* - and
# nothing writes them, so running the check here fails on edits nobody has
# been asked for yet, with the tree half updated. `bin/docket release` names
# those edits instead; make them, then run `make check`, which is what proves
# they landed.
#
# This project names its versions rather than incrementing them (see
# ROADMAP.md, "Versioning decision"), so pass the version:
#
#     make release VERSION=0.3.0
release:
	bin/docket release $(VERSION)
	uv lock
	@echo
	@echo "uv.lock relocked. Make the ROADMAP.md edits named above, then run: make check"

run:
	uv run anesthesia-sim

prebuild:
	git status
	$(MAKE) check
