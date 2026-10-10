---
id: PL-W9VC
title: doc_check's _hash_comments reads a host claim's comments a physical line at a time, so a Makefile comment a backslash continues is read short, and a hash-led line inside a here-document, a multi-line quoted string, a YAML block scalar or a TOML multi-line string is read as a comment: an undated claim is missed or a dated one refused; latent
status: untriaged
feature: one-answer
added: 2026-10-10
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

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. The code is new
in `#1387`.

**Done when.** Each format's comments are read through its shared reader -
`_make_lines` for the Makefile, `docket.shell` for scripts, the workflow and
TOML readers for theirs - or a form none reads is declined by name; a test
pins each form above.
