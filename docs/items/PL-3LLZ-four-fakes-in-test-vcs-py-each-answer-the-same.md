---
id: PL-3LLZ
title: Four fakes in test_vcs.py each answer the same commit-paths question, and each new git read has to be taught to all of them
priority: P3
effort: M
status: done
classes: refactor
feature: dev-tooling
milestone: v0.5.15
touches: subprojects/docket/tests/test_vcs.py
added: 2026-09-13
closed: 2026-09-27
pr: 1177
verify: grep -q 'def _default_run' subprojects/docket/tests/test_vcs.py && uv run pytest subprojects/docket/tests/test_vcs.py
---

**Problem.** Four fakes in test_vcs.py each answer the same commit-paths question, and each new git read has to be taught to all of them

**Found while closing `PL-YDL6`, 2026-09-13.** Teaching the module one new git
question - the paths a commit changed - meant editing four separate fakes in
`subprojects/docket/tests/test_vcs.py`: `_runner`, `_rename_runner`,
`_closure_runner` and `_recovery_runner`. Each grew the same three-line branch
answering `diff --name-only`, and each was found by running the suite and reading
which tests broke rather than by knowing in advance which fakes were involved.

**Why it matters, and why it is not urgent.** It is upkeep cost rather than a
correctness risk: the fakes are independent by design, each shaped to the question
its own tests ask, and that independence is part of why they are readable. What it
costs is that every future read added to `vcs.py` pays the same four-way edit, and
the failure mode is a test breaking for a reason unrelated to what it tests -
which is a slow way to learn where the fakes are.

`.claude/rules/apparatus-standard.md` is the bar here: duplicated logic is
explicitly what to cut, and robustness is explicitly not. So this is a
consolidation only where it does not cost the per-fake clarity.

**Approach, undecided.** A shared default `run` that answers the questions no test
has an opinion about, with each fake overriding only what it cares about, is the
obvious shape. The risk is the opposite failure: a fake that silently answers a
question its test never considered, which is how a test comes to pass for the
wrong reason. Worth doing only if the shared half stays limited to reads whose
answer is genuinely uniform.

**Re-confirmed, 2026-09-27 - changed shape.** Three of the four fakes are gone:
`_rename_runner`, `_closure_runner` and `_recovery_runner` went with the closure
inference `PL-HMZZ` retired in #1056, and `_runner` is the one left. The
duplication did not go with them. It moved from which question a fake answers to
the shape it prints the answer in. #1078 (`PL-NK1L`) taught `-z` to every
changed-path read, and in this file that meant rewriting nine answers by hand:
`_name_only`, `_runner` twice, `_files_runner`, `_cut_runner` twice,
`_landed_runner`, `_filing_runner` and the split-pathspec test's inline fake.
`_name_only`, extracted by `PL-J16N` for two fakes, already answered from the
flags a read sent; the five fakes and the inline one wrote NUL themselves. And 15 fakes
still pass their arguments through `_bare`, which strips the
`-c core.quotePath=false` prefix `PL-PVW2` stopped sending, so it is a no-op in
every one.

**Approach, chosen 2026-09-27.** One place for each of the two ways a read
reaches the fakes:

- **A read's shape.** One formatter per output git prints - `_name_only`, and
  new `_raw`, `_numstat` and `_log_names` - answering from the flags the read
  sent and refusing a shape it does not model, rather than handing a read that
  changed its flags the old shape. Every fake that prints one of those outputs
  calls its formatter, so the next `-z` is one edit per shape.
- **A new read.** `_default_run`, which every fake that ended in `return ""`
  now falls through to. It answers nothing today, which is exactly what those
  fakes returned, and its docstring carries this brief's condition: only an
  answer every fake falling through would give. A fake that must not be asked
  anything else still raises or returns `SILENT`, and the fakes resolving
  `BASE` keep their own `rev-parse`, since moving it would newly resolve the
  base for fakes whose tests never asked.
- `_bare` goes, being a no-op wherever it is called.

**Done when.** A new git read added to `vcs.py` can be answered for the whole of
`subprojects/docket/tests/test_vcs.py` in one place, with each fake still able to
override what its own tests turn on; the suite passes unchanged; and no fake
answers a question whose answer its tests never considered - which is the failure
this consolidation risks and the reason it is worth doing only for reads whose
answer is genuinely uniform.

**Built, 2026-09-27.** Of the file's 33 fakes, 19 now end in `_default_run`;
the rest raise on an unexpected read (2), answer `SILENT` (1), run real git (3),
hand off to another fake (7), or are the split-pathspec test's inline fake,
which answers one read and prints it through `_numstat`. No test's expectation
changed: `test_vcs.py` passes its 241 tests, and the formatters' docstrings
carry the shapes as git 2.43.0 printed them in a scratch repository. Two
literal NULs are left, deliberately: `since_filed`'s `--name-status` walk,
which one test writes and no other fake prints, and `_commits`, which is
already the one place its `--left-right` format is printed.
