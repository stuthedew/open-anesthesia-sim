---
id: PL-9L39
title: Four regexes spell a Markdown code span instead of release.CODE_SPAN_RE - doc_check twice, checks and verify - and each reads a double-backtick span differently from it
priority: P3
effort: S
status: done
classes: defect
feature: read-facts-through-docket
milestone: v0.5.21
touches: tools/doc_check.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/release.py, subprojects/docket/README.md, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_checks.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-03
pr: 1288
payoff: a double-backtick span reads the same in every checker, so a brief quoting a backtick cannot pass one check and trip another
verify: ! grep -qF '_CODE_SPAN = re.compile' subprojects/docket/src/docket/checks.py && ! grep -qF 'CODE_SPAN_RE = re.compile' tools/doc_check.py && ! grep -qF 'BACKTICK_RUN_RE' tools/doc_check.py && ! grep -qF '% 2 == 1' tools/doc_check.py && grep -qF '{CODE_SPAN_PATTERN}' subprojects/docket/src/docket/verify.py
---

**Problem.** Four regexes spell a Markdown code span instead of release.CODE_SPAN_RE - doc_check twice, checks and verify - and each reads a double-backtick span differently from it

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. `tools/doc_check.py:367` (`CODE_SPAN_RE`) and `:662` (`BACKTICK_RUN_RE`); `subprojects/docket/src/docket/checks.py:2953` (`_CODE_SPAN`, beside an import of the real one); `subprojects/docket/src/docket/verify.py:199`. Whether each reader wants a CommonMark span or a looser backticked token is the first question for whoever works it.

**Searched 2026-10-03, before the work.** An `ast` walk of `tools/`, `subprojects/docket/src/docket`, `subprojects/docket/tools`, `.claude/hooks/` and `bin/` for every non-docstring string literal holding a backtick found one more reader of this fact: `tools/doc_check.py`'s `_marks_code`, which took an odd count of backticks to an occurrence's left as inside a span (``before.count("`") % 2 == 1``), wrong on a double-backtick span and inside out on a line a wrapped span closes. Left out, each for its reason: `MATH_SPAN_RE` and `MATH_EDGE_RE`, which read GitHub's inline math rather than a code span; the regexes matching one token shape between single backticks - a reference file, a test name, a `file:line`, a document or item citation, and the identifiers `tools/contrast_check.py` and `tools/core_vocabulary_check.py` read - which read a citation's own syntax and decide nowhere where a span starts; `roadmap.py`'s backtick replacement before it reads ids; and the shell's command substitution in `shell.py` and `.claude/hooks/shell_split.py`.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites** reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.

**Done, 2026-10-03.** Every reader wants a CommonMark span, which answers the brief's first question: each asks what a reader of the rendered page sees as code. So each now takes `docket.release.CODE_SPAN_RE` on the input it read before - a line where it read a line (`verify.strip_non_code`, `doc_check._without_code`, `_marks_code`), a passage or a document where it read one (`checks._standing`; doc_check's path citations, absent markers, `make` mentions and provenance cells). The export gained what they needed: `run` and `content` groups; `CODE_SPAN_PATTERN`, flagless, which `verify.NON_CODE_RE` takes into its alternation; and a paragraph bound, a blank line ending a span, since it now reads whole documents, where one stray backtick would otherwise pair with a run paragraphs below and turn every later span inside out. `doc_check._code_spans` reads a document with its fenced blocks blanked, since the export would read a fence's own run as a span, and then each fenced line on its own, which keeps `docs/ARCHITECTURE.md`'s 66 package-map citations checked as before.

Measured against `origin/main` on the tree before landing, from a detached worktree:

- doc_check's document readers: across its 37 documents the old regex missed 152 wrapped spans and 86 spans after one on their line, and read 108 stretches of prose as code. Eleven citations and `make` mentions are now read that were not; ten resolve, and `subprojects/docket/README.md`'s `docs/docket.toml`, a path that paragraph names as missing, now carries the `absent:` marker the check asks for. No section citation's reading changed (535).
- `checks._standing`: three briefs (`PL-0HPV`, `PL-9VPH`, `PL-Y0RZ`) read a quotation differently at sampled positions, each beside a wrapped span, and the new reading is right in all three. `bin/docket check`'s output is unchanged, and `_answered_beneath` and `_marks_recommendation` read all 1,925 briefs as before, so the paragraph bound changed no answer today.
- `verify.strip_non_code`: 28 of 392,571 lines (every tracked `.py` line, and every line history added to one) strip differently - double-backtick literals and fence lines - and no suppression verdict changed.
- `_without_code`: 21 lines of 2,306 Markdown files blank differently, and the math check's findings are unchanged. `_marks_code`: against the document-level reading, the backtick count misread 1,861 of 133,251 words on lines holding a backtick and the export, still a line at a time, misreads 1,061; the candidate lists for four bases moved by a few lines each.

Eight tests pin it: one per changed answer in `test_release.py`, `test_verify.py`, `test_checks.py` and four in `tests/unit/test_doc_check.py`, which fail on `origin/main`, and one guarding the fenced-line reading, which passes there by design. `verify:` now names all five sites; it named two. The three line readers still cannot see a span wrapped from the line above, and `PL-Z8RS` holds that for the two in doc_check; `verify` reads one diff line by necessity.
