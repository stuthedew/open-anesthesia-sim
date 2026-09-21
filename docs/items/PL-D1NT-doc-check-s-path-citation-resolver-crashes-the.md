---
id: PL-D1NT
title: doc_check's path-citation resolver crashes the whole run on a path it cannot stat: the glob branch is guarded against exactly this and the .exists() branch is not
priority: P2
effort: S
status: ready
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-19
verify: grep -q 'def test_a_citation_the_process_cannot_stat_is_reported_not_raised' tests/unit/test_doc_check.py
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

**Done when.** `python3 tools/doc_check.py check` runs to completion and reports an
ordinary dangling-citation error for a path it is refused permission to stat,
rather than raising; and a regression test in `tests/unit/test_doc_check.py` drives
a document citing a path under a directory the test makes unreadable, asserting the
run finishes and names that one line.

**First live instance, 2026-09-21 (`PL-ZM48`).** This stopped being theoretical:
a documentation change cited the container's agent-proxy README by its absolute
path, `make check` passed locally, and CI went red in 35 seconds on exactly this
traceback - `PermissionError: [Errno 13] Permission denied` out of
`_resolves`'s `.exists()`, aborting the entire documentation gate before a
single real citation was judged.

**The split is the container user.** A session runs as root, where that path is
readable and the citation resolves; the GitHub runner runs as `runner`, where
`/root` is mode 700 and `.exists()` raises instead of returning `False`. So the
defect is invisible to the check a session is told to run before committing, and
visible only after the push. Reproduced deterministically in-session with
`setpriv --reuid=65534 --regid=65534 --clear-groups python3 tools/doc_check.py
check`, which is a local reproduction for whoever fixes this and needs no CI
round-trip.

`PL-ZM48` worked around it by not writing the path - the citation names the
README in prose and points at the `readmePath` field of the proxy's status
endpoint instead. That is a workaround in one document, not a fix: five item
briefs on `main` still carry the same absolute path, and any of them entering
the scanned set fires this again.
