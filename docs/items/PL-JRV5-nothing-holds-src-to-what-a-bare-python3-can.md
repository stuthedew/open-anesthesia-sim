---
id: PL-JRV5
title: Nothing holds src/ to what a bare python3 can parse, and two checks depend on it
status: dropped
added: 2026-09-04
closed: 2026-09-04
reason: same finding as PL-L17Q, framed around the wrong fix; the exposure is the tool's invocation, not src/'s syntax, and PL-L17Q carries both halves
---

**Problem.** Captured alongside `PL-L17Q` in the same session, as the general
statement behind it: nothing holds `src/` to the 3.11 syntax the bare-`python3`
tools can parse, and `tools/contrast_check.py` reads `src/` while running under
that interpreter in the CI `floor` job.

**Why it was dropped rather than worked.** The title names a fix that would be
wrong. Holding `src/` to the floor would pin the application to a three-year-old
interpreter in order to satisfy a promise the *tooling* makes, and the
application has a live reason to use 3.14 syntax - `app/chart_downsampling.py`
already does. The exposure belongs to how the tool is invoked, not to what the
source may contain, and `PL-L17Q` says so and carries the general rule this item
was reaching for.

Kept rather than deleted so the framing is not re-raised: the next session to
notice that `src/` uses syntax the floor cannot parse should read `PL-L17Q` and
not re-open this one.
