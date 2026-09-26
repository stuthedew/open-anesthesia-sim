#!/usr/bin/env bash
# PreToolUse hook on Bash: refuse a bare `python3` aimed at the 3.14 trees.
#
# Two interpreters are in play here and both halves are deliberate. `src/` and
# `tests/` target 3.14 - `pyproject.toml` declares `requires-python =
# ">=3.14,<3.15"` and `.python-version` pins 3.14.7. Everything under `tools/`
# and `.claude/hooks/`, plus `bin/docket` and the `subprojects/docket/` tree it
# runs, runs under whatever bare `python3` is on PATH, with no virtualenv and
# no install step, which is what lets a hook and a bare checkout work at all;
# `tools/ruff.toml` pins that floor at the 3.11
# `subprojects/docket/pyproject.toml` declares. `make check` and the floor
# section of `.github/workflows/quality.yml` both *perform* the bare run on
# purpose, so the 3.11 on PATH is a tested guarantee rather than a stale
# default.
#
# The collision is one line. `src/anesthesia_sim/app_metadata.py` writes
# `except OSError, subprocess.SubprocessError:`, the unparenthesised form PEP
# 758 added in 3.14, so `python3 -m compileall src/` under the floor reports
# `SyntaxError: multiple exception types must be parenthesized` in a file that
# is correct. Sessions and exploration subagents have repeatedly reported that
# as a syntax error on `main` and spent a round proving it is not. `PL-JQJQ`
# carries the count and the reasoning.
#
# **It refuses the invocation rather than explaining the traceback, because
# only the refusal reaches a subagent.** Hooks configured in settings files run
# inside subagents, where tool events fire the same hooks as in the main
# conversation, and `permissionDecisionReason` is shown to the model
# (https://code.claude.com/docs/en/hooks, read 2026-09-16). So the sweep agent
# that would have filed the alarm reads the answer at the moment it would have
# formed the wrong conclusion - which no amount of resident prose achieves,
# since the agent reporting it is not the session carrying the prose.
#
# **An interpreter named by path is deliberately not matched.**
# `/usr/bin/python3.11 -m compileall src/` is how you reproduce the floor
# failure on purpose, and spelling the interpreter out is what separates the
# deliberate act from the accidental one. `.venv/bin/python` and `uv run
# python` pass for the same reason: they are the correct invocation.
#
# **Narrow on purpose: a guarded path in the command, nothing inferred.** A
# tool under `tools/` that *parses* 3.14 source has the same exposure without
# naming a tree here - which is why `make check` runs six of them under `uv run
# python` - but deciding which tool reads which tree is a list that would
# drift, and `CLAUDE.md` is explicit that a tool guessing at the judgment half
# is worse than no tool. The deny message carries that half as prose instead of
# the pattern carrying it.
#
# Fails open in every error path - no python3, an unreadable payload, a command
# bash itself would refuse, `shell_split.py` missing from beside it - like
# `no-prune-guard.sh` beside it. A guard that breaks the session costs more than
# the round it saves.
set -uo pipefail

payload=$(cat)
command -v python3 >/dev/null 2>&1 || exit 0
hooks=$(dirname "${BASH_SOURCE[0]}")

PAYLOAD="$payload" HOOKS="$hooks" python3 -c '
import json, os, re, sys

sys.path.insert(0, os.environ["HOOKS"])
import shell_split

try:
    data = json.loads(os.environ["PAYLOAD"])
except (ValueError, KeyError):
    sys.exit(0)
if data.get("tool_name") != "Bash":
    sys.exit(0)
command = data.get("tool_input", {}).get("command")
if not isinstance(command, str):
    sys.exit(0)

