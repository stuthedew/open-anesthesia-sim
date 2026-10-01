---
id: PL-KGYT
title: Six readers found 2026-10-01 respell facts docket already exports - an item's status, file name and commits, its pr: and id:, the default branch, the pull requests a notes file names - four days after PL-PVW2 said spent, so a tool still arrives at its own spelling of a docket predicate
priority: P1
effort: M
status: ready
classes: defect
feature: recorded-not-inferred
touches: docs/items, tools/doc_check.py, tools/pr_body_check.py, tools/main_ci_status.py, tools/tag_release.py, tools/update_armed.py, tools/pr_record_check.py, tools/required_checks_check.py, Makefile, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, tests/unit/test_doc_check.py, tests/unit/test_pr_body_check.py, tests/unit/test_main_ci_status.py, tests/unit/test_tag_release.py, tests/unit/test_update_armed.py, tests/unit/test_pr_record_check.py, tests/unit/test_required_checks_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: a tool reads each fact docket exports through docket instead of respelling it, so the apparatus stops paying an item per reader for a head that was declared spent
verify: grep -qE '^\*\*Swept 2026-' docs/items/PL-KGYT-*.md
root-cause-of: PL-M9R6, PL-2BWP, PL-X766, PL-XSL4, PL-24BC, PL-9KLN
generator: live - six readers filed 2026-10-01, four days after PL-PVW2 said spent; its sweep covered the nine predicates it had enumerated, and nothing tells a tool that a fact docket exports is read through docket, so each such fact can be respelled again until the sweep this head owes finds none
misread: Which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it
---

**Problem.** Six readers found 2026-10-01 respell facts docket already exports - an item's status, file name and commits, its pr: and id:, the default branch, the pull requests a notes file names - four days after PL-PVW2 said spent, so a tool still arrives at its own spelling of a docket predicate

`PL-PVW2` drained on 2026-09-26 with `generator: spent - ... a sweep of tools/, .claude/hooks/ and docket found no other reader to hand it a member`. The 2026-10-01 survey (`PL-HC8P`; `docs/WORKING_NOTES.md` § "Open thread: recorded-not-inferred") found six, each a tool or module in `PL-PVW2`'s own `touches` respelling a fact docket exports:

- `PL-M9R6` - the pull requests a notes file names (`release.REFERENCED_RE`), read as a substring.
- `PL-2BWP` - an item's commits (`vcs.leading_ids`), read as `git log --grep`.
- `PL-X766` - an item's status (`docket.model`'s parser), read by a regex.
- `PL-XSL4` - an item's `pr:` and `id:`, and a subject's leading ids, read by regexes over 2,000 characters.
- `PL-24BC` - an item's file name (`vcs.ITEM_FILE_RE`), read as `startswith`.
- `PL-9KLN` - the default branch (`vcs.default_base`), as literals in five tools and the Makefile.

`PL-PVW2`'s sweep looked for the nine predicates it had enumerated. These are facts docket exports that its list never named, and nothing told a tool that a fact docket exports is read through docket - the half `.claude/rules/apparatus-standard.md` § "Read the fact from its record; where none exists, write one" now states at write time (`PL-HC8P`, 2026-10-01).

**Why it matters.** Six readers four days after a head said spent is the register's own definition of a fix that did not hold: three post-close instances count as a generator (`.claude/skills/docket/modes/triage.md`). Each costs an item per reader until the mechanism stops, and a tool's own spelling answers differently from docket's at the moments the audit, the recovery record and the release check are trusted.

**Done when.** The six members are closed, the write-time rule stands, and a sweep of `tools/` and `subprojects/docket/` for any other regex or literal over a fact `docket.model`, `vcs` or `release` exports is recorded in this brief under a `**Swept <date>.**` heading at the start of a line, with its count; then `generator:` says spent and the head closes. `verify:` names that heading, the one thing only the head's own work writes, since a member's clause cannot prove the head (`docket check` refuses a shared clause); the members' own commands prove the members.

**Working order.** `PL-M9R6` first (a silent wrong answer), then `PL-2BWP` and `PL-XSL4` (both audit or write records), then `PL-X766`, `PL-9KLN`, `PL-24BC`.

**Generator check.** This head states the fact, in `PL-PVW2`'s words so the two sort together in `bin/docket generators --misread`. The mechanism outlived its fix because the fix was a sweep over an enumerated list, and the two endings bind (`CLAUDE.md` § "A root cause of more than two items is pulled, not queued"): not fixed in the session that filed it, so that session's reply ends with the prompt starting a fresh one on it.
