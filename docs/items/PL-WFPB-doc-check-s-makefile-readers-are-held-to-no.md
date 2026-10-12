---
id: PL-WFPB
title: doc_check's Makefile readers are held to no reference program: hold make_targets, _target_recipes and _recipe_commands to GNU make's own reading (make -pqRr, make -n) over generated Makefiles, as test_shell.py holds docket.shell to bash
priority: P3
effort: M
status: ready
classes: test
feature: reader-checks
touches: tests/unit/test_makefile_reference.py
added: 2026-10-12
payoff: a Makefile form doc_check's readers misread fails the pull request that first writes it, rather than surfacing as an item after it merges
verify: grep -rq 'def test_the_makefile_readers_read_generated_makefiles_as_make_does' tests/unit
---

**Problem.** doc_check's Makefile readers are held to no reference program: hold make_targets, _target_recipes and _recipe_commands to GNU make's own reading (make -pqRr, make -n) over generated Makefiles, as test_shell.py holds docket.shell to bash

Filed 2026-10-12 from the thread answering the owner's question of that day,
whether a published test corpus exists to verify this repository's lexers
against ("Agree with recs", project owner, 21:54 UTC). The measurements, sources
and rerunnable probes are in `/mnt/project-files/v0.6.0/lexer-corpora.md` and
`/mnt/project-files/v0.6.0/lexer-corpora-probes/`, outside the repository.

**No published corpus exists for this; make itself is the oracle.** GNU make's
own regression suite (`tests/`, Perl-driven, GPL-3.0-or-later) tests what make
does, not how a third party reads a Makefile. But `make -pqRr -f FILE
NO_SUCH_GOAL` prints make's own reading of every target: its prerequisites, its
recipe as written, and the file and line the recipe came from, for the
conditional branch that applies only. `make -n -f FILE TARGET` prints the
commands make would hand the shell. GNU make 4.3 runs wherever the gate runs.

**Today the readers' tests record make's answers once, by hand**, at the time
each was written (`tests/unit/test_doc_check.py`, the comments reading "as GNU
make 4.3 read them" and "what GNU make 4.3 printed for them"). Nothing in the
suite runs make. Nine Makefile misreads have closed as items (`PL-4MLK`,
`PL-5M36`, `PL-BMZN`, `PL-G2FY`, `PL-GZXY`, `PL-HD96`, `PL-HR4V`, `PL-TDVJ`,
`PL-X43T`) and three are open and latent (`PL-GSJ6` `.RECIPEPREFIX`, `PL-HSB3`
conditional branches, `PL-QYF4` recipe prefixes kept), each found by a sweep
after the form could already have merged.

**Reproduced 2026-10-12.** A 12-line Makefile setting `.RECIPEPREFIX = >`, with
a continued recipe, `lint: ; ruff check .` and an `ifeq`/`else` defining
`other` in both branches: `make -pqRr` printed recipes for `all`, `lint` and
`other` (the `else` branch only), while `doc_check.make_targets` read a recipe
for `lint` alone, which is `PL-GSJ6`'s form.

**Why it matters.** The Makefile reader is the most productive source of misread
items this store has, and every one was found after merge because no test asks
make. A generated comparison catches a misread on the pull request that first
writes the form, which is what `PL-C4XY` bought `docket.shell` against bash.

**Done when.** A test in `tests/unit/` generates Makefiles with Hypothesis,
derandomized, from the forms the closed items name (continued lines, several
targets, `define`, conditionals, `.ONESHELL`, `.RECIPEPREFIX`, recipe prefixes,
`target: prereq ; recipe`, comments inside rules), and holds `make_targets`,
`_target_recipes` and `_recipe_commands` to `make -pqRr` and `make -n`, skipping
where no GNU make is on `PATH`. The three open items' forms are pinned as known
departures by those items, as `test_shell.py`'s `KNOWN_DEPARTURES` does, so each
fix removes its own entry.

**Generator check.** Work the owner asked for, not a misread: it is the oracle
the closed Makefile items lacked, and no head's `misread:` names a missing
reference program.
