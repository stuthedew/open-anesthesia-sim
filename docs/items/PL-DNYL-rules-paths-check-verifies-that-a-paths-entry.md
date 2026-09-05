---
id: PL-DNYL
title: rules_paths_check verifies that a paths: entry is anchored but not that it points anywhere, so a typo'd prefix is a rule that silently never fires
priority: P2
effort: S
status: done
classes: defect, infra
feature: worker-instructions
milestone: v0.4.2
touches: tools/rules_paths_check.py, tests/unit/test_rules_paths_check.py
added: 2026-09-05
closed: 2026-09-05
pr: 363
verify: python3 tools/rules_paths_check.py && grep -q 'def test_a_prefix_that_resolves_to_nothing_is_refused' tests/unit/test_rules_paths_check.py
---

**Problem.** `tools/rules_paths_check.py` (`PL-LLWN`) holds every
`.claude/rules/*.md` `paths:` entry to a leading `/`, which closes the two
failure modes that were live: an unanchored glob matching its name at any
depth, and the `./` spelling that matches nothing. It says nothing about
whether the anchored path exists. `/scr/anesthesia_sim/core/**` is anchored,
passes the check, and delivers the rule to no session ever.

**Why it matters.** Same failure as the `./` row the check already refuses, and
the check's own docstring names that one as worth catching because "it would
look correct in review". A typo'd prefix is worse on that test, not better: `./`
is at least visibly unusual, while a transposed directory name reads as
correct at every glance. Both leave no trace - a rule that never fires produces
no output, so nothing distinguishes it from a rule whose paths were never
opened.

The blast radius is the same as `PL-6SBB`'s and `PL-ZQ35`'s: these files carry
the standards a session is held to, so one silently not loading means work
judged against a bar nobody applied.

**Where.** `tools/rules_paths_check.py`, beside the anchoring rule;
`tests/unit/test_rules_paths_check.py`.

**Approach.** The literal prefix of an entry - everything before the first
glob metacharacter (`*`, `?`, `[`) - is a real path, and whether it exists is
decidable by reading the tree. `/docs/MODEL.md` must be a file;
`/src/anesthesia_sim/core/**` must have `src/anesthesia_sim/core/` as a
directory. Report a prefix that resolves to nothing, naming the entry and the
nearest existing ancestor, which is what turns "this is wrong" into "you meant
this".

Deliberately still not attempted, and this does not reopen it: whether the glob
describes the *right* set of files. That stays judgment. This asks only whether
it describes any file at all, which the tree answers.

**Decided** (project owner, 2026-09-05): a **hard error**, not an advisory. A
rule may not name a path that does not exist yet - scope written ahead of the
code it governs is written when that code lands, not before. The reasoning is
the same one that made the anchoring rule an error rather than a warning: these
files carry the standards a session is held to, so one silently not loading
means work judged against a bar nobody applied, and there is no reading of the
tree under which a dead path is the intended state.

**Done when.** `make check` **fails** on a `paths:` entry whose literal prefix
resolves to nothing, and the message names both the prefix that is missing and
the nearest existing ancestor, so the reader is shown where the path stopped
being real rather than only that it was not.
