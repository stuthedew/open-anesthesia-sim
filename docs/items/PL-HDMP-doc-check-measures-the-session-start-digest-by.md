---
id: PL-HDMP
title: doc_check measures the session-start digest by running .claude/hooks/docket-digest.sh with the calling interpreter's PATH, so under uv run - how make check runs it since PL-MB3F, and CI's uv step always - the hook's bare python3 is the venv's 3.14, and the reported resident total (5151 characters of digest) is not what a session running bare 3.11 receives (4875)
priority: P3
effort: S
status: ready
classes: defect
feature: resident-gauge-basis
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-09-24
payoff: the resident total make check prints in a container is the one a session actually receives, so a figure quoted in CLAUDE.md or a commit is not 0.4% high
verify: grep -q 'def test_the_digest_is_measured_without_the_calling_virtualenv' tests/unit/test_doc_check.py
---

**Problem.** doc_check measures the session-start digest by running .claude/hooks/docket-digest.sh with the calling interpreter's PATH, so under uv run - how make check runs it since PL-MB3F, and CI's uv step always - the hook's bare python3 is the venv's 3.14, and the reported resident total (5151 characters of digest) is not what a session running bare 3.11 receives (4875)

**Found 2026-09-24, closing `PL-MB3F`.** `python3 tools/doc_check.py check`
reported `.claude/hooks/docket-digest.sh (output) 4875/30`, and `uv run python
tools/doc_check.py check` reported `5151/31`, on the same tree in the same
minute. The extra line comes from the hook's own `python3
tools/left_behind_check.py`, which resolves to `.venv/bin/python3` under `uv
run`. There GitHub is unreachable with a certificate error, and the tool prints
"left-behind: not checked - no network". A session runs the hook with the
system `python3`, where that line does not appear.

The comparison against `origin/main` is unaffected: both sides are measured in
the same run, under the same interpreter. The absolute figure is what is off.
`CLAUDE.md` quotes that figure, and a session may cite it in a commit. It is
about 0.4% of the total.

**A likely fix, to check before building.** When `doc_check` runs the hook,
drop the virtualenv from its `PATH` and environment (`VIRTUAL_ENV` and the
`.venv/bin` entry), so the hook runs as a session runs it. Then confirm
whether the certificate failure under the venv interpreter is a problem in its
own right.

**Re-confirmed 2026-09-25 against 46954a81, by reading, not re-measured.**
`tools/doc_check.py`'s `measure_digest` runs the hook with
`env={**os.environ, "CLAUDE_PROJECT_DIR": ...}`, so the caller's `PATH` reaches
it. `.claude/hooks/docket-digest.sh` calls bare `python3` for `dead_ends.py`,
`main_ci_status.py`, `pr_body_check.py` and `left_behind_check.py`. `make
check`, `make doc-check` and `quality.yml` each run `uv run python
tools/doc_check.py check`. The figures were not re-measured because this
container has no `.venv` and no 3.14, and building one would change a working
tree other sessions share.

**Why it matters.** The resident total that `make check` prints includes a
digest row. In a container, that row is measured under the venv's `python3`,
which cannot verify TLS through the proxy. The row therefore carries a
`left-behind: not checked - no network` line that a session never receives:
+276 characters, 0.4%, on 2026-09-24. The comparison against `origin/main` and
the growth advisory are unaffected, because both sides are measured in one run
and the runtime row is left out of every comparison. The absolute figure is
another matter. It is the one `CLAUDE.md`'s growth series quotes and a commit
may cite, and it is not the figure it says it is. That breaks the floor in
`.claude/rules/apparatus-standard.md`: an answer has to be true.

**Done when.** The digest row `doc_check` reports is measured in the
environment a session runs the hook in. So `python3 tools/doc_check.py check`
and `uv run python tools/doc_check.py check` report the same digest figure on
one tree. A test in `tests/unit/test_doc_check.py` pins that. The brief then
records whether the venv interpreter's certificate failure is a finding of
its own.

**Generator check.** A one-off. The fact misread is which `python3` a hook's
bare call resolves to when a session runs it, and no head's `misread:` states
it. The nearest is `PL-YRYR`, on the machine's git config setting what the
docket suite's test commits cost, which is a different fact. The defect is a
side effect of `PL-MB3F` moving `doc_check` under `uv run` on 2026-09-24, and
that item's close found it.
