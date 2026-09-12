---
id: PL-R808
title: Build the exact left-behind check as a tools/ script comparing a branch tip against refs/pull/<n>/head, declining where those refs are not fetched
status: untriaged
feature: parallel-sessions
added: 2026-09-12
---

**Problem.** Build the exact left-behind check as a tools/ script comparing a branch tip against refs/pull/<n>/head, declining where those refs are not fetched

**Unblocked by `PL-VV4D`**, which decided on 2026-09-12 to build the exact
comparison and to put it in `tools/` beside `vcs.orphaned` rather than in place
of it. That item carries the reasoning and the costs accepted; this one is the
build.

**The invariant.** A pull request merges the head it was opened against, and
GitHub freezes `refs/pull/<n>/head` at that head when the pull request closes.
So: does the branch tip point *past* the pull-request head that merged? Equal or
an ancestor means nothing was left behind; a descendant means exactly the
commits between them were, named with no content comparison - no squash
confound, no rename confound, no blob identity.

**Constraints carried from the decision.**

- `tools/` script, standard library only, so a hook or a bare checkout can run
  it without the project virtualenv. Not a `docket` command: `PL-SK88` decided
  `docket` must not learn about the harness.
- It must **decline** where it cannot read the frozen head, rather than guess or
  report a clean answer. Saying so is the whole point of preferring it to a
  heuristic.

  **Measured 2026-09-12, and it narrows this constraint rather than restating
  it.** An earlier draft of this brief said "decline where `refs/pull/*` have not
  been fetched". That is wrong: the frozen head is answerable with **no fetch and
  no local refs at all**. From this checkout, `git for-each-ref 'refs/pull/*'`
  returns 0, and yet:

  ```text
  $ git ls-remote origin refs/pull/284/head
  7f87bf5971e4b0947c6604aca979f295f24e5c38  refs/pull/284/head
  $ git ls-remote origin refs/pull/312/head
  7d1615f51773a8310cafc5cce282ff2f262481ea  refs/pull/312/head
  ```

  The first is byte-identical to the `#284` vector `PL-VV4D` recorded. So the
  real decline condition is **no network**, not no fetch, and the shape is a
  per-candidate `ls-remote` rather than a bulk fetch. That matters for cost too:
  `git ls-remote origin 'refs/pull/*/head'` returns **500** refs today, against
  the "all 311 ... in 1.9 s" figure `PL-VV4D` costed the bulk approach at.
- `vcs.orphaned` stays as the portable half and is not touched.

**Known test vectors**, from `PL-VV4D`: `#312`'s release branch, where the tip
equals `refs/pull/312/head` and the exact check must stay silent where the
content comparison fired falsely; and `#284`, where the branch stood at
`9fee36c` against a frozen `refs/pull/284/head` of `7f87bf5`, so the one commit
between them is the loss.

**Still to decide as part of the build:** where it is wired - CI, the digest, or
`make check` - and what it prints when it and `vcs.orphaned` disagree, which is
the case a reader most needs help with.
