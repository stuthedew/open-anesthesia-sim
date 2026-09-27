---
id: PL-VZYS
title: A hand-run 'uv run ruff check .' still reads the stale .ruff_cache that PL-QSJM's --no-cache removes from make check and make fix, so the guard sits at the entry point rather than where the tool reads it - the same shape as PL-0MLZ's finding about PYTHONDONTWRITEBYTECODE
priority: P3
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: pyproject.toml, Makefile
added: 2026-09-15
verify: grep -qF 'known-first-party = ["anesthesia_sim"]' pyproject.toml
---

**Problem.** A hand-run 'uv run ruff check .' still reads the stale .ruff_cache that PL-QSJM's --no-cache removes from make check and make fix, so the guard sits at the entry point rather than where the tool reads it - the same shape as PL-0MLZ's finding about PYTHONDONTWRITEBYTECODE

**Why it matters.** `PL-QSJM` put `--no-cache` on the Makefile's two `ruff
check` lines, so the *gate* now asks CI's question. A session iterating by hand
does not: `uv run ruff check .` is what the `docket` skill's own advice produces
(`pytest -q` while iterating, the same habit for ruff), and it still reads
`.ruff_cache`. So after deleting a module, a hand-run ruff reports clean on
imports that no longer resolve.

The residual risk is small, and worth stating rather than overstating: `make
check` is required before a commit and now carries the flag, so this cannot by
itself reach `main`. What it costs is a session's belief about the tree between
edits - the same "guard set by the entry point, bypassed by the most common
invocation" that `PL-0MLZ` records for `PYTHONDONTWRITEBYTECODE` and `PL-TCKV`
for `UV_NATIVE_TLS`. Three instances of one shape is the argument for fixing the
shape: a carrier `uv run` reads, rather than one `make` applies.

**Done when.** A bare `uv run ruff check .` in this checkout does not read a
stale `.ruff_cache` - `[tool.uv]`'s `env` or `env-file` in `pyproject.toml` is
the cheapest candidate, and takes `RUFF_NO_CACHE=true`, which rejects `1` - and
the Makefile flags are either kept as belt-and-braces with a comment saying so,
or removed as redundant. `PL-TCKV` wants the same carrier; `PL-0MLZ`, which
wanted it too, closed on 2026-09-27 without it.

**Found by `PL-0MLZ`, 2026-09-27: the candidate above does not exist.** uv
0.12.19 warns that `env` and `env-file` under `[tool.uv]` are unknown fields
and applies neither, and reads a `.env` only under `--env-file` or
`UV_ENV_FILE`. `PL-0MLZ` took the root `conftest.py`, which only a pytest run
reads, so it offers ruff nothing, and ruff's own configuration carries
`cache-dir` but no switch that turns the cache off. `.claude/settings.json`'s
`env` block does not load in a Projects thread either (`PL-9DYK`).

## Design round 2026-09-27: routes, evidence, recommendation

**Re-confirmed against the tree and at source, 2026-09-27.** The premise
holds and was replayed today on ruff 0.16.4 with uv 0.12.19: on a warm
`.ruff_cache`, deleting `src/anesthesia_sim/app/run_view.py` and re-running a
bare `uv run ruff check .` reports `All checks passed!`, while the same tree
under `--no-cache` reports the `I001` in
`tests/integration/test_simulation_view.py` that imports it. The mechanism
is the one `PL-QSJM` measured, read again at ruff 0.16.4: `categorize` in
`crates/ruff_linter/src/rules/isort/categorize.rs` consults `known_modules`,
then the standard library, then `detect-same-package`, and only then
`match_sources`, which probes the full dotted path under the `src` roots;
`FileCacheKey` in `crates/ruff/src/cache.rs` is the linted file's mtime and
permission bits and nothing else. The carrier this brief named does not
exist: uv 0.12.19's `Options` in `crates/uv-settings/src/settings.rs` has no
`env` or `env-file` field, and the installed `uv run --help` reads a `.env`
only under `--env-file` or `UV_ENV_FILE`, a variable something outside the
checkout has to set first. Ruff's own configuration has one cache setting,
`cache-dir` (`crates/ruff_workspace/src/options.rs`), and no switch that
turns the cache off; `RUFF_NO_CACHE` is a `clap` env binding on the
`--no-cache` flag of `check` and `format`, so it needs a shell to carry it.

**Q1. Which route, if any?** **Recommendation: declare
`known-first-party = ["anesthesia_sim"]` under `[tool.ruff.lint.isort]`,
keep the Makefile's `--no-cache` and `check_ruff_cache` as they are, and
re-point `verify:` at the declaration.** Read at source, `known-first-party`
is "a list of modules to consider first-party, regardless of whether they can
be identified as such via introspection of the local filesystem", and
`categorize` consults it before the probe, so the verdict on an
`anesthesia_sim.*` import stops depending on whether a different file
exists - which is the whole of what the cache cannot track. Measured today
with the setting in place: on the intact tree a cache-free `ruff check`
changes no verdict (`All checks passed!`, so no import block re-sorts); on
the deleted-module tree the hand run and the cache-free run agree (`All
checks passed!` both), where before they disagreed. `S` holds: one line of
configuration, the `verify:`, the Makefile paragraph below, and no test to
write - the measurement is a replay, not a regression test, because the
change is to a setting ruff reads, not to code this repository owns.

*This reopens a recorded refusal, and says so.* `PL-QSJM`'s Makefile comment
records `known-first-party` as "considered and refused" on three grounds,
in a session's own words with no owner decision behind it, so it reopens on
ordinary evidence (`CLAUDE.md`). Taken in turn: (1) "it treats the instance
rather than the fault" - the fault is ruff's cache not tracking filesystem
facts, which is upstream's (astral-sh/ruff#5449) and cannot be fixed here;
the flag on the gate stays for it. (2) "the next rule that reads another
file reintroduces the divergence" - counted against the selected set (`E`,
`F`, `I`, `UP`, `B`, `RUF100`): `match_sources` is the only filesystem probe
any of them makes, and `INP001`, the other cross-file rule upstream names,
is not selected. The number that would make this recommendation wrong is one
such rule in the selection, and it is zero; a rule added later meets
`--no-cache` on the gate, which `check_ruff_cache` keeps there. (3) "it
would silence the sorter on an import of a module that is genuinely gone" -
that `I001` was a resolution failure reported as a sorting error, by a tool
that does not check imports. What does: `pytest` fails collection of the
importing test with an `ImportError`, and `mypy`'s gate covers `src`,
`tools`, `.claude/hooks` and `subprojects/docket/src`; both run in CI on
every pull request, and neither reads a cache.

[superseded 2026-09-27: the declaration was ratified, so this fallback is not built] *Refused: a `PreToolUse` hook on Bash* that refuses a `ruff check` written
without `--no-cache` and prints the flagged spelling, the shape of
`.claude/hooks/gate-status-guard.sh`. It would reach every session and
subagent, which is where the hand run happens, and never a terminal on the
Mac; it is a new workflow mechanism carrying a spelling matcher and a
`KNOWN_GAPS` table of its own, for a `P3` whose residual risk the brief calls
small and which the gate already covers. It is the fallback if the
declaration is refused, not a second thing to build beside it.

*Refused: `.env` plus `UV_ENV_FILE`.* The file would be read only once a
variable is exported outside the checkout, which is the problem in another
place. *Refused: `.claude/settings.json`'s `env` block* - it does not load in
this project's threads (`PL-9DYK`, measured under `PL-0MLZ`). *Refused,
untested: pointing `cache-dir` at a path ruff cannot write*, a hack around
the absence of a switch whose failure mode nobody has read. *Refused as the
whole answer: a line in the `docket` skill or `docs/worker.md`* telling a
session to type `--no-cache` by hand - a rule nobody reads, and with the
declaration in place the hand run needs no rule.

[superseded 2026-09-27: the declaration was ratified, so the item is built rather than dropped] *Dropping the item* is the honest ending if the declaration is refused and
the hook is not wanted: the gate is covered, and what stays exposed is a
session's belief between edits, already documented at the Makefile line.

**How, for the build thread.** `pyproject.toml`: the one line under
`[tool.ruff.lint.isort]`, with a comment naming the two halves of the
mechanism in a sentence and pointing at the Makefile paragraph. `Makefile`:
the "was considered and refused" paragraph becomes history - reopened under
this item, and why - and the flag line stays; `check_ruff_cache` in
`tools/doc_check.py` needs no change. `verify:` becomes a grep for the
declaration in `pyproject.toml` beside the existing `ruff check --no-cache`
grep on the `Makefile`, so both halves are held. `touches:` gains `Makefile`;
`docs/worker.md` has nothing to say about ruff's cache and can leave the
field. Replay the measurement above once before closing - warm cache, move
`src/anesthesia_sim/app/run_view.py` aside, hand run and `--no-cache` both
clean, move it back - and record the date.

**What this says about `PL-TCKV`.** Its `verify:` greps `pyproject.toml` for
`UV_SYSTEM_CERTS` on the same `[tool.uv]` premise, which the evidence above
voids; that item's own brief already says to re-point it if the work
chooses another carrier, and the build thread that takes it meets this note
first.

**Done when, restated for the choice.** A bare `uv run ruff check .` on a
warm cache and a `--no-cache` run give the same verdict after a first-party
module is deleted; the intact tree's verdicts are unchanged; the Makefile
keeps CI's question for every rule; and the refusal it recorded is rewritten
as the decision that replaced it.

## Answers 2026-09-27

**Q1 - Answered 2026-09-27: declare `known-first-party = ["anesthesia_sim"]`
under `[tool.ruff.lint.isort]`, keep the Makefile's `--no-cache` and
`check_ruff_cache`, and re-point `verify:` at the declaration** (project
owner, 2026-09-27, ratified, over a `PreToolUse` hook refusing a hand-typed
`ruff check` without `--no-cache`, and over dropping the item). This decision
is what reopens `PL-QSJM`'s recorded refusal of the declaration: the build
rewrites the Makefile paragraph as history, citing this item. `touches:` and
`verify:` above were re-pointed with this record - `Makefile` in, `docs/worker.md`
out, the grep on the declaration - and the status stays `ready` for the build
thread, which follows § "How, for the build thread" and replays the
measurement before closing.
