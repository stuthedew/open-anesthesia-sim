---
id: PL-8FT2
title: Review the 340 regular expressions in tools/, .claude/hooks/, subprojects/docket/ and the tests that tools/regex_baseline.py lets stand without a reason, starting with the ones that read a format a module already parses
status: untriaged
feature: regex-review
added: 2026-11-03
---

**Problem.** Review the 340 regular expressions in tools/, .claude/hooks/, subprojects/docket/ and the tests that tools/regex_baseline.py lets stand without a reason, starting with the ones that read a format a module already parses

`PL-7JYV` stops a session before it writes a regular expression with no
written reason, and lets the 346 calls the tree already held stand in
`tools/regex_baseline.py`. On 2026-11-03, 340 of them were outside `src/`:
135 in `tools/`, 103 in docket's package, 12 in docket's own tools, 15 in
`.claude/hooks/`, and 75 in the test trees (41 in `tests/unit/`, 28 in
docket's tests, 5 in `tests/integration/`, 1 in `tests/reference/`).

**Why it matters.** About 60 items mention a regular expression, and
`PL-9HD1` traced three to one pattern that read item front matter a line at a
time. A pattern that restates a grammar a module already parses is the shape
the dead end `PL-4S6C` records, and it re-enters until the copy is removed.

**Approach.** Work the patterns that read a format some module already parses
first: item ids, front matter, Markdown structure, shell words and version
numbers, which `regex_check.KNOWN_READERS` names. Then the patterns a string
method replaces outright. For each one that stays, write a `# regex:` comment
with the reason. Lower or delete its baseline entry in the same commit. The
work splits naturally by directory, so a session may close it in several
branches, and should file a member item per directory where one runs long.

**Done when.** `tools/regex_baseline.py` holds no entry outside `src/`.

**Leads from the "Regex usage code review" session, 2026-11-03.** It judged
most of these patterns to be the right tool: shape checks of ids, versions and
hashes, provided each grammar comes from one exported pattern. The code checks
under `tools/` already read Python with `ast`, and `docket.vcs` reads git's
machine formats. It placed the real risk in three places, which are where to
start:

1. Readers of the meaning of English prose, in `tools/doc_check.py` and
   docket's `checks.py`.
2. Docket's hand-written readers of Markdown, YAML and shell. CI now tests
   them against markdown-it-py and PyYAML, and the review found no defect
   filed against them since 2026-10-12 for Markdown and YAML, and since
   2026-10-20 for shell.
3. The Bash guards, which decide from a command's spelling (`PL-SG93`).

It also noted that docket's `SEMVER_PATTERN` uses `\d`, which matches any
Unicode digit, the problem `PL-PNGQ` fixed for `isdigit`. This session
confirmed the pattern in `subprojects/docket/src/docket/model.py`.
