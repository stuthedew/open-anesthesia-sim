---
id: PL-YNCW
title: docket new --touches before the title swallows it, because nargs='*' is greedy and the error names the title instead
status: untriaged
feature: dev-tooling
touches: subprojects/docket/src/docket/cli.py
added: 2026-09-02
---

**Problem.** `bin/docket new --feature parallel-sessions --touches path "Some
title"` fails with `the following arguments are required: title`. `--touches`
is declared `nargs="*"`, so argparse consumes the title into it and then
reports the title as missing. The message names the one thing that was
supplied.

**Observed 2026-09-02**, capturing `PL-MC8Z`. Cost one retry, which is small —
but the capture path is the one place in this project that is meant to be
frictionless, because `CLAUDE.md` requires capture to happen even when usage
is nearly spent and a thought is one interruption from gone. A capture command
that fails on a plausible argument order is friction in exactly the wrong
place.

**Where.** `subprojects/docket/src/docket/cli.py`. Options worth weighing at
triage: `nargs="+"` with repeated use, a comma-separated single value (which
is how `touches` is spelled in the item file anyway), or leaving the parser
alone and fixing only the error message so it names the real cause. The last
is the smallest and may be enough — the failure is recoverable the moment the
reason is legible.

**Done when.** Either the argument order works, or the error says why it did
not.
