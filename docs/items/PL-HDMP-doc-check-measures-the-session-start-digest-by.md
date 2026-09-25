---
id: PL-HDMP
title: doc_check measures the session-start digest by running .claude/hooks/docket-digest.sh with the calling interpreter's PATH, so under uv run - how make check runs it since PL-MB3F, and CI's uv step always - the hook's bare python3 is the venv's 3.14, and the reported resident total (5151 characters of digest) is not what a session running bare 3.11 receives (4875)
status: untriaged
added: 2026-09-24
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
