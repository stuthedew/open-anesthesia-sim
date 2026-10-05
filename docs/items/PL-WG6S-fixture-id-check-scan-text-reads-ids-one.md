---
id: PL-WG6S
title: fixture_id_check.scan_text reads ids one physical line at a time in a shell file under .claude/, where a backslash-newline joins a word, so an id split that way is reported as malformed and the joined one is missed; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/fixture_id_check.py, subprojects/docket/src/docket/shell.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-R417's shell slice, 2026-10-05
added: 2026-10-04
payoff: an id a shell file under .claude/ carries across a backslash-newline is judged as the one id bash reads, so a malformed one can no longer pass as two fragments
verify: grep -q 'fixture ids, an id a backslash-newline joins' tests/unit/test_doc_check.py
---

**Problem.** fixture_id_check.scan_text reads ids one physical line at a time in a shell file under .claude/, where a backslash-newline joins a word, so an id split that way is reported as malformed and the joined one is missed; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

POSIX XCU § 2.2.1. `collect` hands `scan_text` every file under `.claude/`, hook scripts included; over "echo PL-K7\" / "QX" / "echo PL-K7QX\" / "Z" it reports `PL-K7` on line 1, where bash reads `PL-K7QX`, which is valid, and `PL-K7QXZ`, which is not. Markdown and JSON under `.claude/` cannot join a token, so only shell files carry the form. Latent and contrived: no `PL-...\` ends a line anywhere under `.claude/`. The lowest-consequence member the sweep found.

**Why it matters.** `tools/fixture_id_check.py` scans `.claude/` because an
example there is copied into an item, and judges each token as an id. A shell
file joins a word across a backslash-newline, so the check reads a fragment
where bash reads the id: a well-formed id split that way is refused, and a
malformed one passes. The second is the silent half, the one the check exists
to make loud.

**Reproduced 2026-10-05, at triage.** On `main` at `c479363e`, under python3
3.11.15, `scan_text` over a `.sh` file holding `echo PL-K7\` over `QX` and
`echo PL-K7QX\` over `Z` reported `PL-K7` on line 1 and nothing else. The eight
`.sh` files under `.claude/hooks/` hold no backslash-newline at all, and
docket's shell lexer reads each of them whole.

**Done when.** `scan_text` reads a `.sh` file's lines as bash reads their
characters, through docket's shell lexer: each backslash-newline bash removes,
outside single quotes, a comment and a quoted here-document's body, is joined,
so the id it builds is judged whole and reported on the line it starts on, and
the lines from wherever that lexer stops reading are judged as written.
`PL-R417`'s guard gains a `fixture ids, ` case, failing on today's reader.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
