---
id: PL-BZHX
title: The squash body on main arrives hard-wrapped at about 72 columns, which splits Markdown table rows and flattens nested lists in the permanent record: #993's table and sub-bullets are intact on GitHub and broken in a56c86c4
status: untriaged
feature: pr-body-integrity
added: 2026-09-24
---

**Problem.** The squash body on main arrives hard-wrapped at about 72 columns, which splits Markdown table rows and flattens nested lists in the permanent record: #993's table and sub-bullets are intact on GitHub and broken in a56c86c4

**Found by `PL-LWMS`'s re-confirmation, 2026-09-24.** Pull request `#993` (`GET
/repos/stuthedew/open-anesthesia-sim/pulls/993`) carries a four-row Markdown
table with each row on one line, and a two-level list under `CLAUDE.md:`. Its
squash commit on `main`, `a56c86c4` (`git log -1 --format=%B a56c86c4`), breaks
every table row at about column 72: "| `arm` | 0 | Only item files change, no
claim on the branch is" then "unreleased, and ...". It also moves the
sub-bullets to column 0. Markdown renders a broken row as a paragraph and a
flattened sub-bullet as a sibling, so the permanent record loses both
structures. `tools/pr_body_check.py`'s module docstring calls
that record "the permanent
commit message a reader of `main` meets".

**Scale is unmeasured.** The re-confirmation's history auditor counted 40 of 57
recent tabled bodies broken this way, but no second pass re-ran it. Re-measure
before sizing the item.

**Nobody owns it yet.** `PL-Y1W0`'s `pr_body_check.py --compare`, in flight on
`claude/brave-carson-6hbxas`, collapses whitespace on both sides because "the
squash message arrives hard-wrapped". So it treats the wrap as benign by
design, and will not report this.

**First question: which merge path wraps.** A null-armed auto-merge lands the
live body (`PL-M7W1`'s 2026-09-23 evidence). Hand merges go through a client,
and `docs/maintainer.md` names the Mac and the GitHub iPhone app. Compare the
two populations on `main` before choosing a remedy. A merge-client instruction
belongs in `docs/maintainer.md`. Detection belongs in `tools/pr_body_check.py`,
which is new check work and so held by the generator pause.
