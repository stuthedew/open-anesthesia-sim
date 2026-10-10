---
id: PL-QLQF
title: pr_body_check's APPENDED_TRAILER_RE takes a Co-authored-by line at the end of a prose paragraph for the trailer GitHub appends, where git counts a trailer block only as a whole paragraph, so --compare strips a body's own last line and reports two equal bodies as differing, or two differing bodies as equal; latent
status: untriaged
feature: one-answer
added: 2026-10-10
---

**Problem.** pr_body_check's APPENDED_TRAILER_RE takes a Co-authored-by line at the end of a prose paragraph for the trailer GitHub appends, where git counts a trailer block only as a whole paragraph, so --compare strips a body's own last line and reports two equal bodies as differing, or two differing bodies as equal; latent

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditor of
the larger `tools/` checks. `normalise`, which
`verdict` and `compare` call for the hand-run `--compare` mode, strips what
`APPENDED_TRAILER_RE` matches. git-interpret-trailers counts a trailer group
only where it is the message's last paragraph - preceded by one or more empty
or whitespace-only lines - and all trailers, or at least a quarter trailers
with a git-generated one; the pattern asks neither, so it starts a match on a
line inside a paragraph.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against `git interpret-trailers --parse` (git 2.43), which finds no
trailer in either body below:

```text
Thanks to the pairing with
Co-authored-by: Alice <a@x>

Written with
Co-authored-by: the reviewer, who asked for it
```

The first, against a squash body that keeps it, is reported as differing; the
second, against a squash body that lost its last line, is reported equal.
Latent: of 1,060 appended trailer groups in 1,276 squash commits on `main`,
and the 265 recorded bodies, none starts inside a paragraph.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-4ZVH`'s fix left, which reached folded
trailers.

**Done when.** A trailer is stripped only where git reads a trailer block,
and a test pins both forms above against `git interpret-trailers --parse`.