# Split the way bash splits it, by `shell_split.py` beside this file, which the
# three Bash guards share (`PL-PVW2`). A regex would not do, because the failing
# shape puts the path inside a quoted argument: `python3 -c "import ast;
# ast.parse(open(\"src/a.py\").read())"` is one command with one `;` that is
# not a separator. The splitter keeps that string whole, so the path is visible
# and the `;` does not end the invocation. It ends a command at an unquoted
# separator however it is spaced - `true;python3` hid the interpreter and
# `print(1);` joined the next command to this one (`PL-GVFC`, `PL-BBV7`), and a
# `)` glued to the `;` hid it again (`PL-63TT`). A comment and a heredoc body
# are removed, the body being document content this repository writes about the
# floor routinely, and the lines after its terminator are read (`PL-39LD`).
cut = shell_split.segments(command)
if cut is None:
    sys.exit(0)

# Bare, and bare is the whole point: a name with no slash in it is the one
# resolved through PATH, where this container answers 3.11.
INTERPRETER = re.compile(r"^python(?:3(?:\.\d+)?)?$")
# `src/anesthesia_sim/app/` sits under `src/`, so naming it again would only
# widen the pattern. The first lookbehind lets a leading `./` or an absolute
# path through while keeping `mysrc/` out. The second keeps out
# `subprojects/docket/src/` and `subprojects/docket/tests/`, which are floor
# code rather than the 3.14 trees - `subprojects/docket/pyproject.toml` is the
# file declaring 3.11 - and so the right trees to aim a bare interpreter at. A
# relative `src/` after a `cd` into that subproject is still read as the
# product tree: paths are read as written, and no `cd` is followed.
GUARDED = re.compile(r"(?<![\w-])(?<!subprojects/docket/)(?:src|tests)/")
# A whole-tree parse reaches both without naming either.
WHOLE_TREE = ("compileall", "py_compile")

offender = None
for segment, _ in cut:
    # A subshell, a brace group, a negation or an assignment opens the command.
    rest = shell_split.command_words(segment)
    if not rest or not INTERPRETER.match(rest[0]):
        continue
    arguments = rest[1:]
    if any(GUARDED.search(argument) for argument in arguments):
        offender = " ".join(rest)
        break
    if any(a in WHOLE_TREE for a in arguments) and "." in arguments:
        offender = " ".join(rest)
        break

if offender is None:
    sys.exit(0)

reason = (
    "A bare `python3` on PATH here is the 3.11 tools floor, and `src/` and "
    "`tests/` target 3.14. Parsing them with it reports a SyntaxError in code "
    "that is correct:\n\n"
    "    src/anesthesia_sim/app_metadata.py\n"
    "        except OSError, subprocess.SubprocessError:\n"
    "    SyntaxError: multiple exception types must be parenthesized\n\n"
    "That is PEP 758, which 3.14 added and 3.11 cannot parse. It is expected, "
    "it is not a defect on `main`, and it does not need investigating - "
    "`PL-JQJQ` exists because it has been re-derived from scratch more than "
    "once.\n\n"
    "Use the project interpreter instead:\n\n"
    "    uv run python -m compileall src/\n"
    "    uv run pytest tests/unit/...\n\n"
    "The same applies to a tool that reads 3.14 source without naming a tree "
    "on the command line: `make check` runs `contrast_check.py`, "
    "`agent_identity_check.py`, `import_boundary_check.py`, "
    "`workflow_paths_check.py`, `core_vocabulary_check.py` and "
    "`glyph_check.py` under `uv run python` for exactly that reason.\n\n"
    "Do not \"fix\" this by changing the interpreter on PATH. The 3.11 is a "
    "tested guarantee: `tools/`, `.claude/hooks/` and `bin/docket` must run "
    "with no virtualenv, and the bare invocation in `make check` is what "
    "caught `ruff format` rewriting `tools/doc_check.py` into 3.14-only "
    "syntax on 2026-08-31.\n\n"
    "To reproduce the floor failure on purpose, name the interpreter by path: "
    "`/usr/bin/python3.11 -m compileall src/`."
)
sys.stdout.write(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )
)
' 2>/dev/null || exit 0
