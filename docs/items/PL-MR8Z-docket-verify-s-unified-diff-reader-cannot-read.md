---
id: PL-MR8Z
title: docket verify's unified-diff reader cannot read git's quoted header path and takes a removed -- or added ++ content line for a file header, so a deleted assertion in a file whose name git quotes, or a content line opening with two signs, drops out of the line reading; latent
priority: P2
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: verify reads every changed line of a branch, so a file git quotes or a line opening with two signs can no longer let a deleted assertion or an added suppression through on a reading of none
verify: grep -q 'def test_a_removed_line_in_a_file_git_quotes_is_charged_to_that_file' subprojects/docket/tests/test_verify.py && grep -q 'def test_a_content_line_opening_with_two_signs_is_not_read_as_a_header' subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify's unified-diff reader cannot read git's quoted header path and takes a removed -- or added ++ content line for a file header, so a deleted assertion in a file whose name git quotes, or a content line opening with two signs, drops out of the line reading; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`DIFF_HEADER_RE` (1622) cannot read a header path git quotes, so `_net_line_changes` assigns that file's lines to no file: a deleted `assert x == 1` in an unparseable `café.py` gives "PASS ... none" where `plain.py` gives "FAIL ... 1 line(s)". `_net_line_changes` tells a `---`/`+++` header from content by its second character, so a removed line whose content opens `--` and an added one opening `++` are dropped: a diff holding `--1` and `++2` loses both. Both reach only the line reading: a file the interpreter cannot parse, and the `.toml`, `.cfg` and `.ini` files the suppression check reads by line. Not a member of `PL-R417`. Latent: git quotes no tracked path.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, in a scratch git repository where git printed the header as `diff --git "a/caf\303\251.py" "b/caf\303\251.py"`: a commit deleting `assert x == 1` from an unparseable `café.py` gave `_net_line_changes` the removed pair `('', 'assert x == 1')`, and `assertion_check` over `removed_assertions` returned `passed=True` with detail `none` while naming the file as read line by line; the same commit on `plain.py` returned `passed=False` with `1 line(s) in a file read line by line`. In the same repository a `setup.cfg` edit removing the line `-1` and adding `+2` put nothing in either of `_net_line_changes`' lists, because the diff lines `--1` and `++2` were skipped as file headers. Re-counted the same day: none of the 2,687 tracked paths is one `git ls-files` prints quoted.

**Why it matters.** `no existing assertion removed` is one of the four integrity checks `--self` may never relax, and this is its unsafe direction: a PASS reading "none" over an assertion the branch deleted, so a close-out that weakened a test is accepted on a confident answer rather than a declined one. Both halves reach only the line reading, the Python files the bare `python3` cannot parse and the `.toml`, `.cfg` and `.ini` files the suppression check reads by line, which is why it is latent. The quoted-path half is a read `-z` cannot reach: `PL-8HSX` made every path listing ask for `-z`, but measured on git 2.43.0 a patch's `diff --git` header stays quoted under `-z`, and `core.quotePath=false` still quotes a `"` in it, so this reader has to unquote what git prints.

**Generator check.** An instance of `PL-4W2L`'s fact, whether a branch's diff weakens its tests: an assertion removed or loosened, filed after that head closed on 2026-09-23, and one of two since, with `PL-GXLX`: the diff reader misses how git spells a quoted path and which lines are headers, so a removed assertion goes uncounted. Its quoted-path half shares a narrower fact with `PL-PXT7`, how git quotes a path it prints; two items, and no head states it.

**Done when.** `_net_line_changes` charges every added and removed line to the file it came from. A header git prints quoted yields the unquoted path, so a deleted assertion in an unparseable `café.py` is reported as it is in `plain.py`; and only the `---` and `+++` lines that head a file's patch are read as headers, so a content line removed as `--1` or added as `++2` reaches the fold. `test_a_removed_line_in_a_file_git_quotes_is_charged_to_that_file` and `test_a_content_line_opening_with_two_signs_is_not_read_as_a_header` in `subprojects/docket/tests/test_verify.py` pin the two halves.
