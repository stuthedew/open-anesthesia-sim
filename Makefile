.PHONY: sync check fix test run prebuild docket doc-check pr-title release

# Exported to every recipe below rather than written into a pytest line, so that
# `check_coverage_gate`'s string comparison between the `check` target and
# `.github/workflows/quality.yml` still holds (`PL-D3M2`).
#
# `PL-01GD`: CPython invalidates a `.pyc` by comparing the source's size and
# mtime against what the cache recorded, and a one-character edit reverted with
# `git checkout` can leave both unchanged. Observed 2026-09-07 mutation-testing
# `core/tissue.py`: after the revert, with `git status` clean and the correct
# operator in the file, the interpreter kept running the mutated bytecode and
# `make check` failed reporting `tau = 30.0` for a group whose parameters give
# 480.0 - a number unreachable from the source in front of the reader. Two runs
# were spent before `rm -rf __pycache__` resolved it.
#
# The cost is a little interpreter startup; the alternative is a red gate whose
# failure the source cannot explain, and mutating-then-reverting is exactly what
# `.claude/skills/docket/SKILL.md` asks of a session writing a `verify:`
# command. CI is unaffected either way, running pytest directly in a fresh
# container where no stale cache can exist.
export PYTHONDONTWRITEBYTECODE := 1

# `PL-KY7M`: the Claude Code remote container exports `UV_NATIVE_TLS`, which uv
# renamed to `UV_SYSTEM_CERTS` and now warns about once per invocation - ten
# lines a `make check`, none of them actionable, paid by every real advisory in
# the same output. Translated rather than dropped: the setting is the
# container's, the warning says the old name will be removed, and on that
# release an untranslated variable stops applying in silence. `ifdef` makes the
# block inert where nothing set it, so a local checkout is unaffected.
ifdef UV_NATIVE_TLS
export UV_SYSTEM_CERTS := $(UV_NATIVE_TLS)
unexport UV_NATIVE_TLS
endif

sync:
	uv sync --locked --dev

check: sync
	uv run ruff format --check .
# `--no-cache` on `ruff check` alone, and deliberately not on the `ruff format`
# line above. Two halves of ruff meet here and neither is wrong on its own:
#
#   - isort's `match_sources` resolves a first-party import by probing the
#     **full dotted path** under the `src` roots - `a.b.c` is first-party only
#     if `[SRC]/a/b/c` is a directory or `[SRC]/a/b/c.py` or `.pyi` exists - so
#     one file's verdict depends on whether a *different* file exists.
#   - ruff's `FileCacheKey` is the linted file's **mtime and permission bits,
#     and nothing else**. It does not hash the file's contents, and it
#     references no other path.
#
# So deleting a module invalidates nothing, and every file importing it replays
# a clean verdict it can no longer earn: `make check` passes on a tree CI's
# fresh checkout fails. Upstream has the same root cause open for `INP001`,
# which depends on `__init__.py` the same way - astral-sh/ruff#5449, "we don't
# invalidate the cache when an `__init__.py` is added or removed". Nothing in
# ruff's documentation describes what invalidates a cache entry.
#
# Measured 2026-09-15 on ruff 0.16.4, replaying `PL-25KS`'s port: with
# `src/anesthesia_sim/app/chart_series.py` deleted and the spike files still
# importing it, a warm cache reported "All checks passed!" while the same tree
# with `.ruff_cache` removed reported exactly the two `I001`s CI had reported.
# The `__pycache__` `PL-QSJM` first blamed was ruled out in the same session -
# present or absent, the answer was identical - so the cache is the whole
# mechanism and the bytecode was never part of it.
#
# Only deletion is unsafe, which is why the flag is not a passing preference:
# adding a module is picked up correctly, so the cache fails in the one
# direction that turns the gate green on a tree CI rejects.
#
# `known-first-party = ["anesthesia_sim"]` was considered and refused. It would
# work - isort consults `known_modules` before it probes the filesystem, so the
# package's own imports would stop depending on what exists - but it treats the
# instance rather than the fault. The fault is that the cache does not track
# the filesystem facts a verdict rests on, so the next rule that reads another
# file reintroduces the divergence, and it would also silence the sorter on an
# import of a module that is genuinely gone. `--no-cache` covers every rule.
#
# The formatter keeps its cache deliberately. Its output depends only on the
# file in front of it, so a stale entry there needs that file to have changed,
# which is precisely what invalidates the entry. Costed 2026-09-15 over 150
# files: `ruff check` 14 ms warm against 41 ms cache-free, so this line buys
# CI's answer for 27 ms.
#
# `tools/doc_check.py`'s `check_ruff_cache` holds every `ruff check` line in
# this file to the flag, so one added later cannot arrive without it.
# Deliberately not an exported `RUFF_NO_CACHE` beside `PYTHONDONTWRITEBYTECODE`
# above: that variable takes `true`/`false` and rejects `1` outright, so the
# obvious copy of its neighbour's `:= 1` would fail every ruff invocation at
# argument parsing. `PL-QSJM`.
	uv run ruff check --no-cache .
