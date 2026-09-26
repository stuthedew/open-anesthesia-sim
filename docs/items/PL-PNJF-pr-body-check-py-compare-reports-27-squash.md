---
id: PL-PNJF
title: pr_body_check.py --compare reports 27 squash bodies that say something other than their pull request, and nothing can record the pull request's body for them: --recover writes only for an empty body, and a recovery file's header says the commit landed empty
priority: P3
effort: S
status: needs-decision
classes: defect
feature: pr-body-integrity
touches: tools/pr_body_check.py, tests/unit/test_pr_body_check.py, docs/pr-bodies
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-24
recurrences: 2026-09-25 PL-YYDT withdrawn 2026-09-25 PL-PNJF, 2026-09-26 PL-7VWK withdrawn 2026-09-26 PL-PNJF
---

**Problem.** pr_body_check.py --compare reports 27 squash bodies that say something other than their pull request, and nothing can record the pull request's body for them: --recover writes only for an empty body, and a recovery file's header says the commit landed empty

**Found by `PL-Y1W0`, 2026-09-24.** `--compare` names the 27, and they stay
reported: `recovered()` counts only a `docs/pr-bodies/<N>.md` file, and
`recover()` writes one only for a commit `missing()` returns, which is an
empty body. So the only way to clear one is by hand, with a file whose header
(`write_recovery`) says the squash "landed with an empty message body", which
is untrue for all 27.

Which body is the record is not the same question for every shape. For six,
the pull request was edited after auto-merge was armed, so its body is the
later reasoning. For `#466` and `#522`, the body carries a note added after
the merge, and the squash is what was true at merge time. For shapes like
`#744`, the merge sent a short message of its own. That is why this is an item
and not a flag on `--recover`. `PL-73G8` is already changing the header's
provenance claim in the same function, so land that first or decide the two
together.

Reproduced 2026-09-25 against 46954a81 by reading `tools/pr_body_check.py`:

- `comparable()` drops a pull request only when `docs/pr-bodies/<N>.md` exists.
- `missing()` returns empty bodies alone, and `recover()` writes only for
  those.
- `write_recovery()` writes "landed with an empty message body" into every
  file it makes.

So a body that differs can only be cleared by a hand-written file with an
untrue header. I did not re-run the count of 27, which needs about ten
unauthenticated API requests. `--compare` runs by hand only; the session-start
digest runs the empty-body mode.

**Why it matters.** `--compare` is the instrument that says whether merges
still land something other than the pull request's body. `PL-Y1W0`'s
generator check used it to judge whether `PL-WFFX`'s `spent` verdict held.
With 27 findings nothing can clear, its output never reads clean, so a new
instance arrives buried among known ones. And the only way to clear one writes
a false provenance claim into the recovered record.

**Decision needed.** Which body is the record for each shape of difference,
and how a recovery file says which one it holds.

**Recommendation:** keep one store, `docs/pr-bodies/<N>.md`, and let `--recover`
write a file for every body `--compare` names. Replace the fixed "landed
empty" sentence with a header field naming the shape: empty, edited after
arming, a note added after the merge, or a message the merge composed. For the
post-merge-note shape, the header says that `main`'s copy is what was true at
the merge. Decide this together with `PL-73G8`, which rewrites the same
header's provenance claim, so the header changes once and not twice. A session
can take this: it is the structure of an internal record, not a product
question.

**Under `PL-979D`'s answer, 2026-09-25, whose form the owner recorded there
the same day.** For every pull request merged after the `PL-979D`
build lands, which body is the record is answered once: the copy in
`docs/pr-bodies/<N>.md`, written before the merge and checked against the pull
request by `pr-title.yml` on every edit, whatever the merge then sends. The
question survives only for the 27, and there it narrows to this brief's second
half, the header: a file holds either a body *recorded* before the merge or one
*recovered* after it from the API on a date, and says which - `PL-73G8`'s ask
on the same lines, so the two headers change once. The shape names above
(empty, edited after arming, a note added after the merge, a message the merge
composed) become the `--compare` verdict, kept in a recovered file's header
where it is known. Writing a file for any pull request named, not only for an
empty body, stays as recommended, as the same `--record N` the build adds.
Recommendation: fold this item and `PL-73G8` into the `PL-979D` build as its
header work, rather than landing the header twice.

**Done when.** `--compare` reports nothing on a tree where every differing
body has its file, each file's header names its shape truthfully, and
`tests/unit/test_pr_body_check.py` holds one case per shape.

**Not a recurrence of `PL-YYDT`.** `docket new` recorded `PL-YYDT` (filed
2026-09-25) as a filing of this item, and the match rests only on the shared
`tools/pr_body_check.py`. `PL-YYDT` is about four parsers of the pull-request
number in a commit subject, a different mechanism in `PL-HMZZ`'s family. The
entry is withdrawn with this item as the reason. `PL-7VWK` (filed 2026-09-26) matched the same way, on the shared
file alone: it is about `docs/maintainer.md`'s merge rule after `PL-979D`, not
about a recovery header, and its entry is withdrawn for the same reason.

**Generator check.** An instance of `PL-WFFX`'s fact ("The squash commit's
subject and body as the merge sends them, not as the pull request shows
them"), filed after that head closed on 2026-09-22. `recover()` and
`write_recovery()` read any squash body that differs from its pull request's as
an empty one. With `PL-Y1W0` and `PL-BZHX`, this is the third post-close
instance, which counts as a generator whose fix did not hold. `PL-WFFX` is
closed and outside this triage batch, so the record is reported to the triage
coordinator, not written here.
