---
id: PL-R7C0
title: doc_check's tag advisory fires on a full clone that has not fetched tags, so it reports a tagged release as untagged
status: untriaged
added: 2026-09-03
---

**Problem.** `make check` printed:

```text
documentation: 0 errors, 1 advisory
  ROADMAP.md:56: v0.3.3 is the current baseline and carries no tag yet; tag the
  merge once it lands:
    git tag -a v0.3.3 <merge commit> -m "v0.3.3"
```

v0.3.3 **was** tagged. The tag existed on the remote and had been pushed; this
checkout had merely never fetched it, because `git fetch origin main` and
`git fetch origin <branch>` do not bring tags. `git fetch origin --tags` then
`python3 tools/doc_check.py check` reported `0 errors, 0 advisories` with no
other change to the tree.

**Why it matters, and why it is not `PL-J295` again.** `PL-J295` (done, v0.2.8)
fixed the *shallow clone* case: a truncated clone whose tags were never
transferred. Its guard keys on shallowness. This checkout is not shallow - it
has full history - so that guard does not fire, and the advisory speaks with
full confidence about a repository state it has not actually observed.

The cost is the one `CLAUDE.md` names directly: "A check that fires every run
without changing a decision is a defect in the check - it costs attention
forever and trains a session to skim the output where a real advisory also
appears." This one is worse than noise, because it is *actionable-looking*: it
hands the reader a command to run. Observed 2026-09-03 - this session was one
step from putting a `git tag -a v0.3.3` line in front of the project owner for
a tag that already existed, and only checked because the advisory appeared
immediately after an unrelated edit and the timing looked wrong.

It also fires at the worst moment. The advisory exists for the release path,
where `bin/docket release` refuses to cut the next release while the previous
is untagged - so a false "untagged" here is noise sitting exactly where a real
one has to be believed.

**Where.** `tools/doc_check.py`, the release-tag check and the same
`ROADMAP.md:56` advisory `PL-HKF4` is about (that item is about the command
string being unpasteable; this one is about the advisory firing at all).
`subprojects/docket/src/docket/vcs.py` carries `PL-J295`'s shallow-clone
detection and is the natural place for whatever distinguishes these cases.

**Approach, and the judgment it needs.** The honest answer is probably not "fetch
tags" - `CLAUDE.md` is explicit that `fetch_remote` declines to prune and that
these tools must run in a bare or offline checkout, so the check cannot assume
network. The shape that fits the project's existing standard is to make the
check say what it actually knows: it can prove a tag is *absent from this
checkout*, and it cannot prove a release is *untagged*. Two candidate
resolutions, and choosing between them is the work:

1. **Decline, like the shallow case.** Say "cannot check: no tags in this
   checkout, run `git fetch --tags`" when the checkout holds no tags at all for
   recent releases, rather than asserting they are missing. Cheap, and matches
   how `bin/docket check` already declines the recorded-pull-request read on a
   truncated clone.
2. **Distinguish "no tags at all" from "this one tag missing".** A checkout
   holding v0.3.0 through v0.3.2 but not v0.3.3 is genuinely ambiguous - it
   looks the same whether the tag was never made or never fetched. This was
   exactly that case, so option 1 alone would not have caught it.

Option 2 is the one that would have caught this instance, and it may have no
clean local answer, which is the finding: the check may be asserting something
a local checkout cannot decide. Retiring the advisory in favour of a
release-time check that runs where the network is available is a legitimate
outcome - `CLAUDE.md`'s "a check earns its place every run, or it is retired".

**Done when.** A checkout missing a tag that exists on the remote does not
report the release as untagged, or the advisory is retired in favour of a check
that runs where the answer is knowable - and either way the decision is
recorded.

**Found.** Closing `PL-C1KK` (docs/MODEL.md's stale baseline), 2026-09-03, when
the advisory appeared after an edit that could not have caused it.