# No paths: `[tool.mypy] files` in pyproject.toml names what the gate covers,
# and says why `tests/` is not in it.
	uv run mypy
# Under `uv run`, unlike `doc_check.py` below: this one shells out to mypy, so
# it needs the virtualenv the gate above runs in. It reads `warn_unused_ignores`
# over the two test trees `files` excludes, which nothing else evaluates.
#
# **A script added to this target is added to `.github/workflows/quality.yml`
# too, or recorded as deliberately one-sided.** The two gates are separate
# lists and neither knew what the other ran, so this one, `dead_ends.py` and
# `possessive_section_check.py` were all local-only - two of them for weeks -
# and a branch pushed without a local `make check` merged green on a tree this
# target would refuse. `tools/doc_check.py`'s `check_gate_parity` now
# reconciles the two sets in both directions and names `GATE_ONLY` as where a
# reason goes, so the question arrives at the moment a line is added here
# rather than whenever somebody next notices (`PL-PBP5`). It is placed beside
# this line because this is the first `tools/` script the target runs.
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
# The store validation, and since `PL-0HPV` the replay of the `verify:`
# commands this branch can have changed: the items it edited, and the open
# items whose command reads a file it edited (`PL-XMNC`). That is the step
# `.github/workflows/quality.yml` runs on a pull request, and until this line
# a session could not see its finding before pushing. That finding - an open
# item whose `verify:` command already passes - is what 20 of the 56 red
# `pull_request` runs from 2026-09-10 to 2026-09-22 failed on, the commonest
# failing step there, each a round trip for an answer this line gives in
# seconds.
#
# Scoped, and never the whole-store sweep. That one finds work that *merged*
# without its item being closed, which a pre-commit gate on a feature branch
# cannot have changed (`PL-P3B6`), so it runs on every push to `main`, where
# its answer is a fact about `main`. The scoped form asks whether this
# branch's own store edit, or a file it touched, has just made an open item's
# command pass - and that this branch can have changed.
#
# The price, re-timed 2026-09-22 on four cores after `PL-0HPV` moved each
# legacy command's `grep` ahead of the test file it ran first: `172f93e1`'s
# file set, the widest of the last 80 merges with 55 items in scope, 5.0-5.3 s
# against 41-46 s before; three more real merges' sets 1.3-5.4 s where they
# cost 14.1-67.5 s; and 1.1-1.2 s on a branch that changes no item and no
# file an open command reads, which is the validation alone. The slowest
# command in scope sets it rather than how many run - `PL-LWMS`'s
# `pytest tests/unit -k`, 4 s, on any branch touching `tests/unit` - and
# `docket check` prints that reading on its own cost line every run, which is
# the one to trust once these figures have aged.
#
# No shell conditional guards it. A base that cannot be read - no `origin`
# remote, or a bare copy - declines with one "Not checked" line and exits 0
# (`PL-ZPDM`), so the gate stays green offline and says what it skipped. The
# ref is read without a fetch, so the gate needs no network, and a stale one
# can only widen the scope, never hide this branch's own changes: the diff is
# taken from the merge base, which a stale ref moves earlier and no later.
	bin/docket check --verify --verify-base origin/main
