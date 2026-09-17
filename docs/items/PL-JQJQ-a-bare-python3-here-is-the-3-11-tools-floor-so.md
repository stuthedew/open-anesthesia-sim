---
id: PL-JQJQ
title: A bare python3 here is the 3.11 tools floor, so any session or subagent that parses src/ with it hits a false SyntaxError in app_metadata.py and re-investigates PEP 758 from scratch; nothing in the tree records that the failure is expected
priority: P2
effort: S
status: done
classes: infra, session-cost
feature: dev-tooling
milestone: v0.4.26
touches: .claude/hooks/floor-interpreter-guard.sh, .claude/settings.json, src/anesthesia_sim/app_metadata.py, tests/unit/test_floor_interpreter_guard.py, docs/ARCHITECTURE.md, docket.toml
added: 2026-09-16
closed: 2026-09-16
pr: 630
verify: uv run pytest tests/unit/test_floor_interpreter_guard.py && grep -q floor-interpreter-guard .claude/settings.json
---

**Problem.** Two interpreters are in play and both halves are deliberate.
`src/` and `tests/` target 3.14; `tools/`, `.claude/hooks/` and `bin/docket`
run under whatever bare `python3` is on PATH, which `tools/ruff.toml` pins at
the 3.11 floor `subprojects/docket/pyproject.toml` declares, so a hook and a
bare checkout need no virtualenv. In this container that bare `python3` is
3.11.15, by a `/usr/local/bin/python3 -> /usr/bin/python3.11` symlink.

`src/anesthesia_sim/app_metadata.py` writes `except OSError,
subprocess.SubprocessError:` - the unparenthesised form PEP 758 added in 3.14
- and it is the only construct under `src/` that the floor cannot parse. So
`python3 -m compileall src/` reports `SyntaxError: multiple exception types
must be parenthesized` in code that is correct, and nothing in the tree said
so. Sessions and exploration subagents reported it as a syntax error on `main`
more than once, most recently from the `PL-NMTF` session's sweep, and each
time a session spent a round proving it was not.

**Why it matters.** It is the cheap failure that recurs: each instance costs a
round of a session's context to re-derive an answer that is fixed, and the
answer arrives through a subagent - which is the case no resident prose
reaches, because the agent forming the wrong conclusion is not the session
carrying the prose. Six items in the store mention `SyntaxError` and all six
are about the reverse direction (the formatter breaking `tools/`); this
direction had no record at all, which is why it was re-derived rather than
looked up.

**The mechanism the project owner first proposed - point the system `python3`
at 3.14 - was refused, and the reasoning is recorded so it is not re-raised.**
It would suppress the false alarm by deleting the local detector for the one
bug class that has actually bitten this tree: on 2026-08-31 `make fix` (`ruff
format` at `target-version = "py314"`) stripped the parentheses from `except
(OSError, TimeoutError):` in `tools/doc_check.py`, and only the bare-`python3`
line of `make check` caught it. That event is why `tools/ruff.toml`,
`.claude/hooks/ruff.toml` and `tests/unit/test_tools_portability.py` exist.

Stated fairly: CI would still catch it, since the floor section of
`.github/workflows/quality.yml` pins `python-version: '3.11'` through
`actions/setup-python` independently of this container. So the cost is precise
rather than total - detection moves from pre-push, naming the file, to
post-push, which is exactly the property `tests/unit/test_tools_portability.py`'s
docstring says the local approximations exist to keep. Two smaller costs came
with it: `bin/docket`'s own 3.11 floor stops being exercised locally, though
the hooks run it on the bare interpreter every session; and 3.14 is not
installed here at all (`uv python list` shows 3.14.7 as download-only), so it
would be a `uv python install` plus a shim redone on every ephemeral container.

**Built.** `.claude/hooks/floor-interpreter-guard.sh`, a `PreToolUse` hook on
Bash that denies a bare `python`/`python3` whose command names a path under
`src/` or `tests/`, or which compiles the whole tree, with a reason naming
PEP 758, `uv run python`, this item, and the instruction not to "fix" it by
changing the interpreter on PATH. `CLAUDE.md`'s first routing disposition: a
prohibition decidable by reading the command belongs in a check, not in prose
every session carries before it has read anything.

The refusal is what reaches a subagent. Hooks configured in settings files fire
inside subagents, carrying `agent_id` and `agent_type`, and
`permissionDecisionReason` is shown to the model
(https://code.claude.com/docs/en/hooks, read 2026-09-16) - so the sweep agent
that would have filed the alarm reads the answer at the moment it would have
formed the wrong conclusion.

Two things it deliberately does not do. It does not match an interpreter named
by path, so `/usr/bin/python3.11 -m compileall src/` still reproduces the floor
failure on purpose - spelling the interpreter out is what separates the
deliberate act from the accidental one. And it does not try to know which
tools under `tools/` parse 3.14 source without naming a tree on the command
line; that is a list that would drift, and `CLAUDE.md` is explicit that a tool
guessing at the judgment half is worse than no tool. The deny message carries
that half as prose, naming the six scripts `make check` runs under `uv run
python` for that reason.

Carried with it: a comment at the `except` in
`src/anesthesia_sim/app_metadata.py`, so an investigation that does start
terminates at the file the traceback already names, with no hook and no context
needed; `tests/unit/test_floor_interpreter_guard.py`, whose
`test_the_file_the_refusal_names_still_carries_the_construct` fails if the
construct moves, so the message cannot go stale silently, and whose
`test_the_hook_is_wired_under_the_bash_matcher` fails if the hook is ever
unwired; the entry in `docket.toml`'s `workflow_paths`, pasted from the line
`tools/workflow_paths_check.py` printed; and `docs/ARCHITECTURE.md`'s wired-hooks
section, which counted four scripts and now counts five.

**Done when (met).** A bare-interpreter parse of `src/` or `tests/` is refused
with a message that answers the question rather than raising one, the refusal
reaches a subagent, and the floor guarantee the 3.11 interpreter exists to
prove is untouched.
