---
id: PL-QLQF
title: pr_body_check's APPENDED_TRAILER_RE takes a Co-authored-by line at the end of a prose paragraph for the trailer GitHub appends, where git counts a trailer block only as a whole paragraph, so --compare strips a body's own last line and reports two equal bodies as differing, or two differing bodies as equal; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
milestone: v0.5.24
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1434
payoff: pr_body_check --compare keeps a body's own last line, so a squash commit that lost one is reported rather than passed as equal, and a faithful one is not reported as differing
verify: grep -q 'def test_a_trailer_closing_a_prose_paragraph_is_the_bodys_own' tests/unit/test_pr_body_check.py
reenters: PL-4ZVH
recurrences: 2026-10-12 PL-SNQR withdrawn 2026-10-12 PL-SNQR
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

**Re-confirmed 2026-10-11** on main at `16a20a4f`: `normalise` reduces the two
bodies above to `Thanks to the pairing with` and `Written with`, each losing
its last line, while `git interpret-trailers --parse` finds no trailer in
either. None of the 266 bodies under `docs/pr-bodies/` holds a `Co-authored-by:`
line straight after a prose line, so it stays latent.

**Why it matters.** `--compare` is how a session audits that a squash commit
kept the body its pull request carried. Stripping a line git never reads as a
trailer reports a faithful body as differing, or passes a body that lost its
last line as equal, so for this shape the audit answers wrong in both
directions without saying it could not read the body.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-4ZVH`'s fix left, which reached folded
trailers. Latent, so an ordinary item under the spent head, and a re-entry of
`PL-4ZVH` (closed 2026-10-05) at the paragraph boundary its fix did not reach.

**Done when.** A trailer is stripped only where git reads a trailer block,
and a test pins both forms above against `git interpret-trailers --parse`.