# Bare `python3`, like the three lines after it: none of them reads project
# source, so the 3.11 floor parser has nothing it cannot read, and a bare run is
# the no-virtualenv promise `tools/ruff.toml` states. Placed with the
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
# Beside the two guards above, and the same category one level further out:
# those ask whether this branch's work is visible and whether a rule's declared
# scope is the one it gets, this asks whether the always-loaded context a
# session starts with is still inside the budget that makes it safe to load.
# `.claude/hooks/docket-digest.sh` emits `docs/dead-ends.md`'s entry lines at
# session start, and a `SessionStart` hook's output is resent on every turn -
# so an entry added without a thought for the cap is paid by every session
# forever. Reads two files, so it costs milliseconds. `PL-NB35`.
	python3 tools/dead_ends.py check
# Under `uv run`, unlike the bare lines above, because it reads project source:
# the docstrings of every module, for the citations in them, and that source
# targets 3.14. The 3.11 floor parser cannot read all of it, and this names each
# file it could not on a "Not checked" line and passes. That is right in the CI
# floor section, whose bare line is there to prove the tool needs no
# virtualenv, and wrong here, whose job is to check: under 3.11 it is two files
# on every run (`app/bookmarks.py`, `app_metadata.py`), so this gate read none
# of their docstrings and said so every time, which trains a reader to skim
# past the line (project owner, 2026-09-24, ratified, over reporting the skip
# and keeping this line bare, `PL-MB3F`).
	uv run python tools/doc_check.py check
# Beside `doc_check` because it is the notation half of the same question,
# and it imports it. `CITATION_CONNECTIVE` admits the possessive since
# `PL-316G`, so both citation forms are held to the same containment test and
# neither can rot silently - which settles correctness and leaves what each
# form tells a reader. `` `doc.md` § "X" `` says the quotation is a section
# title; `` `doc.md`'s "X" `` says nothing, this project writing the
# possessive to quote a sentence as often as to cite a section.
#
# Only the decidable direction is reported: a quotation matching a heading or
# a `**Bold.**` marker in the file it names *is* a section citation, as a fact
# about the tree. One matching no heading may be a faithful quotation of
# prose, which is correct as written, so nothing is said about it - the
# judgment half `CLAUDE.md` refuses to script is exactly the half left alone.
#
# Under `uv run` for the reason the line above it is: it reads source
# docstrings through `doc_check._quoting_sources`, not only markdown, so under
# the floor it could not read `app/bookmarks.py` or `app_metadata.py`, and no
# gate checked the possessive citations in either (`PL-MB3F`). It could only be
# wired in after the 29 sites it named were converted, since it hard-fails on
# the thing it exists to find - and wiring it is the point of the conversion
# rather than a coda to it. A
# convention nothing enforces decays, and this is what stops the next session
# writing a section citation in a form that says nothing to its reader.
	uv run python tools/possessive_section_check.py
