---
id: PL-DXD4
title: An item-only pull request runs the whole checks job, about 11 minutes with pytest at 9, though only the steps that read the store can change its answer: skip the rest behind docket's own item-only predicate, after auditing the tests that read the real store
status: untriaged
feature: ci-cost
added: 2026-10-17
---

**Problem.** An item-only pull request runs the whole checks job, about 11 minutes with pytest at 9, though only the steps that read the store can change its answer: skip the rest behind docket's own item-only predicate, after auditing the tests that read the real store

**Measured 2026-10-17.** On `main`, 8 of 58 merges in ISO week 41 and 10 of 55
so far in week 42 changed only `docs/items/` (`git diff-tree` per first-parent
commit). Each such pull request runs the whole `checks` job, about 11 minutes,
of which pytest is about 9 (`PL-H9KW`). Skipping the steps that cannot change
the answer would save roughly 9 minutes per run, on the order of 500
run-minutes a month at current volume: about 9% of `quality`'s minutes. Nobody
waits on these pull requests, since they arm auto-merge, so the gain is minutes
rather than anyone's time. `PL-H9KW` is the larger lever and goes first.

**Why it is not a few lines of YAML.**

1. **Some tests read the real store.** `tests/unit/test_docket_gate.py` reads
   every item and asserts the current debt gate's dispositions, so a capture
   can fail it. `bin/docket check` enforces the same rule and would keep
   running, so that one is covered, but the blanket premise is false: 36 test
   files open the real checkout, and each must be cleared or kept (a marker
   run in the fast path) before any step is skipped.
2. **A miss turns `main` red, not the pull request.** The `push` run on `main`
   would still run everything, so a wrongly skipped step fails after the
   merge, and red `main` stops every session. Keep `main`'s run whole; that
   roughly halves the saving and is the backstop.
3. **The predicate already exists.** Which branches carry only item files is
   decided in `subprojects/docket/src/docket/arming.py`, where it already
   decides what merges without review. The workflow step asks that code; it
   does not spell `docs/items/` again (`CLAUDE.md` § "A shared fact has one
   source of truth").
4. **Skip steps, not the workflow.** `checks` is the required check. Step-level
   `if:` conditions keep it reporting; a workflow-level `paths` filter leaves a
   required check pending forever (GitHub Docs, "Troubleshooting required
   status checks" § "Handling skipped but required checks"; `PL-NWSK`).

**Where.** `.github/workflows/quality.yml`; `subprojects/docket/src/docket/arming.py`
for the predicate's entry point; `tools/required_checks_check.py` if the job
shape changes.

**Done when.** On a pull request whose diff is only item files, `checks` runs
the store-reading steps (`bin/docket check`, `doc_check`, `dead_ends`,
`fixture_id_check`, the scoped verify replay and whatever the audit keeps) and
skips the rest, reporting success; `main`'s `push` run is unchanged; and a test
or check shows a diff touching anything outside the store runs the full job.
