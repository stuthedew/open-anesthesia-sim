---
id: PL-W9VC
title: doc_check's _hash_comments reads a host claim's comments a physical line at a time, so a Makefile comment a backslash continues is read short, and a hash-led line inside a here-document, a multi-line quoted string, a YAML block scalar or a TOML multi-line string is read as a comment: an undated claim is missed or a dated one refused; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit/test_doc_check.py, subprojects/docket/src/docket/shell.py, subprojects/docket/src/docket/frontmatter.py, subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_shell.py, subprojects/docket/tests/test_frontmatter_reference.py
blocked-by: PL-PBNK
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-17
payoff: a hash-led line that is a here-document's, a quoted string's or a YAML block scalar's content stops being read as a comment, so it no longer decides whether the host-claim gate refuses a sentence, and a workflow's run scripts have their comments read as bash reads them
verify: grep -q 'def test_a_hash_line_inside_a_here_document_or_a_quoted_string_is_no_comment' tests/unit/test_doc_check.py
---

**Problem.** doc_check's _hash_comments reads a host claim's comments a physical line at a time, so a Makefile comment a backslash continues is read short, and a hash-led line inside a here-document, a multi-line quoted string, a YAML block scalar or a TOML multi-line string is read as a comment: an undated claim is missed or a dated one refused; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
`tools/doc_check.py`'s third part.
`_hash_comments`, new in `#1387`, gives `_host_claim_texts` the comments of a
Makefile, a shell script, a workflow and a TOML file, one physical line each.
In GNU make 4.3 a comment ending in a backslash takes the next line with it
("Splitting Long Lines"), which `_make_lines`' docstring says too; a `#` line
inside a here-document body (POSIX XCU § 2.7.4), a quoted string (§ 2.2), a
YAML block or quoted scalar (YAML 1.2.2 § 8.1, § 7.3) or a TOML multi-line
string is content, not a comment.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against GNU make 4.3, bash 5.2.21, dash, PyYAML 6.0.3 and `tomllib`,
with a real host name in each claim; `example.org` stands in for it here, and
each block below is one file:

```text
Makefile:
# example.org is blocked here, \
probed 2026-10-01.

Makefile:
# The host example.org \
  is blocked.

a.sh:
cat <<EOF
# example.org is blocked
EOF
```

The first is refused as undated, the second goes unreported, and the third
is refused at its second line, where bash prints that line as data; the
quoted-string, YAML block-scalar and TOML multi-line-string forms are refused
the same way. make 4.3 reads the continued comment as one (`all:` under it is
inside
it). Latent: the Makefile has no comment ending in a backslash, and the only
`#` lines inside a continued statement are nine in
`.github/workflows/drift.yml`'s `run:` bodies, which are the script's own
comments.

Beside it, in the same function: a comment that follows a value or command on
its line is never read, and the docstring alone says so.

**Re-confirmed 2026-10-11** on main at `16a20a4f`, under python3 3.13.16:
the continued Makefile comment dated on its second line is refused as
undated, the one whose refusal is on its second line goes unreported, and the
here-document's `#` line is refused at line 2.

**The quoted-string form stands in a tracked file, found at triage
2026-10-11.** `.claude/hooks/floor-interpreter-guard.sh` hands `python3 -c` a
single-quoted string from line 74 to line 199, and the 40 `#` lines inside it
are Python's comments, which `_hash_comments` reads as eight runs of shell
comment. None names a host or a refusal, so no answer changes today - the same
standing as `drift.yml`'s `run:` bodies above, which the capture counted and
this one missed. Whether a form present with no answer changed is live for
`PL-R417` is the parent pass's call, and it was reported there.

**Why it matters.** The host-claim check is a hard gate, so a misread comment
either fails `make check` on a claim that carries its date or passes one that
does not; both are the floor's violation, and the first makes a writer reword
a dated, correct sentence. Each format here already has a reader that knows
where its statements end, so the line-at-a-time reading is a second answer
that can disagree with it.

**Scope after `PL-PBNK`, added at triage 2026-10-11.** `PL-PBNK` retires the
host-claim check's reach into YAML, TOML and Makefile comments, where none of
its 31 claims sits. Done first, it leaves this item the shell forms - the
here-document and the multi-line quoted string - so this is `blocked` on it
rather than built for formats that are about to stop being read.

**Re-scoped 2026-10-17, when `PL-PBNK` closed.** It retired the TOML and
Makefile reach and kept YAML's, since a workflow comment held a real claim
until `#1387` (`PL-B3MK`). So the Makefile continuation and the TOML
multi-line string went with the reach, and this item kept the shell forms and
the YAML ones: a block scalar's content and a multi-line quoted scalar, with a
workflow's `run:` scripts, block scalars themselves, read as bash reads them.

**Built 2026-10-17.** A shell script's comments are `docket.shell.comments`',
the lexer's own record of each comment it discards, so a here-document's body
and a quoted string hold none and a comment after a command is read; a script
it cannot read to its end is read to that line and declined from it by name. A
YAML file's are `docket.frontmatter.comments`', placed on the walk `keys`
already takes, which `test_frontmatter_reference.py` holds to PyYAML: a `#`
opens one exactly where rewriting the text after it leaves the document PyYAML
composes unchanged, over the reference corpus with a trailing comment after a
block scalar, a comment in a flow collection and one on a plain scalar's
continuation line added to it. Where a block scalar's content ends is
`docket.frontmatter.block_content`, which `_run_script` now reads too rather
than its own reckoning, and the header's grammar moved there from
`docket.model`. A workflow's `run:` scripts are read through `_step_scripts`
and `docket.shell.comments`. On the tree, the nine `#` lines in
`.github/workflows/drift.yml`'s `run:` blocks are now read as bash's comments
and every other one as YAML's, with no error and nothing declined.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1387`.

**Done when.** Each format's comments are read through its shared reader -
`_make_lines` for the Makefile, `docket.shell` for scripts, the workflow and
TOML readers for theirs - or a form none reads is declined by name; a test
pins each form above.
