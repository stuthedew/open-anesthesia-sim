---
id: PL-P757
title: bin/docket --items pointed at a nested store makes every annotating commit read as work, silently
priority: P2
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-06
verify: uv run pytest subprojects/docket/tests/test_cli.py && grep -q 'def test_a_nested_store_reads_the_same_in_flight_answer_as_the_default' subprojects/docket/tests/test_cli.py
recurrences: 2026-09-21 PL-X9NB
---

**Problem.** `_tracked` in `subprojects/docket/src/docket/cli.py` derives the
repository root as `args.items.parent`. That is correct only where the store
sits one level below the root. Pointed at this project's own layout -
`bin/docket --items docs/items ...` - it resolves the root to `docs/`, so the
queue prefix it hands `branches_in_flight` is `items/` while git prints
`docs/items/...`.

Nothing matches, so `_annotates_only` reads every commit as work and
`_item_file_ids` reads none as a file edit. Observed 2026-09-06 on a scratch
repository while working `PL-N1JK`: a triage-only commit came back `IN FLIGHT`
under the nested form and as the weaker file-edit mark under the root-level
form, from the same commit.

**Why it matters.** It is the silent-wrong-answer shape. The command exits
zero, the output looks exactly like a real mark, and the direction is the one
`PL-X3WZ` removed - every item any branch has captured or triaged disappears
from `docket next`. The default path (`bin/docket` with no `--items`, which
uses `find_root()`) is unaffected, so this fires only for a caller who typed
`--items`, which the `--items` flag invites and every test in `test_cli.py`
avoids by putting the store at `<root>/items`.

`_tracked`'s own docstring already anticipates a store outside the repository
and says such a case "comes back as the empty prefix, which no path git prints
can match". This is the neighbouring case it does not anticipate: a store
*inside* the repository but more than one level down, where the derived root is
wrong rather than absent.

**Where.** `subprojects/docket/src/docket/cli.py`, `_tracked` and `_load`,
which share the `args.items.parent` derivation.

**Done when.** The root is resolved from the repository rather than from the
store's parent - `find_root()` walking up from `args.items`, or git's own
`rev-parse --show-toplevel` - so that `--items docs/items` and no `--items` at
all give the same in-flight answer, with a test at the nested depth this
project actually uses.

**A second symptom, observed 2026-09-21 working `PL-MBTZ`.** The wrong root
also breaks every `git show <rev>:<path>` this module makes. `git ls-tree` run
from a subdirectory prints paths relative to *that directory*, while
`<rev>:<path>` is always resolved from the repository root - so under
`--items <repo>/docs/items` the listing says `items/PL-0001-....md` and the
`show` for it finds nothing. `bin/docket stranded` then printed every finding
as `(title unreadable)`, and `vcs._standing`, handed two empty texts, fell
through to its report-it direction for every item on every branch. Exit zero
throughout. Reproduced on a scratch repository while building the standing
predicate; the same derivation is the cause, so it closes with this item
rather than beside it.
