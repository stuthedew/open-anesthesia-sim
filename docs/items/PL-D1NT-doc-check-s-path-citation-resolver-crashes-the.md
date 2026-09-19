---
id: PL-D1NT
title: doc_check's path-citation resolver crashes the whole run on a path it cannot stat: the glob branch is guarded against exactly this and the .exists() branch is not
status: untriaged
added: 2026-09-19
---

**Problem.** doc_check's path-citation resolver crashes the whole run on a path it cannot stat: the glob branch is guarded against exactly this and the .exists() branch is not

**Found 2026-09-19 by CI failing on `#685`** (`PL-4Q9B`, record the permitted
ref operations), where a new line in `docs/worker.md` cited
the agent-proxy README by its absolute path under the container's root home.

`_resolves` in `tools/doc_check.py` tries each candidate against `PATH_ROOTS`,
and for an absolute token `root / candidate` is the absolute path itself. The
`patterned` branch wraps its `base.glob(candidate)` in
`except (ValueError, NotImplementedError): continue`, with a comment saying
exactly why - "Unguarded, one such token aborted the whole run on a traceback,
so `doc_check check` reported nothing at all about the several hundred
citations around it" (`PL-0M7L`). The `elif (base / candidate).exists():`
branch one line below has no guard at all.

**Reproduced 2026-09-19, both directions.** The container's root home is mode
`700`:

| Running as | `Path('/root/.ccr/README.md').exists()` |
| --- | --- |
| root (a local session) | `True` |
| uid 65534 (the CI runner) | `PermissionError: [Errno 13]` |

So `make check` passed locally and CI died on a traceback at
`doc_check.py:2360`, reporting nothing about any other citation in the tree.
The asymmetry is the sharp part: the one environment that cannot see the fault
is the one a session develops in.

**Why it matters.** It is `.claude/rules/apparatus-standard.md`'s floor - "what
this apparatus tells a session must be true, or must say what it could not
read" - breached in the same function that already carries the fix for the
identical failure mode. A citation the process cannot stat is a finding about
that line, exactly as a citation `glob` cannot parse is; neither is a reason to
stop. And the failure is total rather than local: one such token silences the
verdict on all ~1,279 citations.

**Shape of a fix.** Widen the existing guard to cover the `.exists()` branch -
`except OSError: continue`, or `os.path.exists`, which returns `False` rather
than raising on a stat it is refused. Either makes the token resolve to "does
not resolve", which is then reported as an ordinary dangling-citation error on
its own line. `PL-0M7L`'s comment is the precedent and the reasoning; this is
that decision applied to the branch it missed.

**A regression test is owed** and is cheap: a document citing a path under a
directory the test makes unreadable, asserting `doc_check` reports it rather
than raising. That is the shape the guard above must hold.

**Worked around in `#685`, not fixed**: the citation was reworded out of
`docs/worker.md`, since fixing the resolver is outside that item's `touches`.
No other absolute-path citation exists in the scanned documentation today, so
nothing else is currently tripping it - the next one will.