# Under `uv run`, all seven of them, like the two lines above, and for a reason
# about the *input* rather than about the tool. These read `app/`, `tests/` and
# modules under `src/anesthesia_sim/` with `ast`, and that source
# targets 3.14. PEP 695 (3.12) type parameters in `app/bookmarks.py`
# are a `SyntaxError` to the 3.11 parser these tools promise to run under, and
# `ast.parse`'s `feature_version` only ever narrows the accepted syntax - it
# cannot teach an older parser a newer language. So the parser has to be the
# one the source is written for.
#
# `contrast_check.py` was bare until `PL-L17Q`, and passed only because
# `app/theme.py` and `app/simulation_view.py` happened to carry no 3.12+ syntax
# - one PEP 695 generic added to either turned the CI floor section red for a
# reason having nothing to do with the change. It still reads those constants
# with `ast` rather than importing them, because the interface imports PySide6
# and a hook or a bare checkout has no toolkit to load.
#
# `workflow_paths_check.py` joined them under `PL-JBZK` for the same reason
# about its input: it reads every file under `tests/` with `ast` to decide
# whether that file imports the simulator, and `tests/` targets 3.14 like the
# rest of the tree.
#
# `agent_identity_check.py` is here for the same reason: it reads every
# module under `app/` with `ast` (`PL-V53R`). It refuses a control
# that carries the agent colour and can be rendered disabled, which is the
# colour Material substitutes and `contrast_check.py` above cannot reach
# because it is declared in no source file (`PL-97VB`).
#
# `core_vocabulary_check.py` joined them under `PL-FZ6T`, and it is the reason
# its three rules are not in `tools/doc_check.py` beside the other checks that
# read `docs/MODEL.md`: it parses every module under `src/anesthesia_sim/core/`
# with `ast` to resolve the Symbols table's Code column, and `doc_check.py` also
# runs bare in the CI floor section. A rule resting on a 3.14 parse could only
# decline there, file by file wherever 3.12+ syntax sits, which is the noise
# `PL-MB3F` moved this gate's `doc_check.py` line to `uv run` to stop.
#
# `glyph_check.py` joined them under `PL-8XPQ`. It holds every string that can
# reach a reader to characters somebody has rendered and looked at - `->`
# (U+2192) drew as a replacement box on 2026-09-04 and no test could see it -
# and it reads `app/`, `core/` and `data/`, because the view prints a `core/`
# validation message verbatim and `display_name` comes out of a data file.
#
# `fixture_id_check.py` joined them under `PL-7922`, and its input is the
# broadest of the group: every `*.py` in the repository, so `tests/` and `src/`
# both, which is the same 3.14 argument `workflow_paths_check.py` makes. It
# refuses a `PL-` literal outside `store.ID_ALPHABET`, which `ID_PATTERN`
# matches nowhere - so a fixture carrying one exercises nothing and every
# assertion resting on it passes vacuously (`PL-GXPP`, 261 substitutions), and
# an example carrying one is copied (`PL-DPY6`, `PL-3BZS`). The rule was
# `subprojects/docket/tests/test_store.py`'s and globbed that directory alone.
#
# `tools/ignore_check.py` above is the same category for a different reason.
# All seven tools here stay standard-library-only and parse at the floor
# themselves, which is what `tests/unit/test_tools_portability.py` holds them
# to; that suite's docstring states the rule this group is an instance of.
# `PL-Y0RZ`, `PL-L17Q`, `PL-JBZK`, `PL-97VB`, `PL-FZ6T`, `PL-8XPQ`, `PL-7922`.
	uv run python tools/contrast_check.py
	uv run python tools/agent_identity_check.py
	uv run python tools/import_boundary_check.py
	uv run python tools/workflow_paths_check.py
	uv run python tools/core_vocabulary_check.py
	uv run python tools/glyph_check.py
	uv run python tools/fixture_id_check.py

fix:
	uv run ruff format .
# `--no-cache` for the reason the `check` target's line above gives, and it
# matters more here rather than less: a stale clean verdict makes `--fix` a
# no-op, so this target reports nothing to fix, `make check` then agrees, and
# the import ruff would have rewritten reaches CI unsorted. The fixing half of
# a gate has to read the same tree the gate does. `PL-QSJM`.
	uv run ruff check --no-cache --fix .
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
	python3 tools/generator_check.py

# Under `uv run` for the reason its line in `check` is (`PL-MB3F`).
doc-check:
	uv run python tools/doc_check.py check

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
