---
id: PL-843V
title: 187 of 683 squash commits on main carry no body, because the merge is submitted with an explicitly empty commit_message that overrides squash_merge_commit_message PR_BODY
priority: P2
effort: M
status: done
classes: defect
feature: pr-body-integrity
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py, Makefile, docs/ARCHITECTURE.md, docket.toml, docs/pr-bodies
added: 2026-09-20
closed: 2026-09-20
payoff: recovers 763,224 characters of design reasoning that 187 squash merges dropped from main's permanent history, and reports the next one while its pull request body is still retrievable
verify: grep -q 'def test_silent_on_the_old_merge_commit_shape' tests/unit/test_pr_body_check.py
recurrences: 2026-09-20 PL-WFFX
---

**Problem.** `main` is squash-merged, and the repository is configured so that
the squash commit message *is* the pull request body:

```
$ curl -sS https://api.github.com/repos/stuthedew/open-anesthesia-sim
  squash_merge_commit_title:   PR_TITLE
  squash_merge_commit_message: PR_BODY
```

So a pull request body is not a review artifact thrown away on merge - it is
the permanent commit message a reader of `main` meets, and it is the densest
record this project produces: what was refused, what was measured, what was
filed, and why.

**The capture said six. It is 187.** The original brief sampled the last 40
squash commits and found six contiguous, which it read as one sitting or one
merge route. Measured instead over all 805 first-parent commits on `main`:

| | count |
| --- | --- |
| first-parent commits on `main` | 805 |
| of those, squash-shaped (subject ends `(#N)`) | 683 |
| **of those, zero-length body** | **187 (27.4%)** |
| of those 187, pull requests that *had* a body on GitHub | 187 |
| characters of reasoning absent from the history | **763,224** |

Every month of the project is affected - 13 of 25 squash commits in 2026-08,
174 of 658 in 2026-09 - across 51 distinct runs whose lengths include 17, 12,
12, 8, 7, 7, six runs of 6, and 17 singletons. The six the capture found are
the tail of a standing condition, not a sitting. Four of the 187 are release
commits, so what was lost there was the release notes.

**Mechanism, measured.** The merge request is submitted with an *explicitly
empty* `commit_message` string rather than with the field absent. GitHub
honours `""` literally, skips the repository default, and suppresses the
`Co-authored-by` trailer with it - which is why these bodies are zero-length
rather than the 46 characters a trailer alone leaves behind (`#325` is the
control: an empty pull request body yields a 46-character commit body
consisting only of the trailer). Of the merged pull requests whose `auto_merge`
object survived the merge, **9 of 9 affected carry `auto_merge.commit_message ==
""` and `commit_title == null`, against 0 of 73 unaffected** - a perfect
separator, accounting for 9 of the 187.

**What sends it is a per-sitting property, which is the signature of a merge
client.** Three independent timing measurements, all derived from `merged_at`:

- Merges less than 60 seconds apart agree on affected-or-not **98.3%** of the
  time against 60.2% by chance. Sittings cut at a 15-minute gap with three or
  more merges are label-pure **80.9%** against 25.0% expected.
- Owner-local hour separates at permutation **p = 5e-5**, holding even when
  labels are shuffled *within* each calendar day, so it is not a bad-day
  artifact. 05h is 15/15 affected and 17h is 27/38, while 00h, 14h, 22h and 23h
  hold 97 merges and **zero**. The band replicates blind on a held-out second
  half: 45.9% in-band against 11.8% out.
- Affected merges land a median **483 s** after CI goes green against **70 s** -
  away-from-desk against at-desk.

GitHub records no client identity either way: `performed_via_github_app` is
null and `committer.login` is `web-flow` on all 683. So the client remains an
inference, however strong the timing, and **only the project owner can close
it** - the question is which client was used to merge at 05:00 and 17:00 that
was not used at 14:00 and 22:00.

**Ruled out by measurement over the full population**, not a sample: pull
request body content (30 structural features; largest gap 8.0 points, rank AUC
0.472 on length, no size threshold), the merge actor (`merged_by` is the owner
on all 683), a body written after the merge (2 of 187, max 364 s), an empty
body at creation, draft state, branch namespace, and a later history rewrite -
`main` was rewritten once when commit signing was enabled on 2026-09-06, and of
the original GitHub-created merge commits that still exist the body is empty in
74/74 of the affected and non-empty in 116/116 of the rest, so the loss
originates at merge time in GitHub's own commit object.

**Done.** `tools/pr_body_check.py` reports a squash commit on the default
branch whose body is empty and which no `docs/pr-bodies/<N>.md` records;
`--recover` fetches the body from the public API and writes it. All 187 are
recovered, byte-identical to what the API returns, verified by round-trip. The
predicate is exact and was checked against the whole history: the 20 body-less
commits it must *not* fire on are the 2026-08 bootstrap commits and the old
`Merge pull request #N from ...` merges, neither of which ends in `(#N)`, and
both have a test.

One file per pull request rather than one archive, for the reason
`docs/dead-ends.md` already records about the queue: a single shared document
serializes every writer. Git notes were tested and refused - a fresh `git
clone` fetches no `refs/notes/*`, so they fail this item's own requirement that
a checkout can read the result without extra configuration.

Advisory rather than a gate: a merge creates the condition, so the branch
running `make check` is never the branch that caused it, and the remedy needs
the network while `make check` must stay green offline.

**Not closed by this work.** Prevention needs a change of merge client, which
is the owner's to make and cannot be enforced from the tree. Detection and
repair are what the tree can do.

**Found while** answering whether the project should have a pull request
template (2026-09-20). It is the reason the answer to that question is not
purely about review ergonomics: the pull request body is `main`'s commit
message here.
