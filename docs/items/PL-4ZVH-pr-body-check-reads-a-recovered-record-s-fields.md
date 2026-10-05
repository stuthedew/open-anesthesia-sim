---
id: PL-4ZVH
title: pr_body_check reads a recovered record's fields and an appended trailer one physical line at a time, so a commit: value folded onto the next line reads as empty and anchors skips that record silently, and a folded Co-authored-by trailer is left in the body; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/pr_body_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-R417's change-record slice, 2026-10-05
added: 2026-10-04
closed: 2026-10-05
pr: 1379
payoff: a recovered record whose commit: is wrapped onto a second line is checked or named rather than skipped in silence, and a folded Co-authored-by trailer no longer makes a matching body read as differs
verify: grep -q 'recovered records, a commit continued on an indented line' tests/unit/test_doc_check.py && grep -q 'appended trailers, a trailer folded onto a second line' tests/unit/test_doc_check.py
---

**Problem.** pr_body_check reads a recovered record's fields and an appended trailer one physical line at a time, so a commit: value folded onto the next line reads as empty and anchors skips that record silently, and a folded Co-authored-by trailer is left in the body; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

A recovered record follows the item front-matter convention, where an indented line continues a value (`model._fold`). `parse_record` reads `commit:` over an indented SHA as an empty commit, and `anchors` then returns 0 - the record never checked - though its own failure message asks for exactly such a hand edit. `APPENDED_TRAILER_RE`, in `normalise` for `--compare` only, does not strip a trailer `git interpret-trailers` folds onto a second line, so the verdict reads `differs`. Latent: none of the 265 records folds a value, and none of 1,037 trailers is folded.

**Why it matters.** `--anchors` is the one check tying a recovered body to the
tree (`PL-73G8`), and `make check` runs it. A record whose `commit:` it reads
as empty is skipped with nothing said, so the anchor a history rewrite left
dangling there passes, and the check reports a corpus it never read as clean
- on the shape its own failure message invites, since the repair it names is
a hand edit of that field. `docket verify`'s `_added_record` already reads
the same files through `docket.model`'s fold, so the two readers of one
record can disagree about it. `--compare`'s half is noise rather than
silence: a folded trailer makes a body that matches read as `differs`, which
buries the bodies that do.

**Reproduced 2026-10-05, at triage.** On `main` at `b67dace8`, under python3
3.11.15: a record holding `commit:` over an indented 40-zero hash gave
`parse_record` `commit` `''`, and `--anchors` over it exited 0 and printed
nothing, where the same hash on the field's own line exits 1 naming it. A body
ending `Co-authored-by: A Long Name` over ` <a@example.com>` came back from
`normalise` with the trailer in it, while git 2.43.0's `interpret-trailers
--parse` reads those two lines as one trailer. Of the 265 records, 204 carry
`commit:` and 61, all `recorded:`, carry none; both readers read every one of
them alike.

**Done when.** `parse_record` reads a record's front matter through
`docket.model`'s fold, so a value continued on an indented line is read
whole, as `_added_record` reads it. `--anchors` names each record whose
`commit:` it cannot read - one with no front matter, or a `commit:` key with
no value the fold reads - on a line of its own, without failing, where it now
skips it; a `recorded:` record, which never carried one, stays unnamed.
`APPENDED_TRAILER_RE` takes a `Co-authored-by:` trailer with every line git
folds into it, one led by a space or a tab (git 2.43.0's
`Documentation/git-interpret-trailers.txt`: "each subsequent line starting
with at least one whitespace, like the "folding" in RFC 822"), so a folded
trailer reads as GitHub's and not the
body's, and a trailer quoted on an unindented line is still compared.
`PL-R417`'s guard gains a case per reader and form, each failing on main's
reader.

**As built, 2026-10-05.** `parse_record` reads a record through
`docket.model.parse_front_matter`, the public form of the fold `_added_record`
reads, after turning CRLF into LF, and drops the one blank line `_write` puts
after the front matter; it answers `None` where no field is read. Over all 265
records it reads every field and body exactly as main's line reader did.
`anchors` prints a line of its own on stdout naming each record with no front
matter or with a `commit:` holding no value, exit unchanged; a `recorded:`
record stays unnamed, and over today's tree it prints nothing and exits 0.
`APPENDED_TRAILER_RE` takes each `Co-authored-by:` trailer with every line
after it led by a space or a tab. `PL-R417`'s guard gained two cases, and
`test_anchors_name_a_record_whose_commit_they_cannot_read` holds the naming;
all three fail with main's `tools/pr_body_check.py` swapped in.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.
