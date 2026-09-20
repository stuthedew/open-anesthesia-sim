---
id: PL-843V
title: Six contiguous squash commits on main carry no body, so those pull requests' reasoning never reached the permanent history despite squash_merge_commit_message PR_BODY
status: untriaged
feature: pr-body-integrity
added: 2026-09-20
---

**Problem.** `main` is squash-merged, and the repository is configured so that
the squash commit message *is* the pull request body:

```
$ curl -sS https://api.github.com/repos/stuthedew/open-anesthesia-sim
  squash_merge_commit_title:   PR_TITLE
  squash_merge_commit_message: PR_BODY
```

So the pull request body is not a review artifact that is thrown away on
merge - it is the permanent commit message a reader of `main` meets. Six of
the last 40 squash commits carry **no body at all**, only the subject line:

| PR | Item(s) | Squash commit |
| --- | --- | --- |
| #763 | `PL-KRZW` | subject only |
| #764 | `PL-K4R5` | subject only |
| #765 | `PL-8G48`, `PL-439V`, `PL-CHQY`, `PL-V3QB` | subject only |
| #766 | `PL-CTD7` | subject only |
| #767 | `PL-0RZ0` | subject only |
| #768 | `PL-8PS6` | subject only |

`git cat-file commit 3c4ffe57` (the squash for #768) is 109 bytes of message:
the subject and nothing else. The pull request body it should have carried is
still on GitHub and runs to 3,600 characters - a table separating the model's
flow envelope from a machine's deliverable range, the `provenance_gap`
reasoning, the one expected `bin/docket verify` REJECT and why it is expected,
and the `PL-7CRY` follow-on. None of that is in the history.

**What is not the cause.** The repository setting is correct and is correct
*now*, so this is not a configuration that needs changing on its own evidence.
Nor is it a general property of the merge route: #762 and #769 - either side of
the window - both carry their full bodies, as do 34 of the 40 sampled. The six
are exactly contiguous, which points at one sitting or one merge route rather
than at drift.

**Candidate causes, none confirmed.** The merge API's `commit_message` argument
overrides the repository default when it is supplied, including when it is
supplied empty; auto-merge enabled through `enable_pr_auto_merge` takes its own
`commit_message`; and the GitHub mobile client has historically not honoured
`squash_merge_commit_message`. `merged_by` on #768 is `stuthedew`, which does
not separate these - auto-merge is attributed to whoever enabled it. Reading
the six merge events is the first step.

**Why it matters.** This project's whole discipline is that the reasoning
survives the session that had it. A body that names what was refused, what was
measured and what was filed is the densest record the project produces, and for
these six it now exists only on GitHub, outside the repository, unreachable by
`git log`, `git blame`, or any checkout. It is silent: the pull request still
reads correctly on GitHub, so nothing about the defect is visible from where
anyone looks.

It is also recoverable *now* and not later. The bodies are still on GitHub and
can be attached as git notes or recorded in the items; once a body is edited or
a repository is migrated, they are gone.

**Done when.** The cause of the #763-#768 window is identified and either fixed
or shown to be a one-off that cannot recur; the six bodies are recovered into
something a checkout can read; and, if the cause can recur, a check reports a
squash commit on `main` whose body is empty.

**Found while** answering whether the project should have a pull request
template (2026-09-20). It is the reason the answer to that question is not
purely about review ergonomics: the pull request body is `main`'s commit
message here.
