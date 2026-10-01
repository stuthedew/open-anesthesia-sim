---
id: PL-M9R6
title: tools/doc_check.py check_tag_span_covers_its_notes tests the release notes for pull request #N as a substring, so #12 is covered by a note naming #123 and the check passes while the span it stands for is uncovered
priority: P2
effort: S
status: done
classes: defect
feature: recorded-not-inferred
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-01
pr: 1271
payoff: a tag whose span holds a closure its notes never name is refused instead of passing on a longer number that happens to contain it
verify: grep -q 'def test_a_span_note_names_its_pull_request_as_a_token' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py check_tag_span_covers_its_notes tests the release notes for pull request #N as a substring, so #12 is covered by a note naming #123 and the check passes while the span it stands for is uncovered

**Recorded alternative, from the 2026-10-01 survey.** Read the exact `— #N` token the notes already write (`release.REFERENCED_RE`) instead of testing for a substring; `PL-JLYG` names the function for a different defect. Shape C: a hard check deciding coverage from wording.

**Why it matters.** The check exists to refuse a tag whose span holds a closure its notes never name. A substring read passes an uncovered span whenever the number is a prefix of a longer one the notes name - `#127` by `#1270`, and every pull request under 1000 by one of the four-digit numbers the notes carry now - so the check gives a wrong answer silently, the first of `CLAUDE.md`'s three friction tests. `release.REFERENCED_RE` already states the token the notes write (` — #N` at the end of a line), so this is a second spelling of a grammar docket exports.

**Reproduced 2026-10-01.** `tools/doc_check.py:3466` reads `if f"#{item.pr}" in notes.read_text(...)`; `python3 -c 'print("#12" in "— #123")'` prints `True`. `subprojects/docket/src/docket/release.py:565` holds `REFERENCED_RE`.

**Done when.** `check_tag_span_covers_its_notes` matches each note's ` — #N` token through `release.REFERENCED_RE`, or a reader docket exports for it, a test pins that `#12` is not covered by a note naming `#123`, and the spans the check reads today answer as before.

**Generator check.** An instance of `PL-PVW2`'s fact - which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it - filed after that head drained on 2026-09-26. Six such instances filed 2026-10-01 make `PL-KGYT`, this item's head.
