---
id: PL-SNQR
title: pr_body_check's normalise strips the closing Co-authored-by paragraph a pull request body writes for itself, but on the squash side GitHub's appended group follows it and only that group is stripped, so --compare reports a faithful squash body as differing; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage pass
added: 2026-10-12
payoff: the read-back comparison no longer reports a faithful squash body as differing when the pull request body closes with its own trailer paragraph
verify: grep -q 'def test_a_body_ending_with_its_own_trailer_paragraph_compares_equal' tests/unit/test_pr_body_check.py
---

**Problem.** pr_body_check's normalise strips the closing Co-authored-by paragraph a pull request body writes for itself, but on the squash side GitHub's appended group follows it and only that group is stripped, so --compare reports a faithful squash body as differing; latent

**Found 2026-10-12 while fixing `PL-QLQF`** (`#1434`). `normalise` strips the
last `Co-authored-by` paragraph of whatever it is given, and is applied to both
sides of `--compare` alike, on the reasoning that a step applied to both "can
hide a difference but never make one". That holds only where both sides end
the same way. A pull request body that closes with a trailer paragraph of its
own loses it, while the squash body carries GitHub's group after it, so only
GitHub's is stripped there and the body's own paragraph is compared against
nothing.

```text
Why, in brief.

Co-authored-by: A <a@x>
```

**Reproduced 2026-10-12** on this branch, with `PL-QLQF`'s fix in place: the
body above normalises to `Why, in brief.`, the same body with
`\n---------\n\nCo-authored-by: Claude <noreply@anthropic.com>\n` appended
normalises to `Why, in brief. Co-authored-by: A <a@x>`, and `verdict` reports
the faithful squash as `differs`. The old pattern does the same. Latent: none
of the 265 bodies recorded under `docs/pr-bodies/` ends with a trailer
paragraph of its own, and no squash body on `main` keeps one once GitHub's
group is stripped (1,318 read).

**Not a recurrence of `PL-QLQF`**, which `docket new` matched it to by title:
that item read a trailer inside a paragraph of prose, which git reads as no
trailer at all. Here git does read the body's paragraph as a trailer block;
the fault is which side `normalise` strips it from.

**Why it matters.** `--compare` is what says a published pull request body
reached `main` intact (`CLAUDE.md`'s read-back rule, `PL-1DN9`), so a faithful
body reported as differing is a false alarm a session spends a round disproving,
and the next one trusts the comparison less. Latent: no recorded body ends with
a trailer paragraph of its own.

**Done when.** `--compare` reports a pull request body that ends with its own
trailer paragraph as equal to a squash body that kept it, and a test pins the
form above.

**Generator check.** A one-off: `normalise` applies one strip to two texts that
end differently. No head's `misread:` states it; `PL-QLQF` read a trailer inside
prose, a different fact, as the brief says.
