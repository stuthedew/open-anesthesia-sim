---
id: PL-KGYT
title: Six readers found 2026-10-01 respell facts docket already exports - an item's status, file name and commits, its pr: and id:, the default branch, the pull requests a notes file names - four days after PL-PVW2 said spent, so a tool still arrives at its own spelling of a docket predicate
priority: P1
effort: M
status: done
classes: defect
feature: recorded-not-inferred
touches: docs/items, tools/doc_check.py, tools/pr_body_check.py, tools/main_ci_status.py, tools/tag_release.py, tools/update_armed.py, tools/pr_record_check.py, tools/required_checks_check.py, Makefile, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, tests/unit/test_doc_check.py, tests/unit/test_pr_body_check.py, tests/unit/test_main_ci_status.py, tests/unit/test_tag_release.py, tests/unit/test_update_armed.py, tests/unit/test_pr_record_check.py, tests/unit/test_required_checks_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-01
pr: 1271
payoff: a tool reads each fact docket exports through docket instead of respelling it, so the apparatus stops paying an item per reader for a head that was declared spent
verify: grep -qE '^\*\*Swept 2026-' docs/items/PL-KGYT-*.md
root-cause-of: PL-M9R6, PL-2BWP, PL-X766, PL-XSL4, PL-24BC, PL-9KLN, PL-4NG0, PL-5QG4, PL-DHGC, PL-W560, PL-M6GY, PL-8P31, PL-9L39, PL-PFD9
generator: spent - the six members closed on #1271, and .claude/rules/apparatus-standard.md § Read the fact from its record now tells a tool at write time (PL-HC8P); the 2026-10-01 sweep searched every name model, vcs and release export rather than an enumerated list, and its 63 finds are filed as eight members, so no reader of an exported fact is left for a later session to find one at a time
misread: Which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it
recurrences: 2026-10-01 PL-4NG0
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

**Progress, 2026-10-01.** Worked on `claude/vibrant-euler-bs5e09`, draft pull request `#1271`, which claims the head and all six members. All six are closed there, each in its own commit: `PL-M9R6`, `PL-2BWP`, `PL-XSL4`, `PL-X766` and `PL-9KLN` each with a regression test that fails on the old code, and `PL-24BC` by its deleted line, since no input tells its two spellings apart. Each was measured against the reader it replaced on this tree before it landed - 1,200 span pairs, 292 live briefs and 926 backlinks all unchanged; 156 of 1,594 subjects lose an id that `pr_body_check` used to take from mid-subject. `PL-9KLN` added `vcs.default_branch`, the default branch by its name on the remote, which four of its five tools now read, and kept `origin/main` on its two Makefile lines with the reason beside each.

**Swept 2026-10-01.** 65 sites, 63 of them new. The search covered `tools/`, `subprojects/docket/src/docket/` and `subprojects/docket/tools/` for every module-level name and public function `docket.model`, `vcs` and `release` export, and the `store` id constants they build on, family by family; tests were left out, since a fixture literal is an input and not a reader. Of 76 hits read against the source, 11 were rejected: the nine in the finished one-off `subprojects/docket/tools/migrate_from_punch_list.py`, which reads the retired punch-list format; `tools/pr_body_check.py`'s `parse_record`, which reads the record format that tool writes; and `open_pull_requests.py`'s one `"merged"` literal. Two more, `verify.py`'s `PR_LINE_RE` and `RECURRENCE_ENTRY`, are `PL-FYV7`'s already. The other 63 are eight facts, filed under `feature: read-facts-through-docket` and named in `root-cause-of:` above: the git facts `vcs` exports (`PL-4NG0`, 13 sites), an item's file name (`PL-5QG4`, 7), its front matter (`PL-DHGC`, 10), `model`'s sets (`PL-W560`, 5), a release notes file's name, version and bullets (`PL-M6GY`, 12), the version token (`PL-8P31`, 7), a code span (`PL-9L39`, 4) and path containment (`PL-PFD9`, 5). Most agree with the export on every input today, and each brief names the ones that do not. One is wrong now: `tools/item_reads.py` reads 20 of 1,624 closed items as open (`PL-DHGC`).
