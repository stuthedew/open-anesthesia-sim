"""Deterministic checks for the documentation this repository must keep true.

`CLAUDE.md` requires a session to sweep the documentation before calling an
item done, because a reader who trusts a wrong statement about which module
runs, what a constant is, or where a file lives can reach a wrong clinical
conclusion from a correct number. That sweep is a grep over five documents
and a judgment on every hit, run at the end of a session, by hand. It leaks:
`weight_kg` sat out of the provenance table until someone noticed it.

The failure modes the sweep looks for that need no judgment at all are
checked here, and never left to a session to remember:

- **Package map.** Every module under `src/anesthesia_sim/` appears in the
  matching tree in `docs/ARCHITECTURE.md`, every module under `tools/` in
  the one in `docs/apparatus.md`, and every path those trees name still
  exists.
- **Provenance table.** Every scientific constant in a `data/**/*.json` file
  has exactly one row in `docs/MODEL.md`'s provenance table, and every row
  names a key that file actually holds, carrying the value the table states.
- **Citations.** Every repository path and every section heading cited from
  a documentation file resolves to something that exists - or, for a path a
  sentence names as absent, planned or deleted, is declared under its
  paragraph as `<!-- absent: path -->`, and is absent.
- **Line citations.** Every citation that points into a file by line -
  `core/parameters.py:274` - names a line that file still has. Held over the
  authoritative documents and over *open* item briefs; a closed brief records
  the tree as it was and is exempt, which is `PL-G424`'s recorded decision.
  Whether a line that exists still holds the symbol the prose names is not
  decided here, and must not be.
- **Bound families.** Where a heading in `docs/MODEL.md` promises one
  assertion per member - the hazard table's rows, and the annotated lists
  that join it - every member names the entity it asserts, or declares in a
  fixed form that it has none and names the open item that owes the link.
  The convention is that document's own, in its section "How this document is
  held to the tree"; this checks the half of it a script can decide.
- **Release train.** Every row of `ROADMAP.md`'s timeline matches the step
  grammar, and the milestones, gates and step numbers run in order. The table
  is the project's only statement of which milestone is current and which is
  next, so it has to stay readable by a tool and not only by a person.
- **Milestone lists.** Every frozen-list and `Required scope` entry is read
  whole by docket's list walker, or the line that stops it is named: an entry
  carried on from the margin, which CommonMark reads as one entry and the
  walker cannot. See `check_milestone_lists`.
- **Frozen-list counts.** Every count a release's frozen list states about
  itself - in a group heading over the entries it counts, or in the version
  or timeline row naming that release - matches the entries below. The same
  number reached six places in `ROADMAP.md` once, and admitting four entries
  meant correcting nine numbers by hand. Prose counts are deliberately not
  read; see `check_gate_counts` for why.
- **The self-cleared group.** Where the current gate's frozen list groups its
  entries, its "Cleared by vX.Y.Z itself" group holds exactly the entries the
  milestone's `Required scope` declares - the rule the roadmap states for what
  a milestone clears itself, written a second time by hand. See
  `check_self_cleared_group`.
- **Current baseline.** `ROADMAP.md`'s version table names each released
  version once, marks exactly one of them the current baseline, and its
  "Current baseline:" heading names that same version - which is the version
  `pyproject.toml` holds. Cutting a release bumps the version file and leaves
  this file naming the previous one until somebody notices, which has now
  happened twice.
- **Host claims.** Every sentence that names a host beside a word of refusal
  carries the date the host was probed, in the documents, the docstrings and
  the comments alike: whether a host answers through the egress proxy is a
  measurement on a day, not a property of the environment. See
  `check_host_claims`.

One more thing is *reported* rather than checked:

- **Resident instructions.** How many lines every session loads before it has
  read anything - `CLAUDE.md` plus the rules carrying no `paths:` frontmatter
  - and whether that total has grown against the default branch. Nothing here
  passes or fails; see `check_resident_instructions` for why it must not.

What is left to judgment - whether a statement is still *true*, whether a
`must` in `docs/MODEL.md` still matches the code, whether a milestone's
out-of-scope list has become a lie - this tool does not attempt. It narrows
the sweep to the hits a human still has to read, which is what `candidates`
mode prints.

Two modes:

- `check`       full report. Errors exit non-zero and gate `make check`;
                advisories are informational and never fail a build.
- `candidates`  diff-scoped. Prints the documentation lines that mention
                anything the working tree changed since HEAD forked from
                `--base`, so close-out reads a short list instead of
                grepping five documents by hand. Exits non-zero, having
                swept nothing, where git cannot read that diff.

Standard library only, and no import of the application package, so this
runs in a bare checkout exactly as it runs in CI. The one exception is
`docket.roadmap`, which owns the release-train grammar this tool checks - also
standard library only, and imported by path rather than by installation for
the same reason.
"""

from __future__ import annotations

import argparse
import ast
import bisect
import html
import io
import json
import os
import platform
import posixpath
import re
import subprocess
import sys
import textwrap
import tokenize
import unicodedata
import warnings
from collections.abc import Callable, Collection, Iterable, Iterator, Mapping, Sequence
from contextvars import ContextVar
from dataclasses import dataclass, field
from decimal import Decimal
from functools import lru_cache
from itertools import zip_longest
from pathlib import Path, PurePath, PurePosixPath
from urllib.parse import unquote

# `ROADMAP.md`'s release-train grammar lives in `docket`, which reasons about
# project state for a living and reads the same table to report which beat of
# the planning cadence is due. A second copy here would drift from it silently,
# and the drift would be in the one document that says which milestone is
# current. Both are standard-library only and both must run in a bare checkout,
# so the import costs nothing but the path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "subprojects" / "docket" / "src"))

try:
    # Every import in this block follows the path insertion above, and each is
    # borrowed rather than reimplemented. `roadmap` carries the release-train
    # grammar and the frozen-list reader; `config`, `model` and `store` carry
    # the queue, which `check_gate_reentries` reads an item's `classes` and
    # `status` from; `release` carries the notes format - where a cut writes
    # them, and the heading below which a bullet stops being a claim - which
    # `check_tag_span_covers_its_notes` reads and must not spell a second time,
    # and the one reading of a code span (`PL-9L39`), which `_code_spans` takes.
    # A second copy of either grammar would drift from the one
    # `bin/docket check` enforces, and the drift would be in the documents that
    # say which milestone is current and what it still owes.
    from docket.config import Config
    from docket.config import load as load_docket_config

    # `fences` is the one reading of where a fenced block is (`PL-92MY`). This
    # tool held three spellings of its own beside docket's two, and one read a
    # triple-backtick code span wrapped to a line's start as a fence nothing
    # closed, so the rest of that brief was never read for line citations.
    # `without_fences` below reads it in a document's body alone, and is what
    # `tools/possessive_section_check.py` reads from here.
    from docket.fences import blocks, fenced_lines
    from docket.fences import without_fences as blank_fences

    # A block scalar's header, and whether a node is a plain scalar, are read
    # where docket reads them (`PL-8MHZ`): this file spelt both beside them, and
    # handed bash the command `|x`, a header YAML refuses, as a plain scalar.
    # Where a block scalar's content ends, and where a YAML file's comments
    # open, are its readings too (`PL-W9VC`).
    from docket.frontmatter import BLOCK_SCALAR_RE, block_content, uncommented

    # `frontmatter` is the one reading of a rule's or a skill's YAML front
    # matter (`PL-R417`): where it closes, and where each key's value ends, so a
    # line opening `paths:` inside another key's quoted value is no key
    # (`PL-BM8T`), and each key's value is a statement of its own to every
    # reader of prose here (`PL-WX79`). `tools/rules_paths_check.py` reads
    # `paths:` through it too.
    from docket.frontmatter import Unread as UnreadFrontMatter
    from docket.frontmatter import body_lines as _body_lines
    from docket.frontmatter import closing as frontmatter_closing
    from docket.frontmatter import comments as yaml_comments
    from docket.frontmatter import keys as frontmatter_keys
    from docket.frontmatter import plain as yaml_plain
    from docket.frontmatter import statements as frontmatter_statements

    # `instructions` is the one reading of a dated sentence: `_sentences` cuts a
    # statement where `docket.roadmap.SENTENCE_BREAK` does and at a blank line
    # inside a front matter's value, and `ISO_DATE_RE` is what counts as a date
    # in one. `check_host_claims` asks whether a sentence naming a host carries
    # a date, the question that module asks of an instruction, so the two
    # cannot disagree about where a sentence ends. Which Markdown files the
    # instruction set holds is its reading too, from the files the repository
    # tracks, so `measure_on_demand` sizes the set `docket check` ages rather
    # than a second walk of the disk (`PL-NNVJ`, `PL-J4YY`).
    from docket.instructions import ISO_DATE_RE, _markdown_under, _sentences
    from docket.lines import file_text, split_lines

    # `markdown` is the one reading of a document's blocks (`PL-R417`): where
    # each statement ends, so a code span or a bold run is read within its own
    # (`PL-FP7J`, `PL-VQBY`), where an HTML block runs (`PL-GT0J`), and which
    # lines are a heading, so a `#` line inside a fence is none (`PL-T1X0`).
    # Which marks on a line are a container's, where a table row's cells are,
    # and what a soft break is once those marks are blanked are its readings
    # too (`PL-NNVJ`).
    from docket.markdown import (
        CODE,
        FENCE,
        HTML,
        PARAGRAPH,
        PROSE,
        SOFT_BREAK,
        TABLE,
        block_lines,
        cell_spans,
        emphasis,
        statement_lines,
        unmarked,
    )
    from docket.markdown import headings as read_headings
    from docket.markdown import read as read_blocks
    from docket.markdown import tables as read_tables

    # `front_matter_spans` is the item grammar's reading of where each field of
    # a brief's front matter ends, so a brief's readers take one at a time
    # (`PL-CZ28`).
    from docket.model import CLOSED_STATUSES, SEMVER_PATTERN, Item, front_matter_spans

    # `python` is the one reading of where a Python statement ends (`PL-R417`):
    # a test is defined by a `def` statement rather than by a line opening one,
    # so `def test_ghost():` inside a fixture string defines nothing, and a
    # changed line counts toward the definition whose statement holds it, a
    # signature wrapped over several lines included (`PL-V2HK`).
    from docket.python import UNTOKENIZABLE, definition, docstrings, read_logical_lines, refusal
    from docket.release import (
        AUTOLINK_RE,
        CODE_SPAN_AT,
        NOTES_BULLET_RE,
        NOTES_DIR,
        RAW_HTML_RE,
        REFERENCED_RE,
        SEMVER_RE,
        SPAN_HEADING,
        code_spans,
        is_tagged,
        notes_bullets,
        notes_claims,
        notes_files,
        notes_ids,
        notes_path,
        notes_version,
        version_in,
        version_key,
    )

    # `_section_end` and `_subsection_end` are the bounds docket's own walkers
    # take, so a milestone's section and a gate's subsection end here where
    # `parse_milestones` and `_gate_entries` read them ending: at a heading as
    # `markdown` reads one, never a `#` line inside a fence (`PL-0Y7J`).
    from docket.roadmap import (
        BASELINE_MARK,
        DECLARATION_RE,
        EXCLUDED_SUBSECTION,
        SCOPE_SUBSECTION,
        TIMELINE_HEADING,
        VERSION_TABLE_HEADING,
        GateEntry,
        MilestoneSection,
        UnreadEntry,
        _section_end,
        _subsection_end,
        baseline_gate,
        baseline_heading,
        list_entry_lines,
        parse_milestones,
        parse_timeline,
        parse_version_table,
        table_rows,
    )

    # `shell_words` is the one reading of how a shell command splits
    # (`PL-PVW2`). A CI step's line and a Makefile recipe line are read through
    # it rather than a split of this tool's own, which cut inside quotes and
    # read `python3 "tools/my file.py"` as `tools/my` (`PL-CWBJ`), and a step's
    # script is cut into those lines by the same reading (`PL-Q9LK`), as are a
    # script's comments, which the host-claim check reads (`PL-W9VC`).
    from docket.shell import Reading, Word, script_lines, shell_words, simple_commands
    from docket.shell import comments as shell_comments
    from docket.store import ID_PATTERN, read_items

    # Reading `git tag` is a second borrowing, for the same reason as the first.
    # `vcs` collapses every way git can fail to answer - not installed, not a
    # repository, timed out - into an empty answer, and a check that asked the
    # question itself would either duplicate that or, by omitting it, fail on a
    # checkout with no git at all. The emptiness is read here as "this checkout
    # cannot say", never as "there are no tags". `GitRunner` is borrowed for its
    # blob batch, which answers every tag's `pyproject.toml` from one process,
    # and `answered` for telling git's silence from an empty file.
    # `changed_path_args` is borrowed so the close-out sweep lists a renamed
    # file's old name, the one stale prose still cites (`PL-KR69`), with
    # `listed_paths` and `logged_fields` reading its `-z` listings (`PL-4YDJ`),
    # and `default_base` so a tag the working tree predates is placed against the
    # branch every docket command compares with (`PL-HVLJ`). `find_cut` and
    # `notes_added` are the one definition of a release's cut, which the
    # printed tag commands use too (`PL-QHCW`). And `subject_pull_request` is
    # the one reading of the pull request number a subject names, which the
    # tag-span read takes the squash shape of (`PL-YYDT`). `default_branch` names
    # the branch the merge gate protects, which a workflow's branch filter is
    # matched against (`PL-C72H`).
    from docket.vcs import (
        ITEM_FILE_RE,
        LONG_GIT_TIMEOUT,
        RECORDS,
        Cut,
        GitRunner,
        GitUnanswered,
        Runner,
        answered,
        call_git,
        changed_path_args,
        default_base,
        default_branch,
        find_cut,
        is_shallow,
        listed_paths,
        logged_fields,
        notes_added,
        read_git,
        resolved,
        subject_pull_request,
        tags,
        untracked_path_args,
    )

    # What `ast.parse` raises where this interpreter cannot parse a file, which
    # `verify` names a file for (`PL-LCBQ`).
    from docket.verify import UNPARSABLE
except ImportError as error:  # pragma: no cover - a checkout missing the subproject
    raise SystemExit(
        "doc_check needs subprojects/docket/src/docket/roadmap.py for the release-train "
        "grammar, docket/vcs.py for the tag read and the default-branch list, "
        "docket/gitargv.py for which git command an argv names, "
        "docket/release.py for where a cut writes its notes, docket/shell.py for "
        "how a shell line splits, docket/fences.py for where a fenced block is, "
        "docket/python.py for where a Python statement ends, "
        "and docket/{config,model,store}.py for the queue, "
        f"and could not import them: {error}"
    ) from error

# `required_checks_check` holds the one reader of a workflow's triggers
# (`PL-848V`), which the merge gate's question is asked of rather than read a
# second way: two hand readers had each taken a few of `on:`'s spellings. It
# holds the one reader of a workflow's steps too (`PL-S3XS`), for the same
# reason: a line regex had taken a `run:` inside another block for a step.
import required_checks_check

# Which files the repository holds is `tracked_files`'s answer, and which of
# them are rule files is `rules_paths_check`'s, so a checkout under
# `.claude/worktrees/` is not read as this one and a nested rule is measured
# only where it is also read (`PL-2P5L`, `PL-9NZ3`).
from rules_paths_check import RULES_DIR, rule_files
from workflow_paths_check import tracked_under

# Documentation whose claims this tool holds to the tree. `CLAUDE.md` and the
# docket skill are included because they cite paths as heavily as the docs
# proper do, and a rule that names a file that no longer exists is a rule
# nobody can follow.
#
# The skills entry reaches below `SKILL.md` deliberately. A skill whose body
# outgrows compaction's 5,000-token re-attachment cap is split into a front
# page and mode files it points at, and the pointers are the whole mechanism -
# `.claude/skills/docket/` is seven such files carrying most of that skill's
# prose and all of its path citations. Matching only `SKILL.md` would have
# checked the page that survives and none of what it sends a session to read,
# which is the coverage-shaped hole a split would otherwise open silently
# (`PL-2XM2`). This widening admits the skills tree and nothing else; the
# reasoning under `_quoting_sources` for leaving the *queue* out is untouched,
# since that one turns on handing every item file to `check_make_targets`.
DOC_GLOBS = (
    "README.md",
    "ROADMAP.md",
    "CLAUDE.md",
    "AGENTS.md",
    "docs/*.md",
    ".claude/rules/**/*.md",
    ".claude/skills/**/*.md",
    "subprojects/*/README.md",
)

# What every session loads before it has read anything. `CLAUDE.md` may live at
# either of two paths, and a `.claude/rules/*.md` joins them unless it carries
# `paths:` frontmatter, which defers it to the sessions that open a matching
# file.
RESIDENT_ROOTS = ("CLAUDE.md", ".claude/CLAUDE.md")
#: The record of what the resident set holds and why: each block routed out or
#: kept, and the reductions already refused. Both resident advisories name it,
#: so a session meeting one reads the answer already written (`PL-X925`).
RESIDENT_LEDGER = "docs/resident-instructions.md"
SKILLS_DIR = ".claude/skills"
WORKER_DOC = "docs/worker.md"
# Instruction text a session loads only once something makes it load: a skill
# when it is invoked, a path-scoped rule when a matching file is read, the
# worker instructions when a worker run starts. Measured apart from the
# resident set rather than folded into it, because "loads at launch" and "may
# be made to load" are different quantities and one number cannot mean both
# (`PL-JQVB`). `docs/consultant-brief.md` is deliberately absent: it is pasted
# by a person as a user message rather than loaded by a session, which is the
# property it was built for, so no session loads it at all.
ON_DEMAND_ROOTS = (SKILLS_DIR, RULES_DIR, WORKER_DOC)

# The SessionStart hook, whose output is placed in every session's context
# before the conversation starts and resent on every turn - resident by every
# property that matters, and counted by nothing until `PL-44DG`. Run rather
# than read; `measure_digest` carries why, and what it costs.
DIGEST_HOOK = ".claude/hooks/docket-digest.sh"
# Generous, because what is being bounded is a hung remote rather than the
# hook's own work: it measured 4.2 s here, of which about 2 s is a fetch. The
# hook bounds its own `--unshallow` at 60 s, so anything past this is a
# failure rather than a slow container, and the measurement declines.
DIGEST_TIMEOUT = 120

# Below this many characters, a change to a resident file is a wording fix
# rather than a rule arriving or leaving, and the advisories below stay quiet
# for it. The total itself is always printed exactly, so a smaller change is
# still visible; what the floor suppresses is the demand for a justification.
#
# Measured rather than picked. Over the 79 commits that had moved this
# measurement by 2026-09-05, every wording fix moved at most 30 characters and
# every change that added or removed a rule moved at least 79, with nothing at
# all in between - so any floor inside that gap separates the two, and this one
# sits in it with margin on both sides. Without a floor, moving this metric from
# lines to characters would newly demand a routing justification for a
# four-character term swap, which is the same defect as the blindness it
# fixes, arriving from the other side (`PL-QV1F`).
MATERIAL_RESIDENT_DELTA = 40

# Every way git can fail to answer, named rather than written as a tuple in the
# `except` clause itself. This file must run under whatever bare `python3` is on
# PATH, but the repository's formatter targets a newer one, and it rewrites a
# parenthesized multi-type `except` into PEP 758's unparenthesized form, which
# older interpreters cannot parse. `subprojects/docket/` was broken exactly this
# way once and now guards it with a portability test; this file has the same
# exposure and no such guard. A name is not rewritten.
GIT_UNAVAILABLE = (OSError, subprocess.SubprocessError)

# Named for the same reason: a file that cannot be read is not a finding, and
# the two ways it can fail must not be written as a tuple in the `except`
# clause itself.
UNREADABLE = (OSError, UnicodeDecodeError)

# Where the package maps live, and where the provenance table lives. The
# simulator's map and the apparatus's are separate documents since `PL-KRGY`,
# and each is held to the tree on its own, so neither can pass on the other's.
ARCHITECTURE = Path("docs/ARCHITECTURE.md")
APPARATUS = Path("docs/apparatus.md")
PACKAGE_MAPS = (ARCHITECTURE, APPARATUS)
MODEL = Path("docs/MODEL.md")


# Where the release train lives. `ROADMAP.md` calls itself the authoritative
# version and milestone map, and it is the only statement of which milestone
# is current and which is next. That makes its rows something a tool has to be
# able to read, not only a person: `docket wave` reports the project's position
# on this table, and a parser guessing at free prose would be guessing at the
# plan.
#
# Where it is, is `docket.toml`'s `roadmap_file`, read through docket for the
# root being checked, so a project moving its plan moves this check with it
# (`PL-WCHF`).
def roadmap_path(root: Path) -> Path:
    """The plan's path relative to `root`, as `docket.config` reads it."""
    return Path(load_docket_config(root).roadmap_file)


REFERENCES = Path("docs/references/README.md")

PACKAGE_ROOT = PurePosixPath("src/anesthesia_sim")

# The subdirectories of the package's `data/` whose JSON files are not
# parameter files. The shipped Workspaces are layout, which
# `layout/shipped.py` reads, and they store no value a clinician could read,
# so neither the provenance table nor the source tiers apply to them
# (`PL-KXTL`).
NON_PARAMETER_DATA_DIRS = frozenset({"workspaces"})

# Directories that hold no reviewable source, so nothing in them belongs in a
# package map and nothing in them answers a path citation.
IGNORED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
        "build",
        "dist",
    }
)

# What a package map is expected to account for. `__init__.py` is excluded
# because it carries no behavior here and listing five of them would bury the
# modules that do.
MAPPED_SUFFIXES = frozenset({".py", ".json"})
UNMAPPED_NAMES = frozenset({"__init__.py"})

# Suffixes that make a code span a claim about a file in this repository.
# A span without one of these is prose or an identifier (`Entry.model_guidance`,
# `flet_charts.*`, `v0.2.0`), not a path, and is not resolved.
PATH_SUFFIXES = frozenset(
    {".py", ".json", ".md", ".yml", ".yaml", ".toml", ".sh", ".cfg", ".ini", ".lock", ".txt"}
)

# Prefixes a path citation may be written against. The documentation writes
# `core/parameters.py` and `data/agents/sevoflurane.json` package-relative,
# and `tools/doc_check.py` repository-relative; both are correct, so both
# roots are tried.
PATH_ROOTS = ("", str(PACKAGE_ROOT))

# Top-level keys in a data file that are not scientific parameters and so are
# not expected in the provenance table. `sources` is the citation array the
# table points *at*; `schema_version` is a file-format number.
NON_PARAMETER_KEYS = frozenset({"schema_version", "sources", "provenance_gap"})

# The closed vocabulary a `sources` entry's `tier` is drawn from, and a second
# copy of `core.parameters.SOURCE_TIERS`. This tool runs in a checkout with no
# virtualenv, so it cannot import the package; the duplication is deliberate
# and `tests/unit/test_parameters.py` fails if the two ever disagree.
SOURCE_TIERS = ("primary", "secondary", "reference-implementation")

TREE_ROOT_RE = re.compile(r"^(?P<path>[\w./-]+/)$")
#: A source file's name as the reference index writes one, the whole of a code
#: span: `name.pdf`.
REFERENCE_FILE_RE = re.compile(r"[\w][\w.-]*\.(?:pdf|txt|csv|json)")
TREE_ENTRY_RE = re.compile(r"^(?P<indent>(?:(?:│   )|(?:    ))*)(?:├──|└──) (?P<name>\S+)")

# A soft break (CommonMark 0.31.2 § 6.8) is `markdown.SOFT_BREAK`, imported
# above. Every reader of a phrase the documents may wrap takes its whitespace
# from it, rather than each meeting the wrap one capture at a time
# (`PL-R417`). It reads the gap and never where a statement ends, so it refuses
# no line: every reader built on it matches within one statement of
# `statement_lines` (`_statement_matches`), which decides the end (`PL-Z1R7`).
# It once refused each line that might open a block, and an ordered marker past
# 1, a pipe line and a block's opening indented four columns or more each carry
# a paragraph on wherever `statement_lines` reads one going on, so a closed
# quotation wrapped onto `2026. Notes follow` was refused as unclosed and a
# link wrapped onto it was never read (`PL-BCZQ`). It reads no `>`: every
# reader matches in text whose container markers `markdown.unmarked` has
# blanked (`_unmarked_text`). Spelt here with the markers, it read a `>` four
# or more columns into a paragraph's next line as a block quote's marker, where
# CommonMark reads it as text (`PL-NNVJ`).
#: The space between two words of a Markdown phrase: spaces or tabs, or a soft
#: break.
GAP = rf"(?:[ \t]++|{SOFT_BREAK})"
#: A character of a quotation: any but its closing mark or a line end, or a soft
#: break, so a quotation runs no further than the paragraph it opens in. A blank
#: line ends one (CommonMark 0.31.2 § 4.8), in a blockquote or out of one. Read
#: as `[^"]`, a quotation ran on past it, so the two halves a paragraph break
#: separates were one quotation (`PL-BYJ5`, `PL-T73L`). Every reader of a quoted
#: phrase here and in `tools/possessive_section_check.py` takes it.
QUOTATION_CHAR = rf'(?:[^"\n]|{SOFT_BREAK})'
#: The rest of a quotation its paragraph never closes, as a pattern's other
#: branch to the closed quotation it reads. Bounded, the closed branch alone
#: matched nothing there, so a citation that opened a quotation and lost its
#: closing mark went unread where `[^"]` had held it, wrongly joined to the next
#: paragraph's mark (`PL-T73L`). Each reader refuses it by name instead.
UNCLOSED_QUOTATION = rf'(?P<unclosed>{QUOTATION_CHAR}*+)(?!")'


#: A backslash escape (§ 2.4) or a character reference (§ 2.5), as a link's
#: destination decodes them.
ESCAPE_OR_REFERENCE_RE = re.compile(
    r"\\(?P<escaped>[!-/:-@\[-`{-~])"
    r"|(?P<reference>&(?:#[0-9]{1,7}|#[Xx][0-9A-Fa-f]{1,6}|[A-Za-z][A-Za-z0-9]{0,31});)"
)
#: How deep links, images and the text inside them are followed before the
#: rest of a statement is read as text, as markdown-it-py's `maxNesting` bounds
#: its reading of them.
INLINE_NESTING = 20


@dataclass(frozen=True)
class Link:
    """An inline link or image (CommonMark 0.31.2 § 6.3, § 6.4), as written.

    `start` is its `[`, or an image's `!`, and `end` is past its `)`.
    `destination` is what it links to as the text writes it, inside any angle
    brackets, and `at` is where that stands; an empty one, `[a]()`, stands
    where one would have. Offsets are the text's that was read.
    """

    start: int
    end: int
    destination: str
    at: tuple[int, int]
    image: bool

    @property
    def target(self) -> str:
        """The destination a renderer follows: each escape and character reference decoded."""
        return ESCAPE_OR_REFERENCE_RE.sub(_decoded, self.destination)


def _decoded(match: re.Match[str]) -> str:
    """The character an escape or a character reference stands for."""
    escaped = match["escaped"]
    return escaped if escaped is not None else html.unescape(match["reference"])


class _InlineReader:
    """Inline content, read left to right as CommonMark 0.31.2 § 6 reads it (`PL-R417`).

    The reading markdown-it-py gives, which `tests/unit/test_inline_reference.py`
    holds this one to over the CommonMark and GitHub Flavored Markdown
    specifications' examples and every tracked document. At each position an
    escape, a code span, a link or image, an autolink and raw HTML are tried in
    turn, and a link's text is found by stepping over each of those whole: a
    `]` inside a code span or an autolink closes no link, text holding a link
    of its own is no link (§ 6.3), and an escaped backtick or bracket opens
    nothing. An image's description is its text, so nothing in one is read.
    Each regex this replaced matched wherever it could, and met each of those
    rules one capture at a time.
    """

    def __init__(self, text: str) -> None:
        self.text = text
        self.spans: list[re.Match[str]] = []
        self.links: list[Link] = []
        #: Where each link's or image's text ends - its `]` - by the link's start.
        self.labels: dict[int, int] = {}
        self._ends: dict[tuple[int, int], int] = {}

    def read(self, start: int, end: int, depth: int = 0) -> None:
        """Record every code span, link and image from `start` to `end`, in order."""
        text = self.text
        position = start
        while position < end:
            character = text[position]
            if character == "`":
                span = CODE_SPAN_AT.match(text, position, end)
                if span is None:
                    position = _run_end(text, position, end)
                    continue
                self.spans.append(span)
                position = span.end()
            elif character == "[" or (character == "!" and text.startswith("[", position + 1)):
                found = self._link(position, end, depth)
                if found is None:
                    position += 1
                    continue
                link, label = found
                self.links.append(link)
                self.labels[link.start] = label
                if not link.image:
                    self.read(position + 1, label, depth + 1)
                position = link.end
            else:
                position = _past_other(text, position, end)

    def _past(self, position: int, end: int, depth: int) -> int:
        """Past whatever opens at `position`, read whole, or past its one character."""
        key = (position, end)
        if key not in self._ends:
            text = self.text
            character = text[position]
            if depth >= INLINE_NESTING:
                found = end
            elif character == "`":
                span = CODE_SPAN_AT.match(text, position, end)
                found = _run_end(text, position, end) if span is None else span.end()
            elif character == "[" or (character == "!" and text.startswith("[", position + 1)):
                link = self._link(position, end, depth + 1)
                found = position + 1 if link is None else link[0].end
            else:
                found = _past_other(text, position, end)
            self._ends[key] = found
        return self._ends[key]

    def _label_end(self, opener: int, end: int, nested: bool, depth: int) -> int:
        """Where the `]` closing the text a `[` at `opener` opens stands, or -1.

        A bracket opening nothing nests, and the next `]` is its own. Unless
        `nested`, a link opening inside the text ends the reading, since a link
        holds no link (§ 6.3); an image's description may hold one.
        """
        text = self.text
        level = 1
        position = opener + 1
        while position < end:
            if text[position] == "]":
                level -= 1
                if level == 0:
                    return position
            before = position
            position = self._past(position, end, depth)
            if text[before] == "[":
                if position == before + 1:
                    level += 1
                elif not nested:
                    return -1
        return -1

    def _link(self, position: int, end: int, depth: int) -> tuple[Link, int] | None:
        """The link or image opening at `position`, and where its text ends; `None` for none.

        Its text, `(`, an optional destination and title, and `)`, with spaces,
        tabs and line endings between them (§ 6.3). A destination that cannot
        be read leaves the link only where `)` comes next, as `[a]()` does.
        """
        text = self.text
        image = text[position] == "!"
        label = self._label_end(position + 1 if image else position, end, image, depth)
        if label < 0 or not text.startswith("(", label + 1):
            return None
        cursor = _past_space(text, label + 2, end)
        if cursor >= end:
            return None
        at = (cursor, cursor)
        destination = _destination(text, cursor, end)
        if destination is not None:
            at, cursor = destination
            gap = _past_space(text, cursor, end)
            title = _title_end(text, gap, end) if gap > cursor else None
            cursor = gap if title is None else _past_space(text, title, end)
        if cursor >= end or text[cursor] != ")":
            return None
        return Link(position, cursor + 1, text[at[0] : at[1]], at, image), label


def _rendered_text(text: str) -> str:
    """The text a renderer shows for one statement of inline Markdown, markup gone.

    A code span gives its content, a link or an image its text, an autolink
    its address, and raw HTML nothing; an escape gives the character it
    escapes, a character reference the one it names, and the delimiters of
    each emphasis CommonMark pairs are gone (0.31.2 § 6). GitHub slugs a
    heading's anchor from this text rather than from its Markdown, so a
    heading holding a code span or a link has the anchor `_github_slugs`
    gives (`PL-9XP0`). An image's text is read as written, markup and all.
    """
    reader = _InlineReader(text)
    reader.read(0, len(text))
    edits = [(span.start(), span.end(), _span_text(span["content"])) for span in reader.spans]
    tails = [(reader.labels[link.start], link.end) for link in reader.links]
    for link, (label, end) in zip(reader.links, tails, strict=True):
        edits += [(link.start, link.start + (2 if link.image else 1), ""), (label, end, "")]
    literals = [(span.start(), span.end()) for span in reader.spans] + tails
    for run in emphasis(text, literals):
        edits += [(run.start, run.start + run.width, ""), (run.end - run.width, run.end, "")]
    shown: list[str] = []
    position = 0
    for start, end, replacement in sorted(edits):
        if start >= position:
            shown += [_plain_text(text[position:start]), replacement]
            position = end
    shown.append(_plain_text(text[position:]))
    return "".join(shown)


def _span_text(content: str) -> str:
    """A code span's content as rendered: line endings as spaces, one space trimmed from each end.

    Trimmed only where both ends have one and the content is not all spaces
    (CommonMark 0.31.2 § 6.1).
    """
    content = content.replace("\n", " ")
    if content.startswith(" ") and content.endswith(" ") and content.strip(" "):
        return content[1:-1]
    return content


def _plain_text(text: str) -> str:
    """`text`, holding no code span, link or emphasis, as rendered: see `_rendered_text`."""
    shown: list[str] = []
    position = 0
    while position < len(text):
        if text[position] == "<":
            found = AUTOLINK_RE.match(text, position) or RAW_HTML_RE.match(text, position)
            if found is not None:
                shown.append(found.group()[1:-1] if found.re is AUTOLINK_RE else "")
                position = found.end()
                continue
        end = text.find("<", position + 1)
        end = len(text) if end < 0 else end
        shown.append(ESCAPE_OR_REFERENCE_RE.sub(_decoded, text[position:end]))
        position = end
    return "".join(shown)


#: The Unicode general categories github-slugger strips from a heading's text:
#: other numbers, every punctuation but connectors such as `_` and the hyphen,
#: symbols, controls, private use, format and unassigned characters, and
#: separators but the space (`script/generate-regex.js` at
#: https://github.com/Flet/github-slugger, read 2026-10-18). It keeps a
#: character Unicode calls alphabetic in any of them, which `str.isalpha` reads
#: only for letters, so a circled letter such as `ⓐ` is dropped here and kept
#: there - the one place this reading parts from it.
SLUG_STRIPPED = frozenset(("No", "Pe", "Pf", "Pi", "Ps", "Po", "Pd", "Cc", "Co", "Cf", "Cn"))


def _slug_keeps(character: str) -> bool:
    """Whether github-slugger keeps `character` in a slug; see `SLUG_STRIPPED`."""
    if character in " -" or character.isalpha():
        return True
    category = unicodedata.category(character)
    return category not in SLUG_STRIPPED and category[0] not in "SZ"


def _github_slugs(titles: Iterable[str]) -> list[str]:
    """The anchor GitHub gives each heading of a document, in order, from its rendered title.

    github-slugger's rule, whose README says it slugs "just like GitHub does
    for markdown headings": the text lower-cased, every character of a
    stripped category gone (`SLUG_STRIPPED`, and `S` and `Z` but the space,
    and `-` kept), and each space written as a hyphen. A slug met before
    takes `-1`, `-2` and so on, counting from that slug, until it is new
    (`index.js`, read 2026-10-18). This tool slugged the raw Markdown, kept
    only `[a-z0-9-]` and never suffixed a repeat (`PL-9XP0`).
    """
    seen: dict[str, int] = {}
    slugs: list[str] = []
    for title in titles:
        slug = "".join(
            "-" if character == " " else character
            for character in _rendered_text(title).lower()
            if _slug_keeps(character)
        )
        result = slug
        while result in seen:
            seen[slug] += 1
            result = f"{slug}-{seen[slug]}"
        seen[result] = 0
        slugs.append(result)
    return slugs


def _run_end(text: str, position: int, end: int) -> int:
    """Past the backtick run at `position`, which a run no closer matches is, whole (§ 6.1)."""
    while position < end and text[position] == "`":
        position += 1
    return position


def _past_other(text: str, position: int, end: int) -> int:
    """Past an escape, an autolink or raw HTML at `position`, or past its one character."""
    character = text[position]
    if character == "\\" and position + 1 < end:
        return position + 2
    if character == "<":
        found = AUTOLINK_RE.match(text, position, end) or RAW_HTML_RE.match(text, position, end)
        if found is not None:
            return found.end()
    return position + 1


def _past_space(text: str, position: int, end: int) -> int:
    """Past the spaces, tabs and line endings at `position`."""
    while position < end and text[position] in " \t\n":
        position += 1
    return position


def _destination(text: str, position: int, end: int) -> tuple[tuple[int, int], int] | None:
    """The link destination at `position` (§ 6.3): where it stands and where it ends, or `None`.

    In angle brackets it may hold a space but no line ending and no unescaped
    `<`; bare, it runs to a space, a control character or a `)` no `(` opened,
    its parentheses nested at most 32 deep, and is never empty.
    """
    if text.startswith("<", position):
        cursor = position + 1
        while cursor < end:
            character = text[cursor]
            if character in "\n<":
                return None
            if character == ">":
                return (position + 1, cursor), cursor + 1
            cursor += 2 if character == "\\" and cursor + 1 < end else 1
        return None
    cursor = position
    level = 0
    while cursor < end:
        character = text[cursor]
        if character <= " " or character == "\x7f":
            break
        if character == "\\" and cursor + 1 < end:
            if text[cursor + 1] == " ":
                break
            cursor += 2
            continue
        if character == "(":
            level += 1
            if level > 32:
                return None
        elif character == ")":
            if not level:
                break
            level -= 1
        cursor += 1
    if cursor == position or level:
        return None
    return (position, cursor), cursor


def _title_end(text: str, position: int, end: int) -> int | None:
    """Past the link title at `position` (§ 6.3), quoted or in parentheses, or `None`.

    A backslash escapes the character after it, a line ending included, so a
    title wrapped after one goes on (`PL-BCZQ`).
    """
    if position >= end or text[position] not in "\"'(":
        return None
    closing = ")" if text[position] == "(" else text[position]
    cursor = position + 1
    while cursor < end:
        character = text[cursor]
        if character == closing:
            return cursor + 1
        if character == "(" and closing == ")":
            return None
        cursor += 2 if character == "\\" and cursor + 1 < end else 1
    return None


NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")

# A prose value that restates a data-file constant declares which one, so it
# can be held to the file the way the provenance table already is. The
# declaration is an HTML comment, so it is invisible in the rendered document
# and the sentence still reads as prose.
#
# **Two kinds, because they are different claims.** `provenance:` says the
# number written beside it *is* this key's value, so both halves are checkable
# - the key against the file, and the value against the prose. `derived:` says
# the figure it names was *computed from* these keys, which no file holds: the
# inputs are checked against the files and the figure is not, because
# recomputing it is judgment about rounding and units that a tool guessing at
# it would get authoritative-looking and wrong. What the tool decides is "the
# inputs this figure was computed from have moved"; what it never decides is
# what the new figure should be.
#
# A bare scan for numerals was rejected and cannot be revived: `2.5` appears in
# `docs/MODEL.md` as an alveolar volume, a solver tolerance in seconds and a
# fresh-gas flow, and `4 L/min` appears as both the reference adult's alveolar
# ventilation and an unrelated fresh-gas rate. A check that bound those to a
# key would be confidently wrong in exactly the places a reader trusts most.
PROSE_MARKER_RE = re.compile(r"^<!--\s*(?P<kind>provenance|derived):\s*(?P<body>.+?)\s*-->$")

# A path a document names *because* it is not in the tree - one the project
# lacks (`setup.py`), a tool it plans, a file since deleted - is declared in a
# marker under the paragraph, the way the markers above declare a restated
# value: `<!-- absent: setup.py -->`, several paths separated by spaces. The
# code span is still a path, so the citation check still reads it, and a
# sentence denying a file exists failed as citing one that does not
# (`PL-HJ8G`). Telling the denial from the claim by its words - "no", "a
# future", "was deleted" - is the wording recognition `PL-GPJ7` retires from
# the hard gates; the marker is syntax, and it is a claim of its own that is
# checked: a path it names must be absent, and cited in its paragraph.
ABSENT_MARKER_RE = re.compile(r"^<!--\s*absent:\s*(?P<paths>.+?)\s*-->$")
# A marker opened on a line and not closed there (`PL-R417`). Markers are read a
# line at a time, as the syntax they are, so a comment carried across lines was
# read as nothing and the claim it made went unchecked; it is refused by name
# instead, which costs the writer one join.
SPLIT_MARKER_RE = re.compile(r"^<!--\s*(?P<kind>provenance|derived|absent):(?!.*-->)")
#: A marker's kind after its comment's opening, on that line or a later one; a
#: comment is read whole by `_split_markers`.
MARKER_OPENING_RE = re.compile(r"<!--\s*(?P<kind>provenance|derived|absent):")
DERIVED_FROM_RE = re.compile(r"^(?P<figure>.+?)\s+from\s+(?P<rest>\S+\.json\s.+)$")
MARKER_SOURCE_RE = re.compile(r"^(?P<relative>\S+\.json)\s+(?P<assertions>.+)$")
ASSERTION_RE = re.compile(r"^(?P<key>[A-Za-z_][\w.]*)\s*=\s*(?P<value>[-+]?\d+(?:\.\d+)?)$")

BRACE_RE = re.compile(r"\{([^{}]*)\}")

# A quoted phrase is a section citation when the section mark says it is: `§
# "X"`, wherever it stands. The mark is the recognition, and it is exact. The
# words around a quotation are not: read without the mark, the `see` and
# `above` positions took every quotation in them for a citation, so prose
# quoting what a command printed - `See "docket check: 0 errors" for what a
# clean run prints` - hard-failed as a section no document has (`PL-YSMV`), as
# a quoted measurement had before it (`PL-KJ63`), and the only repair on offer
# was to reword prose that was not wrong. `CLAUDE.md` keeps hard failure for
# exact rules, and `PL-GPJ7` is the family this is one member of.
#
# Wherever it stands, and not only beside `see`, `under`, `above` or `below`:
# those four positions held 163 of the documents' 471 marks on 2026-09-26, and
# the 308 elsewhere - `per § "X"`, `in § "X"`, a mark opening a sentence - were
# read by nothing, which is how two of them stayed stale for a fortnight
# (`PL-QQCD`). A mark that a code-spanned source stands directly before is not
# this pattern's to resolve: `` `docs/MODEL.md` § "X" `` names its document and
# `QUOTED_SOURCE_RE` holds it by containment, and `` `PL-MB2W` § "X" `` names
# an item brief, which no documentation heading answers and `ITEM_SECTION_RE`
# holds the same way.
#
# The mark names a section of this repository's own documents, and nothing
# else. A section of an outside source - a paper's "Materials and Methods", a
# manual's page - is written without it, as the source's own locator: no
# heading here can answer such a mark, and reading the words before it to tell
# a paper from a document would be the wording recognition this file refuses.
# Five such marks stood in the documents on 2026-09-26 and were rewritten
# under `PL-GPJ7`.
#
# The quotation may span a source line. Prose here hard-wraps at about 78
# characters, so a section title long enough to wrap was unmatchable while
# the quotation was `[^"\n]+` - and unmatchable means unchecked, not reported:
# `check_citations` passed over 18 citations in the documents it already reads
# without examining one of them. It spans a soft break and nothing more, so it
# ends with its paragraph (`QUOTATION_CHAR`), and `_normalized` puts the term
# back on one line before it is compared. A quotation its paragraph never
# closes is the `unclosed` branch, refused by name: `[^"]` read on to the next
# paragraph's mark and held the two halves as one title (`PL-T73L`).
#
# **A closed quotation is read whatever its length** (`PL-WJF2`). It is the
# text up to its paragraph's next mark, which nothing else decides, so it is
# taken possessively, as one reading, here and in the three other citation
# patterns below. Each bounded it at 160 or 200 characters, and a citation
# whose closing mark stood further off matched neither branch and went unread
# without a word. The bound was kept against a stray mark, read on to its
# paragraph's next one and compared as a title nobody wrote; but a stray mark
# nearer its neighbour than the bound was compared all along, so the bound
# never prevented that report, only hid it past a length. Nor did it bound the
# cost: lazy, the repetition tries every split of a line's trailing spaces
# between `QUOTATION_CHAR`'s two halves before a match fails, three per hard
# break, so a quotation never closed across twelve ten-character lines ending
# in one took 259 ms inside the 160 and sixteen lines about 20 s, measured
# 2026-10-05, where possessive takes microseconds.
#
# The gaps around a quotation are `GAP`s, so a citation wrapped inside a
# blockquote is read past the next line's `>` as CommonMark reads it, where
# `[ \n]*` stood and stopped there, leaving it unchecked (`PL-XW87`). The
# quotation's own wrapped lines lose their markers in `_normalized`.
CITATION_RE = re.compile(
    r"§{1,2}" + GAP + rf'*"(?:(?P<term>{QUOTATION_CHAR}++)"|{UNCLOSED_QUOTATION})'
)
# The same two positions without the mark, which is how 147 of the documents'
# citations were written until `PL-YSMV` marked them. Read only to say that one
# lacks its mark, and only where its quotation names a heading: that is a fact
# about the tree, and it makes the quotation a section citation. A quotation
# naming no heading may be a faithful copy of anything - output, a label, a
# figure - and is left alone, which is `tools/possessive_section_check.py`'s
# asymmetry for the same reason. An advisory rather than an error, because the
# position is still wording: a quotation that only coincides with a heading's
# name is told to take a mark it does not need, and a reader can decline that.
#
# The `directed` branch opens on a letter or a code span, as a heading or a
# `**Bold.**` marker does and a quoted measurement - `"~88-256 B each" above` -
# does not. Measured across the documents this reads on 2026-09-13: 40 directed
# citations, none of which opens on anything else.
#
# Each quotation ends with its paragraph, as `CITATION_RE`'s does (`PL-T73L`),
# and is read whatever its length, possessively, as that one is (`PL-WJF2`).
# The `named` branch's opening word is what read it as a citation, so one its
# paragraph never closes is its `unclosed` branch, refused by name; the
# `directed` branch is known only by the direction after its closing mark, so
# an unclosed quotation is none.
UNMARKED_CITATION_RE = re.compile(
    rf'(?:\b(?:see|under){GAP}+"(?:(?P<named>{QUOTATION_CHAR}++)"|{UNCLOSED_QUOTATION}))'
    rf'|(?:"(?P<directed>[`A-Za-z]{QUOTATION_CHAR}*+)"{GAP}+(?:above|below)\b)',
    re.IGNORECASE,
)
#: A direction after a quotation, matched at the quotation's end.
DIRECTION_RE = re.compile(GAP + r"*(?:above|below)\b", re.IGNORECASE)
#: What stands immediately before a quotation that already carries the mark,
#: searched in the text up to and including the match's first character: a
#: soft break is known only by the line it opens onto, so a window ending at
#: the break would read the end of the window there (`PL-XW87`).
MARKED_RE = re.compile(r"§{1,2}" + GAP + r"*(?=.\Z)", re.DOTALL)

# A `**Bold.**` run opening a statement, matched in text whose containers'
# markers `_headings` has blanked, so the run after a list item's bullet or
# number, at any depth, or a block quote's `>` is read as the one at a line's
# start is. This repository subdivides long documents with these rather than
# with deeper `#` levels, and then cites them by name exactly as it cites
# headings - `docs/MODEL.md` alone carries 513 of them against 269 headings.
# Reading only `#` lines therefore made a correct citation look stale, which
# is the worse failure of the two: a reader sent to repair prose that was
# right. Read past a top-level bullet alone, a title after an ordered marker,
# a nested bullet or a `>` was no title, and a correct citation of one was
# refused (`PL-8NPN`). A title wrapped across a soft break is still one title
# (`PL-R417`); `_headings` hands it back on one line, as a citation of it is
# compared.
MARKER_RE = re.compile(rf"^[ \t]*\*\*(?P<title>(?:[^*\n]|{SOFT_BREAK})+?)\.?\*\*", re.M)

# A citation that names its target document and then quotes it:
# `` `docs/WORKING_NOTES.md`, "Splitting error outside the gate's operating
# point" ``. The document is explicit, so nothing has to be inferred about
# which file the quotation belongs to - which is what lets this run over the
# queue and the docstrings without the guesswork that reading a bare quoted
# phrase there would need. The quotation must open on a word character, so a
# stray `")"` in prose is not read as one, and it may span source lines inside
# its paragraph, at any length (`PL-WJF2`); one its paragraph never closes is
# the `unclosed` branch, refused by name (`PL-T73L`).
#: What may stand between a cited document and its quotation. A closed set of
#: connectives, never a content word: the pattern once allowed only `,` and
#: `:`, which left the two forms this project actually writes - `§` and the
#: possessive - matching nothing, and matching nothing is silent rather than
#: reported. Counted 2026-09-13 over `*.py` and `*.md`: 353 `§`, 150 `'s`, 44
#: `,`, 20 bare, 11 `under`, 9 `(`, 5 `'s own`, 4 `:`, 3 `§§`.
#:
#: The possessive was excluded until 2026-09-21, on the ground that this
#: project writes `` `CLAUDE.md`'s "..." `` for a *sentence* it is quoting as
#: often as for a section it is citing, and that the two are indistinguishable
#: without reading the meaning (`PL-V13T`, which measured 28 errors and read
#: every one as a false positive). **The distinction was never needed.**
#: `check_quoted_sources` is the only consumer of this pattern and it tests
#: containment rather than headings, so it asks one question of both uses -
#: whether the cited file contains the words - and a quotation that has drifted
#: is as stale as a title that has. Re-measured on 2026-09-21 over the same
#: tree: 40 errors, of which 24 were verbatim in an earlier version of the
#: cited file and 2 were verbatim in a *different* file from the one named. A
#: majority were real, which is the count the exclusion turned on and the count
#: that reversed it (`PL-316G`).
#:
#: What it costs is a constraint on prose rather than a false-error risk: a
#: quotation in quotation marks has to be quotable, so a rule named by a
#: compressed handle is written out or loses its quotes. Three sites paid it.
#:
#: The tail below the possessive stays out, and for the original reason -
#: "`docs/MODEL.md` gains \"a new section\"", "its eighteen \"...\"" - because
#: admitting an arbitrary word would read prose as a citation and hard-fail on
#: text that is not wrong. That is `PL-KJ63`'s over-reach, so widening this set
#: still means adding a *named* connective with no second use that containment
#: cannot answer, and nothing else.
CITATION_CONNECTIVE = r"(?:[,:(]|§{1,2}|['\u2019]s(?:" + GAP + r"+own)?|\bunder\b)"

QUOTED_SOURCE_RE = re.compile(
    r"(?:\b(?:see|under|in)" + GAP + r"+)?"
    r"`(?P<document>[\w./-]+\.md)`" + GAP + r"*"
    r"(?P<connective>" + CITATION_CONNECTIVE + r")?" + GAP + r"*"
    rf'"(?:(?P<quoted>\w{QUOTATION_CHAR}{{2,}}+)"|(?=\w){UNCLOSED_QUOTATION})'
)
#: The connectives that claim the named document holds the words: the section
#: mark, and the possessive that attributes them to it. A quotation after
#: either that the file does not contain is an error. After the rest - a colon,
#: a comma, a parenthesis, `under`, or nothing - it is an advisory, because
#: those are equally how a brief sets down wording *proposed* for a document or
#: since deleted from it, which the file rightly lacks: a brief proposing a
#: sentence for `CLAUDE.md` after a colon, and one quoting a sentence replaced
#: since after a comma, are the two false refusals reproduced (`PL-HVST`). No
#: spelling separates such a quotation from a claim, so under `PL-GPJ7`'s rule
#: it cannot be a hard failure. Counted 2026-09-26 over the documents, the live
#: briefs and the docstrings: 423 `§` and 15 possessive quotations stay hard,
#: and 28 move - 10 bare, 9 comma, 4 colon, 3 `under`, 2 parenthesis - every
#: one contained in its file that day, so the move lost no finding. The
#: possessive stays hard because neither refusal came through it, and because
#: it is how this project quotes a sentence, whose drift is the point.
CLAIMING_CONNECTIVE = r"§{1,2}|['\u2019]s(?:" + GAP + r"+own)?"
CLAIMING_CONNECTIVE_RE = re.compile(CLAIMING_CONNECTIVE)
#: A code-spanned source - a document, an item, a module - standing directly
#: before a citation, which then quotes *that* source. `` `docs/MODEL.md` under
#: "Known limitations" `` is `QUOTED_SOURCE_RE`'s to hold, by containment, and
#: telling it to take a `§` would break the one match that reads it.
QUALIFIED_RE = re.compile(
    r"`[\w./-]+`" + GAP + r"*" + CITATION_CONNECTIVE + r"?" + GAP + r"*(?=.\Z)", re.DOTALL
)
#: A claiming connective after a code-spanned item id, which cites that item's
#: brief: `` `PL-MB2W` § "Design round, 2026-09-24" `` or `` `PL-CNJ1`'s
#: "writes nothing" ``. `QUALIFIED_RE` hands it on from `check_citations`,
#: since no documentation heading answers it, and `QUOTED_SOURCE_RE` names only
#: a `.md` document, so the seven section marks standing on 2026-09-26 were read
#: by nothing (`PL-QYN4`), and the eleven possessives until `PL-RX0W`. Only
#: the connectives that claim the brief holds the words: `under "X"` names the
#: heading the item is listed under elsewhere, as both such sites did that day,
#: and a quotation after a bare id is prose.
ITEM_SECTION_RE = re.compile(
    rf"`(?P<item>{ID_PATTERN})`{GAP}*(?:{CLAIMING_CONNECTIVE}){GAP}*"
    rf'"(?:(?P<quoted>\w{QUOTATION_CHAR}{{2,}}+)"|(?=\w){UNCLOSED_QUOTATION})'
)

# The `**Tags.**` statement. What it claims is deliberately not a list: the
# version table above it already says which releases exist, so restating them
# would be a second copy to keep true, and it was wrong twice before this check
# was written. The claim is the invariant instead - every completed release
# carries a tag - which is read against the table and `git tag` directly.
#
# What stays prose is the exception. A version that genuinely shipped untagged
# is named in a bold sentence, and the decidable half of that is its count
# against the names it gives; whether the omission is settled or an open
# decision is not, and is left alone.
TAGS_MARK_RE = re.compile(r"^[ \t]*\*\*Tags\.\*\*")
UNTAGGED_CLAIM_RE = re.compile(
    rf"\*\*(?P<count>[A-Za-z]+|\d+){GAP}+versions?{GAP}+(?:are|is){GAP}+untagged\*\*", re.I
)
# The second exception, written the same way: a version whose tag is on the
# commit it shipped from although that commit's version file was never bumped.
# The wording is the claim - the release went out like that - so a tag that is
# merely on the wrong commit cannot honestly be excused by it, and is moved.
STALE_VERSION_CLAIM_RE = re.compile(
    rf"\*\*(?P<count>[A-Za-z]+|\d+){GAP}+versions?{GAP}+shipped{GAP}+with{GAP}+"
    rf"a{GAP}+stale{GAP}+version{GAP}+file\*\*",
    re.I,
)
# `: v0.1.0, v0.2.0 and v0.3.0` - read one version at a time so the list ends
# where the prose resumes, rather than sweeping up every version in the region.
# Both claims and their lists cross a soft break as `GAP` does, a block quote's
# `>` included, so the list also ends where its statement does rather than
# running on past a blank line (`PL-4ZDZ`).
LIST_SEPARATOR_RE = re.compile(rf"(?:[,:]|{GAP})*(?:and{GAP}+)?")
LIST_VERSION_RE = re.compile(rf"v(?P<version>{SEMVER_PATTERN})")
# This document writes its counts as words, so both forms are read. Anything
# outside the table is reported rather than guessed at: a count nobody can read
# is a count nobody is checking.
NUMBER_WORDS = {
    "no": 0,
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

#: A Makefile line that make carries on to the next one (`PL-R417`): it ends in
#: an odd run of backslashes, since in an even run each escapes the next. Read
#: from GNU make 4.3's `readline` and run through it on 2026-10-04: `echo a \\`
#: over `echo next` ran as two commands.
MAKE_CONTINUED_RE = re.compile(r"(?<!\\)(?:\\\\)*\\$")
#: A `define` directive, which opens a variable whose value is every line up to
#: the `endef` closing it (`PL-4MLK`): the word `define` after any of the
#: modifiers make takes ahead of it - `export`, `override`, `private` - alone or
#: before a blank, and with no assignment operator after it, since `define := x`
#: assigns a variable named `define`. Not `unexport`, which make reads as its
#: own directive, so `unexport define X` unexports two variables. Read from
#: `parse_var_assignment` in GNU make 4.3's `src/read.c` and run through make
#: 4.3 on 2026-10-05. `name` is empty where the directive names no variable,
#: which make refuses.
MAKE_DEFINE_RE = re.compile(
    r"[ \t]*(?:(?:export|override|private)[ \t]+)*define"
    r"(?:[ \t]+(?![ \t]|(?:::|[:+?!])?=)|$)(?P<name>[^#]*)"
)
#: An assignment to `.RECIPEPREFIX`, after any of make's modifiers and with
#: any operator, or a `define` of it. From that line on make 4.3 opens a
#: recipe line with the variable's first character instead of a tab (`eval`
#: in GNU make 4.3's `src/read.c` tests a line against `cmd_prefix`), and
#: every reader here knows a recipe line by its tab, so `_make_lines` declines
#: the Makefile by name rather than read its recipes as missing (`PL-GSJ6`).
MAKE_RECIPEPREFIX_RE = re.compile(
    r"[ \t]*(?:(?:export|override|private)[ \t]+)*(?:define[ \t]+)?"
    r"\.RECIPEPREFIX[ \t]*(?:(?:::|[:+?!])?=|$|#)"
)
#: The body lines that nest a `define` or close one, as `do_define` in the same
#: file reads them: a bare `define`, no modifier ahead of it, opens another, and
#: an `endef` alone or before a blank closes one, so `endef # done` closes and
#: `endef#` does not. A line led by a tab is neither, whatever it says.
MAKE_DEFINE_OPENS_RE = re.compile(r"[ \t]*define(?:[ \t]|$)")
MAKE_DEFINE_CLOSES_RE = re.compile(r"[ \t]*endef(?:[ \t]|$)")
#: What make skips ahead of a word and ends one at: `NEXT_TOKEN` and
#: `END_OF_TOKEN` in GNU make 4.3's `src/makeint.h`, every character C's
#: `isspace` takes.
MAKE_SPACE = " \t\n\v\f\r"
MAKE_SPACE_RE = re.compile(r"[ \t\n\v\f\r]")
#: The modifiers `parse_var_assignment` in make 4.3's `src/read.c` takes ahead
#: of an assignment, and the two words that make an assignment of the line
#: after them.
MAKE_MODIFIERS = frozenset({"export", "override", "private"})
MAKE_DEFINING = frozenset({"define", "undefine"})
#: The directives `eval` in the same file reads once no assignment takes the
#: line, each ending the rule above it and opening none: `export` and
#: `unexport` naming variables to pass on, a search path, and the two ways of
#: reading another file in.
MAKE_DIRECTIVES = frozenset(
    {"export", "unexport", "vpath", "include", "-include", "sinclude", "load", "-load"}
)
#: The words that open, turn and close a conditional (`conditional_line`, same
#: file), none of which ends a rule.
MAKE_CONDITIONALS = frozenset({"ifdef", "ifndef", "ifeq", "ifneq", "else", "endif"})
#: A backslash escaping what a rule line's names end or split at: a blank, the
#: `:` ending the targets, the `;` and `#` ending the line, the `|` before
#: order-only prerequisites. GNU make 4.3 unquotes each by rules this reader
#: does not port - `a\:b:` names `a:b`, `a\ b c:` names `a b` and `c`, and
#: `x: a\;b` still ends the rule at the `;` - so a rule line holding one is
#: declined by name (run through make 4.3 on 2026-10-12, `PL-5M36`). Before
#: anything else a backslash names itself, as make keeps it, and `x: a\=b` is a
#: target-specific variable to make and to `_make_rule` alike.
MAKE_ESCAPED_NAME_RE = re.compile(r"\\[ \t:;#|]")
# The target a `make` command names, read from the word after `make`.
MAKE_TARGET_WORD_RE = re.compile(r"[a-z][\w.-]*")
# `make docket`, as the documentation writes it. Read only inside code spans
# and fenced blocks: prose says "make sure" and means nothing of the kind.
MAKE_MENTION_RE = re.compile(r"\bmake\s+(?P<name>[a-z][\w.-]*)")
# A fenced line names a target only where `make` heads a command, which
# `_make_mentions` reads through docket's shell lexer. Read anywhere on the
# line, a fence's shell comment (`# make sure the virtualenv exists`) and
# make's own output (`No rule to make target`) each failed as a target the
# Makefile lacks, and the only repair was to reword a correct sample
# (`PL-L8VP`). This pattern, `make` as a line's first word, is what is left
# for a fence the lexer cannot read: prose, output, another language.
FENCED_MAKE_RE = re.compile(r"^\s*make\s+(?P<name>[a-z][\w.-]*)")

# GitHub renders inline math from `$`...`$` (or `$...$`) and block math from a
# `$$` fence. It does not recognise LaTeX's `\(...\)` or `\[...\]`: `(` and
# `)` are ASCII punctuation, so CommonMark consumes the backslash as a
# character escape before any math parser runs, and `\(t\)` reaches the page
# as the literal text `(t)`. `docs/MODEL.md` carried 97 of them, its entire
# symbol table among them, and seven queue items had copied the form out of it
# (`PL-TH9V`).
#
# `\[...\]` reads the same whether it means display math or a literal bracket
# pair, and it stays a hard error either way (`PL-GPJ7`, decided 2026-09-26):
# the recognition is by these characters, which is exact; prose never needs
# the escape, since `[WIP]` renders as written where no link definition claims
# it and a code span carries any bracket; and a formula rendering as literal
# text in `docs/MODEL.md` is the failure an advisory would leave unread.
TEX_DELIMITER_RE = re.compile(r"\\[()\[\]]")

# The two halves of an inline expression, `$`...`$`, that is not well-formed:
# what `_without_code` leaves, having blanked every one that is. Inline math is
# parsed within a line, so an expression split by a line break renders as
# literal text on both sides. Four in this repository were split that way, one
# of them already on the correct delimiters and broken only by a paragraph
# reflow - which is why the rule is worth keeping after the conversion rather
# than only during it.
MATH_EDGE_RE = re.compile(r"\$`|`\$")


# Where CI's commands live. A workflow step names repository scripts by path
# exactly as the documentation does, and nothing was holding it to them.
WORKFLOW_GLOBS = (".github/workflows/*.yml", ".github/workflows/*.yaml")

# The line of a step's `run:` key, which `required_checks_check.steps` places:
# the key opens a step's shell, either inline or as a block scalar whose body is
# every following line indented past the key. Reading it this way rather than
# parsing YAML keeps this tool standard-library only, which is what lets a hook
# or a bare checkout run it. `lead` is everything before the key, so its length
# is the key's column, which a value's lines are indented past.
RUN_STEP_RE = re.compile(r"^(?P<lead>\s*-?\s*)run:\s*(?P<inline>.*)$")

# A token this check cannot resolve by reading the tree: a shell or GitHub
# expansion, a glob whose intended match is not stated, a URL, or an action
# reference. Skipped rather than guessed at - a checker that guesses at the
# judgment half is worse than no checker. The backquote is there because a
# word keeps a command substitution as written; its body is read on its own.
UNRESOLVABLE = ("$", "`", "*", "?", "://", "@")


@dataclass
class Report:
    """Findings, split by whether a machine or a human has to resolve them."""

    errors: list[str] = field(default_factory=list)
    advisories: list[str] = field(default_factory=list)
    # Checks this checkout could not run, each naming why. Kept apart from
    # advisories because they are the opposite claim: an advisory says
    # something was read and wants judgment, a decline says nothing was read
    # at all, and collapsing the two lets a check that never ran be reported
    # as one that passed (`PL-XCYB`, and `PL-J295` for the tag reader).
    declined: list[str] = field(default_factory=list)
    # What every session loads before it has read anything. Not a finding:
    # `format_check` prints it whether or not anything else fired, because the
    # number is the point rather than any verdict on it. `None` only when the
    # checkout holds no resident instruction file at all.
    resident: ResidentInstructions | None = None
    # Instruction text a session loads only on demand, measured the same way
    # and reported on its own line. Never added to `resident`: the two answer
    # different questions, and a single total would answer neither.
    on_demand: ResidentInstructions | None = None


@dataclass(frozen=True)
class ResidentFile:
    """One instruction file that loads at launch, measured both ways.

    `characters` is what every comparison here reads; `lines` is carried only
    to be printed beside it. Keeping both is what makes the choice of unit
    legible: `CLAUDE.md` holds 21% of its text on 6% of its lines, so the two
    numbers disagree about how large it is, and a reader shown one of them
    alone cannot tell that they do (`PL-QV1F`).
    """

    name: str
    characters: int
    lines: int
    #: `False` for a skill's description, which is payload but no instruction
    #: file. `CLAUDE.md`'s resident-growth series was taken on the instruction
    #: files alone, before `PL-44DG` added the descriptions and the digest to
    #: the total, so the printed line names that subtotal too (`PL-DXF0`).
    instruction_file: bool = True


@dataclass(frozen=True)
class ResidentInstructions:
    """The instruction files loaded at launch, measured, and against the base.

    Measured in characters. Lines were the first unit and were the wrong one:
    they put `.claude/rules/instruction-writing.md`, hard-wrapped so no line
    reaches 80 characters, and `CLAUDE.md`, whose longest line runs 893, on
    scales an order of magnitude apart - and inside an unwrapped paragraph
    they resolve nothing at all, because editing one moves no line. Of the 79
    commits that had moved this measurement by 2026-09-05, six reported exactly
    zero line growth and one of those six added 409 characters of instruction;
    eight moved 200 characters or more while moving at most two lines.
    Characters are also what the reasoning behind this check is about
    (`PL-H7XN`): how much a session loads before it has read anything is a
    quantity of text, not a count of newlines. `PL-QV1F` carries both.

    `baseline_ref` is the default branch this was compared against, and is
    `None` when no checkout could be read - a bare tree, no git, no default
    branch. The comparison is the part that goes missing then; the current
    total is still known, so it is still reported.
    """

    files: tuple[ResidentFile, ...]
    baseline_ref: str | None = None
    baseline_files: tuple[ResidentFile, ...] | None = None
    #: Payload measured by running something rather than by reading a file:
    #: today, the SessionStart hook's output. Counted in `total`, because a
    #: session carries it, and left out of every comparison, because no git
    #: ref can reproduce it - `git show <ref>:<path>` returns a hook's source,
    #: never its output, so there is no baseline to compare against and a row
    #: present on one side only would read as growth of its whole size, once,
    #: and then forever. Keeping it apart is what lets the printed total be
    #: true without making the advisory fire on a store that grew.
    runtime: tuple[ResidentFile, ...] = ()

    @property
    def total(self) -> int:
        """Characters a session actually carries, static payload and dynamic."""
        return self.comparable_total + sum(row.characters for row in self.runtime)

    @property
    def comparable_total(self) -> int:
        """The half a git ref can reproduce: the number every comparison reads."""
        return sum(row.characters for row in self.files)

    @property
    def instruction_total(self) -> int:
        """Characters in the instruction files alone, the basis of `CLAUDE.md`'s growth series."""
        return sum(row.characters for row in self.files if row.instruction_file)

    @property
    def total_lines(self) -> int:
        """Printed beside the total, never compared against it."""
        return sum(row.lines for row in (*self.files, *self.runtime))

    @property
    def baseline_total(self) -> int | None:
        if self.baseline_files is None:
            return None
        return sum(row.characters for row in self.baseline_files)

    @property
    def growth(self) -> int | None:
        """Movement in the comparable half alone. See `runtime`."""
        baseline = self.baseline_total
        return None if baseline is None else self.comparable_total - baseline

    def deltas(self) -> list[tuple[str, int]]:
        """Per-file character change against the baseline, largest growth first."""
        if self.baseline_files is None:
            return []
        before = {row.name: row.characters for row in self.baseline_files}
        after = {row.name: row.characters for row in self.files}
        names = sorted({*before, *after})
        changed = [(name, after.get(name, 0) - before.get(name, 0)) for name in names]
        return sorted((row for row in changed if row[1]), key=lambda row: -row[1])

    def material_deltas(self) -> list[tuple[str, int]]:
        """The per-file changes large enough to be a rule, not a wording fix.

        `MATERIAL_RESIDENT_DELTA` carries the measurement behind the floor.
        """
        return [row for row in self.deltas() if abs(row[1]) >= MATERIAL_RESIDENT_DELTA]


@dataclass(frozen=True)
class TreeMap:
    """One package-map tree, as drawn in `docs/ARCHITECTURE.md` or `docs/apparatus.md`."""

    root: PurePosixPath
    line: int
    files: frozenset[PurePosixPath]
    # Directories drawn without any children beneath them. Such an entry
    # stands for its whole subtree — a unit documented by its own README
    # rather than module by module — so files under it are covered without
    # being listed. No live tree draws one, so the two tests named in
    # `docs/apparatus.md` hold both directions of it; the mechanism is kept
    # because a subtree with its own documentation is the case it exists for.
    covered_dirs: frozenset[PurePosixPath]

    @property
    def entries(self) -> frozenset[PurePosixPath]:
        return self.files | self.covered_dirs


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _expand_braces(token: str) -> list[str]:
    """Expand `a/{x,y}.json` the way the trees and citations write it."""
    match = BRACE_RE.search(token)
    if match is None:
        return [token]
    expanded: list[str] = []
    for option in match.group(1).split(","):
        expanded.extend(_expand_braces(token[: match.start()] + option + token[match.end() :]))
    return expanded


def _walk(root: Path, under: str | PurePath = "") -> Iterator[Path]:
    """Yield every file the repository holds at or below `under`, skipping `IGNORED_DIRS`.

    Read from `tracked_files`, so another checkout under `.claude/worktrees/` is
    not read as this one: walking the disk, a broken quotation in a
    worktree-isolated agent's copy failed this check in the main checkout
    (`PL-2P5L`).
    """
    for path in tracked_under(root, under):
        if not IGNORED_DIRS.intersection(path.relative_to(root).parts):
            yield path


def parameter_data_files(root: Path) -> Iterator[Path]:
    """Yield each JSON file under the package's `data/` outside `NON_PARAMETER_DATA_DIRS`."""
    data_root = root / PACKAGE_ROOT / "data"
    for path in _walk(root, PACKAGE_ROOT / "data"):
        if path.suffix != ".json":
            continue
        if NON_PARAMETER_DATA_DIRS.intersection(path.relative_to(data_root).parts[:-1]):
            continue
        yield path


def read_docs(root: Path) -> dict[Path, str]:
    """Read every documentation file this tool holds to the tree."""
    documents: dict[Path, str] = {}
    for pattern in DOC_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                documents[path.relative_to(root)] = path.read_text(encoding="utf-8")
    return documents


def _fenced_blocks(text: str) -> Iterator[tuple[int, list[str]]]:
    """Yield each closed fenced block as its opening line's number and the lines inside it.

    Each line from where its own text starts, past the markers and indents of
    the block quotes and list items holding it (`markdown.Document.columns`),
    which is the text CommonMark gives the fence (0.31.2 § 4.5); and the last
    line of a fence its container's end closes is one of them, being content
    rather than a closing fence (`fences.Block.body`, `PL-D23H`). Read as
    written, a `make` command in a block-quoted fence was a redirection to a
    file named `make`, the line before its quote ended was dropped, and in a
    list item's fence a here-document's indented delimiter closed nothing, so a
    `make` line in its body was read as a command (`PL-5M36`).
    """
    lines = split_lines(text)
    columns = read_blocks(lines).columns
    for block in blocks(text):
        yield block.start + 1, [_from_column(lines[index], columns[index]) for index in block.body]


def _from_column(line: str, column: int) -> str:
    """`line` from its first character at or past `column`, its tabs read at four-column stops."""
    width = 0
    for index, character in enumerate(line):
        if width >= column:
            return line[index:]
        width = width + 4 - width % 4 if character == "\t" else width + 1
    return ""


def parse_tree(root: Path, start_line: int, block: list[str]) -> TreeMap | None:
    """Read one fenced block as a package-map tree, or decline it.

    A block is a tree when its first line is a lone directory path that
    exists. That is what separates the package maps from the layering and
    data-flow diagrams drawn in the same file with the same fence.
    """
    body = [line for line in block if line.strip()]
    if not body:
        return None
    match = TREE_ROOT_RE.match(body[0].strip())
    if match is None:
        return None
    tree_root = PurePosixPath(match.group("path").rstrip("/"))
    if not (root / tree_root).is_dir():
        return None

    files: set[PurePosixPath] = set()
    directories: set[PurePosixPath] = set()
    parents: set[PurePosixPath] = set()
    stack: list[str] = []

    for line in body[1:]:
        entry = TREE_ENTRY_RE.match(line)
        if entry is None:
            continue
        depth = len(entry.group("indent")) // 4
        name = entry.group("name")
        del stack[depth:]
        stack.append(name.rstrip("/"))
        for expanded in _expand_braces("/".join(stack)):
            path = tree_root / expanded
            if name.endswith("/"):
                directories.add(path)
            else:
                files.add(path)
            if depth:
                parents.add(path.parent)

    return TreeMap(
        root=tree_root,
        line=start_line,
        files=frozenset(files),
        covered_dirs=frozenset(directories - parents),
    )


def _mapped_candidates(root: Path, tree_root: PurePosixPath) -> list[PurePosixPath]:
    """Files under a mapped root that a package map is expected to account for."""
    base = root / tree_root
    return [
        tree_root / PurePosixPath(path.relative_to(base).as_posix())
        for path in _walk(root, tree_root)
        if path.suffix in MAPPED_SUFFIXES and path.name not in UNMAPPED_NAMES
    ]


def check_package_maps(root: Path, report: Report) -> None:
    """Hold each `PACKAGE_MAPS` document's trees to the tree on disk, both ways.

    Each document is read on its own and each must draw a tree, so one that
    loses its map fails rather than passing on the other's. Read from
    `docs/ARCHITECTURE.md` alone, as it was, the `tools/` tree would have gone
    unchecked the moment `PL-KRGY` moved it to `docs/apparatus.md`.
    """
    for document in PACKAGE_MAPS:
        _check_package_map(root, document, report)


def _check_package_map(root: Path, document: Path, report: Report) -> None:
    """Hold one document's trees to the tree on disk, both ways."""
    path = root / document
    if not path.is_file():
        report.errors.append(f"{document}: missing; the package map cannot be checked")
        return

    text = path.read_text(encoding="utf-8")
    trees = [
        tree
        for start, block in _fenced_blocks(text)
        if (tree := parse_tree(root, start, block)) is not None
    ]
    if not trees:
        report.errors.append(
            f"{document}: no package-map tree found; either the file lost its map or the "
            "tree format changed and this check has gone blind"
        )
        return

    for tree in trees:
        where = f"{document} (package map at line {tree.line})"

        for entry in sorted(tree.entries):
            if not (root / entry).exists():
                report.errors.append(f"{where}: lists {entry}, which does not exist")

        for candidate in _mapped_candidates(root, tree.root):
            if candidate in tree.files:
                continue
            if any(parent in tree.covered_dirs for parent in candidate.parents):
                continue
            report.errors.append(f"{where}: does not list {candidate}")


def _leaf_numbers(node: object, prefix: str = "") -> Iterator[tuple[str, float]]:
    """Yield every numeric leaf of a data file as `dotted.key`, value."""
    if isinstance(node, dict):
        for key, value in node.items():
            if not prefix and key in NON_PARAMETER_KEYS:
                continue
            yield from _leaf_numbers(value, f"{prefix}.{key}" if prefix else key)
    elif isinstance(node, bool):
        return
    elif isinstance(node, (int, float)):
        yield prefix, float(node)


def _lookup(document: object, key_path: str) -> float | None:
    node: object = document
    for key in key_path.split("."):
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    if isinstance(node, bool) or not isinstance(node, (int, float)):
        return None
    return float(node)


#: The provenance table's own header, which is what distinguishes it from any
#: other table in its section. Compared on the first three cells only: the
#: fourth names its separator character and that is a typographic choice.
PROVENANCE_HEADER = ("Parameter", "Selected value", "Unit")


def _provenance_rows(text: str) -> tuple[list[tuple[int, list[str]]], str]:
    """The provenance table's rows, found by its header rather than by position.

    `table_rows` yields the rows of the **first** table under a heading, and
    `## Parameter provenance` is over 500 lines of prose in this document - so
    any table written anywhere above the real one displaced it, and the check
    then walked the wrong rows and reported one missing-row error per stored
    constant. Every one of those errors is true of the table it read and false
    of the document, and the remedy they suggest is to add rows, which would
    put parameter rows into a citation list (`PL-ZBZZ`, `PL-K997`: eleven
    errors on 2026-09-10 and twenty-nine on 2026-09-07, each costing a session
    the same diagnosis and each resolved by not writing a table).

    Returns the rows and an empty note, or no rows and a note saying what was
    found instead. Fixed here at the call site rather than in `table_rows`,
    which `parse_version_table`, `parse_timeline` and `parse_milestones` all
    share.

    The section and its tables are `markdown`'s, as `table_rows` reads them, so
    a line a fence or a comment holds is neither a heading nor a row. Matched a
    line at a time, a shell sample's `## a shell comment` ended the section
    above the table, and the check reported no table at all (`PL-0Y7J`).
    """
    lines = split_lines(text)
    opening = next(
        (
            heading
            for heading in read_headings(lines)
            if heading.level <= 2 and heading.title == "Parameter provenance"
        ),
        None,
    )
    if opening is None:
        return [], ""
    end = _section_end(lines, opening.end)
    tables = [table for table in read_tables(lines) if opening.line < table.line < end]
    for table in tables:
        if table.header[:3] == PROVENANCE_HEADER and table.rows:
            return [(index + 1, list(cells)) for index, cells in table.rows], ""
    seen = [" | ".join(table.header) for table in tables if table.header[:3] != PROVENANCE_HEADER]
    if seen:
        return [], (
            f"the {len(seen)} table(s) under 'Parameter provenance' carry no provenance "
            f"header; the first reads `{seen[0]}`, where "
            f"`{' | '.join(PROVENANCE_HEADER)} | ...` was expected. A table written above "
            "the provenance table displaces it - move it below, or into a subsection of "
            "its own"
        )
    return [], ""


def check_provenance(root: Path, report: Report) -> None:
    """Hold `docs/MODEL.md`'s provenance table to the data files, both ways.

    Each row names the data file and the key path it documents, so a row is
    checked against the value that key actually holds rather than against
    whichever number in the file happens to match. A derived row states the
    stored value alongside the derived one (`1.6923 (= 1.1 / 0.65)`), so the
    stored value is required to appear in the cell, not to be the whole of it.
    """
    path = root / MODEL
    if not path.is_file():
        report.errors.append(f"{MODEL}: missing; the provenance table cannot be checked")
        return

    documented: dict[tuple[str, str], int] = {}
    rows, note = _provenance_rows(path.read_text(encoding="utf-8"))
    if not rows:
        report.errors.append(
            f"{MODEL}: {note}"
            if note
            else (
                f"{MODEL}: no provenance table found under 'Parameter provenance'; either "
                "the table moved or its format changed and this check has gone blind"
            )
        )
        return

    for line, cells in rows:
        where = f"{MODEL} (line {line})"
        if len(cells) < 4:
            report.errors.append(f"{where}: provenance row has {len(cells)} cells, expected 4")
            continue

        parameter, value_cell, _unit, source_cell = cells[0], cells[1], cells[2], cells[3]
        spans = [span["content"] for span in code_spans(source_cell)]
        if len(spans) != 2:
            report.errors.append(
                f"{where}: {parameter!r} names {len(spans)} code spans in its source cell; "
                "expected the data file and the JSON key path it documents"
            )
            continue

        relative, key_path = spans
        data_path = root / PACKAGE_ROOT / relative
        if not data_path.is_file():
            report.errors.append(f"{where}: {parameter!r} cites {relative}, which does not exist")
            continue

        document = json.loads(data_path.read_text(encoding="utf-8"))
        stored = _lookup(document, key_path)
        if stored is None:
            report.errors.append(
                f"{where}: {parameter!r} names key {key_path!r}, which {relative} does not "
                "hold as a number"
            )
            continue

        key = (relative, key_path)
        if key in documented:
            report.errors.append(
                f"{where}: {relative} {key_path} already has a row at line {documented[key]}; "
                "each constant is documented once"
            )
            continue
        documented[key] = line

        stated = [float(number) for number in NUMBER_RE.findall(value_cell)]
        if stored not in stated:
            report.errors.append(
                f"{where}: {parameter!r} states {value_cell!r} but {relative} holds "
                f"{key_path} = {stored:g}"
            )

    data_root = root / PACKAGE_ROOT / "data"
    if not data_root.is_dir():
        return
    for data_path in parameter_data_files(root):
        relative = PurePosixPath(data_path.relative_to(root / PACKAGE_ROOT).as_posix())
        document = json.loads(data_path.read_text(encoding="utf-8"))
        for key_path, value in _leaf_numbers(document):
            if (str(relative), key_path) not in documented:
                report.errors.append(
                    f"{MODEL}: no provenance row for {relative} {key_path} = {value:g}; "
                    "every constant a clinician could read belongs in the table"
                )


def _short_citation(entry: object) -> str:
    """Enough of a citation to find the entry by eye, or a placeholder."""
    if isinstance(entry, dict):
        citation = entry.get("citation")
        if isinstance(citation, str) and citation.strip():
            trimmed = citation.strip()
            return trimmed if len(trimmed) <= 60 else trimmed[:57] + "..."
    return "(no citation)"


def check_source_tiers(root: Path, report: Report) -> None:
    """Hold every data file's `sources` to `docs/MODEL.md` § "Source hierarchy".

    Six rules, all exact, and all about what a file *declares* rather than
    about whether the declaration is true:

    1. Every `sources` entry names a `tier` from the closed vocabulary and
       says whether it is `adopted` - whether this file takes it as the
       authority for a value it stores.
    2. A file with no entry that is both `primary` and `adopted` records a
       `provenance_gap` saying so. That is the third of the section's three
       rules: where no primary source has been adopted, the absence is
       recorded rather than left to be read as an oversight.
    3. Every entry carries `authority_for`, a list naming the stored values
       it is the authority for by dotted key path, each a nonempty string
       named once.
    4. `adopted` is true exactly when `authority_for` is not empty.
    5. Each path names a stored value of the same file: a numeric leaf as
       `_leaf_numbers` reads it, the set `check_provenance` holds the table to.
    6. No stored value is named by two entries of one file.

    Rules 3 to 6 repeat the loader's in `core/parameters.py`, so a checkout
    with no virtualenv still checks them. They are what makes the tier of each
    stored value readable from the files, which `tools/source_tier_counts.py`
    prints, and it prints nothing while this check fails (`PL-9LXK`). A stored
    value no entry names is not an error: it adopts no source.

    **The tier and the adoption are separate fields because rule 2 is
    otherwise vacuous.** Every agent file cites primary measurements it has
    explicitly *not* adopted, and so does the reference patient - so a check
    reading tier alone passes all four of this project's data files today
    while every stored coefficient in them came from Gas Man, which is the
    second of the same three rules stated as the failure it exists to
    prevent.

    **What this deliberately does not decide** is whether a citation declared
    `primary` really is a primary measurement of the quantity, which needs
    somebody who has read the paper. A tool guessing at that - by author, by
    journal, by a denylist on a product name - would be authoritative and
    wrong, which `CLAUDE.md` names as worse than no tool at all. This is the
    same split `check_provenance` already runs on: it decides that a
    documented key exists and holds the stated value, never that the value is
    right.
    """
    data_root = root / PACKAGE_ROOT / "data"
    if not data_root.is_dir():
        return

    for data_path in parameter_data_files(root):
        relative = data_path.relative_to(root / PACKAGE_ROOT).as_posix()
        document = json.loads(data_path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            report.errors.append(f"{relative}: is not a JSON object")
            continue

        sources = document.get("sources")
        if not isinstance(sources, list) or not sources:
            report.errors.append(
                f"{relative}: declares no `sources` array; every data file names where its "
                "values came from"
            )
            continue

        stored_values = {key_path for key_path, _value in _leaf_numbers(document)}
        named_by: dict[str, int] = {}
        adopted_primary = False
        for index, entry in enumerate(sources):
            where = f"{relative} sources[{index}] ({_short_citation(entry)})"
            if not isinstance(entry, dict):
                report.errors.append(f"{where}: is not an object")
                continue

            tier = entry.get("tier")
            if tier not in SOURCE_TIERS:
                report.errors.append(
                    f"{where}: declares tier {tier!r}; expected one of {list(SOURCE_TIERS)} "
                    "(docs/MODEL.md, 'Source hierarchy')"
                )

            adopted = entry.get("adopted")
            if not isinstance(adopted, bool):
                report.errors.append(
                    f"{where}: declares adopted {adopted!r}; expected true or false - whether "
                    "this file names the source as the authority for a value it stores, which "
                    "is a different question from what tier the source is"
                )

            if tier == "primary" and adopted is True:
                adopted_primary = True

            paths = entry.get("authority_for")
            if not isinstance(paths, list):
                report.errors.append(
                    f"{where}: declares authority_for {paths!r}; expected a list of the dotted "
                    "key paths of the stored values this file takes the source as the authority "
                    "for, empty where it adopts it for none (docs/MODEL.md, 'Source hierarchy')"
                )
                continue
            if adopted is True and not paths:
                report.errors.append(
                    f"{where}: is adopted but its authority_for is empty; name the stored values "
                    "it is the authority for, or declare it not adopted (docs/MODEL.md, "
                    "'Source hierarchy')"
                )
            elif adopted is False and paths:
                report.errors.append(
                    f"{where}: is not adopted but its authority_for is not empty; a source is "
                    "the authority for a stored value only where the file adopts it "
                    "(docs/MODEL.md, 'Source hierarchy')"
                )
            named: set[str] = set()
            for path in paths:
                if not isinstance(path, str) or not path:
                    report.errors.append(
                        f"{where}: authority_for holds {path!r}; each entry is the dotted key "
                        "path of a stored value, as a nonempty string"
                    )
                elif path in named:
                    report.errors.append(f"{where}: authority_for names {path!r} twice")
                elif path not in stored_values:
                    report.errors.append(
                        f"{where}: authority_for names {path!r}, which is not one of "
                        f"{relative}'s stored values - the numbers its provenance-table rows "
                        "name, by the same key path"
                    )
                elif path in named_by:
                    first = named_by[path]
                    report.errors.append(
                        f"{where}: authority_for names {path!r}, which sources[{first}] "
                        f"({_short_citation(sources[first])}) already names; a stored value has "
                        "one adopted authority, or it would be counted under two tiers"
                    )
                else:
                    named_by[path] = index
                if isinstance(path, str):
                    named.add(path)

        gap = document.get("provenance_gap")
        if gap is not None and not (isinstance(gap, str) and gap.strip()):
            report.errors.append(
                f"{relative}: provenance_gap is present but is not a nonempty string; state the "
                "gap or remove the key"
            )
        elif not adopted_primary and gap is None:
            report.errors.append(
                f"{relative}: no `sources` entry is both tier 'primary' and adopted, and the "
                "file records no `provenance_gap`. docs/MODEL.md, 'Source hierarchy', third "
                "rule: where no primary source has been adopted, record that as an open gap "
                "rather than leaving the silence to be read as a settled citation"
            )


def _is_marker(text: str) -> bool:
    """Whether `text` is a marker line: `provenance:`, `derived:` or `absent:`."""
    stripped = text.strip()
    return any(rule.match(stripped) for rule in (PROSE_MARKER_RE, ABSENT_MARKER_RE))


def _split_marker(document: Path, line: int, kind: str) -> str:
    """What a marker split across lines is told; see `_split_markers`."""
    return (
        f"{document}:{line}: this `{kind}:` marker does not close on its line; a marker is "
        "read a line at a time, so this one was read as nothing - write it on one line"
    )


def _split_markers(lines: Sequence[str]) -> dict[int, str]:
    """Each marker split across lines, by the index of the line it opens on, with its kind.

    A comment is read as the HTML block it is (CommonMark 0.31.2 § 4.6), so a
    marker whose `<!--` stands alone on the line above its kind is split as
    one broken after its kind is: read a line at a time it was nothing, and the
    value or the absence it declared went unchecked (`PL-GT0J`).
    `SPLIT_MARKER_RE` still reads a line on its own, for the comment nothing
    closes, which the block reader reads as the paragraph it is written as. A
    line inside a longer comment is that comment's and opens no marker, as
    `_marker_lines` reads a complete one (`PL-7454`).
    """
    split: dict[int, str] = {}
    inside: set[int] = set()
    if any("<!--" in line for line in lines):
        for block in read_blocks(lines).blocks:
            if block.kind != HTML or block.end - block.start < 2:
                continue
            inside.update(range(block.start + 1, block.end))
            comment = "\n".join(line.strip() for line in lines[block.start : block.end])
            if (opening := MARKER_OPENING_RE.match(comment)) is not None:
                split[block.start] = opening.group("kind")
    for index, line in enumerate(lines):
        if index in inside:
            continue
        if (opening := SPLIT_MARKER_RE.match(line.strip())) is not None:
            split.setdefault(index, opening.group("kind"))
    return split


def _misplaced_markers(lines: Sequence[str], prose: Sequence[str]) -> dict[int, str]:
    """Each marker written where it is not read, by the index of its line, with its kind.

    A marker is read only where it is a line of its own that opens an HTML
    block (`_marker_lines`). CommonMark also reads the comment at a sentence's
    end, as inline raw HTML (0.31.2 § 6.6), and inside a block quote or a list
    item, as an HTML block in that container (§ 5.1, § 5.2). Read as nothing
    there, a marker beside a well-formed one elsewhere let a stale value in
    `docs/MODEL.md`'s prose pass (`PL-Y6LP`), so each is refused by name.

    `prose` is `lines` with code blanked (`_without_code`), so a marker quoted
    in a code span or shown in a fence is no marker. A line inside a longer
    comment is that comment's (`PL-7454`), and a marker split across lines is
    `_split_markers`' to report.
    """
    if not any("<!--" in line for line in lines):
        return {}
    inside = {
        index
        for block in read_blocks(lines).blocks
        if block.kind == HTML
        for index in range(block.start + 1, block.end)
    }
    openings = _marker_lines(lines)
    split = _split_markers(lines)
    misplaced: dict[int, str] = {}
    for index, line in enumerate(lines):
        opening = MARKER_OPENING_RE.search(prose[index]) if index < len(prose) else None
        if opening is None or index in inside or index in split:
            continue
        if index in openings and _is_marker(line):
            continue
        misplaced[index] = opening.group("kind")
    return misplaced


def _misplaced_marker(document: Path, line: int, kind: str) -> str:
    """What a marker `_misplaced_markers` finds is told."""
    return (
        f"{document}:{line}: this `{kind}:` marker does not stand on a line of its own - it "
        "ends a sentence, sits in a block quote or list item, or shares its line - and a "
        "marker is read only on a line of its own, so this one was read as nothing; move it "
        "onto a line of its own under its paragraph"
    )


def _marker_lines(lines: Sequence[str]) -> frozenset[int]:
    """The index of each line a marker can stand on: one that opens an HTML block.

    A comment is an HTML block from its `<!--` to the first line holding a
    `-->` (CommonMark 0.31.2 § 4.6), so a complete marker written under a
    comment opened above it - a paragraph and its marker set aside together -
    is that comment's last line, and the page renders neither. Read a line at
    a time, it was held to its data file, or marked a path absent, as a marker
    a reader is shown (`PL-7454`).
    """
    if not any("<!--" in line for line in lines):
        return frozenset()
    return frozenset(block.start for block in read_blocks(lines).blocks if block.kind == HTML)


def _marked_span(lines: Sequence[str], index: int) -> tuple[int, int]:
    """The prose block a marker sits under, as a half-open range of `lines`.

    Blank lines between them are allowed. Attaching to what *precedes* the
    marker rather than what follows it is what lets the marker be added without
    moving the sentence it is about, and it reads the way a footnote does.

    The block is the one `markdown` reads as ending there, so a paragraph begins
    after a list item's start, a heading or a table as well as after a blank
    line (CommonMark 0.31.2 § 4.8, § 5.2). Taken as every non-blank line above,
    a neighbouring item's or heading's number satisfied a marker its own
    paragraph failed, and a stray backtick there hid the paragraph's own
    citation (`PL-JZNV`). Where the block above holds no prose - an indented
    code block, an HTML block - the span is empty, so the marker is held to
    nothing it could pass on.
    """
    # Back over blank lines *and* over sibling markers: one paragraph often
    # restates values from several data files, which is several markers, and
    # stopping at the first would hand every marker but the nearest an empty
    # block to check against - passing silently, which is the one failure this
    # check may not have.
    end = index
    while end > 0 and (not lines[end - 1].strip() or _is_marker(lines[end - 1])):
        end -= 1
    for block in read_blocks(lines).blocks:
        if block.end == end and block.kind in PROSE:
            return block.start, end
    return end, end


def _marked_block(lines: list[str], index: int) -> str:
    """The run of prose a marker sits under, joined; see `_marked_span`."""
    start, end = _marked_span(lines, index)
    return "\n".join(lines[start:end])


def _marker_assertions(
    body: str, where: str, root: Path, report: Report
) -> list[tuple[str, str, float, float]] | None:
    """Each `key = value` a marker states, paired with what the file holds.

    `None` where the marker itself could not be read, which is reported as an
    error rather than skipped: a marker nobody can parse is a claim nobody is
    checking, and silence about it would leave the prose looking guarded.
    """
    source = MARKER_SOURCE_RE.match(body)
    if source is None:
        report.errors.append(
            f"{where}: expected `<data file>.json <key> = <value>, ...`, found {body!r}"
        )
        return None

    relative = source.group("relative")
    data_path = root / PACKAGE_ROOT / relative
    if not data_path.is_file():
        report.errors.append(f"{where}: cites {relative}, which does not exist")
        return None
    document = json.loads(data_path.read_text(encoding="utf-8"))

    resolved: list[tuple[str, str, float, float]] = []
    for clause in source.group("assertions").split(","):
        assertion = ASSERTION_RE.match(clause.strip())
        if assertion is None:
            report.errors.append(f"{where}: expected `<key> = <value>`, found {clause.strip()!r}")
            return None
        key_path = assertion.group("key")
        stated = float(assertion.group("value"))
        stored = _lookup(document, key_path)
        if stored is None:
            report.errors.append(
                f"{where}: names key {key_path!r}, which {relative} does not hold as a number"
            )
            return None
        resolved.append((relative, key_path, stated, stored))
    return resolved


def check_prose_provenance(root: Path, report: Report) -> None:
    """Hold `docs/MODEL.md`'s *prose* values to the data files, as the table is.

    `check_provenance` reads only the provenance table. The same constants are
    restated in the surrounding prose - the reference adult's alveolar volume
    and ventilation, each agent's blood:gas coefficient, vaporizer maximum and
    MAC - and editing a data file updated the table, which the check forces,
    while leaving those sentences quietly wrong (`PL-1BPV`).

    That is a safety failure rather than untidiness, by this project's own
    standard: a reader who trusts "37.5 s for the reference adult" is reading a
    number for a patient the simulator may no longer ship, and the polish of
    the surrounding document is what makes it credible.

    Every marker's keys are checked against the file. A `provenance:` marker is
    additionally held to the prose it sits under, so the two can drift from
    neither side: the data file moving trips the first check, and the sentence
    being reworded without the marker trips the second. A `derived:` marker
    states the inputs a computed figure came from, and moving any of them
    reports that the figure needs recomputing - by a person, which is where
    the line between the decidable half and the judgment half falls.

    A marker is read where its line opens an HTML block (`_marker_lines`), so
    one closing a comment opened above it is that comment's, set aside with
    the paragraph it was about, and is held to nothing (`PL-7454`). One written
    anywhere else - at a sentence's end, in a block quote - is refused by name
    (`_misplaced_markers`, `PL-Y6LP`).
    """
    path = root / MODEL
    if not path.is_file():
        return  # `check_provenance` has already reported the missing document.

    text = path.read_text(encoding="utf-8")
    lines = split_lines(text)
    fenced = _fenced_lines(text)
    split = {index: kind for index, kind in _split_markers(lines).items() if kind != "absent"}
    openings = _marker_lines(lines)
    for index, kind in _misplaced_markers(lines, _without_code(text)).items():
        if kind != "absent":
            report.errors.append(_misplaced_marker(MODEL, index + 1, kind))
    markers = 0
    for index, line in enumerate(lines):
        # A marker inside a code fence is the format being *shown*, not a claim
        # being made - the section below documents the convention by printing
        # one. Reading it as a claim would force every example to be
        # coincidentally true of the shipped data.
        if index in fenced:
            continue
        if index in split:
            report.errors.append(_split_marker(MODEL, index + 1, split[index]))
            continue
        if index not in openings:
            continue
        match = PROSE_MARKER_RE.match(line.strip())
        if match is None:
            continue
        markers += 1
        where = f"{MODEL} (line {index + 1})"
        kind, body = match.group("kind"), match.group("body")

        figure = ""
        if kind == "derived":
            derived = DERIVED_FROM_RE.match(body)
            if derived is None:
                report.errors.append(
                    f"{where}: a `derived:` marker reads `<figure> from <data file>.json "
                    f"<key> = <value>, ...`; this one is {body!r}"
                )
                continue
            figure, body = derived.group("figure"), derived.group("rest")

        resolved = _marker_assertions(body, where, root, report)
        if resolved is None:
            continue

        block = _marked_block(lines, index)
        in_prose = {float(number) for number in NUMBER_RE.findall(block)}

        for relative, key_path, stated, stored in resolved:
            if stated != stored:
                if kind == "derived":
                    report.errors.append(
                        f"{where}: {figure} was computed from {relative} {key_path} = {stated:g}, "
                        f"but the file now holds {stored:g}; recompute the figure and update "
                        "both it and this marker"
                    )
                else:
                    report.errors.append(
                        f"{where}: states {key_path} = {stated:g} but {relative} holds "
                        f"{stored:g}; update the prose above and this marker together"
                    )
                continue
            if kind == "provenance" and stated not in in_prose:
                report.errors.append(
                    f"{where}: claims the prose above restates {relative} {key_path} = "
                    f"{stated:g}, and that number is not in it; the sentence was reworded "
                    "without its marker, or the marker is attached to the wrong paragraph"
                )

        if kind == "derived":
            wanted = [float(number) for number in NUMBER_RE.findall(figure)]
            if wanted and wanted[0] not in in_prose:
                report.errors.append(
                    f"{where}: names the derived figure {figure!r}, which is not in the prose "
                    "above; the marker is attached to the wrong paragraph"
                )

    if not markers:
        report.errors.append(
            f"{MODEL}: no `<!-- provenance: ... -->` or `<!-- derived: ... -->` markers found; "
            "either every marked value was removed or the format changed and this check has "
            "gone blind"
        )


def check_timeline(root: Path, report: Report) -> None:
    """Hold `ROADMAP.md`'s release train to a shape a tool can read."""
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    if not roadmap.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")

    steps, problems = parse_timeline(text)
    report.errors.extend(f"{roadmap_name}: {problem}" for problem in problems)
    if not steps and not problems:
        # The table is the mechanism, not decoration: losing it to a rename or
        # a reformat would leave every reader of the plan with nothing, and
        # would do it silently.
        report.errors.append(f'{roadmap_name}: no timeline table found under "{TIMELINE_HEADING}"')
        return
    if steps and not any(step.kind == "milestone" for step in steps):
        report.errors.append(f"{roadmap_name}: the timeline names no milestone version")


def check_milestone_lists(root: Path, report: Report) -> None:
    """Fail each frozen-list or `Required scope` entry docket could not read whole.

    docket reads a milestone's gate and scope an entry at a time, through
    `list_entry_lines`, and that walker declines an entry carried on by a line
    with no indent, which CommonMark reads as part of the entry and the walker
    cannot (`PL-MFVV`). It records the line on `MilestoneSection.unread` rather
    than raising, so `wave` still counts what it could read and says the rest
    was not; this is where the line fails, so a plan read short never reaches
    `main`.
    """
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    if not roadmap.is_file():
        return
    for section in parse_milestones(roadmap.read_text(encoding="utf-8")):
        rendered = "v{}.{}.{}".format(*section.version)
        report.errors.extend(
            f"{roadmap_name}:{entry.line}: a list entry of the {rendered} section was not read "
            f"whole, so the gate and scope docket reads there may be short: {entry.why}"
            for entry in section.unread
        )


def check_baseline(root: Path, report: Report) -> None:
    """Hold the three statements of the current version to each other.

    `ROADMAP.md` calls itself the authoritative version and milestone map, and
    every release note, gate record and milestone claim is anchored to it. It
    says which version is current in two places - one row of the version table
    and the heading below it - and `pyproject.toml` says it in a third. A
    release bumps the third and leaves the other two behind, which has now
    happened twice, the second time one release after the first was repaired.

    This refuses rather than writes. The milestone column is editorial prose,
    and a generated row would either be thin or would overwrite something
    considered; refusing costs the owner one hand-written row per release and
    cannot corrupt the file. Whether those versions carry tags is `check_tags`
    below, which reads git and therefore has to stay silent when git cannot
    answer; this one compares three statements already in the tree and can run
    anywhere.
    """
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    version_name = load_docket_config(root).version_file
    version_file = root / version_name
    if not roadmap.is_file() or not version_file.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")

    rows = parse_version_table(text)
    if not rows:
        report.errors.append(
            f'{roadmap_name}: no version table found under "{VERSION_TABLE_HEADING}"'
        )
        return

    seen: dict[str, int] = {}
    for row in rows:
        if row.version in seen:
            report.errors.append(
                f"{roadmap_name}:{row.line}: v{row.version} already has a row at line "
                f"{seen[row.version]}; one row per released version"
            )
        seen.setdefault(row.version, row.line)

    marked = [row for row in rows if row.is_baseline]
    if len(marked) != 1:
        where = ", ".join(f"line {row.line}" for row in marked) or "no row"
        report.errors.append(
            f'{roadmap_name}: {len(marked)} rows are marked "{BASELINE_MARK}" ({where}); '
            "exactly one release is current"
        )
        return

    declared = _project_version(
        version_file, report, "the current baseline row was not held to the version it declares"
    )
    if declared and marked[0].version != declared:
        report.errors.append(
            f"{roadmap_name}:{marked[0].line}: the current baseline row is v{marked[0].version}, "
            f"but {version_name} holds {declared}"
        )

    heading = baseline_heading(text)
    if heading is None:
        report.errors.append(f'{roadmap_name}: no "Current baseline: vX.Y.Z" heading')
    elif heading[1] != marked[0].version:
        report.errors.append(
            f"{roadmap_name}:{heading[0]}: the baseline heading names v{heading[1]}, but the "
            f"table marks v{marked[0].version} current"
        )


# --- the counts a frozen list states about itself ---------------------------

#: How `ROADMAP.md` writes a small number. Digits are read too, because the
#: file uses both and which one a writer reached for says nothing about what
#: the number means.
_UNITS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)
_TENS = ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")

# A stated count of entries: `thirty-seven entries`, `20 entries`. The word
# before `entries` is read as a number and the phrase is passed over when it is
# not one, so "no entries" and "the remaining entries" state no count and are
# left alone rather than reported.
ENTRY_COUNT_RE = re.compile(r"(?P<count>[\w-]+)\s+entries\b")

# A group heading inside a frozen list: an emphasized line whose label is
# followed by a dash and then the count of what comes after it, as in
# `*Stops new debt being introduced - fifteen entries:*`. The count has to sit
# on the far side of the dash, where a heading puts it, which is what keeps a
# paragraph *about* some entries - "Four entries added 2026-08-30 from an
# outside review of the repository" - from being read as a heading over them.
# And it has to sit inside the emphasis the line opens with, as CommonMark
# pairs it: `*Note.* This list was frozen - three entries were admitted later`
# is a paragraph whose emphasis closes before its count (`PL-8NPN`).
#
# `entry` is accepted beside `entries` so that a group holding exactly one can
# be written in English (`PL-L0K3`). Requiring the plural left a post-freeze
# addition of a single item with two bad options and no good one: write "1
# entries", or omit the count, in which case this stops recognizing the line as
# a heading at all and silently attributes the entry to the group above it. The
# narrower `ENTRY_COUNT_RE` below is deliberately left plural-only - it scans
# ordinary prose, where "the one entry in it a user cannot set" is a sentence
# and not a claim about a list's size.
GATE_GROUP_RE = re.compile(
    r"^\*{1,2}.*?(?:\u2014|\s-\s)\s*(?P<entries>[\w-]+)\s+entr(?:y|ies)\b"
    r"(?:,\s*(?P<ids>[\w-]+)\s+item ids?)?"
)

# A frozen list's count of the entries *withheld from delegation*, as in
# `**Seven entries are marked `not-delegable`,**`. Unlike the two counts beside
# it in `check_gate_counts`, this one states a property of the entries rather
# than the list's length - and it is checkable for one reason only: `docket`
# reads `not-delegable:` off each item, so the number is a query over fields
# that already exist rather than a judgment about what an entry's work touches.
#
# `PL-GLBF` is where the line between the two was drawn, and it is worth having
# in front of whoever extends this. The same section's "Three entries reach into
# `src/`" looks equally checkable and is not: the nearest field, `touches:`,
# records the files an item is *expected to change*, where the sentence records
# the scope an item is *permitted to reach*. On that section's own three ids a
# checker over `touches:` computes two against a correct three, because
# `PL-ZN0N` may annotate `noqa` directives in `src/` without planning to edit a
# file there. A check built on the near-miss field would fail a correct
# sentence, which is worse than no check.
#
# Read only inside the gate subsection, so position fixes the meaning the way
# it does for the group headings above: a sentence in one section counting
# another section's list would otherwise be compared against the wrong list.
NOT_DELEGABLE_COUNT_RE = re.compile(
    rf"(?P<count>[\w-]+){GAP}entr(?:y|ies){GAP}(?:is|are){GAP}marked{GAP}`not-delegable`"
)

# An entry count stated in a *heading*, singular accepted: `- 13 entries`,
# `- 1 entry`. Separate from `ENTRY_COUNT_RE` above, which scans prose and is
# plural-only so that "the one entry in it a user cannot set" stays a sentence.
# A heading holds no sentences, so the singular is a count there, and reading
# it is what stops a one-entry subsection being the way round the rule.
HEADING_ENTRY_COUNT_RE = re.compile(r"(?P<count>[\w-]+)\s+entr(?:y|ies)\b")


def _count_word(word: str) -> int | None:
    """The number a count word states, or `None` where it states none."""
    token = word.strip().casefold()
    if token.isdigit():
        return int(token)
    if token in _UNITS:
        return _UNITS.index(token)
    tens, _, unit = token.partition("-")
    if tens in _TENS:
        base = (_TENS.index(tens) + 2) * 10
        if not unit:
            return base
        if unit in _UNITS[1:10]:
            return base + _UNITS.index(unit)
    return None


@dataclass(frozen=True)
class _GateGroup:
    """One count-carrying group heading of a frozen list, and the entries under it."""

    line: int
    #: The heading as one line, emphasis and all, however many it wraps across.
    heading: str
    stated: int
    stated_ids: int | None
    entries: tuple[GateEntry, ...]


def _gate_groups(lines: Sequence[str], section: MilestoneSection) -> Iterator[_GateGroup]:
    """Each count-carrying group heading of a frozen list, and what follows it.

    Yields the heading's line and text, the counts it states, and the entries
    between it and the next such heading. A heading stating no readable count
    is not one of these and is passed over: it groups the list without
    claiming a size, which is a shape the file already uses.

    A heading is read as the statement it is, from its line on through every
    line a soft break carries it onto (`PL-R417`): a label wrapped before its
    count was read as a heading stating none, and the entries under it went to
    the group above. And only a statement opens one, as `statement_lines`
    reads it, so an emphasis run a soft break carries onto a line's start is
    its paragraph's own text rather than a heading (`PL-VQBY`). Its extent is
    the span `statement_lines` gives it too: read by a pattern refusing every
    ordered marker, a heading wrapped before a year such as `2026.` was cut
    there, and a correct list failed its counts (`PL-V7CG`).
    """
    end = _subsection_end(lines, section.gate_line)
    blanked = unmarked(lines)
    headings: list[tuple[int, str, int, int | None]] = []
    for index, stop in statement_lines(lines):
        if not section.gate_line <= index < end or not lines[index].startswith("*"):
            continue  # what `GATE_GROUP_RE` opens with, so no other line is one
        heading = _normalized("\n".join(blanked[index:stop]))
        match = GATE_GROUP_RE.match(heading, 0, _opening_emphasis_end(heading))
        if match is None:
            continue
        stated = _count_word(match.group("entries"))
        if stated is None:
            continue
        ids = match.group("ids")
        headings.append((index + 1, heading, stated, _count_word(ids) if ids else None))

    for position, (line, heading, stated, stated_ids) in enumerate(headings):
        following = headings[position + 1][0] if position + 1 < len(headings) else end + 1
        covered = tuple(entry for entry in section.gate_entries if line < entry.line < following)
        yield _GateGroup(line, heading, stated, stated_ids, covered)


def _opening_emphasis_end(statement: str) -> int:
    """Where the emphasis opening `statement` closes, as § 6.2 pairs it, or 0 where none opens it.

    Its code spans are `_InlineReader`'s, so a delimiter inside one pairs with
    nothing.
    """
    reader = _InlineReader(statement)
    reader.read(0, len(statement))
    spans = emphasis(statement, [span.span() for span in reader.spans])
    return max((span.end for span in spans if span.start == 0), default=0)


def _uncheckable_heading_counts(
    lines: Sequence[str], section: MilestoneSection
) -> Iterator[tuple[int, int]]:
    """Every entry count written into a heading of a section that records a gate.

    `check_gate_counts` reads two positions and can read no others: an
    emphasized group heading inside the frozen list, and a table cell naming
    the release. A heading is neither, and cannot become one - `_gate_groups`
    matches `GATE_GROUP_RE`, which requires the line to open with `*`, and
    `_subsection_end` stops the frozen list at the first `###`, which puts
    every subsection heading below the gate outside the only range it reads.

    So a count written into a heading is held by nothing while reading exactly
    like the ones that are held. These are refused rather than reconciled,
    because the position that would make one checkable already exists one line
    below it, and because a subsection's record is its entries: `PL-4RHP` is
    the heading that carried a number through twenty hand edits to 228 against
    128 entries listed, was filed three times as a defect, and validated
    identically at `174`, `191` and `999`.

    A heading is one `markdown` reads, so a `###` line inside a fence or a
    comment states no count (`PL-0Y7J`).
    """
    end = _section_end(lines, section.line)
    for heading in read_headings(lines):
        if not section.line <= heading.line < end or heading.level < 3:
            continue
        match = HEADING_ENTRY_COUNT_RE.search(heading.title)
        if match is None:
            continue
        stated = _count_word(match.group("count"))
        if stated is not None:
            yield heading.line + 1, stated


def _table_counts(text: str, section: MilestoneSection) -> Iterator[tuple[int, str, int]]:
    """Every entry count the two tables state about one release's frozen list.

    Only a row whose *own* naming cell is this release is read, so the v0.3.0
    row saying what Gate 0 holds - a list recorded under v0.4.0 - is not read
    as a claim about v0.3.0, which records no list at all.
    """
    rendered = "v{}.{}.{}".format(*section.version)
    for where, heading, level, naming in (
        ("version table", VERSION_TABLE_HEADING, 2, 0),
        ("timeline", TIMELINE_HEADING, 3, 1),
    ):
        for line, cells in table_rows(text, heading, level=level):
            if len(cells) <= naming or rendered not in cells[naming]:
                continue
            for cell in cells[naming + 1 :]:
                for match in ENTRY_COUNT_RE.finditer(cell):
                    stated = _count_word(match.group("count"))
                    if stated is not None:
                        yield line, where, stated


@dataclass(frozen=True)
class _Store:
    """The queue read once: its configuration, and its items by id.

    Both halves, because a caller wanting one wants the other: an item's
    `classes` decide nothing without the `debt_classes` or `safety_classes`
    list that says which of them count as debt.
    """

    config: Config
    items: Mapping[str, Item]


#: The store each root's run has read so far, while `analyze` runs, and `None`
#: outside a run. `_read_store` explains why.
_RUN_STORES: ContextVar[dict[Path, _Store | None] | None] = ContextVar(
    "doc_check_run_stores", default=None
)


def _read_store(root: Path) -> _Store | None:
    """The queue, or `None` where the store cannot answer.

    `None` rather than an empty mapping, because the two mean opposite things
    to a check that reads the store to decide what a gate owes: an absent store
    can decide nothing, where an empty one would answer confidently that the
    gate owes nothing at all. `read_items` returns `[]` for a directory that is
    not there, so the directory is asked about rather than inferred from the
    result, and every caller turns the `None` into a `declined` line naming
    what went unchecked in its own terms - `_store_or_decline` below writes
    that line for the gate's re-entry rule, and wrote the same one for the
    disposition rule until `PL-WD5Z` moved that into `bin/docket check`.

    **It is the only spelling of this read, since `PL-R0P3`.** The gate's
    re-entry and disposition rules each spelled it inline, and the two that
    bypassed this helper were the two deciding gate membership. They disagreed
    with it silently and in the one direction that matters: on a checkout with
    no store, `read_items`' `[]` made both go quiet, reporting a gate that owes
    nothing where nothing had been read at all. That is the distinction
    `Report.declined` exists to keep, so unifying the read resolves it this
    way rather than the other.

    **Read once in each `analyze` run** (`PL-LYH3`). Five checks call it
    directly, and three more reach it through `_live_item_briefs`. Each read
    parsed every item file: 16,289 `parse_item` calls for 2,327 items in one
    analysis of this repository on 2026-10-17, 2.0 s of a 32.4 s run. So inside
    a run the first read is kept in `_RUN_STORES` and returned to every later
    caller. That is safe because nothing in this tool writes to the store.
    Outside a run, as when a test calls one check on its own, every call reads
    the disk again.
    """
    stores = _RUN_STORES.get()
    if stores is not None and root in stores:
        return stores[root]
    store = _load_store(root)
    if stores is not None:
        stores[root] = store
    return store


def _load_store(root: Path) -> _Store | None:
    """The queue as the disk holds it now. `_read_store` is the reader to call."""
    try:
        config = load_docket_config(root)
    except (OSError, ValueError):  # pragma: no cover - a config that will not parse
        return None
    store = root / config.items_dir
    if not store.is_dir():
        return None
    try:
        return _Store(config, {item.identifier: item for item in read_items(store)})
    except (OSError, ValueError):  # pragma: no cover - a store that will not parse
        return None


def _store_or_decline(root: Path, report: Report, rule: str) -> _Store | None:
    """The queue for a check that cannot run without it, or `None` having said so.

    One spelling of the decline beside the one spelling of the read. The two
    gate rules below each wrote their own, and whatever reads the store next
    would have written a third.
    """
    roadmap_name = roadmap_path(root)
    store = _read_store(root)
    if store is None:
        report.declined.append(
            f"{roadmap_name}: {rule}, because the item store would not read; "
            "`bin/docket check` is what reports why"
        )
    return store


def _withheld_counts(lines: Sequence[str], section: MilestoneSection) -> Iterator[tuple[int, int]]:
    """Each `N entries are marked `not-delegable`` claim in one frozen list.

    Yields the line the sentence opens on and the number stated. Scanned over
    the gate subsection alone - see `NOT_DELEGABLE_COUNT_RE` for why position
    rather than wording is what bounds it - and read whole, so a sentence a
    wrap splits is still the one claim (`PL-R417`), within the statement
    holding it (`PL-Z1R7`).
    """
    end = _subsection_end(lines, section.gate_line)
    subsection = "\n".join(lines[section.gate_line : end])
    for match in _statement_matches(NOT_DELEGABLE_COUNT_RE, subsection):
        stated = _count_word(match.group("count"))
        if stated is not None:
            yield section.gate_line + _line_of(subsection, match.start()), stated


def _withheld_entries(
    section: MilestoneSection, items: Mapping[str, Item]
) -> list[GateEntry] | None:
    """The section's entries holding an item marked `not-delegable`.

    Entries rather than ids, matching every other count `check_gate_counts`
    holds a frozen list to: one problem recorded under two ids is one entry,
    and the prose counts entries.

    `None` where the list names an id the store does not hold, because the
    count is then not computable rather than smaller. Nothing else in this file
    reports a frozen entry whose id has no item, so reading a missing one as
    "not withheld" would fail a correct sentence on a truncated checkout and
    name the sentence as the fault.
    """
    if any(identifier not in items for entry in section.gate_entries for identifier in entry.ids):
        return None
    return [
        entry
        for entry in section.gate_entries
        if any(items[identifier].not_delegable for identifier in entry.ids)
    ]


def check_gate_counts(root: Path, report: Report) -> None:
    """Hold every count a frozen list states about itself to the list.

    `ROADMAP.md` states the size of a release's frozen list in its own group
    headings and in the two tables that name the release, and the same number
    reached six places once. On 2026-08-31 three of them said "nineteen" while
    one said "twenty-two"; on 2026-09-01 the timeline said eighteen, four
    paragraphs said thirty-one and the list's own intro said thirty-two, and
    admitting four entries that day meant correcting nine numbers by hand -
    then eight of them again an hour later, for a fifth entry.

    The file already states the principle: "a count written into a document
    goes stale the next time an item closes". It applies it to the *closed*
    count, which is deliberately not recorded and read from `bin/docket wave`
    instead. This applies the same rule to the total.

    Only counts whose meaning is fixed by where they sit are read - a group
    heading over the entries it counts, and a cell of the version or timeline
    table naming that release. Prose is deliberately left alone: a checker
    cannot tell "the thirty-seven entries below are its whole content", a
    claim about today's list, from "frozen ... at seventeen entries", a dated
    fact that must never change. Judging that is a reader's job, so the prose
    restates no count instead of being guessed at.

    A count in a *heading* is refused rather than read, because no heading is
    one of those two positions and none can be made into one - the reasoning
    is in `_uncheckable_heading_counts`. A heading carries no date either, so
    the reader's exemption above does not reach it: it counts the subsection
    below it and is wrong the next time one is added.
    """
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    if not roadmap.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")
    lines = split_lines(text)
    store = _read_store(root)
    items = None if store is None else store.items

    for section in parse_milestones(text):
        if not section.records_a_gate:
            continue
        rendered = "v{}.{}.{}".format(*section.version)
        total = len(section.gate_entries)
        groups = list(_gate_groups(lines, section))

        for group in groups:
            entries = len(group.entries)
            ids = sum(len(entry.ids) for entry in group.entries)
            if group.stated != entries:
                report.errors.append(
                    f"{roadmap_name}:{group.line}: this group heading of {rendered}'s frozen list "
                    f"says {group.stated} entries, but {entries} follow it"
                )
            if group.stated_ids is not None and group.stated_ids != ids:
                report.errors.append(
                    f"{roadmap_name}:{group.line}: this group heading of {rendered}'s frozen list "
                    f"says {group.stated_ids} item ids, but the entries under it hold {ids}"
                )

        summed = sum(group.stated for group in groups)
        if groups and summed != total:
            report.errors.append(
                f"{roadmap_name}:{section.gate_line}: the group headings of {rendered}'s frozen "
                f"list count {summed} entries between them, but the list holds {total}"
            )

        for line, stated in _uncheckable_heading_counts(lines, section):
            counted = "entry" if stated == 1 else "entries"
            report.errors.append(
                f"{roadmap_name}:{line}: this heading in {rendered}'s section states {stated} "
                f"{counted}, and nothing checks it - a frozen list's counts are read from its "
                "emphasized group headings, which stop at the first `###`, and from the "
                "table rows naming the release. Drop the number: the entries below are the "
                "record, and `bin/docket wave` is what counts the open ones"
            )

        for line, where, stated in _table_counts(text, section):
            if stated != total:
                report.errors.append(
                    f"{roadmap_name}:{line}: the {where} row for {rendered} says {stated} "
                    f"entries, but its frozen list holds {total}"
                )

        withheld = None if items is None else _withheld_entries(section, items)
        for line, stated in _withheld_counts(lines, section):
            if withheld is None:
                report.declined.append(
                    f"{roadmap_name}:{line}: this `not-delegable` count of {rendered}'s frozen "
                    "list was not compared, because the item store did not answer for every "
                    "id on the list; `bin/docket check` is what reports why"
                )
                continue
            if stated != len(withheld):
                report.errors.append(
                    f"{roadmap_name}:{line}: this sentence says {stated} of {rendered}'s frozen "
                    f"entries are marked `not-delegable`, but {len(withheld)} of them hold "
                    "an item carrying that field"
                )


# The group a frozen list writes for the entries its milestone clears itself:
# `**Cleared by v0.6.0 itself - 12 entries**`. Only a count-carrying group
# heading is read, so this matches the label `GATE_GROUP_RE` has already found,
# and the version has to be the section's own - a list naming another
# milestone's self-clearing would be a different claim, and not one this file
# has made.
SELF_CLEARED_GROUP_RE = re.compile(rf"^\*{{1,2}}Cleared by (?P<version>v{SEMVER_PATTERN}) itself\b")


def check_self_cleared_group(root: Path, report: Report) -> None:
    """Hold the current gate's "Cleared by vX.Y.Z itself" group to its `Required scope`.

    `ROADMAP.md` § "Debt inside the milestone's own scope" states the test for
    which frozen entries a milestone clears itself - whether its `Required
    scope` names the id - and the frozen list then writes the answer again by
    hand, as a group. The two disagreed on v0.6.0: `PL-CNCF` and `PL-PGZF` were
    declared in `Required scope` by `#862` after `#850` had grouped the list,
    so they sat under "Cleared before v0.6.0 begins" while `bin/docket wave`,
    reading the rule, said the milestone cleared them itself. The group
    heading's own count agreed with the entries under it, so `check_gate_counts`
    was satisfied by a list telling a reader the wrong thing about two entries
    (`PL-J6HP`).

    So the group is held to the parse rather than trusted beside it, in both
    directions: an entry under the group that `Required scope` does not name,
    and an entry it names that sits anywhere else. An entry is the milestone's
    own when every id it holds is declared there, which is what `gate_status`
    asks of every id still open - a list's grouping cannot know which those
    are, so it is asked of them all. A list that groups nothing makes no claim,
    and is left alone.

    **The current gate only**, read by the function every gate rule shares
    (`_current_gate`). A released milestone's list is a record, and v0.5.0's
    keeps `PL-YDKJ` in its self-cleared group on purpose, with the paragraph
    beneath the group saying why: a consequence of an entry beside it rather
    than a nineteenth `Required scope` entry. Rewriting that to fit a rule
    written afterwards would be the renegotiation "The gate is a snapshot"
    forbids, one level down.
    """
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    if not roadmap.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")
    gate = _current_gate(text)
    if gate is None:
        return
    groups = list(_gate_groups(split_lines(text), gate))
    if not groups:
        return

    rendered = "v{}.{}.{}".format(*gate.version)
    label = f'"Cleared by {rendered} itself"'
    own = frozenset(gate.own_scope_ids)
    home: dict[GateEntry, _GateGroup] = {}
    for group in groups:
        for entry in group.entries:
            home[entry] = group

    for entry in gate.gate_entries:
        holder = home.get(entry)
        matched = SELF_CLEARED_GROUP_RE.match(holder.heading) if holder is not None else None
        inside = matched is not None and matched.group("version") == rendered
        named = all(identifier in own for identifier in entry.ids)
        ids = " and ".join(entry.ids)
        if inside and not named:
            report.errors.append(
                f"{roadmap_name}:{entry.line}: {ids} sits under {label}, but {rendered}'s "
                "Required scope does not declare it, so by the rule the group stands for "
                "the milestone does not clear it - move the entry to the group that does, "
                "or declare it in Required scope"
            )
        elif named and not inside:
            where = (
                f'under "{holder.heading.strip("* ")}"'
                if holder is not None
                else "under no group heading"
            )
            report.errors.append(
                f"{roadmap_name}:{entry.line}: {ids} is declared in {rendered}'s Required scope, "
                f"so the milestone clears it itself, but its frozen entry sits {where} - "
                f"move it under {label} and correct both groups' counts"
            )


#: Phrases that turn a `Required scope` bullet into an exclusion. Matched
#: lowercased against the bullet's whole text, continuation lines joined.
#:
#: **This is a keyword guess, and it is placed where a guess is safe.** The same
#: guess inside `docket`'s ranker was refused (`PL-NBCS`): there it would decide
#: a placement, so a phrasing it missed would print a wrong marking silently.
#: Here it asks a person to move a sentence and changes no placement at all, so
#: a miss leaves the status quo and a false positive costs one rewording. That
#: asymmetry is the whole reason the rule lives in this file.
SCOPE_EXCLUSION_MARKERS = ("not in scope", "out of scope", "stays at gate", "stays on gate")


#: A test function's name, as the whole of a code span names one, e.g.
#: `` `test_washout` ``.
TEST_NAME_RE = re.compile(r"test_[A-Za-z0-9_]+")
#: A line ending inside a code span, a soft break as `markdown.SOFT_BREAK`
#: reads one: a span's content is read from text whose container markers are
#: blanked (`_code_spans`), so the next line's `>` is gone before this sees it.
#: No test name holds a space, so a name broken here was broken by the wrap,
#: and is read with the break taken out (`PL-6SRZ`).
SPAN_BREAK_RE = re.compile(SOFT_BREAK)
#: Where test functions are defined: the product suite and the apparatus one.
TEST_ROOTS = (Path("tests"), Path("subprojects/docket/tests"))


def _parser_refusal(text: str) -> str | None:
    """Why this interpreter's parser refuses `text`, or `None` where it reads it.

    `docket.python` reads a file with the tokenizer, and says in its module
    docstring that the tokenizer's reading can be wrong without an error. A
    formatted string that nests its own quote (PEP 701) mis-tokenizes on
    Python 3.11 and merges the statements after it into one. Where the
    parser refuses a file, the tokenizer's reading of it may be short, so a
    caller names the file, as `verify` does (`PL-LCBQ`).
    """
    try:
        with warnings.catch_warnings():
            # An invalid escape sequence warns; that is the file's linter's to report.
            warnings.simplefilter("ignore")
            ast.parse(text)
    except UNPARSABLE as error:
        return refusal(error)
    return None


def _defined_tests(text: str) -> set[str]:
    """The test functions a Python file defines, as its `def` statements name them.

    A statement rather than a line (`PL-V2HK`). A pattern over `def ` at a
    line's start read `def test_ghost():` inside a fixture string as a test,
    so a document citing a test nothing defines passed, and it read an
    `async def test_` as none. Raises one of `UNTOKENIZABLE` where the
    tokenizer refuses the file.
    """
    found: set[str] = set()
    for line in read_logical_lines(text):
        keyword, name = definition(line)
        if keyword == "def" and TEST_NAME_RE.fullmatch(name):
            found.add(name)
    return found


def _named_tests(text: str) -> Iterator[tuple[int, str]]:
    """Each test a passage names, with the line its code span opens on.

    The spans are `_code_spans`', which reads a span wrapped across a line as
    one. This repository wraps prose at about 76 columns and names its tests as
    sentences, so the names most worth citing are the ones a wrap breaks, and
    a pattern held to one line saw none of them (`PL-6SRZ`).
    """
    for span in _code_spans(text):
        name = SPAN_BREAK_RE.sub("", span["content"]).strip()
        if TEST_NAME_RE.fullmatch(name):
            yield _line_of(text, span.start()), name


def _names_a_test(text: str) -> bool:
    """Whether a passage names a test at all, which is all a bound family asks."""
    return next(_named_tests(text), None) is not None


def check_named_tests(root: Path, documents: Mapping[Path, str], report: Report) -> None:
    """Resolve every test the documentation names, so a citation cannot rot.

    The specification earns its authority by being checkable, and a named test
    is the most checkable claim in it: `docs/MODEL.md` asserts that an invariant
    or a mitigation is *held* by something, and whether that something still
    exists is decidable by reading the tree. A renamed or deleted test otherwise
    leaves the sentence reading exactly as it did when it was true, which is the
    silent-wrong-answer shape `CLAUDE.md` asks to be caught in code. The hazard
    table's right-hand column is the reason this was built (`PL-FDBK`), and it
    is the cheap half of `PL-8LDF`, which keeps the annotation pass over the
    required invariants.

    **Every documentation file, and not the queue, and the exclusion is the
    point rather than laziness.** Measured 2026-09-13 across every markdown
    file in the tree: 161 test names are cited, 21 of them resolve to nothing,
    and **all 21 sit in `docs/items/`**. That is correct there - an item brief
    names the test its work will add, which is a specification of future work
    and the same forward reference a `verify:` command makes. Failing on those
    would punish the queue for doing what it is for. A document asserts what
    holds *now*, so the files `DOC_GLOBS` reads are held to this. It read
    `docs/MODEL.md` alone until `PL-6SRZ`, while `make check` said the
    documentation's citations resolve: a test deleted from under
    `docs/WORKING_NOTES.md` on 2026-09-21 was reported by nothing.

    What the check cannot judge is whether the test is any good, or whether it
    tests the sentence it is cited under. It validates linkage, exactly as the
    provenance check does, and says so.

    **A test file the tokenizer refuses is declined, not read a line at a
    time** (`PL-V2HK`). What it defines is unknown, so a name defined nowhere
    else is neither passed nor failed where such a file holds the name's text,
    and is an error as before where none does: no file defines a test without
    spelling its name.

    The suite is the test files the repository holds, read from
    `tracked_files`, so a scratch test a session has not added cannot resolve
    a citation the suite does not hold (`PL-J4YY`).
    """
    seen: dict[tuple[Path, str], int] = {}
    for path, text in documents.items():
        for line, name in _named_tests(text):
            seen.setdefault((path, name), line)
    # **Read the citations before looking for the suite, so that a document
    # naming no test declines nothing.** A decline is the claim "this was not
    # checked", and there is nothing to check here until a name is cited -
    # saying otherwise reports a gap about a question nobody asked, which is
    # the every-run noise `CLAUDE.md` calls a defect in the check itself.
    if not seen:
        return
    defined: set[str] = set()
    refused: dict[Path, tuple[str, str]] = {}  # each file the tokenizer refused: its text, why
    searched = False
    for relative in TEST_ROOTS:
        directory = root / relative
        if not directory.is_dir():
            continue
        searched = True
        for path in tracked_under(root, relative, ".py"):
            text = path.read_text(encoding="utf-8-sig")
            try:
                defined |= _defined_tests(text)
            except UNTOKENIZABLE as error:
                refused[path.relative_to(root)] = (
                    text,
                    f"the tokenizer refuses it: {refusal(error)}",
                )
                continue
            # Read, but perhaps short: a name only it could define is declined.
            if (why := _parser_refusal(text)) is not None:
                refused[path.relative_to(root)] = (
                    text,
                    f"the parser refuses it, so the tokenizer's reading may be short: {why}",
                )
    if not searched:
        report.declined.append(
            f"the {len(seen)} test citation(s) in the documentation: no test directory was "
            "found in this checkout"
        )
        return
    for (path, name), line in sorted(seen.items(), key=lambda pair: (pair[0][0], pair[1])):
        # A name ending in `_` cites the tests it prefixes - "the `test_arm_`
        # tests" - and resolves while one of them is defined.
        if name in defined or (
            name.endswith("_") and any(test.startswith(name) for test in defined)
        ):
            continue
        holders = [f"{file} ({why})" for file, (text, why) in refused.items() if name in text]
        if holders:
            report.declined.append(
                f"{path}:{line}: names the test `{name}`, which no file read whole defines; "
                f"Python {platform.python_version()} cannot read {' or '.join(holders)} whole, "
                "which may define it, so the citation was neither passed nor failed"
            )
        else:
            report.errors.append(
                f"{path}:{line}: names the test `{name}`, which no test under "
                f"{' or '.join(str(one) for one in TEST_ROOTS)} defines; the statement it "
                "holds up is unverified until the name resolves"
            )


@dataclass(frozen=True)
class EntityKind:
    """What a bound family's members must name, and the two forms that do it."""

    #: The word the document uses for the thing, in both the declared-none form
    #: and the error text: "test", and later "field".
    noun: str
    #: Whether the member names an entity. Presence is all this asks: resolving
    #: what it finds stays with the check that already does it -
    #: `check_named_tests` for a test name - so this never becomes a second
    #: resolver that could disagree with the first.
    names: Callable[[str], bool]
    #: `docs/MODEL.md` clause 3's fixed form. The words in front of it are the
    #: sentence's own; this parenthesis is what makes a declared absence
    #: distinguishable from a forgotten link by a script rather than by a
    #: reader.
    declares_none: re.Pattern[str]


def _entity_kind(noun: str, names: Callable[[str], bool]) -> EntityKind:
    """An `EntityKind` whose declared-none form is built from its own noun.

    Its words may wrap like any sentence's, so each gap is Markdown's `GAP`.
    """
    return EntityKind(noun, names, re.compile(rf"\bno{GAP}{noun}{GAP}yet{GAP}\(`({ID_PATTERN})`\)"))


TEST_ENTITY = _entity_kind("test", _names_a_test)


@dataclass(frozen=True)
class BoundFamily:
    """A heading that promises one assertion per member, and what each owes.

    `docs/MODEL.md` § "How this document is held to the tree" clause 2: where a
    heading promises one assertion per member, every member names its entity or
    carries the declared-none form. The table is what turns that sentence into
    a decidable question, one family at a time.
    """

    document: Path
    #: The section title, without its hashes, and the depth it sits at. A
    #: renamed heading yields no members, which is an error rather than a pass;
    #: see `check_bound_families`.
    heading: str
    level: int
    kind: EntityKind
    #: How the members are laid out under that heading. A callable rather than
    #: a shape name, so that the list and subsection shapes arrive with the
    #: annotation passes that need them and this file carries no branch nothing
    #: takes.
    members: Callable[[str, BoundFamily], Iterator[tuple[int, str]]]
    #: What the heading promises, in the document's own words, so the error
    #: reads as the document's requirement rather than as the tool's.
    promise: str


def _table_members(text: str, family: BoundFamily) -> Iterator[tuple[int, str]]:
    """Each body row of the first table under the family's heading, as one line.

    Cells are rejoined rather than read by position: which column carries the
    entity is the family's business and can differ between them, and the
    question here is only whether the row names one somewhere.
    """
    for line, cells in table_rows(text, family.heading, family.level):
        yield line, " | ".join(cells)


class UnreadStatement(Exception):
    """A statement a reader found continued in a form it does not read.

    Raised rather than reading a fragment as the statement (`PL-R417`), so the
    caller can say by name what went unread - the decline the head's fix allows
    where reading the form whole would cost more than refusing it.
    """

    def __init__(self, line: int, why: str) -> None:
        super().__init__(f"line {line}: {why}")
        self.line = line
        self.why = why


def _list_members(text: str, family: BoundFamily) -> Iterator[tuple[int, str]]:
    """Each top-level entry of the list under the family's heading, as written.

    The second member shape, and it arrives with the first family that is laid
    out as a list rather than as a table - `BoundFamily.members` is a callable
    so that neither shape is carried before something takes it.

    Continuation lines are folded into the entry they open, because a member of
    this shape routinely wraps and an entity named on a bullet's second line is
    named by that bullet. Its walker, `list_entry_lines`, is borrowed rather
    than rewritten for the reason that walker gives: what a list entry *is* is
    one question, and a fourth answer to it would be a fourth thing to keep
    true. The entry comes back with its line breaks, because a test name
    wrapped inside a code span is read whole only where the break is still
    there to read; joined with a space, it named nothing (`PL-6SRZ`).

    **A lazy continuation is refused by name** (`PL-R417`). CommonMark folds an
    unindented line that carries on an entry's paragraph into the entry (0.31.2
    § 5.2), and the walker does not, so a test named there would be named by no
    member. The walker declines the entry itself (`PL-MFVV`), and this passes
    its decline on as `UnreadStatement`, in its words: the writer is asked for
    the indent or the blank line.

    Its bound is the next heading at depth three or shallower, so a family
    whose list is closed by a `####` heading would read that subsection's
    bullets as its own. No family is laid out that way today; one that is
    belongs in `list_entry_lines` as a depth argument rather than in a second
    walker here.

    The family's heading is one `markdown` reads, as its walker's bound is, so
    a `#` line inside a fence or a comment that repeats the title opens no list
    (`PL-0Y7J`).
    """
    lines = split_lines(text)
    for heading in read_headings(lines):
        if heading.level == family.level and heading.title == family.heading:
            spans, declined = list_entry_lines(lines, heading.end)
            if declined:
                lazy = declined[0]
                raise UnreadStatement(lazy.line, lazy.why) from lazy
            for first, end in spans:
                yield first + 1, "\n".join(lines[first:end])
            return


# Every family bound by clause 2 today. **An entry arrives with the annotation
# pass that makes its family conform, never in anticipation of one**, so the
# check never holds `make check` red for work nobody has done yet. The check was
# introduced over the hazard table, which conformed already, so it landed green;
# `PL-036` added the minimum displayed outputs, and `PL-8LDF` (required
# invariants) and `PL-2M9N` (required tests) are the two passes still due.
#
# Both entries name `TEST_ENTITY`, and for the displayed outputs that was a
# decision rather than an inheritance (`PL-036`, project owner, 2026-09-22,
# ratified, over naming the `SimulationSnapshot` field behind each bullet).
# Three of that list's entries have no snapshot field to name - the playback
# rate and the chart's time base are view settings, and F_A/F_I is derived at
# the point of drawing - so a field-kinded family could only have declared an
# absence that nothing owed, which is the permanent hole clause 3's form exists
# to make impossible. A field would also have checked the wrong half of the
# chain: it proves the value still travels, never that a widget still draws it,
# and a value travelling to a display that no longer shows it is the failure
# that section's own subsection calls silent.
BOUND_FAMILIES = (
    BoundFamily(
        document=MODEL,
        heading="Reasonably foreseeable misuse, and the hazards the presentation carries",
        level=2,
        kind=TEST_ENTITY,
        members=_table_members,
        promise="every row names the test that holds it, or says plainly that it has none",
    ),
    BoundFamily(
        document=MODEL,
        heading="Minimum displayed outputs",
        level=2,
        kind=TEST_ENTITY,
        members=_list_members,
        promise="every entry names the test that holds it",
    ),
)


def check_bound_families(root: Path, report: Report) -> None:
    """Hold every member of an enumerated family to naming what it asserts.

    `check_named_tests` asks whether a name resolves. This asks the prior
    question - whether the statement named anything at all - and it is the
    question a specification written as prose cannot answer about itself. A
    `must` with no link to what holds it reads exactly as it did when a test
    held it, so the sentence decays silently, which is the shape `CLAUDE.md`
    requires to be caught in code. Reading 38 of `docs/MODEL.md`'s invariants
    and required tests against the suite by hand on 2026-09-19 found two held
    only in part; nothing that runs had surfaced either (`PL-4FBP`).

    **Only where the heading promises one assertion per member.** Free prose is
    not read, by decision rather than by reach: the ratified convention leaves
    an unmarked claim outside a family to the close-out sweep, so that a rule
    with an escape nobody declares does not become a rule nobody follows. A
    family is therefore added to `BOUND_FAMILIES` by the annotation pass that
    makes it conform, never in anticipation of one.

    **A family with no members is an error, not a pass.** A renamed heading or
    a deleted table would otherwise retire the family silently while the entry
    above still claims to hold it, which is the same silent decay one row down.

    The declared-none form is resolved against the queue because an exemption
    naming a closed item is a hole rather than a forward reference. What this
    check cannot judge - whether the named test is any good, or tests the
    sentence it sits under - stays a reviewer's question, exactly as it does
    for `check_provenance` and `check_named_tests`.
    """
    items: Mapping[str, Item] | None = None
    store_read = False
    for family in BOUND_FAMILIES:
        document = root / family.document
        if not document.is_file():
            report.declined.append(
                f'{family.document} is absent, so § "{family.heading}" was not held to its members'
            )
            continue
        try:
            members = list(family.members(document.read_text(encoding="utf-8"), family))
        except UnreadStatement as unread:
            report.errors.append(
                f'{family.document}:{unread.line}: § "{family.heading}" is a bound family, '
                f"and its members were not read: {unread.why}"
            )
            continue
        if not members:
            report.errors.append(
                f'{family.document}: § "{family.heading}" is a bound family and has no '
                "members here; the heading has moved or its entries are gone, and the "
                "family is unchecked either way"
            )
            continue
        for line, member in members:
            # Every finding names the family as well as the line, because one
            # document holds several and a line number alone does not say which
            # promise was broken.
            where = f'{family.document}:{line}: § "{family.heading}"'
            if family.kind.names(member):
                continue
            declared = next(_statement_matches(family.kind.declares_none, member), None)
            if declared is None:
                report.errors.append(
                    f"{where} promises that {family.promise}; this member names no "
                    f"{family.kind.noun} and does not declare that it has none "
                    f"(`no {family.kind.noun} yet (`PL-XXXX`)`, naming the open item that "
                    "owes the link)"
                )
                continue
            if not store_read:
                store = _read_store(root)
                items, store_read = (None if store is None else store.items), True
            if items is None:
                report.declined.append(
                    f"{where} declares no {family.kind.noun} yet against "
                    f"`{declared.group(1)}`, which no queue in this checkout can resolve"
                )
                continue
            owed = items.get(declared.group(1))
            if owed is None:
                report.errors.append(
                    f"{where} declares no {family.kind.noun} yet against "
                    f"`{declared.group(1)}`, which the queue does not hold; a declared "
                    "absence must forward-reference work that exists"
                )
            elif not owed.is_open:
                report.errors.append(
                    f"{where} declares no {family.kind.noun} yet against "
                    f"`{declared.group(1)}`, which is {owed.status}; the link that item "
                    f"forward-referenced is owed now, so the {family.kind.noun} goes here "
                    "or another open item takes the debt"
                )


def check_scope_exclusions(root: Path, report: Report) -> None:
    """Keep a milestone's exclusions out of its `Required scope`.

    `bin/docket next` reads exactly two structures for membership - a section's
    frozen list and its `Required scope` - and it reads the second **in full**,
    because a milestone names what it covers in whatever grammar the sentence
    wanted. The cost is that an id written into a scope bullet *in order to
    exclude it* is read as scope. `PL-NBCS` is the case: v0.4.0's stage-3
    exclusion put `PL-B9PY` into v0.4.0's `scope_ids`, and while v0.4.0 was the
    anchor every session was told Gate-1 work was what v0.4.0 was waiting on -
    as a fact, with the milestone named.

    Two rules, and the split between them is the point.

    **An id under both of one milestone's scope headings is an error.** Exact,
    no judgment: the section has said the same id is in scope and out of it.
    This is the shape a later edit would reintroduce after the fix, so it is
    what holds the fix in place.

    **Exclusion language inside a scope bullet is an advisory.** That one is a
    keyword guess - see `SCOPE_EXCLUSION_MARKERS` for why a guess is admissible
    here and was refused inside the ranker - and it is the only rule that
    catches the original shape, where the exclusion is written *only* in the
    scope bullet and there is no contradiction to find.
    """
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    if not roadmap.is_file():
        report.declined.append(f"{roadmap_name} is absent, so its scope headings were not compared")
        return
    text = roadmap.read_text(encoding="utf-8")
    for section in parse_milestones(text):
        excluded = set(section.excluded_ids)
        both = [identifier for identifier in section.own_scope_ids if identifier in excluded]
        if both:
            at = f":{section.scope_line}" if section.scope_line else ""
            scope_heading = SCOPE_SUBSECTION.capitalize()
            excluded_heading = EXCLUDED_SUBSECTION.capitalize()
            report.errors.append(
                f"{roadmap_name}{at}: {section.label} names {', '.join(both)} under both "
                f'"{scope_heading}" and "{excluded_heading}", so the section says the same '
                "item is in scope and out of it; `docket next` reads the scope heading "
                "and reports it as in scope"
            )
        for entry in section.scope_entries:
            # The ids the entry *declares*, and the words that introduce the
            # declaration. Reading the whole bullet was right while the whole
            # bullet was read as scope; since `PL-HWW1` an id outside the slot
            # places nothing, so the hazard is now exactly one shape - an entry
            # whose title says "not in scope" and whose slot declares the item
            # anyway. Prose *after* the slot is a different sentence about a
            # different item, and warning on it would report a hazard that no
            # longer exists, which costs attention every run and trains a
            # reader past the line where the real one appears.
            opening = DECLARATION_RE.search(entry.text)
            if not entry.ids or opening is None:
                continue
            lowered = entry.text[: opening.start()].lower()
            marker = next((m for m in SCOPE_EXCLUSION_MARKERS if m in lowered), None)
            if marker is None:
                continue
            report.advisories.append(
                f'{roadmap_name}:{entry.line}: this "{SCOPE_SUBSECTION.capitalize()}" entry says '
                f'"{marker}" and declares {", ".join(entry.ids)}, which `docket next` '
                f'reads as scope. Move the exclusion under "{EXCLUDED_SUBSECTION.capitalize()} for '
                f'{section.label.split()[0]}" and leave the entry declaring only what is in scope'
            )


def check_scope_declarations(root: Path, report: Report) -> None:
    """Hold a `Required scope` entry to declaring the work it places.

    Membership is the `(queue item ...)` slot and nothing else (`PL-HWW1`), so
    the two ways a section can now be wrong about its own size are both
    decidable and both silent without this. An entry that declares nothing
    places nothing while reading to a person as scope. A declaration naming an
    id the queue does not hold places nothing either - the same reading
    `GateStatus.unknown_ids` takes of a frozen list, applied to the structure
    beside it. Either way the milestone is smaller than the document says, and
    nothing else reports the gap: `bin/docket wave` counts what it parsed, so
    an undeclared entry simply is not there to be missed.

    **Only a section whose other entries declare.** v0.1.0's and v0.2.0's scope
    entries were written before the queue existed and name no ids at all, so
    they place nothing under any reading and failing them would be asking for
    ids to be invented for a milestone that shipped two years of work ago. The
    rule reads what the section already does rather than imposing a form on
    it, which is the same property that lets a milestone be scoped in prose
    before its items are filed.
    """
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    if not roadmap.is_file():
        report.declined.append(f"{roadmap_name} is absent, so its scope declarations were not read")
        return
    text = roadmap.read_text(encoding="utf-8")
    store = _read_store(root)
    items = None if store is None else store.items
    scope_heading = SCOPE_SUBSECTION.capitalize()
    declaring = False

    for section in parse_milestones(text):
        if not any(entry.ids for entry in section.scope_entries):
            continue
        declaring = True
        for entry in section.scope_entries:
            if not entry.ids:
                report.errors.append(
                    f'{roadmap_name}:{entry.line}: this "{scope_heading}" entry of '
                    f"{section.label} declares no queue item where the section's other "
                    f'entries declare: "{_opening(entry.text)}". Membership is the '
                    "`(queue item PL-XXXX)` slot after the entry's title, so an entry "
                    "without one places nothing and the milestone is smaller than it reads"
                )
                continue
            if items is None:
                continue
            for identifier in entry.ids:
                if identifier in items:
                    continue
                report.errors.append(
                    f'{roadmap_name}:{entry.line}: this "{scope_heading}" entry of '
                    f"{section.label} declares {identifier}, which the queue does not "
                    "hold. A declaration is what places an item in a milestone, so a "
                    "typo here places nothing and reports nothing"
                )
    if declaring and items is None:
        # Only where there was something to check. A roadmap whose scope
        # entries declare nothing - one written before the queue existed, or a
        # fixture - has no ids to look up, and a decline there would report a
        # gap that does not exist and suppress the run's own "all resolve".
        report.declined.append(
            f"{roadmap_name}: whether its scope declarations name items that exist, because "
            "the item store could not be read; `bin/docket check` is what reports why"
        )


def _opening(text: str, width: int = 60) -> str:
    """The first few words of an entry, for naming it in a message."""
    return text if len(text) <= width else f"{text[:width].rstrip()}..."


def _current_gate(text: str) -> MilestoneSection | None:
    """The gate the project is clearing now, read by `docket.roadmap.baseline_gate`.

    The one answer `bin/docket wave`, `bin/docket check`'s disposition rule and
    the gate rules below share (`PL-J6HP`); each rule used to find the section
    with a `next(...)` of its own. The version is the version table's baseline
    row rather than `pyproject.toml`, which `check_baseline` holds equal to it,
    so a checkout carrying the roadmap alone can still be checked.

    `None` where no single row is marked current. Which gate is current cannot
    then be read, so nothing is checked - and this is the one place where
    silence is safe rather than a check reported as passing. `check_baseline`
    makes exactly this condition a hard error and names the rows, so the run
    cannot be green while it holds; a decline here would be a second voice on
    one fault.
    """
    return baseline_gate(text)


def check_gate_reentries(root: Path, report: Report) -> None:
    """Name every open `safety`/`science` item the current gate does not place.

    `ROADMAP.md` states one unconditional rule twice - step 4 of "The cadence"
    and "The gate is a snapshot, not a moving target" - and `PL-9PMV` settled
    that the two passages are the same rule rather than two readings of it: a
    finding classed `safety` or `science`, or one at `P0`, re-enters the
    *current* gate regardless of when it was found. Every other class defers to
    the next gate unless its problem predates the freeze, which is a judgment
    call. This one is not.

    Nothing reconciled the two sides of it, so the rule ran only when a session
    happened to think of it. Between the 2026-09-06 freeze and 2026-09-07,
    eleven qualifying items were filed and none reached the list, while
    `bin/docket wave` reported the written list correctly throughout - 84 open
    of 121, omitting every open `P1` the project had, because `docket check`
    pins both classes to the top band and the list held none of them
    (`PL-KTKP`). A count that is right about the document and wrong about the
    project is the silent-wrong-answer shape `CLAUDE.md` asks to be caught in
    code.

    **What is decidable here, and what is deliberately not.** Whether an item
    is *placed* is: `MilestoneSection.scope_ids` names the ids a section places
    - its frozen list, then the ids under `Required scope` - and excludes an id
    the section merely mentions, which is the distinction `PL-NBCS` records.
    Which of the two placements an unplaced one should take is not: it may join
    the frozen list, added with the date and the reason as v0.4.0's three
    post-freeze notes and this gate's own `PL-GS3R`, `PL-BXB2`, `PL-V53R` and
    `PL-0PJG` were, or go under `Required scope` so the milestone clears it per
    "Debt inside the milestone's own scope". So this reports and does not
    decide, which is why it is an advisory rather than an error.

    **It does not read `deferred-from:`, and that is the whole of what
    distinguishes it from `bin/docket check`'s disposition rule**
    (`_check_gate_dispositions` in `subprojects/docket/src/docket/checks.py`,
    which lived in this file until `PL-WD5Z`). A deferral is a recorded
    disposition, so it silences that rule; it is not a disposition
    *this* rule offers, because "The gate is a snapshot" closes by saying these
    two classes "are not deferrable by this project's own standard". So the two
    advisories disagree about a deferred `safety` item deliberately, and this
    one's text now says so rather than leaving a session to read the
    disagreement as a bug in one of them.

    Until `PL-R0Q0` the text offered the deferral it then refused, which is the
    apparatus floor's own failure - a check telling a session something that is
    not true. Accepting one instead would not have been the smaller fix it
    looked: `safety_classes` is a subset of `debt_classes`, so every item this
    names would have become a duplicate of that check's line, and nothing would
    have been left holding the unconditional half of the rule that `PL-KTKP`
    records the cost of losing.

    **An `anticipated` item is excluded, and that is a rule rather than a
    judgment.** `ROADMAP.md` § "The gate is a snapshot, not a moving target"
    makes an `anticipated` `safety` or `science` finding not debt until the
    hazard it describes exists (project owner, 2026-09-16, ratified). Without
    it this named ten area-model findings on every `make check` under two
    remedies neither of which they could take: they cannot be *cleared*, because
    the splitter handles are inert until planned-milestone item 34 makes them
    live, and v0.5.0's `Required scope` cannot hold them because item 34 is two
    milestones out. An advisory with no reachable clean state is the defect
    `CLAUDE.md` describes - one that "fires every run without changing a
    decision" - which is what `PL-83LS` was filed to remove.

    The exclusion is decidable rather than scripted judgment: `anticipated` is a
    declared class the store already carries and `docket check` already holds to
    a vocabulary, so this reads a claim somebody wrote down rather than guessing
    whether a hazard is live. What it costs is recorded beside the rule: a
    `safety` item wrongly classed `anticipated` goes invisible to the gate,
    which is `PL-MVC2`'s shape, and no check can catch a class correctly spelled
    and wrongly applied.

    **The exclusion expires, which is `PL-ZF2G` and why it reads `status` as
    well as `classes`.** On the class alone it never stopped. The rule is about
    *when* a hazard begins, and a finding written against an unbuilt milestone
    went on being passed over after that milestone shipped and the hazard went
    live - so the one thing the rule was for was the one thing it could not
    notice. Requiring `blocked` alongside the class gives it an end: the item
    itself says what it is waiting for, and stops saying it when the wait is
    over.

    It expires on the *promotion* rather than on the blocker closing. Nothing
    rewrites `status` when a blocker closes; `bin/docket check` asked for it
    in an advisory, and on 2026-09-16 that was asking for seven items -
    `PL-W7H9`, `safety, anticipated` behind a `PL-8PSW` that is `done`, among
    them. Since `PL-2349` the item-blocker case is an error instead, so the
    carve-out lapses in the pull request that closes the blocker; a milestone
    blocker's advisory still lets it outlive its hazard by one grooming pass.

    Resolving the blockers here directly would close the window outright, and
    was not built: it would put a second copy of `checks.py`'s resolution logic
    - item edges, milestone edges, `ships_with` - in the tool whose job is to
    read the store rather than reason about it, to buy a pass that an existing
    `bin/docket check` rule already covers. The conjunct is `Item.waits_anticipated`,
    the one `checks.py` reads too, and agreeing with it is worth more here than
    being a pass quicker (`PL-4DK2`).

    The roadmap had already decided one of these by hand, which is what settles
    it. `PL-V6M0` is `safety, anticipated` and was never blocked, and
    `ROADMAP.md` § "Why `anticipated` does not defer it" both seats it at `P1` -
    "`checks.py` grants the class its exemption from the band only at `status:
    blocked`, and nothing blocks this one" - and has it re-entering the gate
    "whatever its presence answer". On the class alone this check would have
    passed over the item that paragraph exists to keep in. So the conjunct is
    this rule agreeing with a disposition the project already took, rather than
    a rule borrowed from the checker.

    The gate it reads is the one `bin/docket wave` reads, through the same
    function (`_current_gate`): the first *unreleased* section recording a
    gate, rather than the newest recorded one, so that an open item is never
    measured against a shipped milestone's closed list.
    """
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    if not roadmap.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")

    gate = _current_gate(text)
    if gate is None:
        return

    store = _store_or_decline(root, report, "the gate's re-entry rule")
    if store is None:
        return
    config = store.config

    placed = set(gate.scope_ids)
    owed = [
        item
        for item in store.items.values()
        if item.status not in CLOSED_STATUSES
        and item.identifier not in placed
        and not item.waits_anticipated
        and any(name in config.safety_classes for name in item.classes)
    ]
    if not owed:
        return

    rendered = "v{}.{}.{}".format(*gate.version)
    listed = ", ".join(
        "{} ({})".format(
            item.identifier,
            "/".join(name for name in item.classes if name in config.safety_classes),
        )
        for item in owed
    )
    report.advisories.append(
        f"{roadmap_name}:{gate.gate_line}: {rendered}'s frozen list does not place "
        f"{_plural(len(owed), 'open item', 'open items')} classed "
        f"{' or '.join(config.safety_classes)}, which re-enter the current gate "
        f"regardless of presence: {listed}. Add each to the frozen list with the "
        "date and the reason it re-entered, or place it in Required scope so the "
        "milestone clears it. Deferring is not a third option here as it is for "
        'the other debt classes: "The gate is a snapshot" ends by making these '
        "two not deferrable, so a `deferred-from:` answers the disposition "
        "error and leaves this one standing - which is the disagreement to "
        "resolve, not a fault in either check"
    )


def _tags_region(text: str) -> tuple[int, str] | None:
    """The `**Tags.**` statement, and everything up to the next section heading.

    The exception sentence has historically sat in a paragraph below the claim
    rather than inside it, so the region runs to the heading rather than to the
    blank line. The mark opens a statement of prose, as `statement_lines`
    reads one, read past its containers' markers, so a claim in a block quote
    or a list item is read (`PL-8NPN`): a `**Tags.**` a soft break carries onto
    a line's start is its paragraph's own text (`PL-VQBY`). The heading that
    ends the region is one `markdown` reads, so a shell sample's `# comment`
    inside a fence below the claim leaves the exception sentence after it in
    the region (`PL-0Y7J`).
    """
    lines = split_lines(text)
    blanked = unmarked(lines)
    start = next(
        (first for first, _ in statement_lines(lines, PROSE) if TAGS_MARK_RE.match(blanked[first])),
        None,
    )
    if start is None:
        return None
    end = next(
        (heading.line for heading in read_headings(lines) if heading.line > start), len(lines)
    )
    return start + 1, "\n".join(lines[start:end])


def _version_list(text: str, start: int, end: int) -> list[str]:
    """Versions written as a run of `v0.1.0`, separated by commas and `and`, before `end`."""
    found: list[str] = []
    position = start
    while True:
        gap = LIST_SEPARATOR_RE.match(text, position, end)
        candidate = LIST_VERSION_RE.match(text, gap.end() if gap else position, end)
        if candidate is None:
            return found
        found.append(candidate.group("version"))
        position = candidate.end()


def _version_claim(
    claim: re.Pattern[str], said: str, body: str, first_line: int, roadmap_name: Path
) -> tuple[frozenset[str], list[str], int]:
    """The versions an exception sentence names, and whether it counts them right.

    Two sentences that each agree with `git tag` can still disagree with each
    other, which is why the count is read at all: it is the one part of the
    claim that no comparison with the repository would catch. Both exceptions
    to the `**Tags.**` statement take this one form, and `said` is how an error
    quotes the sentence back.
    """
    match = next(_statement_matches(claim, body), None)
    if match is None:
        return frozenset(), [], 0
    line = first_line + body[: match.start()].count("\n")
    named = _version_list(match.string, match.end(), match.endpos)

    stated = match.group("count")
    count = int(stated) if stated.isdigit() else NUMBER_WORDS.get(stated.casefold())
    if count is None:
        return frozenset(named), [f'{roadmap_name}:{line}: cannot read "{stated}" as a count'], line
    if count != len(named):
        return (
            frozenset(named),
            [
                f"{roadmap_name}:{line}: the sentence says {stated} {said}, but names "
                f"{len(named)}; the two halves cannot both be right"
            ],
            line,
        )
    return frozenset(named), [], line


def check_tags(root: Path, report: Report) -> None:
    """Hold the roadmap's tag statements to `git tag`, and to each other.

    The statements exist because four versions once went out untagged and the
    gap could not be repaired afterwards with any confidence: `git describe
    --contains` resolves nothing across an untagged release's span, so "which
    release did this change go out in" stops having an answer. A claim about
    which releases are traceable that is not itself traceable is the wrong way
    round, and it went stale exactly as one would expect - by releases landing,
    with nothing reading the sentence.

    Three silences are deliberate. A checkout git cannot answer for - no
    repository, no git - is told nothing at all, because a check that fails on
    how somebody fetched the repository is a check that gets switched off. A
    checkout that answers and holds no tags is told nothing either, for the
    reason `release.is_untagged` gives: adopting the practice is the project's
    decision rather than this tool's. Those two arrived as one empty set until
    `PL-ZPDM`, and they stay one behaviour by choice rather than by collapse.

    A **truncated** checkout is the second, and it was missed for exactly as
    long as this docstring claimed the first one covered it (`PL-J295`). A
    shallow clone does not collapse to an empty tag set: it holds the tags
    pointing into its fetched depth and omits the rest, so every release older
    than that depth reads as never tagged. That fired on `main` in every web
    session container, eight false errors at a time.

    The guard is deliberately narrower than "this clone is shallow". Both the
    session containers and `actions/checkout` clone shallow, so declining on
    that alone would retire the check everywhere it runs - including in a
    checkout that has since fetched its tags and can answer exactly. So the
    findings are computed first, and only withheld when there is something to
    withhold *and* truncation could account for it. A tag being **present** is
    never in doubt, so those inferences are untouched.

    The release being cut right now is the third, and it is now silent. It was
    never an error - its tag goes on its cut once that lands, so there is a window in
    which the newest version is completed and untagged, and failing it would
    turn `make check` red on every release branch, the failure `make release`
    was repaired to stop causing. It was an advisory, and that advisory was
    retired (`PL-R7C0`) because it could not tell a release that was never
    tagged from one tagged since this checkout last fetched.

    Neither silence above covers that case. The empty-tag-set return catches a
    checkout holding *no* tags; `is_shallow` catches truncation. A full clone
    that fetched tags before the newest release was cut is neither, and it is
    the ordinary state of any checkout more than one release old - so the
    advisory fired on a correctly tagged repository and printed a `git tag`
    command for a tag that already existed. Distinguishing the two needs the
    network, which these tools do not have by contract.

    Retiring it loses nothing permanent: the moment that version stops being
    the baseline it falls through to `absent` and is reported as an **error**,
    which is exactly when an untagged release starts to matter - `git describe
    --contains` only fails once history has moved past the gap. The reminder
    to tag also still arrives where it can be answered, from `docket release`,
    which refuses to cut the next release while the previous one is untagged.

    All of that turns on whether a tag *exists*. Whether a present tag sits on
    its own release's commit is the other question, and `_check_tag_versions`
    below answers it (`PL-YKSD`).

    The converse - a tag the version table does not name - is an error only
    against a working tree that holds the tag's commit (`PL-HVLJ`). A release's
    tag goes on the commit that adds its row, and `git fetch --tags` brings the
    tag without moving the tree, so a checkout that fetched after a release
    merged holds the one and not the other until it pulls. That was reported as
    a wrong `ROADMAP.md` to fix before committing, against a correct file.
    `_ahead_of_the_tree` tells the two apart: a tag the default branch holds and
    `HEAD` does not is declined as a checkout that is behind, naming the pull,
    and one `HEAD` holds, or the default branch lacks too, keeps the error.

    That error names the other state that reads the same way from here: a tag
    withdrawn on the remote, which this checkout keeps because `git fetch
    --tags` adds tags and never removes one. Telling those two apart takes the
    network, so the message names the command that asks and the repair rather
    than guessing (`PL-LT77`).
    """
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    if not roadmap.is_file():
        return
    text = roadmap.read_text(encoding="utf-8")

    rows = parse_version_table(text)
    completed = {row.version: row for row in rows if row.is_completed}
    if not completed:
        return

    region = _tags_region(text)
    if region is None:
        report.errors.append(
            f'{roadmap_name}: no "**Tags.**" statement; it is where this file says every '
            "released version is traceable to a tag, and deleting it removes the claim "
            "rather than making it true"
        )
        return
    first_line, body = region

    untagged, problems, claim_line = _version_claim(
        UNTAGGED_CLAIM_RE, "untagged", body, first_line, roadmap_name
    )
    report.errors.extend(problems)
    stale, problems, stale_line = _version_claim(
        STALE_VERSION_CLAIM_RE, "shipped with a stale version file", body, first_line, roadmap_name
    )
    report.errors.extend(problems)
    for named, line, said in (
        (untagged, claim_line, "untagged"),
        (stale, stale_line, "shipping with a stale version file"),
    ):
        for version in sorted(named):
            if version not in completed:
                report.errors.append(
                    f"{roadmap_name}:{line}: v{version} is named as {said}, but no row of the "
                    "version table marks it completed"
                )

    # Two reasons to say nothing here, told apart since `PL-ZPDM` and both
    # deliberate: git would not answer, and a repository that holds no tags.
    # The behaviour is the same and the distinction is not idle - it is what
    # keeps this silence a decision rather than the accident of an empty set.
    held = tags(root)
    if not held.known or not held.names:
        return
    existing = held.names

    marked = [row for row in rows if row.is_baseline]
    baseline = marked[0].version if len(marked) == 1 else ""

    absent: list[str] = []
    for version, row in sorted(completed.items()):
        if version in untagged or is_tagged(version, existing):
            continue
        if version == baseline:
            # Silent, not merely non-fatal: see the docstring. The skip stays -
            # without it the release being cut is an error - but nothing is said,
            # because a local checkout cannot tell "never tagged" from "tagged
            # since you last fetched" (`PL-R7C0`).
            continue
        absent.append(
            f"{roadmap_name}:{row.line}: v{version} is marked completed but git holds no tag "
            "for it, so no commit in its span maps to the release it went out in"
        )

    # Only a finding that a truncated checkout could have invented is withheld,
    # and only when there is one. Declining on `is_shallow` alone would silence
    # this check in every environment that matters - a web session's container
    # and `actions/checkout` both clone shallow - including the ones that have
    # since run `git fetch --tags` and can answer perfectly well.
    truncated = is_shallow(root)
    if absent and truncated is not False:
        report.declined.append(
            "release tags: "
            + (
                "the checkout is a shallow clone"
                if truncated
                else "git cannot say whether this checkout is complete"
            )
            + f", so the {_plural(len(absent), 'release', 'releases')} with no tag here "
            "cannot be told from a release whose tag was never fetched; "
            "`git fetch --tags` makes the question answerable"
        )
    else:
        report.errors.extend(absent)

    for version in sorted(untagged):
        if is_tagged(version, existing):
            report.errors.append(
                f"{roadmap_name}:{claim_line}: v{version} is named as untagged, but git holds a "
                "tag for it"
            )

    unnamed = {
        name: version
        for name in sorted(existing)
        if SEMVER_RE.match(name) is not None
        and (version := name.removeprefix("v")) not in completed
    }
    base, ahead = _ahead_of_the_tree(root, tuple(unnamed)) if unnamed else ("", ())
    for name, version in unnamed.items():
        if name not in ahead:
            report.errors.append(
                f"{roadmap_name}: git holds {name}, but no row of the version table marks "
                f"v{version} completed; a release that shipped is one this table has to name - "
                f"unless `git ls-remote --tags origin` no longer lists {name}, when this clone is "
                f"keeping a tag deleted on the remote and `git tag -d {name}` is the repair"
            )
    if ahead:
        report.declined.append(_behind_the_tags(ahead, base, truncated, roadmap_name))

    _check_tag_versions(
        root,
        report,
        existing,
        {version: row.line for version, row in completed.items()},
        stale,
        stale_line,
    )


def _ahead_of_the_tree(root: Path, names: Sequence[str]) -> tuple[str, tuple[str, ...]]:
    """The tags among `names` the default branch holds and `HEAD` does not, and that branch.

    Placed against the default branch because "behind" means behind it: a tag
    that branch does not hold either is left to the error, since pulling would
    not bring it in. A base that is only a guess places nothing, and nor does a
    read git did not answer, so each of those tags keeps the error it had.

    Ancestry is read as a merge base equal to the tag's commit rather than as
    `merge-base --is-ancestor`, whose two verdicts `_run_git` returns as the
    same empty string. A merge base that is found is always a true answer; in
    a shallow clone one that is not found may only be history this checkout
    never fetched, which `_behind_the_tags` says rather than rules out.
    """
    with GitRunner() as run:
        base = default_base(root, runner=run)
        if not resolved(base):
            return str(base), ()
        ahead: list[str] = []
        for name in names:
            commit = run(
                ["rev-parse", "--verify", "--quiet", f"refs/tags/{name}^{{commit}}"], root
            ).strip()
            if (
                commit
                and _holds(run, root, base, commit)
                and _holds(run, root, "HEAD", commit) is False
            ):
                ahead.append(name)
    return str(base), tuple(ahead)


def _holds(run: Callable[[list[str], Path], str], root: Path, ref: str, commit: str) -> bool | None:
    """Whether `ref`'s history holds `commit`, or `None` where git did not answer."""
    fork = run(["merge-base", commit, ref], root)
    return fork.strip() == commit if answered(fork) else None


def _behind_the_tags(
    ahead: Sequence[str], base: str, truncated: bool | None, roadmap_name: Path
) -> str:
    """The `declined` line for tags the working tree predates, naming what brings them in."""
    one = len(ahead) == 1
    names = ahead[0] if one else f"{', '.join(ahead[:-1])} and {ahead[-1]}"
    them = "it" if one else "them"
    line = (
        f"release tags: git holds {names}, which {base} has and this checkout's HEAD does "
        f"not, so the working tree predates {'that release' if one else 'those releases'} "
        f"rather than leaving {them} out of {roadmap_name}; `git pull` brings {them} in on "
        f"{base.rsplit('/', 1)[-1]}, and `bin/docket branch` says how on any other branch"
    )
    if truncated is False:
        return line
    commits = "that commit" if one else "those commits"
    if truncated:
        return (
            f"{line} - unless this shallow clone's history stops short of {commits}, which "
            "reads the same way; `git fetch --unshallow` tells the two apart"
        )
    return (
        f"{line} - unless this checkout's history stops short of {commits}, which reads the "
        "same way, and git cannot say here whether it does"
    )


def _check_tag_versions(
    root: Path,
    report: Report,
    existing: frozenset[str],
    rows: Mapping[str, int],
    stale: frozenset[str],
    stale_line: int,
) -> None:
    """Hold every release tag to the version its own tree declares (`PL-YKSD`).

    `check_tags` reads which tag *names* exist, and a name cannot show where its
    tag points. So a tag pushed at the wrong commit read as tagged to every
    check this project has: `v0.5.3` was pushed before its release merged, onto
    the commit before its own, whose `pyproject.toml` still declared 0.5.2, and
    `make check` stayed green across it. `bin/docket release` refuses to cut the
    next version only while the previous one is *untagged*, so nothing stood
    between that tag and a release cut on top of it.

    Unlike an absent tag, a present one can always be checked however the
    checkout was fetched, because git holds a tag only together with the commit
    it points at. The version is read with the pattern `check_baseline` reads
    the working tree with, so the two cannot disagree about what a version file
    declares. A tree that yields none - the file absent at that commit, or git
    not answering - is declined rather than refused: an empty read cannot say
    whether the file was never there or is only missing from this clone.

    **A tag with notes is held to its cut first, and the version asks nothing
    more of one that fails it** (`PL-QHCW`). The version catches a tag only
    where the commit it landed on declares another number, and a tag pushed
    one merge late declares the right one: `v0.5.3`'s error was the version,
    but a tag on the merge *after* a cut passed it (`PL-KFWL`). The cut is the
    exact question, and its error names the commit to move the tag to, which
    the version's could not. The releases cut before notes were written have
    no cut to be held to and keep the version check alone.
    """
    roadmap_name = roadmap_path(root)
    with GitRunner() as run:
        cuts = _release_cuts(root, existing, run)
        if cuts is None:
            report.declined.append(
                "release tags: git would not say which commit added each release's notes, so "
                "whether each tag sits on the commit that cut its release is unknown"
            )
        else:
            for name in sorted(cuts.off_cut, key=version_key):
                version = name.lstrip("v")
                where = f"{roadmap_name}:{rows[version]}" if version in rows else str(roadmap_name)
                report.errors.append(_off_cut_error(where, name, cuts, root, run))
        _check_tag_version_files(
            root,
            report,
            existing,
            rows,
            stale,
            stale_line,
            cuts.off_cut if cuts else frozenset(),
            run,
        )


def _check_tag_version_files(
    root: Path,
    report: Report,
    existing: frozenset[str],
    rows: Mapping[str, int],
    stale: frozenset[str],
    stale_line: int,
    off_cut: frozenset[str],
    run: Runner,
) -> None:
    """Hold each release tag not already reported off its cut to its tree's version."""
    roadmap_name = roadmap_path(root)
    version_name = load_docket_config(root).version_file
    version_file = root / version_name
    unread_tree = "no release tag was held to the version its tree declares"
    if not version_file.is_file() or not _project_version(version_file, report, unread_tree):
        return
    releases = sorted(
        (
            (name.removeprefix("v"), name)
            for name in existing
            if SEMVER_RE.match(name) is not None and name not in off_cut
        ),
        key=lambda release: version_key(release[0]),
    )
    unread: list[str] = []
    if releases:
        for version, name in releases:
            text = run(["show", f"refs/tags/{name}:{version_name}"], root)
            try:
                declared = version_in(text) if answered(text) else ""
            except ValueError:  # not TOML, which reads nothing rather than no version
                declared = ""
            if not declared:
                unread.append(name)
            elif declared == version:
                if version in stale:
                    report.errors.append(
                        f"{roadmap_name}:{stale_line}: v{version} is named as shipping with a "
                        f"stale version file, but the commit {name} points at declares {declared}; "
                        "take it out of that sentence, which has nothing left to excuse"
                    )
            elif version not in stale:
                commit = run(["rev-parse", "--short", f"refs/tags/{name}^{{commit}}"], root)
                where = f"{roadmap_name}:{rows[version]}" if version in rows else roadmap_name
                report.errors.append(
                    f"{where}: {name} points at "
                    f"{commit.strip() or 'a commit git would not name'}, whose {version_name} "
                    f"declares {declared}. A release tag goes on the commit its release shipped "
                    "from, so move it there - unless `git ls-remote --tags origin` no longer "
                    "lists it, when this clone is keeping a tag deleted on the remote and "
                    f"`git tag -d {name}` is the repair. If that release really did "
                    "ship without its version bump, name it in the Tags statement's sentence on "
                    "versions that shipped with a stale version file instead"
                )
    if unread:
        report.declined.append(
            f"release tags: no version could be read from the {version_name} at "
            f"{', '.join(unread)} - the file is absent, is not TOML or declares none at that "
            "commit, or git did not answer - so whether each sits on its own release's commit "
            "is unknown"
        )


@dataclass(frozen=True)
class _ReleaseCuts:
    """Where each release tag with notes in this tree sits against its cut."""

    #: Tag name -> the commit it points at, in full.
    tagged: Mapping[str, str]
    #: Tag name -> the commit that cut its release, as the tag's own history
    #: records it. A tag on its cut is its own answer and costs no lookup.
    cut: Mapping[str, Cut]
    #: The tags whose commit did not add their own release's notes.
    off_cut: frozenset[str]
    #: Whether a cut was left unnamed because the clone is truncated.
    truncated: bool = False


def _release_cuts(root: Path, names: Iterable[str], run: Runner) -> _ReleaseCuts | None:
    """Each release tag whose notes are in this tree, read against its own cut.

    `release.CUT_FLAGS` applied to the tags themselves: a tag is on its cut
    when its own commit added its own notes file, compared with its first
    parent, and one `notes_added` read answers that for every tag at once. It
    is read from the tags rather than from `HEAD`, because a branch that merged
    the default branch in after a release carries a merge of its own that added
    that release's notes (`release.CUT_FLAGS`, measured).

    A truncated clone is not declined. Its oldest commit reads as adding every
    file, which can pass a tag that is off its cut but can never fail one that
    is on it, so every finding stands. What it can get wrong is *naming* the
    cut, so a tag's own history is asked only where the clone is whole. `None`
    where git would not answer.
    """
    releases = sorted(
        name
        for name in names
        if SEMVER_RE.match(name) is not None and (root / notes_path(name)).is_file()
    )
    if not releases:
        return _ReleaseCuts({}, {}, frozenset())
    resolved = run(["rev-parse", *(f"refs/tags/{name}^{{commit}}" for name in releases)], root)
    commits = resolved.split()
    if not answered(resolved) or len(commits) != len(releases):
        return None
    tagged = dict(zip(releases, commits, strict=True))
    added = notes_added(set(commits), root, runner=run)
    if added is None:
        return None
    off_cut = frozenset(
        name for name, commit in tagged.items() if notes_path(name) not in added.get(commit, ())
    )
    truncated = bool(off_cut) and is_shallow(root, runner=run) is not False
    cut = {
        name: (
            Cut((commit,))
            if name not in off_cut
            else Cut(declined="the clone is shallow")
            if truncated
            else find_cut(name, f"refs/tags/{name}", root, runner=run)
        )
        for name, commit in tagged.items()
    }
    return _ReleaseCuts(tagged, cut, off_cut, truncated)


def _off_cut_error(where: str, name: str, cuts: _ReleaseCuts, root: Path, run: Runner) -> str:
    """Name a tag that is not on its cut, and the commit it belongs on."""

    def described(commit: str) -> str:
        subject = run(["log", "-1", "--format=%h %s", commit], root).strip()
        return f"`{subject}`" if subject else commit[:8]

    notes = notes_path(name)
    cut = cuts.cut[name]
    if cut.commit:
        belongs = f"Its own history says that is {described(cut.commit)}, so move it there"
    elif cuts.truncated:
        belongs = (
            "This clone is shallow, so which commit did is not named here - `git fetch "
            "--unshallow` names it - and the tag moves there"
        )
    elif not cut.known:
        belongs = "git would not say which commit did, and the tag moves there"
    elif not cut.commits:
        belongs = (
            "None in its own history did, so it sits before its release was cut: move it to "
            f"the commit that added {notes} on the default branch"
        )
    else:
        belongs = (
            f"Its own history added that file {len(cut.commits)} times "
            f"({', '.join(commit[:8] for commit in cut.commits)}), so the cut is whichever of "
            "those the release shipped from, and the tag moves there"
        )
    return (
        f"{where}: {name} points at {described(cuts.tagged[name])}, which did not add {notes}. "
        "A release tag goes on the commit that cut its release, the one that added its notes "
        f"(`PL-QHCW`). {belongs} - unless `git ls-remote --tags origin` no longer lists it, "
        f"when this clone is keeping a tag deleted on the remote and `git tag -d {name}` is "
        "the repair"
    )


# --- what a tag's span covers -----------------------------------------------


#: A tag as `%D` prints it under `--decorate=full`: comma-separated ref names,
#: a tag among them written in full. Matching the full form rather than the
#: `tag: ` prefix is what keeps this independent of the log's decoration style.
TAG_REF_RE = re.compile(r"refs/tags/([^,\s]+)")


def span_bullet(identifiers: Sequence[str], number: str, described: str) -> str:
    """One line of a `SPAN_HEADING` section, spelled in one place.

    The error message that asks for the line and any pass that writes one both
    read this, so what a session is told to paste is what the check accepts.
    """
    return f"- {', '.join(identifiers)} - #{number} - described in {described}"


#: The pull request a `span_bullet` line names, read back in its writer's own
#: spelling. The two sit together so that a change to one is made beside the
#: other, and `test_naming_the_closure_in_the_notes_clears_it` holds each to the
#: other by writing one and reading it.
SPAN_BULLET_RE = re.compile(r"^- .+? - #(\d+) - described in .+$", re.M)


def _pull_requests_named(text: str) -> tuple[frozenset[str], tuple[UnreadEntry, ...]]:
    """The pull requests a notes file names as a reference, not as a substring, and its declines.

    Two places name one, each in its writer's grammar: a claimed bullet's tail,
    ` — #N` as `release.reference` writes it and `release.REFERENCED_RE` reads
    it, and a pointer under `SPAN_HEADING`, as `span_bullet` writes it. Read as
    a substring of the file, `#12` was named by any note naming `#123`, so a
    span holding a closure its notes never name passed whenever its number was
    a prefix of a longer one the notes carry (`PL-M9R6`) - every pull request
    under 1000, against the four-digit numbers the notes carry now.

    Each bullet is read whole, through `release.notes_bullets` (`PL-CL8R`), so
    a reference after a title wrapped onto an indented line is named, where a
    line at a time read the title's first line and found none. A bullet carried
    on from the margin is returned second, by its line in the file, since what
    it ends with was not read.
    """
    claims, pointers = notes_claims(text)
    bullets, declined = notes_bullets(claims)
    named = {
        reference.group(1).removeprefix("#")
        for _, _, bullet in bullets
        for _identifier, tail in NOTES_BULLET_RE.findall(bullet)
        if (reference := REFERENCED_RE.search(tail)) and reference.group(1).startswith("#")
    }
    pointed, pointers_declined = notes_bullets(pointers)
    named.update(
        found.group(1)
        for _, _, bullet in pointed
        if (found := SPAN_BULLET_RE.match(bullet)) is not None
    )
    # The pointer half's lines count from its heading; the file's from the top.
    below = claims.count("\n")
    return frozenset(named), declined + tuple(
        UnreadEntry(entry.line + below, entry.why) for entry in pointers_declined
    )


@dataclass(frozen=True)
class _TagSpans:
    """One read of this checkout's tagged history, in the shapes the rule needs."""

    #: Commit hash -> the release version whose span holds it. A span runs from
    #: just after one release tag up to and including the next, which is what
    #: `git describe --contains` resolves a commit to.
    version: Mapping[str, str]
    #: Commit hash -> the pull request number its squash subject names.
    pull_request: Mapping[str, str]
    #: Release version -> the commit that cut it, from `_release_cuts`: the tag's
    #: own commit where it added the notes, as it should, and otherwise the one
    #: the tag's history says did (`PL-QHCW`).
    cut: Mapping[str, str]
    #: The newest release version reachable here, whose span is judged only
    #: once the tree holds a newer release's notes.
    newest: str


def _tag_spans(root: Path) -> _TagSpans | None:
    """This checkout's history in span form, or `None` where git would not answer.

    Read from `HEAD` rather than from the default branch. `HEAD` is the one ref
    that always exists - a bare checkout, a detached CI merge ref, a feature
    branch - and it carries the tagged history in every one of them, where
    `origin/main` is absent in some and stale in others. A feature branch's own
    commits sit past the newest tag and so fall outside every span, which is
    the same answer the default branch would give for them.

    Two passes rather than one, because they ask git different questions: which
    span a commit is in is read off the decorations of a plain log, and which
    commit cut a release is read off the one that *added* its notes file. The
    second is deliberately not inferred from the subject line - "cut v0.4.28"
    is prose, and a release whose subject is worded another way would silently
    lose its exemption. Nor is it read from `HEAD`, where it once was: a branch
    that merged the default branch in has a merge that added every notes file
    since its fork, so it is `_release_cuts`, the one reading of a cut there is.
    """
    history = _git_text(root, "log", "--format=%H%x09%D%x09%s", "--decorate=full", "HEAD")
    if history is None:
        return None
    version: dict[str, str] = {}
    pull_request: dict[str, str] = {}
    names: set[str] = set()
    current = ""
    for line in split_lines(history):
        commit, _, rest = line.partition("\t")
        decoration, _, subject = rest.partition("\t")
        refs = TAG_REF_RE.findall(decoration)
        names.update(refs)
        tagged = [name.removeprefix("v") for name in refs if SEMVER_RE.match(name) is not None]
        if tagged:
            # Newest first, so the tag met here opens the span every older
            # commit belongs to - and the tagged commit is in its own span,
            # which is where `git describe --contains` puts it.
            current = max(tagged, key=version_key)
        if current:
            version[commit] = current
        # Read through `docket`'s one parser, the squash shape alone, as this
        # span was written against (`PL-YYDT`).
        named = subject_pull_request(subject)
        if named is not None and named.squash:
            pull_request[commit] = str(named.number)
    if not version:
        return None

    with GitRunner() as run:
        cuts = _release_cuts(root, names, run)
    if cuts is None:
        return None
    cut = {name.lstrip("v"): release.commit for name, release in cuts.cut.items() if release.commit}
    return _TagSpans(version, pull_request, cut, max(version.values(), key=version_key))


def check_release_row_item_count(root: Path, report: Report) -> None:
    """Hold a version-table row's item count to the items its notes file claims.

    The release session writes both from the same items, by hand, so nothing
    else says whether they agree. On 2026-10-18 all 45 rows that carry a count
    agreed with their notes (`PL-S9X7`). A row with no count cell, or a
    version with no notes file, is skipped, since the older releases have
    neither. The notes are counted by `notes_ids` on the claimed half of the
    file, as `docket.release.notes_by_version` counts them, so a pointer
    bullet naming another release's item is not counted here either.
    """
    roadmap_name = roadmap_path(root)
    roadmap = root / roadmap_name
    if not roadmap.is_file():
        return
    for row in parse_version_table(roadmap.read_text(encoding="utf-8")):
        if row.items is None:
            continue
        notes = root / notes_path(row.version)
        if not notes.is_file():
            continue
        claimed = len(notes_ids(notes_claims(notes.read_text(encoding="utf-8"))[0]))
        if claimed != row.items:
            report.errors.append(
                f"{roadmap_name}:{row.line}: v{row.version} says {row.items} items, "
                f"but {notes_path(row.version)} claims {claimed}; correct whichever is wrong"
            )


def check_tag_span_covers_its_notes(root: Path, report: Report) -> None:
    """Hold each release tag's span to notes that name every closure inside it.

    A tag is what a commit resolves to. `git describe --contains` answers with
    a version, the reader opens that version's notes, and where the work is not
    there the trail stops: the two records disagree about what shipped and
    neither points at the other. Measured over this repository on 2026-09-22,
    20 closing pull requests across 16 tagged spans were in exactly that state,
    against 12 across 11 when `PL-P669` was filed on 2026-09-14 - the mechanism
    is live, and each instance is permanent once the tag is pushed.

    **What this does not decide.** Whether to absorb such work into the release
    that shipped it or let it go to the next release is a judgment `PL-028F`
    settled and left with a person: absorbing means the release narrative
    describes work that cut did not do. So the rule asks for the *pointer* and
    nothing else, and both dispositions satisfy it - `ROADMAP.md` § "Tags"
    carries the reasoning, and `SPAN_HEADING` is where a pointer goes.

    **Two exemptions, each for a stated reason rather than for quiet.**

    The release's own cut is the first. Its pull request is inside its own span
    by construction and is stamped by the *next* release, every time, which
    `ROADMAP.md` already writes down as the one case that recurs on every
    release; it accounted for 40 of the 63 span-crossing closures here. Taking
    it from the commit that added the notes file makes the exemption a fact
    about the tree rather than a reading of prose.

    The newest tag's span is the second, until the tree holds a newer
    release's notes. Before then its strangers are described in a release
    that has not been cut, so a pointer naming one cannot be written, and
    requiring it would turn `make check` red on a state nobody can clear - the
    failure `PL-8HJ2` removed and `check_tags` stays silent on for the same
    reason. The cut that writes the next notes names that release, so the span
    is judged from the cut onward, on the cut's own branch (`PL-JLYG`). Judged
    from the next tag instead, it was skipped at the v0.5.6 cut and turned
    `main` red for every session once the owner pushed the tag.

    **What it cannot see, and says nothing about.** A closure whose squash
    subject carries no `(#N)` is invisible to the span read: 85 of this store's
    recorded pull requests are, all of them numbered 3 to 105, from before the
    convention. A truncated clone declines rather than reporting, because a
    span this checkout cannot walk and one whose notes are genuinely short look
    identical from inside it. So does a span whose notes carry a bullet on from
    the margin, which may name what reads as missing (`PL-CL8R`).
    """
    roadmap_name = roadmap_path(root)
    held = tags(root)
    if not held.known or not held.names:
        return
    # A repository that writes no release notes has nothing for this rule to
    # hold, and is told so by silence rather than by a decline - the reasoning
    # `release.is_untagged` gives for the tag read, one document along:
    # adopting the practice is the project's decision and not this tool's.
    if not (root / NOTES_DIR).is_dir():
        return
    store = _read_store(root)
    if store is None:
        report.declined.append(
            f"{NOTES_DIR}: no tag span was compared against its notes, because the item "
            "store would not read; `bin/docket check` is what reports why"
        )
        return
    spans = _tag_spans(root)
    if spans is None:
        report.declined.append(
            f"{NOTES_DIR}: no tag span was compared against its notes, because git would "
            "not read this checkout's history"
        )
        return

    written = notes_files(root)
    newest_waits = not written or version_key(notes_version(written[-1].name)) <= version_key(
        spans.newest
    )
    commit_of = {number: commit for commit, number in spans.pull_request.items()}
    # Version -> (pull request, the release describing it) -> the items it
    # carried. One line per pull request is what the reader wants, and the
    # release is part of the key because one pull request can close items that
    # two different cuts went on to stamp - #225 closed `PL-SZ56`, stamped by
    # v0.3.0, and `PL-21GS`, stamped twelve releases later by v0.4.15.
    uncovered: dict[str, dict[tuple[str, str], list[Item]]] = {}
    named: dict[str, frozenset[str]] = {}
    unread: dict[str, tuple[UnreadEntry, ...]] = {}
    for item in sorted(store.items.values(), key=lambda entry: entry.identifier):
        # `done` rather than `CLOSED_STATUSES`: a dropped item shipped nothing,
        # so no release's notes owe it a line and its pull request is not a
        # closure the span is missing.
        if item.status != "done" or not item.pr:
            continue
        commit = commit_of.get(item.pr)
        if commit is None:
            continue
        version = spans.version.get(commit)
        if (
            version is None
            or (newest_waits and version == spans.newest)
            or spans.cut.get(version) == commit
        ):
            continue
        notes = root / notes_path(version)
        if not notes.is_file():
            continue
        if version not in named:
            named[version], unread[version] = _pull_requests_named(
                notes.read_text(encoding="utf-8")
            )
        if item.pr in named[version]:
            continue
        described = item.milestone or "a later release"
        uncovered.setdefault(version, {}).setdefault((item.pr, described), []).append(item)

    findings: list[str] = []
    for version in sorted(uncovered, key=version_key):
        # A bullet read short may be the one naming what reads as missing
        # (`PL-CL8R`), so the span is not judged. One read whole can only have
        # named more, so a span with nothing missing needs no such caveat.
        if unread[version]:
            report.declined.extend(
                f"{notes_path(version)}:{entry.line}: v{version}'s tag span was not compared "
                f"against its notes, since a bullet there was not read whole: {entry.why}"
                for entry in unread[version]
            )
            continue
        rows = sorted(uncovered[version], key=lambda row: (int(row[0]), row[1]))
        numbers = sorted({number for number, _ in rows}, key=int)
        bullets = [
            "`"
            + span_bullet(
                tuple(entry.identifier for entry in uncovered[version][row]), row[0], row[1]
            )
            + "`"
            for row in rows
        ]
        findings.append(
            f"{notes_path(version)}: "
            + _plural(len(numbers), "closing pull request", "closing pull requests")
            + " inside v"
            + version
            + "'s tag span "
            + ("is", "are")[len(numbers) > 1]
            + " named nowhere in its notes ("
            + ", ".join(f"#{number}" for number in numbers)
            + f"), so `git describe --contains` resolves {('it', 'them')[len(numbers) > 1]} to a "
            "release whose own account does not reach the work. Add "
            + ("it", "them")[len(numbers) > 1]
            + f' under a "{SPAN_HEADING}" heading - '
            + "; ".join(bullets)
            + f" - rather than among what the cut stamped; {roadmap_name} "
            '§ "Tags" is why the two records differ'
        )

    # Only a finding a truncated checkout could have invented is withheld, and
    # only when there is one - the shape `check_tags` settled on, for the same
    # reason: declining on `is_shallow` alone would silence this everywhere it
    # runs, including the clones that have since fetched and can answer.
    truncated = is_shallow(root)
    if findings and truncated is not False:
        report.declined.append(
            f"{NOTES_DIR}: "
            + (
                "the checkout is a shallow clone"
                if truncated
                else "git cannot say whether this checkout is complete"
            )
            + f", so the {_plural(len(findings), 'span', 'spans')} whose notes look short here "
            "cannot be told from a span this clone cannot walk; "
            "`git fetch --unshallow --tags` makes the question answerable"
        )
    else:
        report.errors.extend(findings)


def _project_version(pyproject: Path, report: Report, unread: str) -> str:
    """The version `pyproject` declares, or empty where it declares none or cannot be read.

    A file that is not TOML is declined, naming `unread`: `version_in` raises
    `tomllib.TOMLDecodeError` for it, which raised here ended the whole run
    rather than the check reading it (`PL-5M36`).
    """
    try:
        return version_in(pyproject.read_text(encoding="utf-8"))
    except ValueError as error:  # `TOMLDecodeError`, or bytes that are not UTF-8
        report.declined.append(f"{pyproject.name}: cannot be read as TOML ({error}), so {unread}")
        return ""


def _is_path_citation(token: str) -> bool:
    if not token or not re.fullmatch(r"[\w./*{},-]+", token):
        return False
    # Slashes and dots alone - `/`, `./`, `../` - name a place by position
    # rather than a file by name. Read from the repository root, `/` would cite
    # the root itself, which is always there, and `../` would climb out of it.
    if not token.strip("./"):
        return False
    if token.endswith("/"):
        return True
    return PurePosixPath(token).suffix in PATH_SUFFIXES


def _repository_paths(token: str) -> Iterator[str]:
    """Each repository-relative path `token` may name, under every root in `PATH_ROOTS`.

    **A leading `/` is the repository root**, as `.gitignore` and the `paths:`
    frontmatter of `.claude/rules/` read one, and never the filesystem's. Read
    the other way, `/docs/MODEL.md` was reported dangling on a file that is
    there, and `/root/.ccr/README.md` asked the machine running the check: a
    session's root could stat it and CI's unprivileged runner could not, so one
    commit gave two verdicts, and `#880` failed in CI after passing in the
    session that wrote it (`PL-H0CF`). A path whose `..` climbs out of the
    repository is not yielded at all, for the same reason: it names nothing
    here, and asking whether it exists would ask the machine again. So whether
    a citation resolves depends on the tree alone - the same commit answers the
    same way as root, as an unprivileged user, and on a machine where the
    outside path is not there.
    """
    for prefix in PATH_ROOTS:
        for candidate in _expand_braces(token.lstrip("/")):
            path = posixpath.join(prefix, candidate) if prefix else candidate
            normal = posixpath.normpath(path)
            if normal != ".." and not normal.startswith("../"):
                yield path


def _resolves(root: Path, basenames: frozenset[str], token: str) -> bool:
    patterned = "*" in token or "{" in token
    for path in _repository_paths(token):
        if patterned:
            try:
                if next(root.glob(path), None) is not None:
                    return True
            except (ValueError, NotImplementedError):
                # `Path.glob` raises rather than returning nothing for some
                # token shapes prose legitimately contains: older interpreters
                # raise `ValueError` on a bare `**` component, and an absolute
                # pattern (`/docs/*.md`) gave `NotImplementedError: Non-relative
                # patterns are unsupported` until `_repository_paths` began
                # reading a leading `/` from the repository root. Unguarded,
                # one such token aborted the whole run on a traceback, so
                # `doc_check check` reported nothing at all about the several
                # hundred citations around it. A token glob cannot parse is a
                # citation that does not resolve, which is a finding about that
                # line and not a reason to stop (`PL-0M7L`).
                continue
        # `os.path.exists`, never `Path.exists`, and a later tidy-up must not
        # put the method back. Through 3.13 `Path.exists` re-raises every
        # `OSError` it does not read as "absent" - it ignores ENOENT, ENOTDIR,
        # EBADF and ELOOP and lets EACCES out - so a token naming a path this
        # process may not stat aborted the whole run on a traceback. 3.14
        # rewrote the method to `return os.path.exists(self)`, which is what
        # this line calls directly, so the verdict stops depending on which
        # interpreter ran the check. That dependency is why the defect reached
        # `main` twice while `make check` was green in the session that wrote
        # the line: a session runs as root on 3.14, CI runs `python3
        # tools/doc_check.py check` unprivileged on the system one, and there
        # it reported nothing at all about any of the ~1,279 citations around
        # it (`PL-D1NT`). It is the guard the `glob` branch above has carried
        # since `PL-0M7L`: a path the process cannot stat is a citation that
        # does not resolve, which is a finding about that line and not a
        # reason to stop. Every path asked about is inside the repository
        # since `PL-H0CF`, so the refused stat is now a checkout's own oddity
        # rather than the ordinary case.
        elif os.path.exists(root / path):
            return True
    # A bare filename (`parameters.py`, `WORKING_NOTES.md`) is written without
    # a directory throughout the documentation; resolve it by name.
    return "/" not in token and token in basenames


#: What `git check-ignore` returns when at least one path it was given is
#: ignored. Exit 1 says none were; anything else - 128 for a malformed path or
#: a directory that is not a checkout - is git declining to answer rather than
#: answering no.
GIT_PATH_IS_IGNORED = 0


def _covered_by_gitignore(root: Path, token: str) -> bool:
    """Whether `.gitignore` covers `token`, so its absence is deliberate.

    A generated directory is documentation's to name: `docs/worker.md` names
    `out/` precisely *because* nothing tracks it. Requiring it to exist made
    one tree give two verdicts - green wherever a session had just rendered a
    screenshot into it, red in CI on identical content - so this is what stops
    a citation's verdict depending on the working tree for every path git will
    never carry. A path that is merely *uncommitted* is a different case and
    still errors: CI's disagreement about that one resolves when it is
    committed, where a path `.gitignore` covers can only ever be answered
    wrongly in one of the two places (`PL-MXSL`).

    Asked of git rather than read out of `.gitignore`, because this file's
    negations are load-bearing - `.vscode/*` excludes the directory's contents
    and `!.vscode/settings.json` re-admits the tracked project settings - and a
    reader of the anchored directory rules alone would call that file exempt.

    One call per token, never `git check-ignore --stdin`: the batch form aborts
    on the first malformed path and then reports nothing about the rest.
    Measured 2026-09-15 over this store's own citations, it died on `fatal: //:
    '//' is outside repository` after 49 answers of 1,549 - `PL-0M7L`'s shape,
    one token's failure swallowing every other citation's verdict.

    Every way git can decline - no checkout, a path outside the repository, no
    git on `PATH` - is read as *not* covered, so the citation is reported as it
    would have been without this exemption. It is granted only on a positive
    answer, and for a braced token only when every expansion has one. A
    leading `/` is the repository root here as in `_repository_paths`, so
    `/out/` asks about `out/` rather than about the filesystem's root.
    """
    for candidate in _expand_braces(token.lstrip("/")):
        # The exit status itself is the verdict, three ways, so it is read
        # off the call rather than through `GitCall.answer`'s classification.
        ignored = call_git(["check-ignore", "-q", "--no-index", "--", candidate], root)
        if ignored.code != GIT_PATH_IS_IGNORED:
            return False
    return True


def _normalized(text: str) -> str:
    """`text`, read with its container markers blanked, on one line.

    So a quotation that wrapped compares as written. A quotation inside a `>`
    blockquote carries the marker of every line it wraps onto, so
    `§ "v0.5.1 -\n> the interface moves to Qt"` once compared as
    `v0.5.1 - > the interface moves to Qt` and failed against a heading that
    is there (`PL-V13T`). Every caller hands this text `_unmarked_text` has
    blanked, which drops a `>` that marks a block quote and keeps one that is
    a paragraph's text (`PL-NNVJ`).
    """
    return " ".join(text.split())


#: Typography that differs between a passage and an honest quotation of it.
#: This project writes both `-` and `—` for the same dash, and a quotation
#: copied by hand settles on one of them; the passage is still there, so a
#: mismatch here is a false error rather than a stale citation.
TYPOGRAPHY = str.maketrans({"—": "-", "–": "-", "’": "'", "‘": "'", "“": '"', "”": '"'})


def _comparable(text: str) -> str:
    """`text` reduced to what a faithful quotation must still match."""
    return _normalized(text).translate(TYPOGRAPHY).casefold()


def _without_emphasis(text: str) -> str:
    """`text` with the delimiters of each emphasis CommonMark pairs in it removed.

    A faithful quotation leaves out a passage's bold and italic marks, so
    `writes **nothing**` is quoted as "writes nothing" (`PL-RX0W`). Only the
    delimiters CommonMark 0.31.2 § 6.2 pairs are removed, as `emphasis` pairs
    them, so a `*` in arithmetic and a `_` inside a name stay. A delimiter
    inside a code span pairs with nothing.
    """
    runs = emphasis(text, [span.span() for span in code_spans(text)])
    cuts = sorted(
        cut
        for run in runs
        for cut in ((run.start, run.start + run.width), (run.end - run.width, run.end))
    )
    kept: list[str] = []
    position = 0
    for start, end in cuts:
        kept.append(text[position:start])
        position = end
    kept.append(text[position:])
    return "".join(kept)


def _comparable_statements(text: str) -> str:
    """The document `text` as `_comparable` reads it, one statement to a line, and each fence.

    A quotation is one line once `_normalized`, so it stands in this only
    where one statement holds it, a soft break inside one crossed. A heading
    and the paragraph under it, or two paragraphs, are two (CommonMark 0.31.2
    § 4.2, § 4.8), so a quotation spliced across them is words no reader of
    the file meets together, which a test of containment in the whole file
    collapsed into one string passed (`PL-Q8LJ`). A fence is no statement, but
    its words are the file's, so each is one too, read whole.
    """
    lines = split_lines(text)
    blanked = split_lines(_unmarked_text(text))
    blocks = read_blocks(_body_lines(lines)).blocks
    fences = [(block.start, block.end) for block in blocks if block.kind == FENCE]
    return "\n".join(
        _comparable(_without_emphasis("\n".join(blanked[first:end])))
        for first, end in [*_statements(lines), *fences]
    )


def _headings(text: str) -> list[str]:
    """Every title a citation may name: headings and `**Bold.**` markers.

    Both are section titles here, and the documents cite them the same way.
    Restricting this to `#` lines did not narrow the check, it made it wrong
    in one direction only - `docs/MODEL.md` cites its own `**The chart's
    vertical range is denominated in MAC, and fixed.**` marker, and that
    citation is correct.

    A marker opens a statement of prose, as `statement_lines` reads one, and
    is read past its containers' markers (`PL-8NPN`). A bold run a soft break
    carries onto a line's start is its paragraph's own text, and was read as a
    title of its own (`PL-VQBY`); an indented code block's is a literal.
    """
    blanked = _unmarked(text, _body_lines(split_lines(text)))
    markers = (
        MARKER_RE.match(blanked, start, end) for start, end in _statement_offsets(text, PROSE)
    )
    return _hash_headings(text) + [_normalized(match["title"]) for match in markers if match]


def _hash_headings(text: str) -> list[str]:
    """Every heading's title: the titles that name a section and nothing else.

    A `**Bold.**` marker is often a paragraph's or a bullet's lead sentence as
    well, so quoting one is not by itself a citation of a section (`PL-FKH6`),
    and GitHub gives one no anchor for a link to name.

    Read from `markdown.headings`, as docket's walkers read theirs (`PL-HKHP`),
    so a heading is one where CommonMark renders one: a `#` line inside a fence
    or a comment is none, and a setext heading is one. Read a line at a time, a
    shell sample's `# make sure the venv exists` answered a `§` citation of it
    (`PL-T1X0`). A frontmatter block is read as nothing, as GitHub renders it
    as a table where CommonMark reads its closing `---` as a setext underline.
    """
    return [
        heading.title for heading in read_headings(_body_lines(split_lines(text))) if heading.title
    ]


def _cites_heading(term: str, headings: Iterable[str]) -> bool:
    """Whether `term` names one of `headings`.

    Three tolerances, all for writing that is correct as written. A prefix
    ending on a word boundary counts, because prose shortens a long heading
    (`"Completed: v0.2.0"` for `Completed: v0.2.0 - isoflurane and
    desflurane`). Sentence punctuation closed inside the quotation marks is
    ignored, because `See "Known limitations."` is ordinary US style, not a
    citation of a heading that ends in a period. And `TYPOGRAPHY` is folded on
    both sides, because a title copied by hand settles on one of the dashes
    this project writes and the heading is still there. A rename still breaks
    the match, which is the drift being checked.
    """
    term = term.translate(TYPOGRAPHY)
    candidates = {term, term.rstrip(" .,;:")}
    return any(
        heading == candidate
        or (heading.startswith(candidate) and heading[len(candidate)] in " -:,;")
        for heading in (title.translate(TYPOGRAPHY) for title in headings)
        for candidate in candidates
        if candidate
    )


def _code_spans(text: str) -> list[re.Match[str]]:
    """Every code span in a document as docket reads one, in document order.

    The prose is read a statement at a time (`_statement_spans`), so a span
    wrapped across a line break is one span, a fence's own backticks open none,
    and a stray backtick pairs with nothing past its own statement. CommonMark
    reads no span inside a fence, but a package map's comments cite paths as
    spans, and the maps in `docs/ARCHITECTURE.md` and `docs/apparatus.md` are
    held to the tree that way; so each fenced line is then read on its own, as
    every line was read before
    `PL-9L39`. Offsets are the document's either way.
    """
    spans = list(_statement_spans(text))
    fenced = _fenced_lines(text)
    offset = 0
    for index, line in enumerate(split_lines(text, keepends=True)):
        if index in fenced:
            spans.extend(code_spans(text, offset, offset + len(line.removesuffix("\n"))))
        offset += len(line)
    return sorted(spans, key=lambda span: span.start())


def _statement_spans(text: str) -> Iterator[re.Match[str]]:
    """Every code span outside a fence, each read within the statement holding it.

    A statement as `markdown.statement_lines` cuts one: CommonMark keeps a
    span inside its paragraph (0.31.2 § 6.1), and a paragraph ends at a list
    item's, a block quote's, a heading's or an HTML block's start as well as at
    a blank line, which `code_spans` alone reads only the last of. Read
    across them, a stray backtick paired with the next statement's first span
    and blanked the prose between them (`PL-FP7J`). A prose statement's spans
    are `_inline`'s, so an escaped backtick opens none and a backtick inside an
    autolink or raw HTML is that construct's (`PL-R417`); an indented code
    block's and an HTML block's, which CommonMark reads none in, are read with
    `code_spans`, as a fence's lines are. Offsets are the document's.
    """
    spans = list(_inline(text)[0])
    for start, end in _statement_offsets(text, (CODE, HTML)):
        spans.extend(code_spans(text, start, end))
    yield from sorted(spans, key=lambda span: span.start())


def _links(text: str) -> tuple[Link, ...]:
    """Every inline link and image in a document's prose, as `_inline` reads them, in order."""
    return _inline(text)[1]


@lru_cache(maxsize=8)
def _inline(text: str) -> tuple[tuple[re.Match[str], ...], tuple[Link, ...]]:
    """The code spans, links and images of a document's prose, a statement at a time.

    Each statement is `_statements`' (`PL-R417`): a front matter's key, read as
    written, or a statement of the body, read by `_InlineReader` with its
    containers' markers blanked (`_unmarked`), so a line a soft break carries a
    destination or a span onto opens with whitespace alone. A table row is read
    a cell at a time, split where GitHub Flavored Markdown 0.29 § 4.10 splits it
    before reading any inline - at each pipe no backslash escapes, a pipe inside
    a code span included - and a cell past the header's last is dropped, as GFM
    drops it. Offsets are `text`'s, and each span's groups are the blanked
    text's.
    """
    lines = split_lines(text)
    body = _body_lines(lines)
    blanked = _unmarked(text, body)
    starts = [0]
    for line in split_lines(text, keepends=True):
        starts.append(starts[-1] + len(line))
    holder = {
        index: block
        for block in read_blocks(body).blocks
        for index in range(block.start, block.end)
    }
    reader = _InlineReader(blanked)
    for first, end in _statements(lines, PROSE):
        block = holder.get(first)
        if block is None or block.kind != TABLE:
            reader.read(starts[first], starts[end])
            continue
        header = len(_cells(blanked, starts[block.start], starts[block.start + 1]))
        for start, stop in _cells(blanked, starts[first], starts[end])[:header]:
            reader.read(start, stop)
    return tuple(reader.spans), tuple(reader.links)


def _unmarked(text: str, lines: Sequence[str]) -> str:
    """`text` with the container markers `lines` holds blanked, as `markdown.unmarked` blanks them.

    `lines` is the document `text` was cut from, read as Markdown, and `text`
    may have blanked some of its own text since, every line at its length.
    Offsets are kept, so an offset into it is one into `text`.
    """
    raw = split_lines(text, keepends=True)
    blanked = unmarked(lines, [line.removesuffix("\n") for line in raw])
    return "".join(line + piece[len(line) :] for line, piece in zip(blanked, raw, strict=True))


@lru_cache(maxsize=1024)
def _unmarked_text(text: str) -> str:
    """`text`, a document, with its body's container markers blanked and its front matter kept.

    What every reader of a phrase matches in, so a gap read across a soft break
    meets the next line's words where CommonMark does (`SOFT_BREAK`). Kept for
    as many documents as the tree holds, since `sweep` asks `mentions` of
    every document once per token.
    """
    return _unmarked(text, _body_lines(split_lines(text)))


def _cells(text: str, start: int, end: int) -> list[tuple[int, int]]:
    """The cells of the table row from `start` to `end`, as offsets, as `cell_spans` splits it."""
    return [(start + first, start + stop) for first, stop in cell_spans(text[start:end])]


def _statement_offsets(
    text: str, kinds: Collection[str] | None = None
) -> Iterator[tuple[int, int]]:
    """Each statement `_statements` cuts `text` into, as offsets into it."""
    starts = [0]
    for line in split_lines(text, keepends=True):
        starts.append(starts[-1] + len(line))
    for first, end in _statements(split_lines(text), kinds):
        yield starts[first], starts[end]


def _statements(
    lines: Sequence[str], kinds: Collection[str] | None = None
) -> list[tuple[int, int]]:
    """Each statement of a document, as its span of `lines`: its front matter's, then its body's.

    A YAML front matter is no Markdown (`PL-WX79`). Read as Markdown, its keys
    were one paragraph its closing `---` underlines as a setext heading
    (CommonMark 0.31.2 § 4.3), so a backtick or a quotation one key left open
    paired with the next key's and a date in one key dated another's sentence.
    Each key's value is one statement, where `docket.frontmatter.statements`
    ends it, as `docket.instructions` reads one (`PL-2MLT`), and the body is
    `markdown.statement_lines`' from the line after the front matter closes,
    every line in its place. A front matter's statements are prose, so `kinds`
    naming none of `PROSE` reads none of them.
    """
    fence = frontmatter_closing(lines)
    body = statement_lines(_body_lines(lines), kinds)
    if fence is None or (kinds is not None and not PROSE & frozenset(kinds)):
        return list(body)
    # Set aside on purpose: a block `keys` cannot split comes back a line at a
    # time, every line kept, and is named where a reading of it decides
    # anything - `tools/rules_paths_check.py` refuses a rule's, and `docket
    # check` declines an instruction file's dated sentences by name. An item's
    # front matter, and a pull request body record's, is `docket.model`'s
    # grammar rather than YAML, a field to a line, which is the reading it gets.
    spans, _declined = frontmatter_statements(lines[1:fence])
    return [*((1 + a, 1 + b) for a, b in spans), *body]


def _fenced_lines(text: str) -> frozenset[int]:
    """The index of every line of a closed fence in a document, read in its body alone."""
    return fenced_lines("\n".join(_body_lines(split_lines(text))))


def without_fences(text: str) -> str:
    """`text` with every line of a closed fence blanked, a fence read in its body alone.

    `docket.fences.without_fences`, but a YAML front matter is kept as written,
    since a fence-shaped line in a block scalar is none (`PL-WX79`). Offsets and
    line breaks are kept.
    """
    start = sum(len(line) for line in split_lines(text, keepends=True)[: _frontmatter_end(text)])
    return text[:start] + blank_fences(text[start:])


def _as_passage(text: str) -> str:
    """`text`, a passage cut from a file, as a document that opens no front matter.

    Only a whole file opens with one. A run of comment, a docstring or a
    brief's body read as a document opened one wherever its first line was
    `---` and a later line closed it, so the comment between two `# ---`
    banners was read a line at a time and a date on its next line dated none
    of its sentence (`PL-WX79`). That first line holds nothing a reader here
    looks for - CommonMark 0.31.2 reads it as a thematic break (§ 4.1), or
    indented four columns as a line of code - so it is blanked, its length
    kept, and offsets and line numbers stay `text`'s.
    """
    lines = split_lines(text)
    if frontmatter_closing(lines) is None:
        return text
    return " " * len(lines[0]) + text[len(lines[0]) :]


def _as_passages(pieces: Iterable[tuple[int, str]]) -> Iterator[tuple[int, str]]:
    """Each of `pieces`, a row and the text cut from a file there, as `_as_passage` reads it."""
    for row, piece in pieces:
        yield row, _as_passage(piece)


def _statement_matches(
    pattern: re.Pattern[str], text: str, kinds: Collection[str] | None = None
) -> Iterator[re.Match[str]]:
    """Every match of `pattern` in `text`, each within one statement `statement_lines` cuts.

    Matched with the statement's offsets as its bounds, so a `GAP` or a
    `QUOTATION_CHAR` read across a soft break stops where CommonMark 0.31.2 ends
    the paragraph, heading or table row holding it - at a block quote, a setext
    underline or a table opening under it, and on an ATX heading's own line -
    rather than wherever the next line's opening allows one to go on
    (`PL-Z1R7`). A fence is no statement, so none is read in one. Each match
    keeps its bounds as `pos` and `endpos`, so a reader looking before or after
    it - a mark, a direction - looks no further than its statement. Each is
    matched in `_unmarked_text(text)`, which is its `string`, so a reader
    looking around it reads that rather than `text` (`PL-NNVJ`). Offsets are
    `text`'s.
    """
    blanked = _unmarked_text(text)
    for start, end in _statement_offsets(text, kinds):
        yield from pattern.finditer(blanked, start, end)


def _unresolved(token: str) -> str:
    """What a path citation that resolves to nothing is told, after its token.

    A path outside the repository is told so rather than that it does not
    exist, which on the machine running the check may be false: the container
    paths sessions cite, `/root/.ccr/README.md` among them, are there (`PL-H0CF`).
    """
    if token.startswith("/"):
        where = "which is not in this repository - a leading `/` is read from its root"
    elif next(_repository_paths(token), None) is None:
        where = "which is outside this repository"
    else:
        where = "which does not exist"
    return (
        f"{where}; a sentence naming it as absent, planned, deleted or elsewhere says so "
        f"under its paragraph: <!-- absent: {token} -->"
    )


def check_citations(root: Path, documents: dict[Path, str], report: Report) -> None:
    """Resolve every path and section a documentation file cites, and a live brief's paths.

    A brief's path citations are held to a narrower rule than a document's,
    which `_check_brief_paths` gives with the measurement behind it.
    """
    basenames = frozenset(path.name for path in _walk(root))
    headings = {path: _headings(text) for path, text in documents.items()}
    every_heading = [heading for titles in headings.values() for heading in titles]

    for path, text in documents.items():
        absent = _absent_paths(root, basenames, path, text, report)
        for match in _code_spans(text):
            token = match["content"]
            if not _is_path_citation(token) or _resolves(root, basenames, token):
                continue
            line = _line_of(text, match.start())
            if token in absent.get(line, ()):
                continue
            # Asked only of a citation that has already failed to resolve, so a
            # run with nothing wrong in it starts no subprocess at all and the
            # cost falls on the findings rather than on the 1,279 citations
            # around them.
            if _covered_by_gitignore(root, token):
                continue
            report.errors.append(f"{path}:{line}: cites `{token}`, {_unresolved(token)}")

        # A link is inline content of a paragraph, a heading or a table cell
        # (CommonMark 0.31.2 § 6.3), so it is read from the prose alone: a
        # link-shaped line in a fence, an HTML block or a code span is a literal,
        # and was held to the tree as a link (`PL-M2J4`). Each statement is the
        # document's, so a code span on a line of its own ends no paragraph a
        # link stands in (`PL-Q6HR`).
        for link in _links(text):
            target = link.target
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative, _, anchor = target.partition("#")
            line = _line_of(text, link.start)
            resolved = (root / path).parent / relative if relative else root / path
            if not resolved.exists():
                report.errors.append(f"{path}:{line}: links to {target}, which does not exist")
                continue
            if anchor:
                # GitHub anchors a heading and nothing else, so a `**Bold.**`
                # marker that answers a `§` citation answers no anchor: a link
                # naming one opens the page at its top (`PL-T1X0`).
                linked = resolved.relative_to(root)
                linked_text = documents.get(linked)
                if linked_text is None:
                    linked_text = resolved.read_text(encoding="utf-8")
                # GitHub anchors a heading a block quote or a list item holds
                # too, so every heading is read (`PL-9XP0`).
                lines = _body_lines(split_lines(linked_text))
                titles = [heading.title for heading in read_headings(lines, nested=True)]
                if unquote(anchor).lower() not in _github_slugs(titles):
                    report.errors.append(
                        f"{path}:{line}: links to {target}, but {linked} has no such heading"
                    )

        # A fence or a code span holds a literal - an example, a command, the
        # form being described - and a literal is not a claim about the tree. So
        # do an indented code block and an HTML block, a literal or a comment,
        # and the section readers read the blocks `PROSE` names (`PL-KR6M`).
        prose = without_fences(text)
        spans = [(span.start(), span.end()) for span in _statement_spans(text)]

        for match in _statement_matches(CITATION_RE, prose, PROSE):
            # A code-spanned source directly before the mark says where the
            # section lives: a document, or an item brief no heading here
            # answers, and `check_quoted_sources` holds either by containment.
            before = match.string[max(match.pos, match.start() - 200) : match.start() + 1]
            if _inside(match.start(), spans) or QUALIFIED_RE.search(before):
                continue
            line = _line_of(prose, match.start())
            if match["unclosed"] is not None:
                report.errors.append(_unclosed(f"{path}:{line}", "this §", "the section it names"))
                continue
            term, same_file = _cited_section(match.string, match)
            if same_file:
                if not _cites_heading(term, headings[path]):
                    report.errors.append(
                        f'{path}:{line}: cites section "{term}" in this file, which has no '
                        "such heading"
                    )
            elif not _cites_heading(term, every_heading):
                report.errors.append(
                    f'{path}:{line}: cites section "{term}", which no documentation file has '
                    "(§ names a section of these documents; write an outside source's "
                    "section without the mark)"
                )

        for match in _statement_matches(UNMARKED_CITATION_RE, prose, PROSE):
            before = match.string[max(match.pos, match.start() - 200) : match.start() + 1]
            if (
                _inside(match.start(), spans)
                or MARKED_RE.search(before)
                or QUALIFIED_RE.search(before)
            ):
                continue
            if match["unclosed"] is not None:
                opener = match.group(0).split(None, 1)[0]
                report.advisories.append(
                    _unclosed(
                        f"{path}:{_line_of(prose, match.start())}",
                        f'this "{opener}"',
                        "whether it names a section",
                    )
                )
                continue
            term, same_file = _cited_section(match.string, match)
            if _cites_heading(term, headings[path] if same_file else every_heading):
                report.advisories.append(
                    f'{path}:{_line_of(prose, match.start())}: "{term}" names a section '
                    f'without the mark, so a rename of it would pass unreported; write § "{term}"'
                )

    _check_brief_paths(root, basenames, report)


def _check_brief_paths(root: Path, basenames: frozenset[str], report: Report) -> None:
    """Hold each live brief's path citations to the files this repository has deleted.

    **Only a path the tree once held is a finding** (`PL-1RTM`, `PL-3NKZ`). A
    brief names files that do not exist for reasons a standing document does
    not: the module its work will create, an example (`tools/x_check.py`), a
    file in another repository or on the container. Measured 2026-10-03, 95
    of the 1,843 path citations in live briefs resolved to nothing, and the
    `touches` exemption `PL-3NKZ` proposed would have excused 11 of them - so
    holding them as the documents are held fires about 80 times on sentences
    that are right. 22 named a path git history holds and the tree does not,
    which is a record rather than a reading of intent: the file existed and
    went, so the citation was true once and the brief is now wrong about where
    to look, or names the deletion on purpose and says so with the
    `absent:` marker the documents use. A path no commit ever held - a
    misspelling among them - is not judged, which is the trade.

    Live briefs only, and a fence is not read, as in `check_line_citations`:
    a closed brief records the tree its work was done against
    (`.claude/rules/citation-drift.md`), and an item reporting a stale citation
    must be able to show it. A checkout whose history git cannot read, or
    holds only part of, says so in `declined` rather than reading as clean.
    """
    deleted: dict[str, str] | None = None
    asked = False
    unjudged = 0
    for path, raw in _live_item_briefs(root):
        text = without_fences(raw)
        absent = _absent_paths(root, basenames, path, text, report)
        # A front-matter field at a time, and the body after them (`PL-CZ28`).
        spans = (
            (first + _line_of(piece, match.start()) - 1, match["content"])
            for first, piece in _brief_pieces(raw, path, "path citation", report.declined)
            for match in _statement_spans(piece)
        )
        for line, token in spans:
            if not _is_path_citation(token) or _resolves(root, basenames, token):
                continue
            if token in absent.get(line, ()):
                continue
            if not asked:
                asked, deleted = True, _deleted_paths(root)
            commit = None if deleted is None else _deleted_by(token, deleted)
            if commit is None:
                unjudged += 1
                continue
            if _covered_by_gitignore(root, token):
                continue
            report.errors.append(
                f"{path}:{line}: cites `{token}`, which {commit} removed from the tree; point it "
                "where the content went, or where the brief names the removal on purpose, say "
                f"so under its paragraph: <!-- absent: {token} -->"
            )
    if not unjudged:
        return
    count = _plural(unjudged, "path citation", "path citations")
    if deleted is None:
        report.declined.append(
            f"item briefs: git could not read this checkout's history, so {count} in live "
            "briefs that resolve to nothing were not checked for a file the tree once held"
        )
    elif (shallow := is_shallow(root)) is not False:
        why = (
            "the checkout is a shallow clone"
            if shallow
            else "git cannot say whether this checkout is complete"
        )
        report.declined.append(
            f"item briefs: {why}, so {count} in live briefs that resolve to nothing were "
            "checked against the "
            "history it holds; a file removed before that is not reported, and `git fetch "
            "--unshallow` reads the rest"
        )


def _deleted_paths(root: Path) -> dict[str, str] | None:
    """Every path a commit on this checkout's history deleted, to the newest such commit.

    `None` where git cannot answer. `--no-renames`, so a move is read as what
    it is to a citation of the old path - that path deleted. A path deleted and
    later restored is in the tree again, so a citation of it resolves before
    this is asked.
    """
    text = _git_text(
        root, *changed_path_args("log", "--diff-filter=D", "--name-only", "--format=%x1e%h", "HEAD")
    )
    if text is None:
        return None
    deleted: dict[str, str] = {}
    for commit, paths in logged_fields(text):
        for gone in paths:
            deleted.setdefault(gone, commit)
    return deleted


def _deleted_by(token: str, deleted: Mapping[str, str]) -> str | None:
    """The newest commit that deleted what `token` cites, or `None` where none did.

    Read the way `_resolves` reads a citation: under every root in
    `PATH_ROOTS`, a directory answered by any file deleted under it, and a bare
    filename by any deleted file of that name. A pattern is not matched - it
    cites a set rather than a file - so a glob whose every match went is not
    reported.
    """
    if "*" in token:
        return None
    for path in _repository_paths(token):
        normal = posixpath.normpath(path)
        if path.endswith("/"):
            commit = next((c for gone, c in deleted.items() if gone.startswith(normal + "/")), None)
        else:
            commit = deleted.get(normal)
        if commit is not None:
            return commit
    if "/" in token:
        return None
    return next((c for gone, c in deleted.items() if PurePosixPath(gone).name == token), None)


def _absent_paths(
    root: Path, basenames: frozenset[str], path: Path, text: str, report: Report
) -> dict[int, set[str]]:
    """The paths each line may name as absent, by 1-based line, from `absent:` markers.

    Each marker covers the paragraph it sits under, as a `provenance:` marker
    does, and is held to its own claim: every path it names must be absent -
    so a planned tool that gets built, or a deleted file that comes back, fails
    until the sentence and the marker are updated with it - and cited in that
    paragraph, so a marker left behind by a reworded sentence fails rather than
    lingering. A path `.gitignore` covers is not held absent, since its
    presence differs between a working tree and CI. A marker shown in a fence
    is the format being shown, and is not read. Nor is one in a front matter,
    whose blocks are read from the body alone: a front matter is YAML, where
    `<!--` opens no comment, and read as Markdown one a value left open hid the
    body's paragraphs down to the next `-->` (`PL-WX79`). Nor is one closing a
    comment opened above it, which is that comment's (`_marker_lines`,
    `PL-7454`). One written anywhere a marker is not read is refused by name
    (`_misplaced_markers`, `PL-Y6LP`).
    """
    lines = _body_lines(split_lines(without_fences(text)))
    split = _split_markers(lines)
    openings = _marker_lines(lines)
    for index, kind in _misplaced_markers(lines, _without_code(text)).items():
        if kind == "absent":
            report.errors.append(_misplaced_marker(path, index + 1, kind))
    declared: dict[int, set[str]] = {}
    for index, line in enumerate(lines):
        if split.get(index) == "absent":
            report.errors.append(_split_marker(path, index + 1, "absent"))
        if index not in openings:
            continue
        marker = ABSENT_MARKER_RE.match(line.strip())
        if marker is None:
            continue
        start, end = _marked_span(lines, index)
        cited = {span["content"] for span in code_spans("\n".join(lines[start:end]))}
        for token in marker.group("paths").split():
            if token not in cited:
                report.errors.append(
                    f"{path}:{index + 1}: marks `{token}` absent, but the paragraph above does "
                    "not cite it; the marker is under the wrong paragraph, or the sentence was "
                    "reworded without it"
                )
            elif _resolves(root, basenames, token) and not _covered_by_gitignore(root, token):
                report.errors.append(
                    f"{path}:{index + 1}: marks `{token}` absent, but it is in the tree; update "
                    "the sentence and drop it from the marker"
                )
            for number in range(start + 1, end + 1):
                declared.setdefault(number, set()).add(token)
    return declared


def _inside(offset: int, spans: Sequence[tuple[int, int]]) -> bool:
    """Whether `offset` falls within one of `spans`, each a half-open range."""
    return any(start <= offset < end for start, end in spans)


def _unclosed(where: str, opener: str, unread: str) -> str:
    """What a citation reader says of a quotation its paragraph never closes (`PL-T73L`).

    `opener` is what read the quotation as a citation - the mark, the word or
    the source before it - and `unread` is what the reader would have decided.
    One wording for the four readers, so the remedy reads the same wherever the
    mark went missing.
    """
    return (
        f"{where}: {opener} opens a quotation its paragraph never closes, so {unread} was "
        "not read; close it before the paragraph ends"
    )


def _cited_section(text: str, match: re.Match[str]) -> tuple[str, bool]:
    """The section a citation names, and whether it names one in its own file.

    `above` and `below` point into the citing file, so a heading elsewhere does
    not answer them; any other mark may send the reader anywhere the documents
    go. The term is whichever group matched: `CITATION_RE` has one, and
    `UNMARKED_CITATION_RE` names its directed position by group. A match on
    either one's `unclosed` branch names no section, and is refused before it
    reaches here (`PL-T73L`). A direction is read within the citation's own
    statement, so a heading quoting a section does not take one from the
    paragraph under it (`PL-Z1R7`).
    """
    term = _normalized(match.group(match.lastgroup or 0))
    direction = DIRECTION_RE.match(text, match.end(), match.endpos)
    same_file = match.lastgroup == "directed" or bool(direction)
    return term, same_file


#: A citation that points into a file by line: `core/parameters.py:274`, or a
#: span, `app/theme.py:60-72`. The path half is held to `_is_path_citation`'s
#: own suffix rule after the match, so this only has to be loose enough to
#: catch what prose writes.
LINE_CITATION_RE = re.compile(r"`([\w./-]+):(\d+)(?:-(\d+))?`")


def _live_item_briefs(root: Path) -> Iterator[tuple[Path, str]]:
    """Every open item brief in the store, with its text.

    Closed briefs are skipped rather than filtered later, so the reason sits
    where the decision does: a closed brief - one whose `status:` is in
    `CLOSED_STATUSES` - describes a tree that no longer exists and is not
    repaired.

    Which briefs are closed is the store's answer, read once by `_read_store`,
    so a status is the field `docket.model` parses rather than the first token
    a regex found after `status:` (`PL-X766`): that read a quoted `"done"` with
    its quotes, a value in no status set, and put a closed brief under the
    live checks. A store that will not read yields nothing here, since no
    other reading of it is the store's; `bin/docket check` is what says why.
    """
    store = _read_store(root)
    if store is None:
        return
    items = root / store.config.items_dir
    for item in sorted(store.items.values(), key=lambda entry: entry.path):
        if item.status in CLOSED_STATUSES:
            continue
        path = items / item.path
        yield path.relative_to(root), path.read_text(encoding="utf-8", errors="replace")


def _brief_pieces(
    text: str, where: Path, unread: str, declined: list[str]
) -> list[tuple[int, str]]:
    """A brief as the pieces its readers read apart, each with the line it starts on.

    Each front-matter field is one, ending where `docket.model` ends it, and so
    is the body after the closing `---`. Read from the file's first line as one
    Markdown paragraph, a backtick one field left open paired with the next
    field's, hiding the path a later field cited, and a quotation ran on into
    the next field (`PL-CZ28`). Every other line of the front matter - a
    comment, or one no field reads - is read alone. A brief with no front
    matter is one piece. Each piece of one that has is a passage of it, so a
    body opening with a thematic break opens no front matter (`_as_passage`).

    A field reaches its readers as `_fold` reads it, one statement (`PL-4J5H`).
    Each line folded into it is indented four columns more, past where a list
    item, a block quote, a fence, an HTML block, a heading, a setext underline,
    a thematic break or a table row can open (CommonMark 0.31.2 § 4, § 5), so
    none ends the paragraph where `_fold` reads on. A reader takes a line from
    a piece and never a column, so the indent moves nothing it reports. Two
    fields are declined instead, each named in `declined` with `where` and the
    `unread` its readers look for: one with a blank or unread line inside it,
    since no line carries a paragraph over a blank one and `_fold`
    reads past it, and one continuing on a line that opens with `>`, which
    `SOFT_BREAK` drops as a block quote's marker where `_fold` reads it as text.
    """
    layout = front_matter_spans(text)
    if layout is None:
        return [(1, text)]
    fields, body = layout
    lines = split_lines(text, keepends=True)
    held = {
        index
        for span in fields
        for index in range(span.start, span.end)
        if index not in span.interior
    }
    alone = [(index, lines[index]) for index in range(1, body - 1) if index not in held]
    joined: list[tuple[int, str]] = []
    for span in fields:
        folded = lines[span.start + 1 : span.end]
        if span.interior:
            why, fix = (
                "holds a blank or unread line among the lines folded into it, where a "
                "Markdown paragraph ends and docket reads on",
                "join the value's lines, or end it above that line",
            )
        elif any(line.lstrip().startswith(">") for line in folded):
            why, fix = (
                "continues on a line opening with `>`, which the citation readers drop as a "
                "block quote's marker and docket reads as text",
                "rewrap the value so no line opens with one",
            )
        else:
            joined.append(
                (span.start, lines[span.start] + "".join(f"    {line}" for line in folded))
            )
            continue
        declined.append(
            f"{where}:{span.start + 1}: `{span.key}` {why}, so no {unread} in it was checked; {fix}"
        )
    pieces = sorted([*joined, *((index, line) for index, line in alone if line.strip())])
    return list(
        _as_passages(
            [(first + 1, piece) for first, piece in pieces] + [(body + 1, "".join(lines[body:]))]
        )
    )


def _cited_file(root: Path, basenames: Mapping[str, list[Path]], token: str) -> Path | None:
    """The one file `token` names, or `None` where it names no single file.

    Ambiguity declines rather than guessing. Four bare filenames in this store
    match more than one tracked file, and picking one of them would report a
    line count from a file the sentence was not talking about - a wrong answer
    stated confidently, which is worse here than no answer at all.
    """
    for path in _repository_paths(token):
        # `os.path.isfile` rather than `Path.is_file`, for the reason
        # `_resolves` gives at its `os.path.exists`.
        if os.path.isfile(root / path):
            return root / path
    if "/" in token:
        return None
    matches = basenames.get(token, [])
    return matches[0] if len(matches) == 1 else None


def check_line_citations(root: Path, documents: dict[Path, str], report: Report) -> None:
    """Resolve every citation that points into a file by line number.

    `check_citations` above decides whether a cited *path* exists. This is the
    same question one line finer, and it is the one `PL-38PN` asked in the
    store on 2026-09-03 and nothing answered: a line number is a promise that a
    session can go straight to the code, and a wrong one costs a search plus
    the doubt about whether the rest of the brief describes the current tree.

    **What it decides, and what it must not.** A line past the end of its file
    cannot be what the sentence says, whatever the sentence says - that is
    resolvability, and it is this tool's existing contract. Whether a line that
    *does* exist still holds the symbol the prose names is a different claim,
    and it stays a reader's. The distinction is not fussiness: measured over
    this store on 2026-09-19, 644 resolvable line citations carried 232 whose
    target line had changed since the citation was written (36.0%), but a
    changed line is not a wrong citation - a reformat moves one without
    touching what it says. Checking that half would be scripting the judgment,
    which `CLAUDE.md` refuses, so only the certain half is held here.

    **Closed briefs are exempt, and that is the decision rather than an
    oversight** (`PL-G424`). The same measurement split the surface by whether
    a session would ever act on the sentence: closed item briefs carried 48.0%
    stale line citations (196 of 408), open briefs 15.6% (36 of 231), and the
    standing documents 0% (0 of 5). Nobody has repaired a closed one, because a
    closed brief records what was true when the work was done. Holding them to
    the tree would fire 196 errors that no session should act on, which is the
    defect `CLAUDE.md` retires a check for.

    Item briefs are read here rather than through `read_docs`, because
    `DOC_GLOBS` deliberately holds the authoritative documents and `docs/items/`
    is the queue, nearly two thousand files of it.
    """
    basenames: dict[str, list[Path]] = {}
    for path in _walk(root):
        basenames.setdefault(path.name, []).append(path)

    # A live brief a front-matter field at a time, and its body after them
    # (`PL-CZ28`), each piece with the line it starts on.
    sources = [(path, 1, raw) for path, raw in documents.items()] + [
        (path, first, piece)
        for path, brief in _live_item_briefs(root)
        for first, piece in _brief_pieces(brief, path, "line citation", report.declined)
    ]
    for path, offset, raw in sources:
        # A fence holds a literal, and read as a claim it made an item that
        # documents a stale citation an error for quoting the one it reports.
        for match in LINE_CITATION_RE.finditer(without_fences(raw)):
            token, first, last = match.group(1), int(match.group(2)), match.group(3)
            if not _is_path_citation(token):
                continue
            target = _cited_file(root, basenames, token)
            if target is None:
                continue
            highest = int(last) if last else first
            count = len(split_lines(target.read_text(encoding="utf-8", errors="replace")))
            if highest > count:
                report.errors.append(
                    f"{path}:{offset + _line_of(raw, match.start()) - 1}: cites `{token}:"
                    f"{match.group(2)}{'-' + last if last else ''}`, but that file has "
                    f"{count} lines. Anchor the citation to a symbol rather than "
                    f"re-pointing it at a line number, which drifts again."
                )


def _docstrings(tree: ast.Module) -> Iterator[tuple[int, str]]:
    """Every docstring, an attribute docstring included, with the line it starts on.

    `docket.python.docstrings` decides which strings those are. Reading only a
    module's, a class's and a function's left a citation in an attribute
    docstring unchecked (`PL-8W1J`).
    """
    for node in docstrings(tree):
        if isinstance(node.value, str):  # always, and how the type checker learns it
            yield node.lineno, node.value


def _unread_source(relative: Path, error: Exception, unread: str = "citation") -> str:
    """The `declined` line for a source file whose docstrings were not read.

    Names the interpreter, because which one ran is the whole difference: the
    same file parses under one and not another, and a reader shown only "could
    not parse" would go looking for a syntax error that is not there. `unread`
    names what the caller looks for in a docstring, so each check's decline says
    what it, rather than another check, left unchecked.
    """
    if isinstance(error, OSError):
        return (
            f"{relative}: could not be read ({error}), so no {unread} in its docstrings was checked"
        )
    if isinstance(error, SyntaxError):
        where = f"{relative}:{error.lineno}" if error.lineno else str(relative)
        return (
            f"{where}: Python {platform.python_version()} cannot parse this file "
            f"({error.msg}), so no {unread} in its docstrings was checked; run under "
            "`uv run python` if the project's own interpreter can"
        )
    return (
        f"{relative}: Python {platform.python_version()} cannot parse this file "
        f"({error}), so no {unread} in its docstrings was checked"
    )


def _quoting_sources(
    root: Path, documents: dict[Path, str], declined: list[str]
) -> Iterator[tuple[Path, int, str]]:
    """Every text that may quote a document, as (file, first line, text).

    Three sets, and the two `DOC_GLOBS` misses are where this project actually
    writes its citations: the queue, which is most of its prose, and the
    docstrings, which are where a contributor reading the code is sent
    somewhere else. `DOC_GLOBS` itself is left alone - widening it would hand
    every item file to `check_make_targets` and to `candidates`, neither of
    which wants them.

    **The queue half is the *live* briefs only**, which is `_live_item_briefs`
    and the same line `check_line_citations` draws. Each comes as its
    `_brief_pieces`, a front-matter field at a time and then its body, so a
    quotation one field leaves open is refused there rather than read on into
    the next field (`PL-CZ28`). A closed brief is a record
    of what was true when the work was done, so its drift is not a finding -
    `.claude/rules/citation-drift.md` is the ratified decision, and this
    function read every brief instead, which made the two checks disagree
    about the same file. The disagreement was not academic: the
    `## Current baseline` section of `ROADMAP.md` is replaced wholesale at
    every release, so a closed brief quoting one of its headings went red at
    the next cut, and the only ways out were repairing a historical record or
    editing the roadmap to suit a check (`PL-ZM8P`).

    **A source file this run cannot read is declined, never skipped**
    (`PL-MB3F`). The source is written for the project interpreter, and CI's
    floor section also runs this under 3.11, whose parser reads neither PEP 695
    generics nor PEP 758's unparenthesised `except`. Such a file used to be
    skipped without a word, under the same "all resolve" a clean run prints. A
    broken quotation in `app/bookmarks.py` would have passed `make check` and
    failed CI - reproduced, though no run had failed that way - and
    `tools/possessive_section_check.py` read neither that file nor
    `app_metadata.py` in either gate. Each file is appended to `declined` as
    the walk meets it, so a caller reads `declined` only after exhausting this.

    The file is parsed as bytes, as Python reads source, so a byte-order mark
    or a PEP 263 coding cookie is honoured rather than declined.
    """
    for path, text in documents.items():
        yield path, 1, text
    for path, text in _live_item_briefs(root):
        pieces = _brief_pieces(text, path, "quotation", declined)
        yield from ((path, first, piece) for first, piece in pieces)
    for path in sorted(_walk(root)):
        if path.suffix != ".py":
            continue
        relative = path.relative_to(root)
        try:
            tree = ast.parse(path.read_bytes())
        except (OSError, SyntaxError, ValueError) as error:
            declined.append(_unread_source(relative, error))
            continue
        for line, docstring in _as_passages(_docstrings(tree)):
            yield relative, line, docstring


def check_quoted_sources(root: Path, documents: dict[Path, str], report: Report) -> None:
    """Hold a citation that names a markdown file and then quotes it to that file.

    This is the form the existing branches in `CITATION_RE` do not reach, and
    the one that decays worst. `docs/WORKING_NOTES.md` rewrites and deletes
    threads as they resolve - the file's own header asks for that - so a
    citation into it by section title is stale the moment the thread is
    rewritten, and nothing said so.

    **The test is containment, not headings, and that is what makes it
    exact.** A citation names a document and then quotes it; whether the
    quotation is a section title or a sentence is a distinction this tool
    would have to guess at, and guessing produced six false errors against
    prose that was quoted correctly. Whether the named document contains the
    words is decidable, it is the same question in both cases, and a
    quotation that has drifted is as stale as a title that has - `PL-XF89`
    cites a `WORKING_NOTES` thread renamed from "Open:" to "Mostly settled:",
    which a heading test and a containment test both catch.

    Case, dash style and quote style are folded, because a passage copied by
    hand settles on one of the forms this project writes and the passage is
    still there either way. So is emphasis, which a quotation leaves out
    (`_without_emphasis`, `PL-RX0W`). The words must stand in one statement of the file,
    as `_comparable_statements` reads it, so a splice across a heading and its
    paragraph is not in it (`PL-Q8LJ`). An elided quotation is skipped outright: one
    written with an ellipsis cannot be found verbatim, and declining to
    answer beats a false error.

    **Only a claiming connective makes a miss an error** - `§` or the
    possessive, `CLAIMING_CONNECTIVE_RE`. After any other the same miss is an
    advisory: the words may be a proposal for the file or a sentence it has
    since dropped, which it rightly lacks, and a reader can tell that from
    drift where no spelling can (`PL-HVST`).

    **An item id is a source too, after the mark or the possessive** -
    `ITEM_SECTION_RE`. The
    brief its file holds is tested the same way, closed or open, because a
    citation of a closed brief still claims the words are there; only a
    closed brief's own citations go unread, since `_quoting_sources` reads the
    live briefs alone. An id no file under `docs/items/` holds is an error, and
    one two files hold is declined rather than guessed at. Which file holds an
    id's brief is `vcs.ITEM_FILE_RE`'s reading of its name; a glob of this
    tool's own took a file whose name carries no slug for one, which `docket`
    reads as no item's (`PL-5QG4`).
    """
    bodies: dict[str, str | None] = {}
    briefs: dict[str, list[str]] = {}

    def body_of(cited: str) -> str | None:
        if cited not in bodies:
            target = root / cited
            bodies[cited] = (
                _comparable_statements(target.read_text(encoding="utf-8"))
                if target.is_file()
                else None
            )
        return bodies[cited]

    def briefs_of(item: str) -> list[str]:
        if not briefs:
            for brief in sorted((root / load_docket_config(root).items_dir).glob("*.md")):
                if found := ITEM_FILE_RE.match(brief.name):
                    held = briefs.setdefault(found.group(1), [])
                    held.append(brief.relative_to(root).as_posix())
        return briefs.get(item, [])

    for path, offset, text in _quoting_sources(root, documents, report.declined):
        prose = without_fences(text)
        for match in _statement_matches(QUOTED_SOURCE_RE, prose):
            cited = match.group("document")
            line = offset + _line_of(text, match.start()) - 1
            claims = CLAIMING_CONNECTIVE_RE.fullmatch(match.group("connective") or "")
            if match["unclosed"] is not None:
                refusal = _unclosed(
                    f"{path}:{line}",
                    f"this citation of {cited}",
                    "whether the file holds the words",
                )
                (report.errors if claims else report.advisories).append(refusal)
                continue
            quoted = _normalized(match.group("quoted"))
            if "..." in quoted or "…" in quoted:
                continue
            body = body_of(cited)
            if body is None:
                finding = f"{path}:{line}: quotes {cited}, which does not exist"
            elif _comparable(_without_emphasis(quoted)).rstrip(" .,;:") not in body:
                finding = f'{path}:{line}: quotes {cited} as "{quoted}", which is not in that file'
            else:
                continue
            if claims:
                report.errors.append(finding)
            else:
                report.advisories.append(
                    f"{finding} - drift, if it quotes the file; if it quotes wording proposed "
                    "for it or since removed, nothing to do (only `§` or the possessive claims "
                    "the file holds the words)"
                )

        for match in _statement_matches(ITEM_SECTION_RE, prose):
            item = match.group("item")
            line = offset + _line_of(text, match.start()) - 1
            if match["unclosed"] is not None:
                report.errors.append(
                    _unclosed(
                        f"{path}:{line}",
                        f"this citation of {item}",
                        "whether its brief holds the words",
                    )
                )
                continue
            quoted = _normalized(match.group("quoted"))
            if "..." in quoted or "…" in quoted:
                continue
            held = briefs_of(item)
            if not held:
                report.errors.append(
                    f"{path}:{line}: quotes {item}, which no file under docs/items/ holds"
                )
            elif len(held) > 1:
                report.declined.append(
                    f'{path}:{line}: quotes {item} as "{quoted}", but {len(held)} files under '
                    "docs/items/ carry that id, so which brief it cites was not decided"
                )
            elif _comparable(_without_emphasis(quoted)).rstrip(" .,;:") not in (
                body_of(held[0]) or ""
            ):
                report.errors.append(
                    f'{path}:{line}: quotes {item} as "{quoted}", which is not in {held[0]}'
                )


@dataclass(frozen=True)
class _OpenRule:
    """Which rule a line led by a tab belongs to, where `_make_lines` reads one.

    `kind` is `none` where no rule is open, so the line is read as any other;
    `targets` where one is, so the line is its recipe's; `targetless` where the
    open rule names no target, whose recipe make reads and drops; and
    `undecided` where a conditional's branch changed which rule is open, so the
    answer turns on the branch make takes. `line` is where that rule or
    conditional opens, which tells two open rules apart.
    """

    kind: str
    line: int = 0


NO_RULE = _OpenRule("none")


def _make_lines(text: str, every_branch: bool = True) -> Iterator[tuple[str, int]]:
    """Every statement of a Makefile, as make reads it, with the line it opens on.

    The one reading of where a Makefile statement ends (`PL-R417`), which every
    reader of the file takes. Make carries a line ending in a backslash on to
    the next, and does one of two things with the pair. On a recipe line it
    keeps the backslash and the newline and drops only the continuation's
    leading tab, handing the shell the whole command to read the pair itself
    (GNU make manual, "Splitting Recipe Lines"). On any other line - a rule, an
    assignment, a comment - the pair and the whitespace around it become one
    space (GNU make manual, "Splitting Long Lines"), so a rule's prerequisites
    go on past its first line, and a comment ending in a backslash takes the
    next line with it, recipe line or not. All three were run through GNU make
    4.3 on 2026-10-04. A recipe line comes back with its leading tab, and any
    other statement without the blanks make skips ahead of it, so a reader
    knows a recipe line by its tab and by nothing else.

    Read a physical line at a time, a continued command was two (`PL-G2FY`),
    and a continued prerequisite list's second line was a recipe line.

    **A line led by a tab is a recipe line only while a rule is open**, as
    `eval` in GNU make 4.3's `src/read.c` reads one: from a rule line until a
    statement ends the rule - an assignment, a `define`, a directive
    (`MAKE_DIRECTIVES`) or another rule line. Outside a rule the line is read
    as the line its words make it, joined as any other line is (`PL-BMZN`). A
    comment, a blank line and a conditional's directive end no rule, as they
    end none in make, and come back as no statement, so no reader has a say of
    its own over where a rule ends (`PL-TDVJ`). A rule line opens a rule as
    `_make_rule` reads it, and a recipe it carries after a `;` comes back after
    it as the rule's first recipe line, on the rule's own line, spelled as make
    hands it to the shell; a blank one, `target: ;`, runs nothing and comes
    back as none (`PL-GZXY`). Read with no rule held, every line a tab led was
    a recipe line, so an assignment indented with one reached the coverage gate
    as a command; and two readers ended a rule at different lines, one of them
    at a comment, where make reads on. Variable references are read as
    written, as every reader of this file reads them.

    **A conditional is read with every branch taken in turn**, since which one
    make takes turns on variables this reader does not evaluate. Where a branch
    changes which rule is open, the line after it may be read under a rule make
    does not have open, so a line led by a tab is declined until a statement
    after the branch settles the rule again. That suits a reader that holds
    every command make might run. A reader that asks what a target runs in
    every configuration passes `every_branch` false, and a recipe line inside a
    conditional is then declined, since make runs it only in its branch
    (`PL-HSB3`).

    **A `define` is one statement, through the `endef` closing it**
    (`PL-4MLK`). The lines between are a variable's value (GNU make manual,
    "Defining Multi-Line Variables"), so none is a rule or a recipe line, and
    the directive ends the rule above it as any assignment does. It comes back
    as written, its lines joined by newlines, on the directive's line. The body
    is read as make 4.3's `do_define` reads it, in logical lines, by
    `MAKE_DEFINE_OPENS_RE` and `MAKE_DEFINE_CLOSES_RE`. Read a line at a time,
    a `define` holding `deploy:` declared a target make has no rule for. Led
    by a tab, a `define` opens a variable outside a rule and is a recipe line
    inside one, which the rule held tells apart.

    Raises `UnreadStatement` where make's reading cannot be given: a `define`
    no `endef` closes, or one naming no variable, both of which make refuses
    (run through GNU make 4.3 on 2026-10-05); a line led by a tab where no rule
    is open that is no assignment, directive or conditional, which make refuses
    where it reads it; a line led by a tab after a branch that changed which
    rule is open (both run through make 4.3 on 2026-10-06); a rule line
    escaping what its names end at, which make unquotes (`MAKE_ESCAPED_NAME_RE`,
    `PL-5M36`), where every reader of a rule took the names as written; an
    assignment to `.RECIPEPREFIX`, after which make opens a recipe line with
    another character (`MAKE_RECIPEPREFIX_RE`, `PL-GSJ6`); and, with
    `every_branch` false, a recipe line inside a conditional.
    """
    lines = split_lines(text)
    index = 0
    rule = NO_RULE
    # Each open conditional's line, and the rule open where its current branch began.
    branches: list[tuple[int, _OpenRule]] = []
    while index < len(lines):
        opens = index
        parts = _make_physical_lines(lines, index)
        index += len(parts)
        if parts[0].startswith("\t") and rule != NO_RULE:
            if rule.kind == "undecided":
                raise UnreadStatement(
                    opens + 1,
                    f"a branch of the conditional on line {rule.line} changes which rule is "
                    "open, so which rule this line belongs to turns on the branch make "
                    "takes, which this reader does not evaluate",
                )
            if rule.kind == "targets":
                _one_branch(branches, every_branch, opens + 1)
                recipe = [parts[0], *(part.removeprefix("\t") for part in parts[1:])]
                yield "\n".join(recipe), opens + 1
            continue
        line = _make_joined(parts).lstrip(MAKE_SPACE)
        statement = _make_uncommented(line)
        if not statement.strip(MAKE_SPACE):
            continue
        if MAKE_RECIPEPREFIX_RE.match(statement):
            raise UnreadStatement(
                opens + 1,
                "this line assigns `.RECIPEPREFIX`, after which make opens a recipe line "
                "with that character instead of a tab, and this reader knows a recipe line "
                "only by its tab",
            )
        define = MAKE_DEFINE_RE.match(line)
        if define is not None:
            if not define["name"].strip():
                raise UnreadStatement(
                    opens + 1,
                    "this `define` names no variable, which make refuses as an empty name",
                )
            depth = 1
            while depth:
                if index == len(lines):
                    raise UnreadStatement(
                        opens + 1,
                        "this `define` is closed by no `endef`, which make refuses as an "
                        "unterminated `define`",
                    )
                body = _make_physical_lines(lines, index)
                index += len(body)
                if not body[0].startswith("\t"):
                    if MAKE_DEFINE_OPENS_RE.match(_make_joined(body)):
                        depth += 1
                    elif MAKE_DEFINE_CLOSES_RE.match(_make_joined(body)):
                        depth -= 1
            rule = NO_RULE
            yield "\n".join(lines[opens:index]).lstrip(MAKE_SPACE), opens + 1
            continue
        word = _make_word(statement)
        if _make_assigns(statement) or word in MAKE_DIRECTIVES:
            rule = NO_RULE
        elif word in MAKE_CONDITIONALS:
            rule = _make_branch(word, rule, branches, opens + 1)
            continue
        elif parts[0].startswith("\t"):
            raise UnreadStatement(
                opens + 1,
                "this line is led by a tab where no rule is open, and is no assignment, "
                "directive or conditional, which make refuses where it reads the line "
                '("recipe commences before first target")',
            )
        else:
            opened = _make_rule(line)
            if opened and opened.targets and MAKE_ESCAPED_NAME_RE.search(_make_rule_line(line)[0]):
                raise UnreadStatement(
                    opens + 1,
                    "a backslash on this rule line escapes a blank, `:`, `;`, `#` or `|`, which "
                    "make 4.3 unquotes in a name by rules this reader does not port",
                )
            if opened is None:
                rule = NO_RULE
            elif not opened.targets:
                rule = _OpenRule("targetless", opens + 1)
            else:
                rule = _OpenRule("targets", opens + 1)
                written = [parts[0], *(part.removeprefix("\t") for part in parts[1:])]
                _, inline = _make_rule_line("\n".join(written))
                if inline is not None and inline.strip(MAKE_SPACE):
                    _one_branch(branches, every_branch, opens + 1)
                    yield line, opens + 1
                    yield f"\t{inline.lstrip(MAKE_SPACE)}", opens + 1
                    continue
        yield line, opens + 1


def _one_branch(branches: list[tuple[int, _OpenRule]], every_branch: bool, line: int) -> None:
    """Decline a recipe line inside a conditional, for a reader that needs every branch.

    Raises `UnreadStatement` naming the conditional, as `_make_lines` declines
    the line for a reader that passes `every_branch` false (`PL-HSB3`).
    """
    if branches and not every_branch:
        raise UnreadStatement(
            line,
            f"this recipe line sits inside the conditional on line {branches[-1][0]}, so make "
            "runs it only in that branch, and which branch make takes turns on variables "
            "this reader does not evaluate",
        )


def _make_branch(
    word: str, rule: _OpenRule, branches: list[tuple[int, _OpenRule]], line: int
) -> _OpenRule:
    """The rule open after a conditional's directive on `line`, which ends none.

    An `ifdef`, `ifndef`, `ifeq` or `ifneq` opens a branch, and an `else` or
    `endif` closes one. Where the rule open as a branch closes is not the one
    open where it began, the branch changed it, and which rule make has open
    after it turns on whether make took it. An `else` or `endif` closing no
    conditional, which make refuses, changes nothing.
    """
    if word not in ("else", "endif"):
        branches.append((line, rule))
        return rule
    if not branches:
        return rule
    where, began = branches.pop()
    if rule != began:
        rule = _OpenRule("undecided", where)
    if word == "else":
        branches.append((where, rule))
    return rule


@dataclass(frozen=True)
class _MakeRule:
    """A rule line, as `_make_rule` reads it.

    `targets` is empty for a rule naming none, whose recipe make reads and
    drops. `prerequisites` holds the normal and the order-only ones alike,
    since make brings both up to date before the recipe runs.
    """

    targets: tuple[str, ...]
    prerequisites: tuple[str, ...]


NO_TARGETS = _MakeRule((), ())


def _make_rule(statement: str) -> _MakeRule | None:
    """The rule a Makefile statement opens, or `None` where it opens none.

    The one reading of a rule line (`PL-HR4V`), which `_make_lines` and each
    reader of its statements take, where `make_targets` and `_target_recipes`
    once read the targets and prerequisites by patterns of their own, so a
    trailing comment's words were prerequisites and `.PHONY` names, `a: X = 1`
    and `a ::= 1` each declared a target make has no rule for, and `a b:`
    declared neither target.

    Read as `eval` in GNU make 4.3's `src/read.c` reads a line no assignment,
    `define`, directive or conditional takes, each of which opens none. The
    line ends at its first `;` or `#` outside a variable reference and
    unescaped (`_make_rule_line`). Its first colon outside a reference and
    unescaped ends the targets, `&:` grouping them, and a second straight after
    it makes the rule double-colon. A line with no such colon opens no rule,
    since make reads it as nothing or refuses it as missing a separator. Past
    the colon, an assignment makes the line a
    target-specific variable, which opens no rule; otherwise the words are the
    prerequisites, the order-only ones after a `|`, and a static pattern rule's
    after its target pattern's colon. Each form was run through make 4.3 on
    2026-10-06. Variable references are read as written, as every reader of
    this file reads them.
    """
    uncommented = _make_uncommented(statement)
    if (
        _make_assigns(uncommented)
        or _make_word(uncommented.lstrip(MAKE_SPACE)) in MAKE_DIRECTIVES | MAKE_CONDITIONALS
    ):
        return None
    head, _ = _make_rule_line(statement)
    colon = _make_unquoted(head, ":")
    if colon < 0:
        return None
    targets = tuple(MAKE_SPACE_RE.split(head[:colon].removesuffix("&").strip(MAKE_SPACE)))
    if targets == ("",):
        return NO_TARGETS
    rest = head[colon + 1 :].removeprefix(":")
    if _make_assigns(rest):
        return None
    rest = rest[_make_unquoted(rest, ":") + 1 :]
    pipe = _make_unquoted(rest, "|")
    if pipe >= 0:
        rest = f"{rest[:pipe]} {rest[pipe + 1 :]}"
    return _MakeRule(targets, tuple(word for word in MAKE_SPACE_RE.split(rest) if word))


def _make_rule_line(text: str) -> tuple[str, str | None]:
    """A rule line cut where make 4.3 ends it, and the recipe it carries.

    Cut at the first `;` or `#` outside a variable reference and unescaped,
    as `eval` in `src/read.c` cuts it: a `#` opens a comment, and a `;` hands
    the rest of the line to the shell, `#` and all, as the rule's first recipe
    line. The recipe is `None` where the line carries none.
    """
    stop = _make_unquoted(text, ";#")
    if stop < 0:
        return text, None
    return text[:stop], text[stop + 1 :] if text[stop] == ";" else None


def _make_assigns(text: str) -> bool:
    """Whether make 4.3 reads `text` as an assignment, `define` and `undefine` included.

    Ported from `parse_var_assignment` in GNU make 4.3's `src/read.c`: a
    variable's definition (`_make_defines_variable`), after any of the
    modifiers `export`, `override` and `private`, or the word `define` or
    `undefine` after them.
    """
    rest = text.lstrip(MAKE_SPACE)
    while rest:
        if _make_defines_variable(rest):
            return True
        word = _make_word(rest)
        if word in MAKE_DEFINING:
            return True
        if word not in MAKE_MODIFIERS:
            return False
        rest = rest[len(word) :].lstrip(MAKE_SPACE)
    return False


def _make_defines_variable(text: str) -> bool:
    """Whether `text` opens with a variable's definition, as make 4.3 reads one.

    Ported from `parse_variable_definition` in GNU make 4.3's
    `src/variable.c`: a name, with any variable reference in it passed over
    whole, then any blanks and one of `=`, `:=`, `::=`, `+=`, `?=` and `!=`. A
    colon that starts none of them is a rule's, and a comment, or a word after
    the blanks that is no operator, makes the text no definition.
    """
    at = len(text) - len(text.lstrip(MAKE_SPACE))
    blank = False
    while at < len(text):
        char = text[at]
        at += 1
        if char == "#":
            return False
        if char == "$":
            if at == len(text):
                return False
            at += 1
            if text[at - 1] in "({":
                at = _make_reference_end(text, at, text[at - 1])
            continue
        if char in " \t":
            blank = True
            at = len(text) - len(text[at:].lstrip(MAKE_SPACE))
            if at == len(text):
                return False
            char = text[at]
            at += 1
        if char == "=":
            return True
        if text.startswith("=", at):
            if char in ":+?!":
                return True
            if blank:
                return False
            continue
        if char == ":":
            return text.startswith(":=", at)
        if blank:
            return False
    return False


def _make_unquoted(text: str, stops: str) -> int:
    """Where the first of `stops` stands in `text`, outside a variable reference and unescaped.

    Ported from `find_map_unquote` in GNU make 4.3's `src/read.c`, given
    `MAP_VARIABLE`: a `$(...)` or `${...}` reference is passed over whole, `$`
    and the character after it otherwise, and a stop character after an odd
    run of backslashes is escaped by them. -1 where none stands.
    """
    at = 0
    while at < len(text):
        char = text[at]
        if char == "$":
            at += 2
            if text[at - 1 : at] in ("(", "{"):
                at = _make_reference_end(text, at, text[at - 1])
            continue
        if char in stops and (at - len(text[:at].rstrip("\\"))) % 2 == 0:
            return at
        at += 1
    return -1


def _make_reference_end(text: str, at: int, opener: str) -> int:
    """Past the close of the reference `opener` opened just before `at`, or the text's end.

    A reference nested in it with the same bracket is counted, as make 4.3's
    `find_map_unquote` and `parse_variable_definition` count one.
    """
    closer = ")" if opener == "(" else "}"
    depth = 1
    while at < len(text):
        char = text[at]
        at += 1
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if not depth:
                break
    return at


def _make_uncommented(line: str) -> str:
    """`line` up to its comment, as `remove_comments` in GNU make 4.3's `src/read.c` cuts it."""
    cut = _make_unquoted(line, "#")
    return line if cut < 0 else line[:cut]


def _make_word(text: str) -> str:
    """The first word of `text`, which no blank leads: `end_of_token` in make 4.3's `src/misc.c`."""
    return MAKE_SPACE_RE.split(text, maxsplit=1)[0]


def _make_physical_lines(lines: list[str], index: int) -> list[str]:
    """The physical lines from `index` on that make reads as one logical line."""
    end = index + 1
    while end < len(lines) and MAKE_CONTINUED_RE.search(lines[end - 1]):
        end += 1
    return lines[index:end]


def _make_joined(parts: list[str]) -> str:
    """One logical line outside a recipe: each continuation, with the blanks around it, a space."""
    joined = [part[:-1].rstrip() for part in parts[:-1]] + [parts[-1]]
    pieces = [joined[0], *(part.lstrip() for part in joined[1:])]
    return " ".join(piece for piece in pieces if piece)


#: What make passes over ahead of a recipe line's command: blanks and the `@`
#: (no echo), `-` (ignore a failure) and `+` (run under `-n`) prefixes, in any
#: mix (GNU make manual §5.2 "Recipe Echoing", §5.5 "Errors in Recipes", §9.3
#: "Instead of Executing Recipes"). Run through GNU make 4.3 on 2026-10-18,
#: `@ - +echo one` ran `echo one`.
RECIPE_PREFIXES = "@-+ \t"


def _recipe_command(line: str) -> str:
    """The command a recipe line hands the shell, as GNU make 4.3 reads it, or "" for none.

    `start_job_command` in `src/job.c` passes over `RECIPE_PREFIXES` and starts
    nothing where nothing is left, so a tab-only line, or one holding `@`
    alone, runs nothing (run through make 4.3 on 2026-10-12, `PL-5M36`). What
    is left is the command, so `@ruff check src` runs `ruff check src`; read
    with its prefix, an `@`-led cached `ruff check` passed the ruff-cache check
    (`PL-QYF4`).
    """
    return line.strip().lstrip(RECIPE_PREFIXES)


def make_targets(text: str) -> tuple[frozenset[str], frozenset[str]]:
    """Every target a Makefile names, and the subset that carries a recipe.

    The two differ exactly where this check earns its place. A name listed in
    `.PHONY` but never given a recipe is still a target as far as `make` is
    concerned: it accepts the argument, prints "Nothing to be done", and exits
    0. Documentation that tells a session to run it is therefore naming a
    check that reports success without running, which is worse than one that
    errors - an erroring command gets investigated, a passing one gets
    believed. Read by statement, as `_make_lines` gives them, so a `.PHONY`
    list or a prerequisite list a backslash continues is read whole, and its
    second line is not taken for a recipe (`PL-R417`); a `define` body, a
    variable's value, declares nothing (`PL-4MLK`); and a rule runs on past a
    comment line, as make reads it, where this once ended it, so a target
    whose first recipe line follows a comment read as having none
    (`PL-TDVJ`). Each rule line is read by `_make_rule`, so every target it
    names is declared, and neither a comment's words nor a target-specific
    variable declares one (`PL-HR4V`). `.PHONY` declares its prerequisites,
    not itself, being make's special target rather than one a document runs;
    and a recipe after a `;` on the rule's own line is a recipe (`PL-GZXY`). A
    recipe line `_recipe_command` finds no command in is none, so a target whose
    only recipe line is a tab is one that exits 0 without running, as make
    says "Nothing to be done" for it (`PL-5M36`). Raises `UnreadStatement`
    where `_make_lines` does, and at a recipe line inside a conditional, since
    whether the target carries a recipe then turns on the branch make takes
    (`PL-HSB3`).
    """
    declared: set[str] = set()
    with_recipe: set[str] = set()
    current: tuple[str, ...] = ()
    for line, _ in _make_lines(text, every_branch=False):
        if line.startswith("\t"):
            if _recipe_command(line):
                with_recipe.update(current)
            continue
        rule = _make_rule(line) or NO_TARGETS
        if ".PHONY" in rule.targets:
            declared.update(rule.prerequisites)
            current = ()
            continue
        current = rule.targets
        declared.update(current)
    return frozenset(declared), frozenset(with_recipe)


def _make_mentions(text: str) -> Iterator[tuple[str, int]]:
    """Every `make <target>` written as code, with the line it sits on.

    Anywhere in a code span, a line ending in it read as the space it renders
    as and a block quote's markers taken out, as `_named_tests` takes them
    (`PL-4ZDZ`); in a fence, only as a command's first word, the fence read as
    bash reads its lines, through docket's `shell.script_lines` (`PL-R417`):
    `make \\` over `check` is `make check`, which a line at a time read as
    nothing, and a `$(make check)` in an unquoted here-document's body is the
    command bash runs (`PL-55R2`). A fence bash cannot read - prose, output,
    another language - is read a line at a time from the line where it stops
    being readable, as every fence was before.

    A fenced line names a target wherever `make` heads one of the simple
    commands bash runs from it (`_simple_commands`), so `cd sub && make x`,
    `true; make x` and `set -o pipefail; make check | tail` each name theirs,
    which read from the line's first clause alone they did not (`PL-GZXY`).
    Each is reported on the line its `make` stands on, so one in a `$( )`
    carried across lines is not placed where the substitution opens; and a
    fence in a block quote is read without its markers, as `_fenced_blocks`
    gives it (`PL-5M36`).
    """
    for match in _code_spans(text):
        for mention in MAKE_MENTION_RE.finditer(SPAN_BREAK_RE.sub(" ", match["content"])):
            yield mention.group("name"), _line_of(text, match.start())
    for start, body in _fenced_blocks(text):
        script = "".join(f"{line}\n" for line in body)
        for piece, offset in script_lines(script):
            first = start + script.count("\n", 0, offset) + 1
            reading = shell_words(piece)
            if not reading.clauses:
                for at, line in enumerate(piece.split("\n")):
                    if (command := FENCED_MAKE_RE.match(line)) is not None:
                        yield command.group("name"), first + at
                continue
            for run in simple_commands(reading, piece):
                # Past a wrapper, as `timeout 600 make check` runs `make` (`PL-RHPK`).
                program = run.runs()
                arguments = run.words[program + 1 :] if program is not None else ()
                if program is not None and run.words[program] == "make" and arguments:
                    if (name := MAKE_TARGET_WORD_RE.match(arguments[0])) is not None:
                        yield name.group(), first + piece.count("\n", 0, run.start)


def check_make_targets(root: Path, documents: dict[Path, str], report: Report) -> None:
    """Hold every documented `make` command to a target that actually runs.

    `make docket` was named by three documents for two releases while the
    recipe sat under the pre-rename target name, so the store validation those
    documents promised had not run once. The failure is silent by
    construction, which is what makes it worth a check rather than a reader's
    attention.

    A Makefile whose statements `_make_lines` declines is reported as declined,
    since the targets it declares are then not known.
    """
    makefile = root / "Makefile"
    if not makefile.is_file():
        return
    try:
        declared, with_recipe = make_targets(makefile.read_text(encoding="utf-8"))
    except UnreadStatement as statement:
        report.declined.append(
            f"Makefile:{statement.line}: {statement.why}, so no documented `make` command "
            "was checked against it"
        )
        return
    for path, text in sorted(documents.items()):
        reported: set[tuple[str, int]] = set()
        for name, line in _make_mentions(text):
            if name in with_recipe or (name, line) in reported:
                continue
            reported.add((name, line))
            if name in declared:
                report.errors.append(
                    f"{path}:{line} names `make {name}`, which is declared but carries "
                    "no recipe, so it exits 0 without running"
                )
            else:
                report.errors.append(
                    f"{path}:{line} names `make {name}`, which the Makefile does not define"
                )


def workflow_commands(text: str) -> tuple[list[tuple[str, int]], list[UnreadStatement]]:
    """Every line of shell a workflow's `run:` steps execute, with the line number it starts on.

    A block scalar's body reaches bash as one script, so it is read as one,
    cut by docket's `shell.script_lines`: the lines a backslash, a quote or a
    substitution carries a command across are one line here, spelled as the
    workflow spells them, and a here-document's body and delimiter are no
    line at all, being the input of the command before them. A substitution
    in the body of a delimiter with no quoted part is the exception, a line
    of its own at the line it opens on, since bash expands that body and runs
    it (`PL-55R2`). Read one line at a time, as it was until `PL-Q9LK`,
    `drift.yml`'s `python3 - <<'PY'` body was a run of commands, and a
    continued command was declined.

    YAML hands bash the body less its own indentation, which its first
    non-blank line sets, and keeps the rest: `x\\` over an indented `y` is
    two words to bash, where stripping each line first would make it `xy`.

    **Which lines are a step's `run:` key is read from the workflow's
    structure** (`PL-S3XS`), through `required_checks_check.steps`: the `run:`
    of an entry of a job's `steps:` list. Read a line at a time, a `run:` line
    inside another key's block scalar was a step, a `defaults:` block's `run:`
    was a step declined, and a step written as a flow mapping across lines
    kept its closing brace in the command.

    **Where a step's value ends, and in which form, is read as YAML reads it**
    (`PL-R417`), through `_run_script`. A step, a job or a workflow in a form
    either reader declines is no commands here. It is returned beside the
    commands instead, so the check can say which it did not read and carry on
    to the next.

    **The declines are returned, not written to a list the caller passes**
    (`PL-GC59`). A caller that passed `[]` dropped them without a word, the
    shape in which `tools/dead_ends.py` once dropped the walker's (`PL-DQ9C`).
    """
    scripts, unread = _step_scripts(text)
    commands = [
        (command.strip(), script[body.count("\n", 0, offset)][1])
        for body, script in scripts
        for command, offset in script_lines(body)
        if command.strip()
    ]
    return commands, unread


def workflow_runs(text: str) -> tuple[list[tuple[str, ...]], list[UnreadStatement]]:
    """Every simple command a workflow's `run:` steps execute, each as its words.

    Each step's script is read in one pass of docket's `shell.shell_words`,
    which reads a compound command whole, so a `case` construct's word, its
    patterns and its `esac` are no commands and the commands in its arms are
    (`PL-M3M4`). Taken from `workflow_commands`' lines, each read on its own,
    the arm `check) make check ;;` read as `check` and `make check`, a script
    the merge gate never runs.

    A script that pass cannot read to its end is declined whole, at the line
    where the reading stops, and gives no commands. Read a line at a time
    instead, as it was until `PL-7CQ5`, a `case` construct above an unclosed
    quote gave `check`, `make check` and `esac` as commands, and only the
    unreadable line was declined.

    The declines come back beside the commands in the order of their lines,
    as `workflow_commands` returns its own: a step it declines is declined
    here too.
    """
    scripts, steps = _workflow_scripts(text)
    runs = [words for _, body, script in scripts for words in _script_runs(body, script, steps)]
    return runs, sorted(steps, key=lambda step: step.line)


def pull_request_runs(
    text: str,
) -> tuple[list[tuple[tuple[str, ...], UnreadStatement | None]], list[UnreadStatement]]:
    """Every simple command a workflow's steps may run on a pull request, with any doubt.

    `workflow_runs` reads every step, whatever its condition. This one reads
    the `if:` of each step and of the job that holds it, through
    `_runs_on_pull_requests`. A step that either condition keeps off the
    `pull_request` event gives no commands, so a script that runs only on a
    push to `main` is not counted as merge-gate coverage (`PL-ZXM1`). Each
    command of a step whose condition this reader cannot evaluate comes with
    the `UnreadStatement` that names the condition. The caller can then
    decline the command rather than count it as run on every pull request.
    The steps it declines come back beside the commands, as `workflow_runs`
    returns them.
    """
    lines = split_lines(text)
    scripts, steps = _workflow_scripts(text)
    runs: list[tuple[tuple[str, ...], UnreadStatement | None]] = []
    for step, body, script in scripts:
        doubt: UnreadStatement | None = None
        for key, whose in ((step.job_if, "job"), (step.keys.get("if"), "step")):
            condition = _runs_on_pull_requests(lines, key, whose)
            if condition is False:
                break
            if isinstance(condition, UnreadStatement):
                doubt = doubt or condition
        else:
            runs += [(words, doubt) for words in _script_runs(body, script, steps)]
    return runs, sorted(steps, key=lambda step: step.line)


#: A condition on the event that started the workflow. It is the one form of
#: `if:` that `_runs_on_pull_requests` evaluates, beside `always()` and
#: `success()`. A GitHub expression writes a string in single quotes only
#: ("Evaluate expressions in workflows and actions", docs.github.com, read
#: 2026-10-18).
EVENT_CONDITION_RE = re.compile(r"github\.event_name (?P<op>==|!=) '(?P<event>[a-z_]+)'")

#: Conditions under which a step runs whenever the steps before it succeeded.
ALWAYS_CONDITIONS = frozenset({"always()", "success()"})

#: A condition under which a pull request may skip a step that still counts as
#: the merge gate's, and why. The key is the condition as
#: `_runs_on_pull_requests` reads it, with no `${{ }}` and its blanks collapsed.
#: Like `GATE_ONLY`, it records a difference between the gates on purpose, so a
#: session that puts a gate script under a new condition has to say here why the
#: merge gate still asks it, or the comparison is declined.
GATE_CONDITIONS: dict[str, str] = {
    "steps.scope.outputs.scope != 'items'": (
        "the item-only fast path (`PL-DXD4`). It is false only on a pull request "
        "that `bin/docket ci-scope` finds changes nothing but item files, and "
        "`quality.yml` puts under it only steps whose result no item file can "
        "change. A push to `main` runs every step"
    )
}


def _runs_on_pull_requests(
    lines: Sequence[str], key: tuple[int, int] | None, whose: str
) -> bool | UnreadStatement:
    """Whether the `if:` at `key` lets a `pull_request` event run what it guards.

    `key` is the line index and column of the `if:` key, as
    `required_checks_check` gives a step's keys. `None` means there is no
    `if:`, so the step runs. The value is read as a plain scalar on its own
    line. A `${{ }}` around it is taken off, and its runs of blanks become one
    space. Only three forms are evaluated: `always()`, `success()`, and
    `github.event_name` compared with one event by `==` or `!=`. Those are the
    forms the workflows here use to guard a gate script, beside the conditions
    `GATE_CONDITIONS` records.

    Any other condition comes back as an `UnreadStatement` that names it, as
    does a value that is quoted, written as a block or carried onto the next
    line. Guessing would count a check as run when a pull request may skip it
    (`PL-ZQ3R`).
    """
    if key is None:
        return True
    index, column = key
    value = lines[index][column:].removeprefix("if:")
    condition = re.split(r"\s#", value, maxsplit=1)[0].strip()
    below = next((line for line in lines[index + 1 :] if line.strip()), "")
    if not condition or condition[0] in "'\"|>&*!{[" or _indent(below) > column:
        return UnreadStatement(
            index + 1,
            f"this {whose}'s `if:` is quoted, written as a block or carried past its line, "
            "which this reader does not read, so whether a pull request runs it is not known",
        )
    if condition.startswith("${{") and condition.endswith("}}"):
        condition = condition[3:-2]
    condition = " ".join(condition.split())
    if condition in ALWAYS_CONDITIONS or condition in GATE_CONDITIONS:
        return True
    event = EVENT_CONDITION_RE.fullmatch(condition)
    if event is None:
        return UnreadStatement(
            index + 1,
            f"this {whose}'s `if:` is `{condition}`, which this reader does not evaluate, so "
            "whether a pull request runs it is not known",
        )
    return (event["event"] in MERGE_GATE_EVENTS) == (event["op"] == "==")


def _script_runs(
    body: str, script: list[tuple[str, int]], steps: list[UnreadStatement]
) -> Iterator[tuple[str, ...]]:
    """The simple commands of one step's script, as `workflow_runs` reads them."""
    reading = shell_words(body)
    if reading.clauses:
        yield from _simple_commands(reading, body)
        return
    # `script_lines` hands the line where the reading stops on, with every
    # line after it, as its last piece.
    stop = script_lines(body)[-1][1]
    steps.append(
        UnreadStatement(
            script[body.count("\n", 0, stop)][1],
            "this `run:` step's script cannot be read to its end from this line - a "
            "quote, a command substitution or a backslash runs past it, or a `<<` has "
            "no delimiter - and none of the step was read, since a line of it read "
            "alone can be a fragment of a command bash runs, such as a `case` arm",
        )
    )


def _step_scripts(
    text: str,
) -> tuple[list[tuple[str, list[tuple[str, int]]]], list[UnreadStatement]]:
    """Each `run:` step's script, whole and a line at a time, as `workflow_commands` reads it.

    The script whole is the text bash is handed, each line ending in a
    newline; the lines carry the workflow line each sits on. The steps that
    `_step_script` declines come back beside the scripts.
    """
    scripts, unread = _workflow_scripts(text)
    return [(body, script) for _, body, script in scripts], unread


def _workflow_scripts(
    text: str,
) -> tuple[
    list[tuple[required_checks_check.Step, str, list[tuple[str, int]]]], list[UnreadStatement]
]:
    """The scripts `_step_scripts` gives, each with the step that runs it, and the declines."""
    lines = split_lines(text)
    try:
        steps = required_checks_check.steps(lines)
    except required_checks_check.Undecidable as workflow:
        steps = [required_checks_check.Step(workflow.line or 1, refused=workflow)]
    scripts: list[tuple[required_checks_check.Step, str, list[tuple[str, int]]]] = []
    unread: list[UnreadStatement] = []
    for step in steps:
        try:
            script = _step_script(step, lines)
        except UnreadStatement as declined:
            unread.append(declined)
            continue
        scripts.append((step, "".join(f"{line}\n" for line, _ in script), script))
    return scripts, unread


def _step_script(step: required_checks_check.Step, lines: list[str]) -> list[tuple[str, int]]:
    """The script one step's `run:` hands bash, a line at a time, or nothing where it has none.

    Raises `UnreadStatement` where the step, or the job holding it, was
    refused, naming why, or where its `run:` value is in a form `_run_script`
    declines.
    """
    if step.refused is not None:
        raise UnreadStatement(step.line, step.refused.why)
    if "run" not in step.keys:
        return []
    index, column = step.keys["run"]
    match = RUN_STEP_RE.match(lines[index])
    if match is None or len(match["lead"]) != column:
        raise UnreadStatement(
            index + 1,
            "this `run:` step's key is quoted, or spaced from its colon, which this reader "
            "does not split; write it `run:`",
        )
    end = index + 1
    while end < len(lines) and (not lines[end].strip() or _indent(lines[end]) > column):
        end += 1
    return _run_script(match, lines, index + 1, end)


def _indent(line: str) -> int:
    """How many spaces open a line, which is all YAML's indentation is made of (§ 6.1)."""
    return len(line) - len(line.lstrip(" "))


def _run_script(
    step: re.Match[str], lines: list[str], first: int, end: int
) -> list[tuple[str, int]]:
    """The script a `run:` step hands bash, a line at a time, each with its line number.

    `first` and `end` bound the lines after the key that are blank or
    indented past it, which is everything the value can span. Two forms are
    read, the two this repository's workflows write:

    - **A plain scalar on the key's line** is the command, less a comment after
      it, which YAML reads as none of the value (§ 6.6), so `run: echo 'x # y'`
      hands bash `echo 'x` (`PL-W9VC`). Nothing after it may
      carry it on: YAML folds a plain scalar's following, deeper lines into it
      as one line (YAML 1.2.2 § 7.3.3), so `run: python3 x.py` over an indented
      `--flag` is `python3 x.py --flag` to bash, where the line alone was half
      of it. A comment line is no continuation (§ 6.6).
    - **A literal block (`|`)** is the script, kept line for line. Its header
      may carry a chomping indicator, an indentation indicator - the content
      then sits that many columns past the key rather than where its first line
      does - and a comment (§ 8.1.1); each was read as the command before. It
      ends at the first line indented less than its content (§ 8.1.1.1), where
      `docket.frontmatter.block_content` ends it (`PL-W9VC`), which
      a sibling key like `shell:` is: read to the next line no deeper than the
      step's dash, as it was, that key became a line of the script. Only a
      comment may stand between the two, deeper than the key and short of the
      content (§ 8.1.1.2); any other line there is one PyYAML refuses, so it is
      declined at its own line, where the block's first lines were read as the
      whole script (`PL-5M36`).

    Every other form is declined by name, raising `UnreadStatement` at the
    key's line: a folded block (`>`), whose lines YAML joins before bash reads
    them (§ 8.1.3, `PL-6P6H`); a plain scalar carried onto the lines after it,
    or one opening on the line after the key, which YAML folds the same way; a
    quoted scalar, which YAML unquotes; and an anchor, alias, tag or flow
    collection, or any other node `docket.frontmatter.plain` says is no plain
    scalar, such as `|x`, a header YAML refuses, which was handed to bash as
    the command `|x` (`PL-8MHZ`). None is written in this repository's
    workflows, so each is refused rather than folded, the cheaper answer
    `PL-R417` allows while no workflow writes one.
    """
    line = first
    # Less its comment, which YAML reads as none of the value (§ 6.6); where the
    # key's line holds only a comment, the value is whatever the lines after it hold.
    inline = uncommented(step["inline"]).strip()
    after = [
        (at, text)
        for at, text in enumerate(lines[first:end], start=first)
        if text.strip() and not text.lstrip().startswith("#")
    ]
    header = BLOCK_SCALAR_RE.fullmatch(inline)
    if header is not None and header["style"] == "|":
        body = lines[first:end]
        # The key's line is `first - 1`, and the key's column the step's lead.
        content = block_content(lines, first - 1, len(step["lead"]), inline)
        assert content is not None, "a header `BLOCK_SCALAR_RE` matched"
        margin, stop = content[0], content[1] - first
        for at, text in enumerate(body[stop:], start=first + 1 + stop):
            if text.strip() and not text.lstrip().startswith("#"):
                raise UnreadStatement(
                    at,
                    "this line stands deeper than the `run:` key above it and short of its "
                    "literal block's content, which YAML refuses, where this reader would end "
                    "the block at it",
                )
        return [(text[margin:], first + 1 + at) for at, text in enumerate(body[:stop])]
    if header is not None:
        raise UnreadStatement(
            line,
            "this `run:` step is a folded block (`>`), whose lines YAML joins into one "
            "before bash reads them, and this reader does not; write it as a literal block "
            "(`|`)",
        )
    if inline and not yaml_plain(inline):
        form = "a quoted scalar" if inline[0] in "\"'" else f"a YAML node opening `{inline[0]}`"
        raise UnreadStatement(
            line,
            f"this `run:` step is {form}, which YAML resolves before bash reads it, and "
            "this reader does not; write the command itself, on the key's line or as a "
            "literal block (`|`)",
        )
    if after:
        where = "carried onto the line after it" if inline else "opening on the line after it"
        raise UnreadStatement(
            line,
            f"this `run:` step is a plain scalar {where}, which YAML folds into one line "
            "before bash reads it, and this reader does not; write it on the key's line or "
            "as a literal block (`|`)",
        )
    return [(inline, line)] if inline else []


def _shell_words(where: str, command: str, report: Report, unread: str) -> tuple[str, ...]:
    """The words a shell line runs, quotes removed, as docket's `shell.shell_words` reads them.

    That is the one reading of how a shell command splits (`PL-PVW2`), and
    this tool kept a split of its own until `PL-CWBJ`: a pattern cutting at
    whitespace and operators, inside quotes too, so `python3 "tools/my
    file.py"` read as `tools/my`. A command substitution's body is read as
    the command it is, so a path named inside one is read as well.

    The reading is of one line as bash reads one: a workflow's, which
    `workflow_commands` cuts so that a line holds every physical line a
    command spans, or a Makefile recipe's, which `_make_lines` hands over as
    make hands it to the shell, its continuations included.
    One whose quote, substitution or trailing backslash runs past its end, or
    whose `<<` never meets its delimiter, is a command this cannot place, so
    it is declined, naming `unread`, and answers no words rather than a guess
    at them.
    """
    reading = _shell_reading(where, command, report, unread)
    if reading is None:
        return ()
    return tuple(
        token.text
        for clause in reading.every_clause()
        for token in clause.tokens
        if isinstance(token, Word)
    )


def _shell_commands(
    where: str, command: str, report: Report, unread: str
) -> tuple[tuple[str, ...], ...]:
    """The simple commands a shell line runs, each as its words, read as `_shell_words` reads it.

    `_shell_words` hands back every word on the line, which is right for a
    question about paths and wrong for one about what a script was passed: in
    `python3 tools/x.py --check | tee log`, `tee` and `log` are not its
    arguments. So the words are cut where bash ends a simple command, at each
    control operator. A redirection does not end one, and neither its file nor
    the descriptor written against it - the `2` of `2>&1`, the `{fd}` of
    `{fd}>log` - is an argument, so both are left out, as `_simple_commands`
    says.
    """
    reading = _shell_reading(where, command, report, unread)
    return () if reading is None else _simple_commands(reading, command)


def _simple_commands(reading: Reading, command: str) -> tuple[tuple[str, ...], ...]:
    """The simple commands a reading of `command` runs, each as its words.

    Cut, and their redirections lifted out, by docket's `shell.simple_commands`,
    the one reading of where bash ends a simple command and what it hands one
    (`PL-7DXZ`). A word of a `case` construct's own syntax - the word it
    matches, `in`, a pattern, `esac` - is no word of a command (`PL-M3M4`).
    """
    return tuple(run.words for run in simple_commands(reading, command))


def _shell_reading(where: str, command: str, report: Report, unread: str) -> Reading | None:
    """Docket's reading of one shell line, or `None` once it is declined, naming `unread`."""
    reading = shell_words(command)
    if not reading.clauses:
        first, _, rest = command.partition("\n")
        more = rest.count("\n") + 1 if rest else 0
        shown = f"`{first}`" + (f" and the {more} line(s) after it" if more else "")
        report.declined.append(
            f"{where}: {shown} cannot be read to its end - a quote, a command substitution "
            f"or a backslash runs past it, or a `<<` has no delimiter - so {unread}"
        )
        return None
    return reading


def _command_paths(words: Iterable[str]) -> Iterator[str]:
    """Every word of a shell line that is written as a path."""
    for word in words:
        token = word.strip(",")
        # `--cov=src/x` and `KEY=path` carry the path on the right of the `=`.
        if "=" in token:
            token = token.rpartition("=")[2]
        token = token.removeprefix("./")
        if "/" not in token or token.startswith("-"):
            continue
        if any(mark in token for mark in UNRESOLVABLE):
            continue
        yield token


QUALITY_WORKFLOW = Path(".github/workflows/quality.yml")
# The floor section is the `run:` steps after the step that installs the
# floor's interpreter and before the step that installs uv. `docs/apparatus.md`
# lists them between these two markers.
FLOOR_OPENS = "actions/setup-python@"
FLOOR_CLOSES = "astral-sh/setup-uv@"
FLOOR_LIST_OPENS = "<!-- floor-commands -->"
FLOOR_LIST_CLOSES = "<!-- /floor-commands -->"


def _command_key(command: str) -> str:
    """A command's first two words, stopping at an option, which is how the floor list names one.

    `python3 tools/pr_body_check.py --anchors` and `python3
    tools/pr_body_check.py` are the same tool here. The list in
    `docs/apparatus.md` drifted by gaining and losing whole commands, never by
    an argument, and `bin/docket ci-scope` is quoted there without its
    arguments.
    """
    words: list[str] = []
    for word in command.split()[:2]:
        if word.startswith("-"):
            break
        words.append(word)
    return " ".join(words)


def floor_commands(text: str) -> tuple[list[tuple[str, int]], list[UnreadStatement]] | None:
    """The commands `quality.yml`'s floor section runs, or None where it has no such section."""
    lines = split_lines(text)
    scripts, unread = _workflow_scripts(text)
    commands: list[tuple[str, int]] = []
    inside = False
    for step, _, script in scripts:
        if "uses" in step.keys:
            index, column = step.keys["uses"]
            action = lines[index][column:].removeprefix("uses:").strip()
            if action.startswith(FLOOR_OPENS):
                inside = True
                continue
            if inside and action.startswith(FLOOR_CLOSES):
                return commands, unread
        if inside:
            commands.extend(script)
    return None


def check_floor_list(root: Path, report: Report) -> None:
    """Hold `docs/apparatus.md`'s list of the CI floor commands to the workflow.

    The list was written by hand, and it drifted five times between 2026-09-05
    and 2026-10-11: commands were added to the floor section and removed from
    it, and nothing compared the two (`PL-5N7T`). `check_workflow_paths`
    resolves the paths each command names, which is a different question. A
    path that exists says nothing about whether the list is complete.

    The list is the code spans between `FLOOR_LIST_OPENS` and
    `FLOOR_LIST_CLOSES` that start with `python3 ` or `bin/`. Each side is
    compared by `_command_key`. A workflow with no floor section, or no
    workflow, is not held, and a list whose markers are missing while the
    floor section exists is an error.
    """
    workflow = root / QUALITY_WORKFLOW
    if not workflow.is_file():
        return
    read = floor_commands(workflow.read_text(encoding="utf-8"))
    document = root / APPARATUS
    text = document.read_text(encoding="utf-8") if document.is_file() else ""
    opens, closes = text.find(FLOOR_LIST_OPENS), text.find(FLOOR_LIST_CLOSES)
    if read is None:
        if opens != -1:
            report.errors.append(
                f"{APPARATUS}: lists the floor section's commands, but {QUALITY_WORKFLOW} "
                f"has no step using {FLOOR_OPENS} followed by one using {FLOOR_CLOSES}"
            )
        return
    commands, unread = read
    for declined in unread:
        report.declined.append(
            f"{QUALITY_WORKFLOW}:{declined.line}: a step was not read ({declined.why}), "
            f"so the floor list in {APPARATUS} may be held to fewer commands than run"
        )
    if opens == -1 or closes < opens:
        report.errors.append(
            f"{APPARATUS}: no list of the floor section's commands between "
            f"{FLOOR_LIST_OPENS} and {FLOOR_LIST_CLOSES}, so nothing holds it to "
            f"{QUALITY_WORKFLOW}"
        )
        return
    listed = {
        _command_key(span["content"])
        for span in code_spans(text, opens, closes)
        if span["content"].startswith(("python3 ", "bin/"))
    }
    run = {_command_key(command): line for command, line in commands}
    line = text.count("\n", 0, opens) + 1
    for key in sorted(run.keys() - listed):
        report.errors.append(
            f"{APPARATUS}:{line}: the floor list leaves out `{key}`, which "
            f"{QUALITY_WORKFLOW}:{run[key]} runs in the floor section"
        )
    for key in sorted(listed - run.keys()):
        report.errors.append(
            f"{APPARATUS}:{line}: the floor list names `{key}`, which the floor section "
            f"of {QUALITY_WORKFLOW} does not run"
        )


def check_workflow_paths(root: Path, report: Report) -> None:
    """Resolve every repository path a CI step runs.

    `tools/punch_list.py` was deleted with every documentation reference to it
    found and fixed, while the workflow step invoking it was missed and would
    have failed on merge. A broken CI reference is discovered at the worst
    possible moment - after review, on the merge - so it is held to the same
    standard as a path cited in prose.
    """
    workflows = sorted(
        path for pattern in WORKFLOW_GLOBS for path in root.glob(pattern) if path.is_file()
    )
    if not workflows:
        return
    # A token claims to be a repository path when its first segment names
    # something at the top of the checkout. That is what separates `bin/docket`
    # from `actions/checkout@v7.0.1`, and it is why the suffix rule in
    # `_is_path_citation` does not work here: `bin/docket` has no suffix, and
    # it is exactly the reference this check exists to hold.
    top_level = {child.name for child in root.iterdir()}
    unread = "the paths it runs were not resolved"
    for path in workflows:
        relative = path.relative_to(root)
        reported: set[tuple[str, int]] = set()
        commands, steps = workflow_commands(path.read_text(encoding="utf-8"))
        for command, line in commands:
            words = _shell_words(f"{relative}:{line}", command, report, unread)
            for token in _command_paths(words):
                if PurePosixPath(token).parts[0] not in top_level:
                    continue
                if (token, line) in reported:
                    continue
                reported.add((token, line))
                if not (root / token).exists():
                    report.errors.append(f"{relative}:{line}: runs `{token}`, which does not exist")
        _decline_steps(report, relative, steps, unread)


def _decline_steps(
    report: Report, workflow: Path, steps: Iterable[UnreadStatement], unread: str
) -> None:
    """Say which steps `workflow_commands` declined, and what went unchecked for it."""
    for step in steps:
        report.declined.append(f"{workflow}:{step.line}: {step.why}, so {unread}")


# What marks the invocation the two files promise to keep identical. The
# coverage threshold is the whole point of the promise - it is what holds
# `core/` at 100% of statements and branches - so the flag that carries it is
# the right key. Deliberately narrower than "every pytest command": `drift.yml`
# runs a bare `uv run pytest` on purpose, because a coverage failure there
# would report as a dependency break, and a blanket rule would fire on it every
# run (`PL-22Z3`).
COVERAGE_GATE_MARK = "--cov-fail-under"

# How CI's pytest line marks itself as one part of the coverage run (`PL-T9X9`).
# It is the Makefile's line with ` --cov-fail-under=N` replaced by these flags
# at its end, and `--cov-report=` keeps the part from printing its own partial
# total.
COVERAGE_PART = re.compile(r" --cov-report= --part (?P<index>\d+)/(?P<parts>\d+)$")

# The command that holds the parts' combined coverage to the threshold.
COVERAGE_REPORT = re.compile(r"^uv run coverage report\b.* --fail-under=(?P<threshold>\S+)$")


def _recipe_commands(text: str) -> Iterator[tuple[str, int]]:
    """Every command a Makefile recipe hands the shell, with the line it opens on.

    A recipe line is one beginning with a tab while a rule is open, as
    `_make_lines` reads it, which hands back a recipe after a rule line's `;`
    as one (`PL-GZXY`); which target it belongs to does not matter here,
    because the mark above is what selects the line rather than its position.
    A line a tab leads above the first rule, or after an assignment ends the
    rule above it, is the statement its words make and no command: read by its
    tab alone, an assignment indented with one was a command (`PL-BMZN`). A
    command a backslash continues is one, spelled as make hands it over; read a
    physical line at a time it was two, the first ending in the backslash
    (`PL-G2FY`). A line in a `define` body is a variable's value and no command
    (`PL-4MLK`). Each is the command `_recipe_command` reads, make's prefixes
    gone (`PL-QYF4`). Raises `UnreadStatement` where `_recipe_statements` does.
    """
    for line, number in _recipe_statements(text):
        if line.startswith("\t") and (command := _recipe_command(line)):
            yield command, number


def _recipe_statements(text: str, every_branch: bool = True) -> list[tuple[str, int]]:
    """`_make_lines`' statements, for a reader that takes each recipe line for a command.

    That is how GNU make 4.3 hands a recipe to the shell by default, a line to
    a shell. A Makefile naming the special target `.ONESHELL` anywhere hands
    each whole recipe to one shell instead (GNU make manual, "Using One
    Shell"), so a here-document's body runs on across recipe lines and a line
    is no command of its own; run through make 4.3 on 2026-10-10, it took
    effect named after the rule it changed and named beside another target.
    No Makefile here names it, so one that does is declined by name rather
    than read as one script, the cheaper of `PL-X43T`'s two endings. Read a
    line at a time, a `ruff check` in a here-document's body was a command the
    ruff cache check refused. Raises `UnreadStatement` at the line naming it,
    and where `_make_lines` does, with `every_branch` passed on to it.
    """
    statements = list(_make_lines(text, every_branch))
    for statement, line in statements:
        if statement.startswith("\t"):
            continue
        if ".ONESHELL" in (_make_rule(statement) or NO_TARGETS).targets:
            raise UnreadStatement(
                line,
                "this Makefile names `.ONESHELL`, under which make hands each recipe to one "
                "shell as a script, and this reader reads each recipe line as a command of "
                "its own",
            )
    return statements


def check_coverage_gate(root: Path, report: Report) -> None:
    """Hold the Makefile's coverage run and CI's to the same command.

    Both files say in comments that they must stay the same, and nothing
    checked it. They are the local gate and the merge gate, so a drift between
    them means a session sees one answer and CI sees another - or, worse, both
    stay green while only one of them still enforces the threshold. That is a
    silent divergence in the check that holds `core/` at 100%, which is the
    kind of exact rule a hard failure is for rather than an advisory
    (`PL-D3M2`).

    Exact string equality, not a parse, after one normalization: Make doubles
    `$` in a recipe to pass a single one through to the shell, so a command
    containing a shell substitution is spelled `$$(...)` there and `$(...)` in
    the workflow. That is a documented rule of Make rather than a judgment about
    which differences are legitimate, which is what keeps this decidable - and
    `CLAUDE.md` reserves scripted rules for exactly that half. Nothing else is
    normalized; any other difference is still a drift.

    The escape became load-bearing when the worker count stopped being `-n auto`
    and became `$(python3 -c 'import os; print(os.cpu_count() * 2)')`, which
    reads the runner the way `auto` did while asking for twice the width, for a
    suite where much of the work waits on subprocesses rather than CPU
    (`PL-VZ8P`).

    A command continued across lines is compared whole, as each shell is
    handed it - make's continuation less its leading tab, the workflow's less
    YAML's indentation - and with its continuations, under the same strict
    rule: the two files split it alike or not at all. Read a physical line at
    a time, the Makefile's first fragment was compared with CI's whole command
    (`PL-G2FY`).

    CI may run the suite in parts, on several runners, and hold their combined
    coverage to the threshold in a `coverage report` step (`PL-T9X9`). Each
    part's line is then the Makefile's with `--cov-fail-under=N` replaced by
    `COVERAGE_PART`'s flags, so `_coverage_parts` puts the threshold back
    before the comparison. The rule stays exact: a part compares equal only if
    the rest of its line is the Makefile's, character for character.

    Silent where neither file names the mark, so a checkout that has not
    adopted a coverage gate is not failed for the absence of one; declined
    where `_make_lines` declines the Makefile, since its side is then unknown.
    """
    makefile = root / "Makefile"
    workflows = sorted(
        path for pattern in WORKFLOW_GLOBS for path in root.glob(pattern) if path.is_file()
    )
    local: list[tuple[str, str]] = []
    if makefile.is_file():
        try:
            local = [
                # `$$` -> `$` per the docstring: this is Make's escape for a literal
                # `$`, so the shell sees what the workflow's line already says.
                (command.replace("$$", "$"), f"Makefile:{line}")
                for command, line in _recipe_commands(makefile.read_text(encoding="utf-8"))
                if COVERAGE_GATE_MARK in command
            ]
        except UnreadStatement as statement:
            report.declined.append(
                f"Makefile:{statement.line}: {statement.why}, so the coverage gate was not compared"
            )
            return
    remote: list[tuple[str, str]] = []
    parts: list[tuple[re.Match[str], str]] = []
    thresholds: list[tuple[str, str]] = []
    steps: list[UnreadStatement] = []
    for path in workflows:
        relative = path.relative_to(root)
        commands, unread = workflow_commands(path.read_text(encoding="utf-8"))
        for command, line in commands:
            origin = f"{relative}:{line}"
            if COVERAGE_GATE_MARK in command:
                remote.append((command, origin))
            elif part := COVERAGE_PART.search(command):
                parts.append((part, origin))
            elif threshold := COVERAGE_REPORT.search(command):
                thresholds.append((threshold["threshold"], origin))
        _decline_steps(report, relative, unread, "the coverage gate was not compared")
        steps += unread
    # A step CI's side could not read may be the coverage run, so neither
    # "absent" nor "differs" would be a fact; the declines above say why.
    if steps:
        return
    if parts:
        folded = _coverage_parts(parts, thresholds, report)
        if folded is None:
            return
        remote += folded
    if not local and not remote:
        return
    # Reported before the comparison, because "the sets differ" is the wrong
    # sentence for a gate that is missing from one side entirely - and an
    # absent gate is the more serious of the two findings.
    for name, found, other in (("Makefile", local, remote), ("CI", remote, local)):
        if not found and other:
            report.errors.append(
                f"the {name} runs no `{COVERAGE_GATE_MARK}` command while "
                f"{other[0][1]} does, so only one of the two gates gates coverage"
            )
            return
    if {command for command, _ in local} != {command for command, _ in remote}:
        where = ", ".join(f"{origin}: `{command}`" for command, origin in local + remote)
        report.errors.append(
            "the coverage gate differs between the Makefile and CI, so the local "
            f"gate and the merge gate are not asking the same question - {where}"
        )


def _coverage_parts(
    parts: Sequence[tuple[re.Match[str], str]],
    thresholds: Sequence[tuple[str, str]],
    report: Report,
) -> list[tuple[str, str]] | None:
    """CI's parts as the one coverage run they split, or None after reporting an error.

    The parts must be numbered 1 to N, once each, or some tests would run in
    no part. One threshold must hold their combined coverage, since without
    it no CI step enforces one. Each part then folds back into its line with
    `--cov-fail-under=` that threshold, for the comparison with the Makefile.
    """
    numbers = sorted((int(found["index"]), int(found["parts"])) for found, _ in parts)
    count = numbers[0][1]
    if numbers != [(index, count) for index in range(1, count + 1)]:
        where = ", ".join(
            f"{origin}: part {found['index']}/{found['parts']}" for found, origin in parts
        )
        report.errors.append(
            f"CI runs the coverage run in parts that are not numbered 1 to {count} once each, "
            f"so some tests may run in no part - {where}"
        )
        return None
    distinct = {threshold for threshold, _ in thresholds}
    if len(distinct) != 1:
        found_at = ", ".join(f"{origin}: `--fail-under={value}`" for value, origin in thresholds)
        report.errors.append(
            "CI runs the coverage run in parts, and "
            + (
                f"its `coverage report` steps disagree on the threshold - {found_at}"
                if distinct
                else "no `uv run coverage report --fail-under` step holds their combined coverage"
            )
        )
        return None
    threshold = distinct.pop()
    return [
        (found.string[: found.start()] + f" {COVERAGE_GATE_MARK}={threshold}", origin)
        for found, origin in parts
    ]


#: A `ruff check` invocation, however it is prefixed: the two words, one after
#: the other, in one simple command as the shell reads it. Word by word, so that
#: `ruff format --check` - which is a different command with a sound cache - is
#: not swept in by the word `check`; and words rather than a pattern over the
#: text, so that a continuation between the two is no gap (`PL-R417`).
RUFF_CHECK = ("ruff", "check")
RUFF_NO_CACHE_FLAG = "--no-cache"


def check_ruff_cache(root: Path, report: Report) -> None:
    """Hold every `ruff check` the Makefile runs to a cache-free invocation.

    `ruff check`'s import sorter decides first-party by probing the full dotted
    path under the `src` roots, so its verdict on one file depends on whether a
    *different* file exists - while ruff's cache keys a stored result to the
    linted file's mtime and permission bits and nothing else. Nothing
    invalidates the entry when the module it depended on is deleted, so every
    file importing that module keeps a stale clean verdict and the local gate
    passes on a tree CI's fresh checkout fails. Measured on ruff 0.16.4,
    2026-09-15: the delete direction goes stale, the add direction does not,
    which puts the whole of the failure in the direction that turns the gate
    green (`PL-QSJM`). Upstream carries the same root cause open for `INP001`,
    which depends on `__init__.py` the same way (astral-sh/ruff#5449).

    The exposure is narrower than it was, and not gone. All four files the port
    left stale were outside the package, where only the filesystem probe
    settled an `anesthesia_sim.*` import; since `PL-VZYS` a `known-first-party`
    declaration settles every such import by name before the probe is reached,
    and one in `subprojects/docket/ruff.toml` does the same for `docket`. What
    still reaches the probe is a tool importing a sibling under `tools/` - nine
    imports of five modules on 2026-09-27, four of which go stale on deletion -
    and whatever first-party package arrives next, so the flag stays required.

    An exact rule about one flag on one line, so a hard failure rather than an
    advisory - there is no context in which a cached `ruff check` is the
    intended thing here, and `CLAUDE.md` reserves advisories for signals
    needing judgment.

    **The Makefile only, deliberately**, which is where this differs from
    `check_coverage_gate` directly above. That check holds the two files
    together because both run the gate; this one must not, because CI has no
    cache to go stale - a fresh checkout restores uv's cache and never
    `.ruff_cache` - so requiring the flag there would be requiring a no-op, and
    a rule that fires where nothing can go wrong is the defect `CLAUDE.md` asks
    checks to be retired for. CI's line is the reference answer this one exists
    to make the Makefile match.

    Silent where the Makefile runs no `ruff check` at all: the rule is about how
    an invocation is spelled, not about whether a checkout ought to have one.
    Declined where `_make_lines` declines the Makefile, whose commands are then
    not known.
    """
    makefile = root / "Makefile"
    if not makefile.is_file():
        return
    try:
        commands = list(_recipe_commands(makefile.read_text(encoding="utf-8")))
    except UnreadStatement as statement:
        report.declined.append(
            f"Makefile:{statement.line}: {statement.why}, so whether the Makefile runs "
            "`ruff check` without the flag was not decided"
        )
        return
    unread = "whether it runs `ruff check` without the flag was not decided"
    for command, line in commands:
        for words in _shell_commands(f"Makefile:{line}", command, report, unread):
            pairs = zip(words, words[1:], strict=False)
            if RUFF_CHECK in pairs and RUFF_NO_CACHE_FLAG not in words:
                report.errors.append(
                    f"Makefile:{line} runs `{' '.join(words)}` without `{RUFF_NO_CACHE_FLAG}`, "
                    "so a module deleted since the last run leaves a stale clean result on "
                    "every file that imports it and the local gate passes where CI fails"
                )


def _without_code(text: str) -> list[str]:
    """Every line with its code blanked, so only prose reaches the math rules.

    Blanking rather than deleting keeps the line numbering true. Well-formed
    math spans are blanked too: they are correct by construction, and what the
    rules look for is the debris a malformed one leaves behind. One is a code
    span on one line with a `$` against each of its runs, as GitHub reads
    `$`...`$`, so it is found among the code spans rather than ahead of them
    (`_blanked_code`).

    **An indented code block is code too**, by CommonMark's own definition: a
    run of lines indented four columns past their container, which cannot
    interrupt a paragraph. A regex shown that way failed as LaTeX GitHub does
    not render, in a document and in an item alike (`PL-XGYH`). Which lines are
    one is `markdown`'s reading, as `block_lines` gives it: a heading, a
    thematic break and a one-line HTML block each end on their own line, so a
    line indented four under one opens a code block, where a flag set by any
    non-blank line above read it as that line's paragraph going on and refused
    its TeX-shaped text (`PL-K77Q`).

    A fenced block is where `docket.fences` finds one, blanked from its opening
    line through its closing one, so an opener nothing closes blanks nothing
    and the prose below it is still read (`PL-92MY`). It is found in the body
    alone, and a YAML front matter's statements are its keys (`_statements`),
    so a fence-shaped line in a block scalar pairs with none of the body's
    fences and a backtick one key leaves open pairs with nothing (`PL-WX79`).

    **A code span is read from its statement whole, not a line at a time**
    (`PL-Z8RS`). CommonMark lets a span continue across a line ending (0.31.2
    § 6.1), and read a line at a time, a wrapped span's closing run paired with
    the next span's opening run on its line and blanked the prose between them:
    a TeX delimiter there went unchecked. Nor past its statement, which a list
    item's or a block quote's start ends as surely as a blank line does
    (`PL-FP7J`): a stray backtick paired across one the same way. One
    exception keeps the split-math rule's evidence: where a wrapped span's run
    stands against a `$`, the span is an inline expression the wrap broke, so
    that run is left for `MATH_EDGE_RE` to report on its line, as it was when
    neither half read as a span.
    """
    source = split_lines(text)
    code = _fenced_lines(text) | block_lines(_body_lines(source), (CODE,))
    lines = [
        "" if index in code or not raw.strip() else raw.expandtabs(4)
        for index, raw in enumerate(source)
    ]
    # A code span is blanked before either rule runs: `\(` inside one is a
    # quotation of the broken syntax rather than a use of it, and a shell
    # snippet like `"$upstream..HEAD"` is not an unclosed expression. Each is
    # read within its statement, as `_statement_spans` reads one (`PL-FP7J`).
    for first, end in _statements(source):
        lines[first:end] = _blanked_code("\n".join(lines[first:end])).split("\n")
    return lines


def _blanked_code(prose: str) -> str:
    """One statement's text with its code spans blank, and each inline expression's dollars.

    An inline expression is a code span on one line with a `$` against each of
    its runs. Read ahead of the code spans, a line at a time, a pattern for
    `$`...`$` took a backtick a span opened on the line above had already
    claimed for a well-formed expression, so the backtick and dollar the page
    shows as literal text went unreported (`PL-9TZH`); and it paired the dollar
    ending one span with the one opening the next, blanking the prose between
    them as math (`PL-8NPN`). A dollar the expression before has taken opens
    none.
    """
    kept: list[str] = []
    done = 0
    for span in code_spans(prose):
        start, end = span.span()
        blank = _blanked_span(prose, span)
        expression = start > done and prose[start - 1] == "$" and prose[end : end + 1] == "$"
        if expression and "\n" not in blank:
            start, end, blank = start - 1, end + 1, f" {blank} "
        kept += [prose[done:start], blank]
        done = end
    return "".join(kept) + prose[done:]


def _blanked_span(prose: str, span: re.Match[str]) -> str:
    """A code span's text as `_without_code` hands it on: blank, its line breaks kept.

    A span a line ending splits keeps a run that stands against a `$` - see
    `_without_code`.
    """
    blank = re.sub(r"[^\n]", " ", span.group(0))
    if "\n" not in blank:
        return blank
    run = len(span["run"])
    if prose[span.start() - 1 : span.start()] == "$":
        blank = span["run"] + blank[run:]
    if prose[span.end() : span.end() + 1] == "$":
        blank = blank[:-run] + span["run"]
    return blank


#: A script, in one mode, that one gate runs and the other deliberately does
#: not, and why. The key is the script as `_gate_invocations` spells it - its
#: path, then its mode, as `tools/pr_title_check.py --discover` - so an entry
#: excuses that mode alone and never the script's others (`PL-RW3T`). The value
#: is the side it is allowed to be alone on and the reason it is there, and
#: `check_gate_parity` below refuses every asymmetry that is not written here.
#: It is the answer to the question a session meets when it wires a new script
#: into `make check`: cover it in CI too, or say in one line why the merge gate
#: cannot ask it (`PL-PBP5`).
GATE_ONLY: dict[str, tuple[str, str]] = {
    "bin/docket check": (
        "ci",
        "the floor run: `quality.yml` runs it before `uv` exists, which is what proves "
        "the store's own check needs no virtualenv under the 3.11 floor, and `make "
        "check` asks everything it asks inside its `--verify` run, which only adds the "
        "replay",
    ),
    "bin/docket ci-scope --base --github-output": (
        "ci",
        "the item-only fast path's question: `quality.yml` asks it on a pull request "
        "to decide which steps to skip, and `make check` runs every check whatever a "
        "branch changed, so it has nothing to decide (`PL-DXD4`)",
    ),
    "tools/pr_record_check.py": (
        "ci",
        "the event mode: it reads the pull request's number from `PR_NUMBER`, which "
        "only the `pull_request` event sets, so a checkout has nothing to read and "
        "`make check` runs the `--discover` mode below in its place",
    ),
    "tools/pr_record_check.py --discover": (
        "local",
        "the event mode's stand-in: it asks this branch's open pull request for the "
        "number and skips silently with no token, no network or no pull request, so it "
        "can never be the merge gate's answer, and CI reads the event instead (`PL-HMZZ`)",
    ),
    "tools/pr_title_check.py": (
        "ci",
        "the event mode: it reads the title from `PR_TITLE`, which only the "
        "`pull_request` event sets, so a checkout has nothing to read and `make check` "
        "runs the `--discover` mode below in its place",
    ),
    "tools/pr_title_check.py --discover": (
        "local",
        "the event mode's stand-in: it asks this branch's open pull request for the "
        "title and skips silently with no token, no network or no pull request, so it "
        "can never be the merge gate's answer, and CI reads the event instead (`PL-J3BB`)",
    ),
    "tools/required_checks_check.py": (
        "ci",
        "its answer is not in the tree: it reads the repository's required status "
        "checks off the GitHub API and reconciles them against the jobs that report "
        "them, so a checkout with no network and no token has nothing to compare",
    ),
}

#: Where a gate script may be named. `.py` is every check this project has
#: written; `bin/docket` is the one that is not a `.py` path, being the store's
#: own entry point.
GATE_SCRIPT_SUFFIX = ".py"
GATE_SCRIPT_NAMES = ("bin/docket",)

#: The workflow trigger that makes a job part of the merge gate. A workflow
#: that runs only on a schedule - `drift.yml` here - is not one: a branch can
#: be merged without it ever having looked. Nor is `pull_request_target`, which
#: "runs in the context of the default branch of the base repository, rather
#: than in the context of the merge commit" (*Events that trigger workflows*,
#: docs.github.com, read 2026-10-05), so the steps it runs are not the branch's.
MERGE_GATE_EVENTS = frozenset({"pull_request"})


def _target_recipes(text: str) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Every Makefile target's own recipe lines and its prerequisites.

    `_recipe_commands` above reads recipe lines without asking which target
    they belong to, which is right for a check that selects on a mark in the
    command. This one has to know, because the question is what one *target*
    runs.

    Blank lines and comment lines do not end a recipe, which is a rule of Make
    rather than a convenience: this Makefile carries a paragraph of reasoning
    above almost every command, and reading a comment as the end of the target
    would have found one command under `check` where there are twenty.
    `_make_lines` gives no statement for either, so this reader and
    `make_targets` end a rule at the same line, where make ends it (`PL-TDVJ`).

    Read by statement (`_make_lines`), so a command a backslash continues is
    one, and a prerequisite list it continues is read whole rather than its
    second line taken for a command (`PL-G2FY`). A `define` is one statement, an
    assignment, so it ends the target above it and nothing in its body is a
    target or a command (`PL-4MLK`). A line a tab leads where no rule is open is
    no command (`PL-BMZN`). Each rule line is read by `_make_rule`, so a
    comment's words are no prerequisites, a target-specific variable gives no
    target a rule, and every target a rule names takes its recipe and its
    prerequisites, which make gathers across every rule line naming a target,
    though not in the order make runs them (`PL-HR4V`); a recipe after a `;`
    on the rule's own line is its first command (`PL-GZXY`). A recipe line
    `_recipe_command` finds no command in is none here, as it is none to
    `make_targets` (`PL-5M36`), and a line's command is that one, make's
    prefixes gone (`PL-QYF4`). Raises `UnreadStatement` where
    `_recipe_statements` does, a Makefile naming `.ONESHELL` included
    (`PL-X43T`), and at a recipe line inside a conditional, since what the
    target runs then turns on the branch make takes. Read with every branch
    taken, `check:` over `ifdef X` ran both branches' commands, where make runs
    one (`PL-HSB3`).
    """
    recipes: dict[str, list[str]] = {}
    prerequisites: dict[str, list[str]] = {}
    current: tuple[str, ...] = ()
    for line, _ in _recipe_statements(text, every_branch=False):
        if line.startswith("\t"):
            command = _recipe_command(line)
            for target in current if command else ():
                recipes[target].append(command)
            continue
        rule = _make_rule(line) or NO_TARGETS
        current = rule.targets
        for target in current:
            recipes.setdefault(target, [])
            prerequisites.setdefault(target, []).extend(rule.prerequisites)
    return recipes, prerequisites


def _target_commands(
    recipes: dict[str, list[str]],
    prerequisites: dict[str, list[str]],
    target: str,
    seen: set[str] | None = None,
) -> list[str]:
    """What `make <target>` runs, prerequisites first, each target once."""
    seen = set() if seen is None else seen
    if target in seen or target not in recipes:
        return []
    seen.add(target)
    commands: list[str] = []
    for prerequisite in prerequisites.get(target, []):
        commands += _target_commands(recipes, prerequisites, prerequisite, seen)
    return commands + recipes[target]


def _gate_scripts(root: Path, words: Iterable[str]) -> Iterator[tuple[int, str]]:
    """Every repository script a command's words name, as a repository-relative path.

    Each comes with where it stands among the words, since what follows it
    there is what it was passed.

    The rule is deliberately about *this project's own* scripts and not about
    the commands around them. `ruff`, `mypy`, `pytest` and `uv` are third-party
    programs whose two invocations are already reconciled one by one, where
    that is worth doing, by `check_coverage_gate` and `check_ruff_cache` above;
    `sudo apt-get install` is an OS package rather than a gate. What recurs -
    and what `PL-PBP5` was filed about - is a check written here, wired into
    one gate, and never added to the other.

    A token counts when it ends in `.py` or is `bin/docket`, *and* names a file
    that exists. The second half is what keeps a `.py` written in prose, or a
    path a step creates, out of the comparison.
    """
    for at, word in enumerate(words):
        token = word.strip(",").removeprefix("./")
        if "=" in token:
            token = token.rpartition("=")[2]
        if not token.endswith(GATE_SCRIPT_SUFFIX) and token not in GATE_SCRIPT_NAMES:
            continue
        if any(mark in token for mark in UNRESOLVABLE):
            continue
        if (root / token).is_file():
            yield at, token


def _mode(arguments: Sequence[str]) -> tuple[str, ...]:
    """What a script's arguments choose it to do: its subcommand, then its options' names.

    The subcommand is every word ahead of the first option - `check` in
    `bin/docket check` - and an option's name is the word as written, or its
    part before an `=`. The rest are values and are dropped, since
    `--verify-base origin/main` locally and `--verify-base "$VERIFY_BASE"` in
    CI are one mode handed two refs, and the names are sorted, since their order
    chooses nothing.
    """
    subcommand: list[str] = []
    for word in arguments:
        if word.startswith("-"):
            break
        subcommand.append(word)
    names = {word.partition("=")[0] for word in arguments if word.startswith("-")}
    return (*subcommand, *sorted(names))


def _gate_invocations(root: Path, commands: Iterable[Sequence[str]]) -> Iterator[tuple[str, ...]]:
    """Every repository script the commands run, each followed by the mode it runs in."""
    for words in commands:
        for at, script in _gate_scripts(root, words):
            yield (script, *_mode(words[at + 1 :]))


def _gates_pull_requests(text: str, branch: str | None = None) -> bool:
    """Whether every pull request onto `branch` runs this workflow on `pull_request`.

    Asked of `required_checks_check`'s one reader of a workflow's triggers
    (`PL-848V`), so the merge gate and the required-checks reconciliation read
    each spelling of `on:` alike. Two hand readers had each read a few: this
    one took `on:` over a commented or anchored block, `- pull_request` and
    `pull_request:  # why` for a workflow gating nothing (`PL-PZP7`,
    `PL-S3XS`). `branch` is what a branch filter is matched against, `None`
    where no default branch could be established.

    A spelling or filter that reader declines - a flow collection carried past
    its line (`PL-R417`), a path filter - raises `UnreadStatement` naming it.
    """
    try:
        return required_checks_check.reports_on(
            required_checks_check.triggers(split_lines(text)), MERGE_GATE_EVENTS, branch
        )
    except required_checks_check.Undecidable as unread:
        raise UnreadStatement(unread.line or 1, unread.why) from unread


def check_gate_parity(root: Path, report: Report) -> None:
    """Hold the scripts `make check` runs and the scripts the merge gate runs to one set.

    `make check` is the gate a session runs before it commits and CI's job is
    the gate a branch has to pass to merge, and they are two independently
    maintained lists of commands. Nothing compared them, so a script wired into
    one was silently absent from the other - and the asymmetry is invisible in
    both directions. `tools/dead_ends.py`, `tools/ignore_check.py` and
    `tools/possessive_section_check.py` were all `make check`-only, two of them
    for weeks, which means a branch pushed without a local `make check` landed
    green on a tree `make check` would have refused. `PL-PBP5`.

    **The two gates are not made one, and that is the finding rather than a
    compromise.** CI cannot run `make check`: its floor section runs the
    standard-library tools under the 3.11 floor *before* `uv` exists, which is
    what proves they need no virtualenv, and `make check` begins by creating
    one. The local gate is also legitimately stricter in places - `ruff check
    --no-cache`, which CI needs no equivalent of - and the merge gate
    legitimately asks one question a checkout cannot. So what is enforced here
    is that every difference is *recorded*, in `GATE_ONLY` above, with the
    reason it exists. A session adding a check meets the question at the moment
    it would otherwise be decided by not thinking about it.

    **Scripts and their modes, not command strings.** How a script is invoked
    differs by construction - `python3 tools/x.py` at the floor, `uv run
    python tools/x.py` after the sync - so comparing command strings would
    report every line as a drift, and nothing ahead of the script is compared.
    What follows it is, reduced to the mode `_mode` reads, because a script run
    with `--anchors` in one gate and `--check` in the other is two checks with
    one of them unenforced: matched by path alone, `tools/pr_body_check.py
    --anchors` ran only in `make check` from `PL-73G8` until `PL-3PH2`, counted
    as covered by CI's `--check` (`PL-RW3T`). The match is exact rather than
    "covered by a run with more options", since an option can switch what a
    script checks rather than add to it and telling which would mean reading
    each script's parser; an exact match reports the difference and asks for
    its reason instead.

    **Only workflows that run on every pull request onto the default branch
    count as the merge gate.** A branch can merge without a scheduled workflow
    ever having looked, so counting `drift.yml` would report a script as
    covered that gates nothing; nor does a workflow whose branch filter leaves
    the default branch out. `_gates_pull_requests` asks that of the one reader
    of a workflow's triggers. `pr-title.yml` does count, which is what makes
    `tools/pr_title_check.py` the worked example rather than a fourth finding:
    it is `make check`-only within `quality.yml` and has a workflow of its own.

    **A command counts only where every pull request runs it** (`PL-ZQ3R`).
    `pull_request_runs` reads the `if:` of each step and of the job holding
    it. A step that a condition keeps off pull requests runs nothing here, and
    a condition it cannot evaluate is declined where the step runs a gate
    script. On the other side, `_target_recipes` declines a recipe line inside
    a Makefile conditional, since make runs it only in that branch. Until then,
    a script that CI ran only on a push to `main`, or that `make check` ran in
    one configuration, counted as run by that gate on every pull request.

    Silent where either file is missing, so a partial checkout is not failed
    for what it does not carry; declined where `_make_lines` declines the
    Makefile, since what `make check` runs is then not known; and reporting no
    difference once anything on either side is declined - a workflow, a step,
    a line of a script or of the `check:` recipe - since the unread part may
    run what the other side does (`PL-5M36`).
    """
    makefile = root / "Makefile"
    workflows = sorted(
        path for pattern in WORKFLOW_GLOBS for path in root.glob(pattern) if path.is_file()
    )
    if not makefile.is_file() or not workflows:
        return
    try:
        recipes, prerequisites = _target_recipes(makefile.read_text(encoding="utf-8"))
    except UnreadStatement as statement:
        report.declined.append(
            f"Makefile:{statement.line}: {statement.why}, so the scripts `make check` runs "
            "were not compared"
        )
        return
    if "check" not in recipes:
        return
    unread = "the scripts it runs were not compared"
    declined_before = len(report.declined)
    local = {
        invocation
        for command in _target_commands(recipes, prerequisites, "check")
        for invocation in _gate_invocations(
            root, _shell_commands("Makefile", command, report, unread)
        )
    }
    merge: set[tuple[str, ...]] = set()
    default = default_branch(root)
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        where = path.relative_to(root)
        try:
            gates = _gates_pull_requests(text, default if resolved(default) else None)
        except UnreadStatement as trigger:
            report.declined.append(f"{where}:{trigger.line}: {trigger.why}, so {unread}")
            continue
        if not gates:
            continue
        runs, declined = pull_request_runs(text)
        for words, doubt in runs:
            invocations = set(_gate_invocations(root, [words]))
            if doubt is None:
                merge |= invocations
            elif invocations:
                declined.append(doubt)
        _decline_steps(report, where, declined, unread)
    # A workflow, a step or a line of the `check:` recipe left unread may hold
    # a script that side runs, so a difference would not be a fact; the
    # declines above say what went unread. Counting the declined steps alone
    # passed over a recipe line `_shell_reading` declined (`PL-5M36`).
    if len(report.declined) > declined_before or not local or not merge:
        return
    for invocation in sorted(local - merge):
        spelled = " ".join(invocation)
        if GATE_ONLY.get(spelled, ("", ""))[0] == "local":
            continue
        report.errors.append(
            f"`make check` runs {spelled} and no workflow triggered by a pull request "
            "does, so a branch pushed without a local `make check` merges green on a "
            f"tree `make check` would refuse.{_other_modes(invocation, merge, 'They run')} "
            "Add a step for it to `.github/workflows/quality.yml` - the floor section "
            f"where it needs no virtualenv, under `uv run` where it does - or record `{spelled}` "
            "in `tools/doc_check.py`'s `GATE_ONLY` with the reason the merge gate "
            "cannot ask it"
        )
    for invocation in sorted(merge - local):
        spelled = " ".join(invocation)
        if GATE_ONLY.get(spelled, ("", ""))[0] == "ci":
            continue
        report.errors.append(
            f"a pull-request workflow runs {spelled} and `make check` does not, so the "
            "first place a session can learn the answer is a red CI run after review "
            f"has started.{_other_modes(invocation, local, '`make check` runs')} Add it to "
            f"the `check:` target, or record `{spelled}` in `tools/doc_check.py`'s "
            "`GATE_ONLY` with the reason a checkout cannot ask it"
        )


def _other_modes(invocation: tuple[str, ...], gate: set[tuple[str, ...]], who: str) -> str:
    """The sentence naming the modes the other gate runs this script in, where it runs any.

    It is the case a match by path passed (`PL-RW3T`), and a reader shown only
    that the mode is missing would go looking for the script and find it there.
    """
    others = sorted(" ".join(other) for other in gate if other[0] == invocation[0])
    if not others:
        return ""
    return (
        f" {who} {invocation[0]} only as {', '.join(others)}, which does not cover "
        "it: a subcommand or an option can change what a script checks."
    )


def check_math_delimiters(root: Path, report: Report) -> None:
    """Hold every markdown file to the math syntax GitHub actually renders.

    Two failures, both silent: the wrong delimiters render as literal text, and
    a correct expression split across a source line break renders as literal
    text on both sides. Neither raises anything anywhere - the page simply
    shows `(F_D)` where it should show a symbol, which is a traceability
    failure in a document whose symbol table is how a reader maps a displayed
    clinical value back to the equation that produced it.

    Every markdown file is read, not only `DOC_GLOBS`: this is a question about
    rendering rather than about claims held to the tree, and a queue item
    renders on GitHub like anything else.
    """
    for path in _walk(root):
        if path.suffix != ".md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UNREADABLE:
            continue
        relative = path.relative_to(root)
        # GitHub does not render frontmatter as prose - it hides it or shows
        # it as a table - so there is no math there to render wrongly. Scanning
        # it read a `verify:` command whose regex escapes a parenthesis as
        # LaTeX and failed the run, whose only available repair was to contort
        # a working shell command (`PL-WTQ1`, hit on `PL-6194`). The body of
        # the same document is still scanned: the skip is the frontmatter's
        # line span and nothing else.
        skip_to = _frontmatter_end(text)
        for number, line in enumerate(_without_code(text), 1):
            if number <= skip_to:
                continue
            for match in TEX_DELIMITER_RE.finditer(line):
                report.errors.append(
                    f"{relative}:{number} writes math as `{match.group(0)}`, which GitHub "
                    "does not render; use `$`...`$` inline or a `$$` fence for a block"
                )
            for match in MATH_EDGE_RE.finditer(line):
                report.errors.append(
                    f"{relative}:{number} leaves `{match.group(0)}` unpaired, so an inline "
                    "expression renders as literal text: one split across a line break, left "
                    "open, or with a backtick a code span opened before it has claimed"
                )


#: What may close a line after its last word: emphasis, a code span, a
#: bracket or a quotation mark. `_ends_a_sentence` looks past these to the
#: punctuation they follow.
CLOSING_MARKS = "*_`)]\"'”’"

#: The marks after which a line ends a sentence or introduces what follows.
SENTENCE_ENDS = ".:!?"


def check_wrapped_list_items(root: Path, report: Report) -> None:
    """Refuse a list item that a line wrap opened in the middle of a sentence.

    CommonMark lets a `-`, `+` or `*` item, or one numbered `1.`, start on the
    line straight after a paragraph's last line (0.31.2 § 5.3). A wrap that
    puts a spaced dash or plus sign at the start of a line therefore renders
    the rest of the sentence as a list item. Nothing shows it in the raw text,
    which is what a session reads, so it is found only on the rendered page
    (`PL-LNNL`). `PL-DSMK`, `PL-N7LK` and `PL-T4FK` fixed nine of them by hand.

    A list may interrupt a paragraph on purpose, and 21 lists in this tree did
    so when the rule was written, beside the YAML lists in the front matter of
    `.claude/rules/`. Each of the 21 either follows a line that
    ends a sentence or introduces the list, such as `How it was verified:`, or
    follows a one-line label such as `**Verification**` with an item that
    opens with a capital letter or code. So an item is refused only when the
    line above it ends with no `.`, `:`, `!` or `?`, and either the paragraph
    above runs over more than one line or the item opens with a lower-case
    letter. Both are what a wrap leaves behind: a sentence cut where it goes
    on, and a clause that carries it on.

    Every Markdown file is read, and in the item store only the open briefs.
    A closed brief is a record of the tree its work was done against, not a
    live statement, so `.claude/rules/citation-drift.md` decides its prose is
    not a finding. 76 closed briefs held such wraps when the store was added,
    and rewrapping them would change records for no reader. An open brief is
    where a session writes new prose, so a wrap there fails where it is
    written (`PL-XLYK`). `_live_item_briefs` decides which briefs are open,
    from the store's own reading of each status. A file's front matter is YAML
    rather than Markdown, so its lines are skipped, as `check_math_delimiters`
    skips them.
    """
    for path in _walk(root):
        relative = path.relative_to(root)
        if path.suffix != ".md" or relative.parts[:2] == ("docs", "items"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UNREADABLE:
            continue
        _check_wrapped_list_items_in(relative, text, report)
    for relative, text in _live_item_briefs(root):
        _check_wrapped_list_items_in(relative, text, report)


def _check_wrapped_list_items_in(relative: Path, text: str, report: Report) -> None:
    """Report each list item in one Markdown file that a wrap opened mid-sentence."""
    lines = split_lines(text)
    document = read_blocks(lines)
    skip_to = _frontmatter_end(text)
    ends = {block.end: block for block in document.blocks if block.kind == PARAGRAPH}
    for item in document.items:
        paragraph = ends.get(item.start)
        if item.start < skip_to or paragraph is None or paragraph.depth != item.depth:
            continue
        opens = _from_column(lines[item.start], document.columns[item.start])
        if _ends_a_sentence(lines[item.start - 1]):
            continue
        if paragraph.end - paragraph.start > 1 or opens[:1].islower():
            report.errors.append(
                f"{relative}:{item.start + 1} starts a line with a list marker in the middle "
                "of the sentence above it, so the rest of that sentence renders as a list "
                "item; move the marker to the end of the line above, or put a blank line "
                "before a list meant as one"
            )


def _ends_a_sentence(line: str) -> bool:
    """Whether `line` ends with a mark that ends a sentence or introduces a list."""
    last = line.rstrip().rstrip(CLOSING_MARKS)
    return bool(last) and last[-1] in SENTENCE_ENDS


def _frontmatter_end(text: str) -> int:
    """The 1-based line number the frontmatter's closing `---` sits on, or 0.

    Beside `_frontmatter` rather than derived from it by the caller, because
    what a caller skipping the block needs is the span, and recomputing that
    from the block's contents is the arithmetic that goes wrong by one.
    """
    block = _frontmatter(text)
    return 0 if block is None else len(block) + 2


def _frontmatter(text: str) -> list[str] | None:
    """The YAML frontmatter block's lines, or `None` if the file has none.

    It closes where `docket.frontmatter.closing` says: on a `---` that opens its
    line, never an indented one, which is a line of the value above it, such as
    a literal block's (`PL-R417`); read as the close, it cut the block short.
    """
    lines = split_lines(text)
    end = frontmatter_closing(lines)
    return None if end is None else lines[1:end]


def is_path_scoped(text: str) -> bool:
    """Does this rules file defer itself to the sessions that match its paths?

    A rule carrying `paths:` frontmatter loads when a session reads a matching
    file; one without it loads at launch with the same priority as
    `.claude/CLAUDE.md`. That distinction is the whole content of the resident
    total, so it is read here exactly as Claude Code documents it.

    A key is one `docket.frontmatter.keys` reads, so a line opening `paths:`
    inside another key's quoted value is none, where matched a line at a time it
    took a resident rule out of the total (`PL-BM8T`). A block that reader
    cannot split counts as declaring no scope, the direction that overstates
    the resident total rather than hiding a rule from it, and
    `tools/rules_paths_check.py` refuses the same block by name in the same
    `make check`.
    """
    block = _frontmatter(text)
    if block is None:
        return False
    try:
        return any(key.name == "paths" for key in frontmatter_keys(block))
    except UnreadFrontMatter:
        return False


def _skill_description(name: str, text: str) -> ResidentFile | None:
    """A skill's frontmatter block, which is resident even though its body is not.

    Claude Code lists every available skill by name and description before a
    session has invoked any of them, so that block is loaded at launch and
    resent on every turn exactly as `CLAUDE.md` is. The rest of the file loads
    only when the skill fires, and `measure_on_demand` is what counts that.
    `PL-JQVB` established that a skill's resident cost was invisible here;
    this is the half of it that a size gauge can see.

    Measured rather than the whole file: the `docket` skill's frontmatter is
    625 characters against 5,097 for the file, so counting the file would
    overstate what a session loads at launch by eight times and counting
    nothing understates it by all of it.

    The two counts overlap by these characters, deliberately. Invoking a skill
    loads the whole file, frontmatter included, so `measure_on_demand` is
    right to count it; and the description reaches a session that never
    invokes it, so this is right to count it too. They answer different
    questions and are printed on different lines, which is the split `PL-JQVB`
    asked for rather than a double count.
    """
    if not name.endswith("/SKILL.md"):
        return None
    block = _frontmatter(text)
    if block is None:
        return None
    described = "\n".join(block)
    return ResidentFile(f"{name} (description)", len(described), len(block), instruction_file=False)


def _measure(name: str, text: str) -> ResidentFile | None:
    """One resident file measured, or `None` when it defers itself to a path.

    Three kinds, and the second and third are what `PL-44DG` added. A rules
    file carrying `paths:` is not resident and drops out. A file under
    `SKILLS_DIR` contributes its frontmatter and nothing else. Everything else
    - `CLAUDE.md` and the unscoped rules - is resident in full.

    One function rather than two, because `_baseline` runs it over the default
    branch's copies of the same files: a second reader for the working tree
    would be free to drift from this one, and then a stored baseline and a
    fresh measurement would be measuring different things while reporting one
    number.
    """
    if name.startswith(f"{SKILLS_DIR}/"):
        return _skill_description(name, text)
    if name.startswith(f"{RULES_DIR}/") and is_path_scoped(text):
        return None
    return ResidentFile(name, len(text), len(split_lines(text)))


def _measure_on_demand(name: str, text: str) -> ResidentFile | None:
    """One instruction file a session loads only once something makes it load.

    The mirror of `_measure`, and the `paths:` test runs the other way round
    for exactly that reason: a rule that defers itself to a path is not
    resident, which is why `_measure` drops it - and it is the clearest case of
    text a session may be made to load, which is why this keeps it. A rule with
    no `paths:` is already counted as resident and must not be counted twice.
    """
    if name.startswith(f"{RULES_DIR}/") and not is_path_scoped(text):
        return None
    return ResidentFile(name, len(text), len(split_lines(text)))


def measure_resident(root: Path) -> list[ResidentFile]:
    """Which instruction files load at launch in this working tree, and how big.

    The rules are `rules_paths_check.rule_files`, at any depth, and the skills
    the tracked files under `SKILLS_DIR`: a file not yet added to git is
    measured once it is, which is the trade every reader of `tracked_files`
    makes (`PL-9NZ3`).

    `SKILLS_DIR` is walked beside the rules, and contributes each skill's
    frontmatter rather than its file - see `_skill_description`. The dynamic
    half of the payload is not here but in `measure_digest`, because it is
    produced by running something rather than by reading a file, and nothing
    that reads a git ref can reproduce it.
    """
    measured: list[ResidentFile] = []
    names = [name for name in RESIDENT_ROOTS if (root / name).is_file()]
    for found in (rule_files(root), tracked_under(root, SKILLS_DIR, ".md")):
        names += [path.relative_to(root).as_posix() for path in found]
    for name in names:
        row = _measure(name, (root / name).read_text(encoding="utf-8"))
        if row is not None:
            measured.append(row)
    return measured


def session_environment(environ: Mapping[str, str]) -> dict[str, str]:
    """The environment a session runs the SessionStart hook in, rebuilt from the caller's.

    `make check` and CI run this tool under `uv run`, which sets `VIRTUAL_ENV`
    and puts the virtualenv's `bin` first on `PATH`. Passed on as it was, the
    hook's bare `python3` became the virtualenv's interpreter, while a session
    runs the hook with the system's. On 2026-09-24 the two printed digests 276
    characters apart, from one line the virtualenv's interpreter printed and
    the system's did not (`PL-HDMP`). So `VIRTUAL_ENV` is dropped, and so is
    each `PATH` entry inside it.
    """
    virtualenv = environ.get("VIRTUAL_ENV", "")
    kept = {name: value for name, value in environ.items() if name != "VIRTUAL_ENV"}
    if virtualenv and "PATH" in environ:
        inside = Path(virtualenv).resolve()
        kept["PATH"] = os.pathsep.join(
            entry
            for entry in environ["PATH"].split(os.pathsep)
            if not entry or not Path(entry).resolve().is_relative_to(inside)
        )
    return kept


def measure_digest(root: Path) -> ResidentFile | None:
    """What the SessionStart hook emits into every session, by running it.

    The hook's output is instruction text by every property that matters here:
    it is placed in the context before the conversation starts and resent on
    every turn, exactly as `CLAUDE.md` is. Nothing counted it, and it is the
    half of the resident payload that **grows on its own** - it carries the
    dead-ends list and scales with the store, so it is the one component that
    can rise without any edit to an instruction file. That makes it precisely
    the part a size gauge most needs to see. Measured 2026-09-21, it was 4,169
    characters against a reported resident total of 66,773, so the gauge the
    project consults about resident size was 7.2% low (`PL-44DG`).

    **Run rather than read, and the alternative was drift.** The hook is six
    commands, two of them producing a line only in an exception case, and its
    output is not derivable from its source. Listing the ones worth counting
    here would put the hook's line list in a second place, which is how
    `workflow_paths` went nine entries short and how `gate_paths` acquired two
    hand-maintained entries - silent both times, and silent in the direction
    that hurts. Running the file itself cannot drift from the file itself.

    **What it costs, counted rather than guessed.** About 4.2 s on a `make
    check` measured at 2 m 24 s, so roughly 3%, and no hook runs `doc_check`
    on an edit - `make check`, `make doc-check` and CI are the only callers.
    Two of the hook's lines reach the network: `docket branch --brief`
    fetches, and `main_ci_status.py` reads a check verdict. That is a real
    change to what `make check` does and is the reason this is worth a
    paragraph rather than a line. It does not reach the growth advisory: the
    row this returns is carried in `ResidentInstructions.runtime`, which is
    left out of every comparison, so a measurement that varies with the store
    or with an offline container moves the printed total and no verdict.

    **It declines rather than guesses.** No hook, no `bash`, a non-zero exit
    or a timeout all return `None`, and the caller turns that into a
    `Report.declined` line - a total short by 4,000 characters with nothing
    saying so is the partial reading handed over as a complete one that
    `.claude/rules/apparatus-standard.md` makes the floor.
    """
    hook = root / DIGEST_HOOK
    if not hook.is_file():
        return None
    try:
        result = subprocess.run(
            ("bash", str(hook)),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=DIGEST_TIMEOUT,
            check=False,
            env={**session_environment(os.environ), "CLAUDE_PROJECT_DIR": str(root)},
        )
    except GIT_UNAVAILABLE:
        return None
    if result.returncode:
        return None
    return ResidentFile(
        f"{DIGEST_HOOK} (output)", len(result.stdout), len(split_lines(result.stdout))
    )


def measure_on_demand(root: Path) -> list[ResidentFile]:
    """Which instruction files this tree can make a session load, and how big.

    Measured because the growth instrument could not see them, and four fifths
    of this project's instruction growth went where it could not look: between
    `v0.4.0` and `v0.4.22`, `CLAUDE.md` grew 3,135 characters and
    `.claude/skills/docket/SKILL.md` grew 15,416, of which the resident
    advisory reported the first number and none of the second (`PL-JQVB`).
    Routing a rule into a skill is the *right* answer under `CLAUDE.md`'s four
    dispositions, so nothing here scolds it - but a routing pass that reads as
    a pure reduction when it is a relocation cannot be checked, and this is
    what makes both halves of the move visible in one place.
    """
    measured: list[ResidentFile] = []
    for name in _markdown_under(root, ON_DEMAND_ROOTS):
        row = _measure_on_demand(name, (root / name).read_text(encoding="utf-8"))
        if row is not None:
            measured.append(row)
    return measured


def _git_text(root: Path, *args: str) -> str | None:
    """Git's stdout verbatim, or `None` when it could not answer.

    `_git` drops blank lines, which is right for listing refs and wrong for
    counting the lines of a file, so the two readers are kept apart. Read by
    `vcs.call_git`, as docket reads the same question (`PL-S9JK`): a blob comes
    back translated as `read_text` translates its file, and one the revision
    does not hold as `""` rather than `None`, which is the file's absence and
    measures as no file.
    """
    text = call_git(args, root).answer
    return text if answered(text) else None


def _resident_baseline(root: Path) -> tuple[str, tuple[ResidentFile, ...]] | None:
    """The same measurement at the tip of the default branch.

    The tip rather than the merge base, because the question this answers is
    "does merging this make every session's resident context larger than it is
    on the default branch" - which a merge base cannot see, since it reports
    nothing when the growth arrived on the branch being merged into.

    Both sides are measured here by the same measure function, from file
    contents read out of git rather than from any number written down, so
    changing what is measured cannot make a stored baseline incomparable with a
    fresh one. That is also why the measure travels as an argument: the
    on-demand set needs the same comparison against the same ref, and a second
    copy of this walk would be free to drift from this one.
    """
    return _baseline(root, (*RESIDENT_ROOTS, RULES_DIR, SKILLS_DIR), _measure)


def _baseline(
    root: Path, roots: Sequence[str], measure: Callable[[str, str], ResidentFile | None]
) -> tuple[str, tuple[ResidentFile, ...]] | None:
    """One measured set as it stands at the tip of the default branch.

    The branch is `vcs.default_base`'s, and only where it is established: where
    the read of `origin/main` went unanswered and a local `main` resolved, the
    loop over the candidates this held before `PL-S9JK` measured against the
    local copy unmarked, where every docket command marks that answer a guess.
    """
    ref = default_base(root)
    if not resolved(ref):
        return None
    listing = _git_text(root, "ls-tree", "-r", "-z", "--name-only", ref, "--", *roots)
    if listing is None:
        return None
    measured: list[ResidentFile] = []
    for name in sorted(listed_paths(listing)):
        if not name.endswith(".md"):
            continue
        text = _git_text(root, "show", f"{ref}:{name}")
        if text is None:
            continue
        row = measure(name, text)
        if row is not None:
            measured.append(row)
    return str(ref), tuple(measured)


def check_resident_instructions(root: Path, report: Report) -> None:
    """Report what every session loads before it has read anything.

    Claude Code's memory documentation ties instruction-file size to adherence
    rather than to token cost: a long resident file makes every rule in it
    slightly less likely to be followed, the safety-critical standard among
    them. Nothing in this project's history ever shortened one - the rule that
    a behavior change takes effect in the session that asks for it guarantees
    growth, and PL-034's one-time trim regrew within a release.

    So the total is printed on every run and growth is named, which puts
    `PL-H7XN`'s routing question in front of whoever added the rule: at what
    moment does a session need this, and what is the cheapest thing that
    delivers it then - a check, the skill, a path-scoped rule, or resident.

    Reported, never thresholded, and this is the deliberate half. A limit would
    be met by deleting a rule to reach a number, which is the one outcome the
    routing pass must not produce; and no number this tool could hold would
    know which rules a session must see before it reads anything. Growth is a
    fact about the files; whether it is justified is not, so the judgment is
    left where `stranded` leaves its own.

    Both advisories read characters, and both stay quiet below
    `MATERIAL_RESIDENT_DELTA` - the growth one on the net total it is a claim
    about, the trim one on each file it names. Only the advisories: the total
    and the exact delta print either way, so a small change is still visible
    and only the demand for a justification is withheld. A check that fires on
    a term swap costs attention on every later run and teaches a session to
    skim the line a real finding will appear on, which is the failure
    `CLAUDE.md` names when it says a check earns its place every run.

    A net total cannot see the outcome a limit would have caused, though, which
    is why the second advisory exists. A change that adds resident text and
    trims other resident text to pay for it sums to nothing here, so the trim
    never appears as growth and the diff reads as free. That is the forbidden
    outcome arriving without a limit to blame, and it is decidable without
    judgment: growth and shrinkage in the same change, whatever they sum to.
    A routing pass that only moves text out still shrinks alone, and is still
    silent. `PL-BKQW` carries the reasoning; `PL-K6QR` records the project
    owner asking for text to be added without other text suffering for it.
    """
    files = measure_resident(root)
    if not files:
        return
    baseline = _resident_baseline(root)
    digest = measure_digest(root)
    if digest is None and (root / DIGEST_HOOK).is_file():
        report.declined.append(
            f"what {DIGEST_HOOK} adds to every session: it would not run here, so the "
            "resident total below counts the instruction files alone and is short by "
            "whatever the digest emits"
        )
    report.resident = ResidentInstructions(
        files=tuple(files),
        baseline_ref=None if baseline is None else baseline[0],
        baseline_files=None if baseline is None else baseline[1],
        runtime=() if digest is None else (digest,),
    )
    deltas = report.resident.deltas()
    if not deltas:
        return
    rendered = ", ".join(f"{name} {count:+d}" for name, count in deltas)
    material = report.resident.material_deltas()
    ref = report.resident.baseline_ref
    growth = report.resident.growth
    if growth is not None and growth >= MATERIAL_RESIDENT_DELTA:
        report.advisories.append(
            f"resident instructions grew {_plural(growth, 'character', 'characters')} "
            f"against {ref} ({rendered}); every "
            "session loads this before it has read anything. Two answers, and there is no "
            "third: route it to the cheapest thing that delivers it when it is needed - a "
            "check, the `docket` skill, a path-scoped rule - or keep it and say why a "
            "session could violate it before it would look anything up. Text the project "
            "owner asked for is the second answer, already given. Never trim other "
            f"resident text to offset the number. {RESIDENT_LEDGER} records what each "
            "resident block was tested against and the reductions already refused, so read "
            "it before deciding. `PL-H7XN` carries the test."
        )
    if any(count > 0 for _, count in material) and any(count < 0 for _, count in material):
        moved = ", ".join(f"{name} {count:+d}" for name, count in material)
        report.advisories.append(
            f"resident instructions both grew and shrank against {ref} ({moved} characters); the "
            "two net out in the total, so text cut to pay for an addition never shows up "
            "as growth at all. Check that the removed lines were routed somewhere a "
            "session still reads them, rather than cut to make room - making room is not "
            "one of the two answers to the growth advisory. A routing is recorded in "
            f'{RESIDENT_LEDGER} § "What was routed out". `PL-BKQW` carries the test.'
        )


def check_on_demand_instructions(root: Path, report: Report) -> None:
    """Report the instruction text a session can be made to load, and nothing else.

    Printed, never advised on, and the silence is the design. `CLAUDE.md`'s
    four dispositions make routing a rule into a skill or onto a path the
    *preferred* answer to the resident growth advisory, so a signal that fired
    when one happened would fire on the project doing the right thing - which
    is the check `CLAUDE.md` says is a defect in the check. What was missing
    was never a verdict but a number: the growth advisory reads one set, a
    routing pass moves text into the other, and the move showed up as a
    reduction with nothing on the far side of it.

    The two totals are printed together for that reason, and are never summed.
    A session comparing a branch against the base can see both move, which is
    all this needs to do; whether the new home is the right one at the moment
    the rule is needed stays the routing judgment `CLAUDE.md` asks for.
    """
    files = measure_on_demand(root)
    if not files:
        return
    baseline = _baseline(root, ON_DEMAND_ROOTS, _measure_on_demand)
    report.on_demand = ResidentInstructions(
        files=tuple(files),
        baseline_ref=None if baseline is None else baseline[0],
        baseline_files=None if baseline is None else baseline[1],
    )


def _check_reference_files_exist(root: Path, report: Report) -> None:
    """Refuse a source document the reference index names but does not hold.

    `docs/references/README.md` is the provenance record for the model's own
    sources: a reader follows it to see the text a coefficient or a compartment
    structure came from. An entry naming a file the directory does not contain
    sends them looking for something that is not there, and leaves them unable
    to tell a deliberate removal from an accidental one - which is the exact
    question a provenance record exists to answer.

    It became reachable on 2026-09-06, when the two publisher-copyright texts
    were removed from the history and their entries went on naming them.
    Nothing in `make check` noticed. Whether an entry should keep its file or
    keep only its citation stays a person's judgment; whether a named file is
    present is decidable, so only that half is checked here.

    An entry that names no file is correct and passes - that is the shape a
    citation-only entry takes.

    A name is a code span's whole content, read from the spans `_code_spans`
    gives a statement at a time: a span carried across a line ending is one
    span, and a filename its backticks leave as prose is no file (`PL-P6D5`).
    """
    path = root / REFERENCES
    try:
        text = path.read_text(encoding="utf-8")
    except UNREADABLE:
        return
    for span in _code_spans(text):
        name = span["content"]
        if REFERENCE_FILE_RE.fullmatch(name) is None or (path.parent / name).exists():
            continue
        report.errors.append(
            f"{REFERENCES}:{_line_of(text, span.start())} names {name}, which is not "
            f"in {REFERENCES.parent}/; drop the filename and keep the citation if the "
            "text was deliberately removed, since citing a work is not "
            "redistributing it"
        )


#: A host as prose names one: dotted labels ending in a top-level domain, bare
#: or after a URL's `//`. Bounded on both sides, so a dotted name inside a longer
#: one, an address's domain and a path's last segment are not read as a host.
#: The domains are a list rather than any label, because a dotted identifier is
#: far commoner in this tree than a host; every host it called blocked on
#: 2026-10-06 ends in one of them.
HOST_RE = re.compile(
    r"(?:(?<=//)|(?<![\w.@/-]))"
    r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+"
    r"(?:org|com|net|gov|edu|io|dev|ai|sh|blog)(?:\.[a-z]{2})?"
    r"(?![\w-])"
)
#: A word saying a host did not answer. `EGRESS_BLOCKED`, the proxy's own word,
#: is spelt out because `\b` does not split a word at its `_`. `block` and
#: `blocks` are `HOST_BLOCK_RE`'s.
HOST_REFUSAL_RE = re.compile(
    rf"\b(?:block(?:ed|ing)|refus(?:e|es|ed|al|als|ing)|den(?:y|ies|ied|ial)|unreachable"
    rf"|EGRESS_BLOCKED|(?:cannot|can't|could{GAP}+not|couldn't){GAP}+(?:be{GAP}+)?reach(?:ed)?)\b",
    re.IGNORECASE,
)
#: `block` and `blocks`, which say a host was refused - an egress block, a
#: policy that blocks it - and as often name a block of text: a code block, a
#: fenced block, a YAML block. Across the tree on 2026-10-12, dated records
#: included, four sentences named a host beside one of them and no other word
#: of refusal, two of them claims and two blocks of text. So a sentence whose
#: only refusal is one of them is an advisory rather than refused (`PL-79DP`).
HOST_BLOCK_RE = re.compile(r"\bblocks?\b", re.IGNORECASE)
#: Every stem `HOST_REFUSAL_RE` and `HOST_BLOCK_RE` read, so a source holding
#: none of them, nor a host, is passed over unparsed: it cannot carry a claim in
#: any comment or docstring however they are joined.
HOST_REFUSAL_STEM_RE = re.compile(r"block|refus|den(?:y|i)|reach", re.IGNORECASE)


#: Where a sentence records the day it was written rather than claiming the
#: present: an item's brief, which `bin/docket show` prints under its `added:`
#: date; a release's notes, under its version; and a recovered pull request's
#: body, under its merge. Holding them to this rule would refuse records nobody
#: rewrites, which is why a closed brief keeps its stale line citations
#: (`PL-G424`).
#: Each spelled by its owner: the store where `docket.toml` puts it,
#: `release.NOTES_DIR` and `vcs.RECORDS` (`PL-WCHF`).
def dated_records(root: Path) -> tuple[str, ...]:
    """The directories `root` keeps dated records in, as path prefixes."""
    return (load_docket_config(root).items_dir.strip("/") + "/", f"{NOTES_DIR}/", RECORDS)


#: The YAML files whose comments the host-claim check reads, by suffix, the
#: citation file among them, each through `docket.frontmatter.comments`, and a
#: workflow's `run:` scripts through `docket.shell.comments`, as a shell
#: script's are (`PL-W9VC`). TOML and a Makefile write a comment the same way
#: and are not read, since no committed version of either has held a host claim
#: in one - this check's reading, run over the 312 versions of the TOML, make
#: and YAML files on 2026-10-17 - and reading their comments right would take a
#: comment-preserving reader of each, which `tomllib` is not (`PL-PBNK`). YAML
#: is kept on the same count: a workflow's comment held one until `#1387`
#: (`PL-B3MK`).
YAML_SUFFIXES = frozenset({".yml", ".yaml", ".cff"})
#: A comment's marker - `#`, the `#:` that documents an attribute - and the one
#: space after it, so what is left reads as the prose it is.
COMMENT_MARK_RE = re.compile(r"^#+:?[ \t]?")
#: A JSON string on its line, an escape taken whole; JSON allows no line ending
#: inside one.
JSON_STRING_RE = re.compile(r'"(?:[^"\\\n]|\\.)*"')


def _without_destinations(text: str) -> str:
    """`text` with each inline link's destination blanked, its length kept.

    Where a citation points is not what its sentence says, so a sentence
    linking to a page on a host it calls refused names no host by the link.
    The links are `_links`', so one written inside a code span is the span's
    text, and keeps its destination.
    """
    pieces: list[str] = []
    last = 0
    for link in sorted(_links(text), key=lambda link: link.at):
        start, end = link.at
        pieces += (text[last:start], re.sub(r"[^\n]", " ", text[start:end]))
        last = end
    return "".join(pieces) + text[last:]


def _undated_host_claims(
    text: str, files_named: frozenset[str]
) -> Iterator[tuple[int, tuple[str, ...], str | None]]:
    """Each sentence of `text` that names a host beside a refusal and carries no date.

    As the index of the line its first host stands on, the hosts it names, and
    the `block` or `blocks` that is its only word of refusal, which may name a
    block of text instead (`HOST_BLOCK_RE`), or `None` where another word makes
    it a claim. `text` is read as Markdown, which is what a document is and
    what this tree writes a docstring and a comment in: a fence is a literal
    and is passed over, and a sentence goes on across a soft break. A YAML
    front matter is read a key at a time (`_statements`), so a date in the next
    key dates no claim, and no line of it opens a fence that hides the body's
    (`PL-WX79`). A name that a file in the tree carries is that file, so a
    hook's `.sh` is never a host.
    """
    lines = split_lines(text)
    unlinked = split_lines(_unmarked(_without_destinations(text), _body_lines(lines)))
    for first, end in _statements(lines, PROSE):
        statement = "\n".join(unlinked[first:end])
        for start, stop in _sentences(statement):
            sentence = statement[start:stop]
            hosts = [
                host for host in HOST_RE.finditer(sentence) if host.group(0) not in files_named
            ]
            if not hosts or ISO_DATE_RE.search(sentence):
                continue
            if HOST_REFUSAL_RE.search(sentence):
                block = None
            elif found := HOST_BLOCK_RE.search(sentence):
                block = found.group(0)
            else:
                continue
            line = first + statement.count("\n", 0, start + hosts[0].start())
            yield line, tuple(dict.fromkeys(host.group(0) for host in hosts)), block


def _dedented(docstring: str) -> str:
    """A docstring as written, its body's indentation removed and its lines kept.

    Read with `clean=False`, so a claim is reported on the row it stands on;
    left indented, every line of a method's docstring would read as an indented
    code block, which is no prose at all.
    """
    head, newline, body = docstring.partition("\n")
    return head.lstrip() + newline + textwrap.dedent(body)


def _comment_runs(found: Iterable[tuple[int, str, bool]]) -> Iterator[tuple[int, str]]:
    """Each run of the comments in `found`, as the row it opens on and its text.

    `found` holds each comment in order, as its row, its text from its `#`, and
    whether it stands alone on its row. Comments standing alone on consecutive
    rows are one text, since that is how this tree wraps a paragraph of
    comment; one after code stands alone. Each loses its marker
    (`COMMENT_MARK_RE`).
    """
    run: list[str] = []
    first = last = 0
    for row, comment, alone in found:
        text = COMMENT_MARK_RE.sub("", comment)
        if run and not (alone and row == last + 1):
            yield first, "\n".join(run)
            run = []
        if not alone:
            yield row, text
        elif run:
            run.append(text)
        else:
            run, first = [text], row
        last = row
    if run:
        yield first, "\n".join(run)


def _python_comments(source: bytes) -> Iterator[tuple[int, str]]:
    """Each run of comment in `source`, as `_comment_runs` reads them.

    Read from bytes, as Python reads source, so a byte-order mark or a coding
    cookie is honoured. Raises one of `UNTOKENIZABLE` where the tokenizer
    refuses `source`, an error token included, as `docket.python` does, so
    every interpreter refuses the same files.
    """

    def found() -> Iterator[tuple[int, str, bool]]:
        for token in tokenize.tokenize(io.BytesIO(source).readline):
            if token.type == tokenize.ERRORTOKEN:
                raise tokenize.TokenError(f"an error token at {token.string!r}", token.start)
            if token.type == tokenize.COMMENT:
                row, column = token.start
                yield row, token.string, not token.line[:column].strip()

    yield from _comment_runs(found())


def _spanned_comments(
    text: str, spans: Iterable[tuple[int, int]]
) -> Iterator[tuple[int, str, bool]]:
    """Each comment at `spans` in `text`, as its line's index, its text and whether it is alone."""
    for start, end in spans:
        opening = text.rfind("\n", 0, start) + 1
        yield text.count("\n", 0, start), text[start:end], not text[opening:start].strip()


def _script_comments(
    relative: Path, text: str, report: Report, rows: Sequence[int]
) -> Iterator[tuple[int, str]]:
    """Each run of comment in the shell script `text`, its rows those of `rows`, as bash reads it.

    Read through `docket.shell.comments`, so a `#`-led line in a here-document's
    body or a quoted string is none (`PL-W9VC`). `rows` holds the row each line
    of `text` stands on in `relative`, by its index. Where the script cannot be
    read to its end, that row is named in `report.declined`, and no comment
    from it on is read.
    """
    spans, stop = shell_comments(text)
    found = [(rows[row], comment, alone) for row, comment, alone in _spanned_comments(text, spans)]
    yield from _comment_runs(found)
    if stop is not None:
        report.declined.append(
            f"{relative}:{rows[text.count(chr(10), 0, stop)]}: this script cannot be read to "
            "its end from this line - a quote, a substitution or a backslash runs past it, "
            "or a `<<` has no delimiter - so no host claim in a comment from it on was checked"
        )


def _yaml_comments(relative: Path, text: str, report: Report) -> Iterator[tuple[int, str]]:
    """Each run of comment in the YAML file `text`, and in its `run:` steps' scripts if a workflow.

    The file's are `docket.frontmatter.comments`', so a `#`-led line in a block
    scalar's content or a quoted scalar is none; a workflow's `run:` script is
    such a block, and its comments are bash's, read as `_script_comments` reads
    a script's (`PL-W9VC`). What could not be read is named in
    `report.declined`: the file, or a step `_step_scripts` declines.
    """
    lines = split_lines(text)
    try:
        placed = yaml_comments(lines)
    except UnreadFrontMatter as error:
        report.declined.append(
            f"{relative}: {error}, so no host claim in a comment of it was checked"
        )
        return
    yield from _comment_runs(
        (index + 1, lines[index][column:], not lines[index][:column].strip())
        for index, column in placed
    )
    if not any(PurePosixPath(relative.as_posix()).match(glob) for glob in WORKFLOW_GLOBS):
        return
    scripts, unread = _step_scripts(text)
    for body, script in scripts:
        yield from _script_comments(relative, body, report, [row for _, row in script])
    report.declined += [
        f"{relative}:{step.line}: {step.why}, so no host claim in its script's comments was checked"
        for step in unread
    ]


def _json_strings(text: str) -> Iterator[tuple[int, str]]:
    """Each string in a JSON file, as its row and what stands between its quotes.

    Not decoded: a host, a refusal and a date are written in ASCII, and an
    escape left as written cannot open a line the file does not have.
    """
    for row, line in enumerate(split_lines(text), 1):
        for match in JSON_STRING_RE.finditer(line):
            yield row, match.group(0)[1:-1]


def _host_claim_texts(
    path: Path, relative: Path, report: Report, dated: tuple[str, ...]
) -> Iterator[tuple[int, str]]:
    """The prose `path` holds, each piece as the row it opens on and its text.

    A Markdown file is one piece, a document; a run of comment, a docstring
    and a JSON string are passages of their file, which open no front matter
    (`_as_passage`). Nothing for a file of another format or a dated record; a
    piece that could not be read is named in `report.declined` rather than
    passed as read.
    """
    posix = relative.as_posix()
    if posix.startswith(dated):
        return
    suffix = path.suffix
    if suffix not in (".md", ".py", ".json", ".sh") and suffix not in YAML_SUFFIXES:
        return
    try:
        data = path.read_bytes()
    except OSError as error:
        report.declined.append(
            f"{relative}: could not be read ({error}), so no host claim in it was checked"
        )
        return
    # A host, a refusal and a date are all written in ASCII, so a byte UTF-8
    # cannot decode is replaced rather than declined: no claim is written in it.
    text = data.decode("utf-8", errors="replace")
    if suffix == ".md":
        yield 1, text
    elif suffix == ".sh":
        rows = range(1, text.count("\n") + 2)
        yield from _as_passages(_script_comments(relative, text, report, rows))
    elif suffix in YAML_SUFFIXES:
        yield from _as_passages(_yaml_comments(relative, text, report))
    elif suffix == ".json":
        yield from _as_passages(_json_strings(text))
    elif HOST_RE.search(text) and HOST_REFUSAL_STEM_RE.search(text):
        # Parsed as bytes, as `_quoting_sources` parses them, so a byte-order
        # mark or a coding cookie is honoured rather than declined.
        try:
            tree = ast.parse(data, filename=posix)
        except (SyntaxError, ValueError) as error:
            report.declined.append(_unread_source(relative, error, "host claim"))
        else:
            for row, docstring in _docstrings(tree):
                yield row, _as_passage(_dedented(docstring))
        try:
            yield from _as_passages(_python_comments(data))
        except UNTOKENIZABLE as error:
            report.declined.append(
                f"{relative}: the tokenizer refused this file ({refusal(error)}), so no "
                "host claim in a comment past that point was checked"
            )


def check_host_claims(root: Path, report: Report) -> None:
    """Refuse a sentence calling a host blocked that does not say when (`PL-CLW5`).

    Whether a host answers through this container's egress proxy is a probe on
    a day. The owner sets the allowed domains in settings no file here reads,
    so a sentence calling a host blocked goes false without a line of the tree
    moving, and a session that trusts it works around a route that answers. A
    dated sentence stays true, since it says what one probe found, and
    `.claude/rules/citing-sources.md` already asks for the date. So a sentence
    naming a host beside a word of refusal - blocked, refused, denied,
    unreachable, or the proxy's `EGRESS_BLOCKED` - carries an ISO date, or is
    refused. One whose only such word is `block` or `blocks`, which as often
    names a code block or a YAML block, is an advisory instead (`PL-79DP`).

    Read wherever the tree writes prose a later session takes for the present:
    every Markdown file but the records `dated_records` names, a Python file's
    docstrings and comments, a shell script's comments and a YAML file's
    (`YAML_SUFFIXES`), a workflow's `run:` scripts' among them, each read as
    its own grammar places them (`PL-W9VC`), and a JSON file's strings, where a
    data file keeps its provenance notes. Whether a sentence is
    about a host at all is judgment, so what counts is narrow and written down:
    a host is what `HOST_RE` reads, and a name some file in the tree carries is
    that file.
    """
    paths = list(_walk(root))
    files_named = frozenset(path.name for path in paths)
    dated = dated_records(root)
    for path in paths:
        relative = path.relative_to(root)
        for row, text in _host_claim_texts(path, relative, report, dated):
            for line, hosts, block in _undated_host_claims(text, files_named):
                named = ", ".join(f"`{host}`" for host in hosts)
                if block is not None:
                    report.advisories.append(
                        f"{relative}:{row + line} names {named} beside `{block}` in a "
                        "sentence that carries no date: if it says the host was blocked, "
                        "write the date it was probed in the same sentence (`PL-CLW5`); if "
                        "it names a block of text, such as a code block, nothing to do "
                        "(`PL-79DP`)"
                    )
                    continue
                report.errors.append(
                    f"{relative}:{row + line} names {named} beside a refusal in a sentence "
                    "that carries no date: whether a host answers through the egress proxy "
                    "is a probe on a day, so write the date it was probed in the same "
                    "sentence (`PL-CLW5`)"
                )


def analyze(root: Path) -> Report:
    """Run every mechanical documentation check over a checkout.

    The checks share one read of the item store for the whole run, which
    `_read_store` explains (`PL-LYH3`).
    """
    run = _RUN_STORES.set({})
    try:
        return _analyze(root)
    finally:
        _RUN_STORES.reset(run)


def _analyze(root: Path) -> Report:
    """`analyze`'s checks, in the order they report."""
    report = Report()
    documents = read_docs(root)
    if not documents:
        report.errors.append("no documentation files found; is this a repository checkout?")
        return report
    check_package_maps(root, report)
    check_provenance(root, report)
    check_source_tiers(root, report)
    check_prose_provenance(root, report)
    check_citations(root, documents, report)
    check_line_citations(root, documents, report)
    check_quoted_sources(root, documents, report)
    check_timeline(root, report)
    check_milestone_lists(root, report)
    check_baseline(root, report)
    check_gate_counts(root, report)
    check_self_cleared_group(root, report)
    check_scope_exclusions(root, report)
    check_scope_declarations(root, report)
    check_named_tests(root, documents, report)
    check_bound_families(root, report)
    check_gate_reentries(root, report)
    check_tags(root, report)
    check_tag_span_covers_its_notes(root, report)
    check_release_row_item_count(root, report)
    check_make_targets(root, documents, report)
    check_workflow_paths(root, report)
    check_floor_list(root, report)
    check_coverage_gate(root, report)
    check_ruff_cache(root, report)
    check_gate_parity(root, report)
    check_math_delimiters(root, report)
    check_wrapped_list_items(root, report)
    check_host_claims(root, report)
    check_resident_instructions(root, report)
    check_on_demand_instructions(root, report)
    _check_reference_files_exist(root, report)
    return report


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def _format_measured(label: str, when: str, measured: ResidentInstructions) -> str:
    """One line: how much instruction text a set holds, and how it moved against the base."""
    breakdown = ", ".join(
        f"{row.name} {row.characters}/{row.lines}" for row in (*measured.files, *measured.runtime)
    )
    growth = measured.growth
    if growth is None:
        against = "no default branch here to compare against"
    elif growth > 0:
        against = f"{growth} more characters than {measured.baseline_ref}"
    elif growth < 0:
        against = f"{-growth} fewer characters than {measured.baseline_ref}"
    else:
        against = f"unchanged against {measured.baseline_ref}"
    return (
        f"{label}: {_plural(measured.total, 'character', 'characters')} over "
        f"{_plural(measured.total_lines, 'line', 'lines')} {when} "
        f"(chars/lines: {breakdown}) - {against}"
    )


def _format_resident(resident: ResidentInstructions) -> str:
    """One line: what every session loads, and how that compares to the base.

    It also names the instruction files' subtotal. `CLAUDE.md`'s
    resident-growth series is on that basis, so a reader compares it with
    that subtotal rather than with the whole payload (`PL-DXF0`).
    """
    measured = _format_measured("resident instructions", "loaded at launch", resident)
    return (
        f"{measured}; the instruction files alone come to "
        f"{_plural(resident.instruction_total, 'character', 'characters')}, the basis "
        "of the resident-growth series in CLAUDE.md"
    )


def _format_on_demand(on_demand: ResidentInstructions) -> str:
    """One line: what this tree can make a session load, printed beside the resident total.

    Deliberately not summed with it. A skill that never fires costs a session
    nothing, and a rule scoped to `src/**` costs a workflow session nothing, so
    a combined figure would overstate every session's load and understate the
    one it happened to describe.
    """
    return _format_measured("instructions loaded on demand", "reachable this way", on_demand)


def format_check(report: Report) -> str:
    summary = (
        "documentation: "
        f"{_plural(len(report.errors), 'error', 'errors')}, "
        f"{_plural(len(report.advisories), 'advisory', 'advisories')}"
    )
    if report.declined:
        summary += f", {len(report.declined)} not checked"
    lines = [summary]
    if report.resident is not None:
        lines.append(_format_resident(report.resident))
    if report.on_demand is not None:
        lines.append(_format_on_demand(report.on_demand))
    if report.errors:
        lines.append("")
        lines.append("Errors (the documentation is wrong; fix before committing):")
        lines.extend(f"  {message}" for message in report.errors)
    if report.advisories:
        lines.append("")
        lines.append("Advisories (judgment needed):")
        lines.extend(f"  {message}" for message in report.advisories)
    if report.declined:
        lines.append("")
        lines.append("Not checked (this checkout cannot answer; nothing is claimed):")
        lines.extend(f"  {message}" for message in report.declined)
    if not report.errors and not report.advisories and not report.declined:
        lines.append(
            "Package map, provenance table, citations, release train, current "
            "baseline, release tags, documented make targets and CI paths all resolve, as do "
            "the citations in the documentation, the queue and the source docstrings."
        )
    return "\n".join(lines)


def _git_output(root: Path, *args: str) -> str:
    # A failure raises rather than answering with an empty list, because every
    # caller reads the list as what changed, and an empty one is a diff with
    # nothing in it. A base that did not resolve, or a checkout that is not a
    # repository at all, printed "nothing to sweep", and the close-out sweep
    # was skipped over a diff nobody had read (`PL-9RFP`).
    #
    # `vcs.read_git`, so the read is classified, decoded and bounded as docket
    # reads the same question: a path whose bytes are not text here is unread
    # rather than a traceback (`PL-0T5X`), and a git that hangs is given up on
    # where this once waited for ever (`PL-S9JK`).
    return read_git(args, root, timeout=LONG_GIT_TIMEOUT)


# What a diff changes that documentation is likely to name: a definition, a
# data-file key, or the file itself.
#
# `DEFINITION_RE` requires the punctuation that makes a line a declaration
# rather than a sentence. Without it, a wrapped prose line beginning "class
# describes the deliverable" reads as a class named `describes`, so editing a
# single queue item seeded the search with an ordinary English word and
# returned 26 lines about nothing (`PL-B2NS`). A Python file's definitions are
# read from its statements instead (`_changed_definitions`, `PL-V2HK`), so this
# reads only the lines of a Python file the tokenizer refuses, and of a file in
# no Python suffix. A JSON file's keys are read from both copies' `json` parse
# (`_changed_json_keys`, `PL-VX3Q`), so `JSON_KEY_RE` reads only the lines of a
# copy `json` refuses.
DEFINITION_RE = re.compile(r"^[-+]\s*(?:async\s+)?(?:def|class)\s+(\w+)\s*[(:]")
JSON_KEY_RE = re.compile(r'^[-+]\s*"(\w+)"\s*:')
#: A `-U0` patch's hunk header: the rows it removes from the old file and adds
#: to the new one, each a first row and a count that is 1 where it is left out.
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", re.MULTILINE)
#: A patch's old-file header where the base has no such file.
NEW_FILE_RE = re.compile(r"^--- /dev/null$", re.MULTILINE)
#: The suffixes whose definitions are read as statements.
PYTHON_SUFFIXES = (".py", ".pyi")

# A term's shape decides how it is searched for, because the two shapes carry
# different risk. `doc_check.py`, `changed_tokens` and `TreeMap` cannot be
# written by accident in an English sentence, so they are searched for as bare
# words wherever they appear. A term that is *also* an ordinary word -
# `settle`, `render`, `check`, `model` - is searched for only where the line
# marks it as code, which this project does with backticks throughout.
#
# Searching the second kind as bare words is the defect this rule exists to
# fix: one function named `settle` returned 30 lines of unrelated prose, a
# module named `render.py` returned 37, and one JSON file whose keys are
# English words returned over 900 (`PL-B2NS`).
#
# The line between them is shape alone: a term that is a single run of letters
# is one prose can write by accident, and anything else - an underscore, an
# internal capital, a digit, a dot, a slash, a hyphen - is a shape it does
# not. A leading capital is not enough on its own, because `Gate` and `Scope`
# are class names here and ordinary words in `ROADMAP.md`.
ORDINARY_WORD_RE = re.compile(r"[A-Za-z][a-z]*")

# The term is the tail or the head of a dotted or slashed reference:
# `docket.render`, `tools/render`, `render.py`. The word character on the far
# side of the separator is required so that a sentence ending "...how we
# render." does not read as code.
QUALIFIED_LEFT_RE = re.compile(r"\w[./]$")
QUALIFIED_RIGHT_RE = re.compile(r"[./]\w")

# Past this many lines for one term, the output has stopped being a shortlist:
# a reader skims it, and the genuine candidates beside it get skimmed too. The
# ceiling applies only to a term that is also an ordinary word, where a large
# count is evidence that the word is common rather than that the symbol is
# widely documented - one settings key named `check` matched 80 lines of
# `docket check`. A distinctive term with eighty hits has eighty genuine
# references, and a rename needs every one of them, so it is never capped.
CROWDED_TERM_LIMIT = 10


def _changed_paths(root: Path, base: str) -> list[str]:
    # Both halves through docket's one parse of a `-z` listing, so a path is
    # named as written by each, whatever it holds (`PL-Y2L6`, `PL-PQ0R`).
    paths = listed_paths(_git_output(root, *changed_path_args("diff", "--name-only", base)))
    paths += listed_paths(_git_output(root, *untracked_path_args()))
    return sorted(set(paths))


def changed_tokens(
    root: Path, base: str, documents: Iterable[Path], unread: list[str]
) -> dict[str, set[str]]:
    """What each changed file gives the documentation a chance to contradict.

    A changed *source* file is named in prose by its filename or by a
    definition it declares, so those are the tokens to look for. A changed
    *documentation* file is different: what breaks is a cross-reference to a
    heading it no longer has, so a removed heading is the token. Searching a
    documentation file by its own name only reports that other documents link
    to it, which is true whether or not anything drifted.

    A Python file whose definitions could not be read as statements, and a
    JSON file a copy of which `json` refuses, is appended to `unread`, saying
    why and that its lines were read instead.
    """
    docs = {str(path) for path in documents}
    tokens: dict[str, set[str]] = {}
    for relative in _changed_paths(root, base):
        # A patch, whose `+` and `-` lines are file lines: translated as
        # `read_text` translates the file (`PL-0R4M`).
        patch = file_text(_git_output(root, "diff", "-U0", base, "--", relative))
        diff = [line for line in split_lines(patch) if line.strip()]
        if relative in docs:
            found = _removed_headings(root, base, relative, patch)
        elif PurePosixPath(relative).suffix in PYTHON_SUFFIXES:
            name = PurePosixPath(relative)
            found = {
                name.name,
                name.stem,
                *_changed_definitions(root, base, relative, patch, unread),
            }
        else:
            name = PurePosixPath(relative)
            found = {name.name, name.stem}
            # A key is a term only where the file declaring it is a data file.
            # The same `"key":` shape inside a changed markdown file is
            # somebody's example, and the tree holds no such key.
            if name.suffix == ".json":
                found |= _changed_json_keys(root, base, relative, diff, unread)
            else:
                found |= {match[1] for line in diff if (match := DEFINITION_RE.match(line))}
        tokens[relative] = {token for token in found if len(token) > 3}
    return tokens


def _changed_definitions(
    root: Path, base: str, relative: str, patch: str, unread: list[str]
) -> set[str]:
    """What the definitions holding a changed row define, on either side of `patch`.

    A statement rather than a line (`PL-V2HK`). A `def` or `class` line
    inside a fixture string defines nothing, and a parameter changed on the
    third line of a wrapped signature changes that definition, which a pattern
    over each changed line read the other way round both times. So each side's
    copy is read into logical lines, and each `def` or `class` statement
    spanning a row the hunk headers name changed is a term: the base's copy for
    the rows removed, the working tree's for the rows added, as the diff
    compares them.

    A copy the tokenizer refuses has its changed lines read a line at a time,
    as every file's were, and is appended to `unread`. So is a copy the
    tokenizer reads but the parser refuses, since the tokenizer's reading of it
    may have merged statements (`_parser_refusal`). Its changed lines are read
    both ways, so no definition the tokenizer merged away is dropped
    (`PL-LCBQ`).
    """
    found: set[str] = set()
    removed: set[int] = set()
    added: set[int] = set()
    for hunk in HUNK_RE.finditer(patch):
        first, count, new_first, new_count = (int(group or 1) for group in hunk.groups())
        removed.update(range(first, first + count))
        added.update(range(new_first, new_first + new_count))
    for rows, copy in ((removed, base), (added, "")):
        if not rows:
            continue
        try:
            if copy:
                text = _git_output(root, "show", f"{copy}:{relative}").removeprefix("\ufeff")
            else:
                # Undecoded line ends, so its rows are the ones git's counted.
                text = (root / relative).read_bytes().decode("utf-8-sig")
            lines = read_logical_lines(text)
            short = _parser_refusal(text)
        except (OSError, *UNTOKENIZABLE) as error:
            said = refusal(error) if not isinstance(error, OSError) else str(error)
            unread.append(
                f"{relative}: Python {platform.python_version()} cannot tokenize its copy "
                f"{f'at {copy}' if copy else 'in the working tree'} ({said}), so its changed "
                "lines were read a line at a time"
            )
            return found | {
                match.group(1)
                for line in split_lines(patch)
                if (match := DEFINITION_RE.match(line)) is not None
            }
        for line in lines:
            name = definition(line)[1]
            if name and any(line.first <= row <= line.last for row in rows):
                found.add(name)
        if short is not None:
            unread.append(
                f"{relative}: Python {platform.python_version()} cannot parse its copy "
                f"{f'at {copy}' if copy else 'in the working tree'} ({short}), so its tokenizer's "
                "reading may be short, and its changed lines were also read a line at a time"
            )
            found |= {
                match.group(1)
                for line in split_lines(patch)
                if (match := DEFINITION_RE.match(line)) is not None
            }
    return found


#: What a `json` reading holds where its copy holds no file: nothing at all,
#: so every key the other side holds is one the change added or removed.
ABSENT = object()


def _changed_json_keys(
    root: Path, base: str, relative: str, diff: Sequence[str], unread: list[str]
) -> set[str]:
    """Every key on the path to a value the diff changed, from both copies as `json` reads them.

    JSON lets white space, a line ending included, stand between any two
    tokens (RFC 8259 § 2), so the key a changed value sits under can stand lines
    above it - an array's entries - and a key's colon on the line below it.
    Read off each changed line, such a change seeded no key, and the documents
    stating the value were left off the list (`PL-VX3Q`). So the base's copy
    and the working tree's are each parsed, as RFC 8259 reads them
    (`_json_reading`), and the two readings compared by `_json_keys_changed`,
    as `_changed_definitions` reads Python from both copies' statements. A copy
    missing on one side holds nothing there. A copy `_json_reading` refuses has
    the diff's lines read a line at a time, as every file's were, and is
    appended to `unread`.
    """
    readings: list[object] = []
    for copy in (base, ""):
        try:
            if copy:
                held = _git_output(root, "ls-tree", "-z", "--name-only", copy, "--", relative)
                text = _git_output(root, "show", f"{copy}:{relative}") if held.strip("\0") else None
            else:
                file = root / relative
                text = file.read_bytes().decode("utf-8") if file.is_file() else None
            readings.append(ABSENT if text is None else _json_reading(text.removeprefix("\ufeff")))
        except ValueError as error:
            unread.append(
                f"{relative}: json cannot read its copy "
                f"{f'at {copy}' if copy else 'in the working tree'} ({error}), so its changed "
                "lines were read a line at a time"
            )
            return {match[1] for line in diff if (match := JSON_KEY_RE.match(line))}
    return _json_keys_changed(*readings) or set()


def _json_reading(text: str) -> object:
    """`text` as RFC 8259 reads it, refusing with `ValueError` what `json` reads past.

    Three things `json`'s defaults read past, each misreading a comparison. A
    name an object holds twice keeps its last value, so a change to the first
    went unseen, and RFC 8259 § 4 calls such an object's reading unpredictable. A
    `NaN` or an `Infinity`, which § 6 lets no number be, is read as a float,
    and a `NaN` equals nothing, so an unchanged one read as changed. And a
    number is rounded to a float, so two past its range or its precision read
    as one. The first two are refused, as a copy `json` cannot parse is, and a
    number is read as written, a `Decimal`.
    """
    return json.loads(
        text,
        parse_float=Decimal,
        parse_constant=_refused_constant,
        object_pairs_hook=_unique_members,
    )


def _refused_constant(name: str) -> object:
    """Refuse `NaN`, `Infinity` or `-Infinity`, which RFC 8259 § 6 lets no JSON number be."""
    raise ValueError(f"`{name}` is no JSON number")


def _unique_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """An object's members, refusing a name it holds twice."""
    members: dict[str, object] = {}
    for name, value in pairs:
        if name in members:
            raise ValueError(f'two members are named "{name}"')
        members[name] = value
    return members


def _json_keys_changed(before: object, after: object) -> set[str] | None:
    """The keys on the path to each value that differs between two `json` readings.

    `None` where none differs. A member whose value differs names its key and
    every key below it on the way to the difference, as a key changed on its own
    line was named; a member only one side holds, or a value whose type changed,
    names every key inside it too. An array is compared an entry at a time, by
    position, so an entry added or removed changes every entry after it.
    """
    if isinstance(before, dict) and isinstance(after, dict):
        found: set[str] = set()
        for name in before.keys() | after.keys():
            below = _json_keys_changed(before.get(name, ABSENT), after.get(name, ABSENT))
            if below is not None:
                found |= {name, *below}
        return found or None
    if isinstance(before, list) and isinstance(after, list):
        changes = [
            change
            for old, new in zip_longest(before, after, fillvalue=ABSENT)
            if (change := _json_keys_changed(old, new)) is not None
        ]
        return set().union(*changes) if changes else None
    if type(before) is type(after) and before == after:
        return None
    return _json_keys(before) | _json_keys(after)


def _json_keys(value: object) -> set[str]:
    """Every member name a `json` reading holds, at any depth."""
    if isinstance(value, dict):
        return set(value).union(*(_json_keys(member) for member in value.values()))
    if isinstance(value, list):
        return set().union(*(_json_keys(entry) for entry in value))
    return set()


def _removed_headings(root: Path, base: str, relative: str, patch: str) -> set[str]:
    """The title of each heading of a document's base copy that its working tree's copy lacks.

    Read from `markdown.headings` over both copies, as `_changed_definitions`
    reads Python through statements, rather than from each removed line of the
    diff (`PL-B47B`): a setext heading spans its text and its underline
    (CommonMark 0.31.2 § 4.3), so a removed one left no `#` line, and a removed
    `# comment` inside a fence is code (§ 4.5) and was taken for one. A YAML
    front matter is no heading, though its closing `---` underlines its keys as
    one, and read whole it was reported removed whenever a key changed
    (`PL-WX79`). A title the working tree's copy still has as a heading - one
    moved, or a line reflowed - is not removed.

    Any row `patch` touches can retitle one, which is why no row is asked
    about: a setext heading's text is its paragraph's lines, so a line added
    under it, or the blank line above it removed so the paragraph before joins
    it (§ 4.8), changes its title while every row of it stays. Counted only
    where the patch removed one of its rows, either change left the old title
    off the list (`PL-F6T5`). A document the base does not have lost none.
    """
    if HUNK_RE.search(patch) is None or NEW_FILE_RE.search(patch) is not None:
        return set()
    before = split_lines(_git_output(root, "show", f"{base}:{relative}").removeprefix("\ufeff"))
    after = (root / relative).read_bytes().decode("utf-8-sig")
    kept = {heading.title for heading in read_headings(_body_lines(split_lines(after)))}
    return {
        heading.title for heading in read_headings(_body_lines(before)) if heading.title not in kept
    }


def is_distinctive(term: str) -> bool:
    """Is this a shape an English sentence cannot produce by accident?"""
    return ORDINARY_WORD_RE.fullmatch(term) is None


def _marks_code(text: str, spans: Sequence[re.Match[str]], start: int, end: int) -> bool:
    """Does the document present this occurrence as code rather than as English?

    `spans` are the document's code spans in order, as `_code_spans` reads
    them: whole, so a span wrapped onto a line from the one above is the span
    it is, and its closing run no longer pairs with the line's next opening one
    and reads the prose between them as code (`PL-Z8RS`).
    """
    inside = bisect.bisect_right([span.start() for span in spans], start) - 1
    return (
        (
            inside >= 0
            and spans[inside].start("content") <= start
            and end <= spans[inside].end("content")
        )
        or text.startswith("(", end)
        or QUALIFIED_LEFT_RE.search(text, max(0, start - 2), start) is not None
        or QUALIFIED_RIGHT_RE.match(text, end) is not None
    )


def mentions(term: str, text: str, spans: Sequence[re.Match[str]] | None = None) -> list[int]:
    """The lines on which a document names the term as code, not as a word.

    A distinctive term counts wherever it stands as a word, so a line reading
    `changed_tokens returns` is reported without needing backticks. A term
    that is also an ordinary word counts only where the line marks it as code.
    Both are word-bounded, so `mine` no longer matches "determine".

    **The document is read whole, not a line at a time** (`PL-R417`). A term
    with a space in it - a removed heading's title - is a phrase the prose
    wraps like any other, and a title cited across a soft break lay on no one
    line: 448 of the 2,180 `§ "..."` citations in the tracked Markdown wrapped
    on 2026-10-04, so the sweep left them out or printed that nothing mentioned
    the term. A mention counts on the line it opens on, and one a line break
    splits counts only inside one statement, as `statement_lines` cuts them:
    not across a code block's own line break, nor from a heading's line into
    the paragraph under it (`PL-Z1R7`). `spans` are the document's code spans,
    read once by a caller asking about many terms.
    """
    distinctive = is_distinctive(term)
    if not distinctive and spans is None:
        spans = _code_spans(text)
    phrase = GAP.join(re.escape(word) for word in term.split())
    statements: list[tuple[int, int]] | None = None
    lines: list[int] = []
    for match in re.finditer(rf"(?<!\w){phrase}(?!\w)", _unmarked_text(text)):
        if not distinctive and not _marks_code(text, spans or (), match.start(), match.end()):
            continue
        line = _line_of(text, match.start())
        if "\n" in match.group(0):
            statements = list(_statement_offsets(text)) if statements is None else statements
            if not any(start <= match.start() and match.end() <= end for start, end in statements):
                continue
        if not lines or lines[-1] != line:
            lines.append(line)
    return lines


def _more_specific(candidate: str, incumbent: str, distinctive: bool) -> bool:
    """Which of two matching terms better explains why a line was chosen.

    A line is kept once however many terms hit it, so one of them has to be
    the label - and keeping whichever arrived first labelled it by the sort
    order instead. A changed `render.py` contributes both `render` and
    `render.py`, `render` sorts first, and two `ROADMAP.md` lines plainly
    about the module printed as `(render)` (`PL-Z0G0`).

    Distinctive first, then longest. The distinctive half carries more than
    length does: since `PL-B2NS` the label also tells the reader whether the
    term was one the tool had to narrow to code context, and an ordinary
    English word that happens to be longer would hide that.
    """
    return (distinctive, len(candidate)) > (is_distinctive(incumbent), len(incumbent))


def _diff_from(root: Path, base: str) -> tuple[str, str]:
    """The commit the sweep diffs from, and the words its output names it by.

    The diff starts at `git merge-base BASE HEAD`, the commit where the two
    histories last met (`PL-X229`). Every reader in `changed_tokens` diffed
    from the base itself, so a base that had gained commits since the fork
    listed their files as this branch's: 11 files and 184 lines where the
    branch had changed one file, named on 13 lines. The words are the base's
    name alone where the merge base is the base's own commit, as with the
    default `HEAD`, so only uncommitted changes are read then, as before.
    Where the two histories share no commit, git's answer is "no merge base",
    and the diff is from the base's own tree, which the words say. A base git
    cannot read raises `GitUnanswered`.
    """
    fork = _git_output(root, "merge-base", base, "HEAD").strip()
    if not fork:
        return base, f"{base}'s own tree, since it shares no history with HEAD"
    if fork == _git_output(root, "rev-parse", "--verify", f"{base}^{{commit}}").strip():
        return fork, base
    return fork, f"{base} from its merge base with HEAD, {fork[:8]}"


def format_candidates(root: Path, base: str) -> str:
    """Print the documentation lines a close-out sweep would grep for.

    The diff runs from where HEAD forked from `base` to the working tree, as
    `_diff_from` decides. Raises `GitUnanswered` where the diff cannot be
    read, which `main` reports as a sweep that did not happen rather than one
    that found nothing.
    """
    fork, against = _diff_from(root, base)
    documents = read_docs(root)
    unread: list[str] = []
    tokens = changed_tokens(root, fork, documents, unread)
    if not tokens:
        return f"No changes against {against}; nothing to sweep."

    lines = [f"Documentation to review for the diff against {against}:", ""]
    total = 0
    narrowed: set[str] = set()
    spans: dict[Path, list[re.Match[str]]] = {}
    for relative, wanted in tokens.items():
        # One entry per documentation line, however many tokens hit it, so a
        # rename does not print the same line a dozen times.
        hits: dict[tuple[Path, int], str] = {}
        crowded: list[str] = []
        for token in sorted(wanted):
            distinctive = is_distinctive(token)
            if not distinctive:
                narrowed.add(token)
            found = [
                (doc, number)
                for doc, doc_text in documents.items()
                if doc != Path(relative)
                for number in mentions(
                    token,
                    doc_text,
                    None if distinctive else spans.setdefault(doc, _code_spans(doc_text)),
                )
            ]
            if not distinctive and len(found) > CROWDED_TERM_LIMIT:
                crowded.append(
                    f"    ({token}) matches {len(found)} lines marked as code - a word in "
                    "this tree rather than a shortlist. Grep for it if the change touched it."
                )
                continue
            for key in found:
                incumbent = hits.get(key)
                if incumbent is None or _more_specific(token, incumbent, distinctive):
                    hits[key] = token
        if not hits and not crowded:
            continue
        total += len(hits)
        lines.append(f"  {relative}")
        lines.extend(
            f"    {doc}:{number}  ({token})" for (doc, number), token in sorted(hits.items())
        )
        lines.extend(crowded)
        lines.append("")

    if not total:
        lines.append("  Nothing in the documentation mentions anything this diff changed.")
        lines.append("")
    if unread:
        # Read another way rather than skipped, and said, so a definition the
        # list misses there is one the reader knows to look for (`PL-V2HK`).
        lines.append(
            "Read a line at a time rather than as statements, so a definition there inside a "
            "string or wrapped over several lines may be missed or misread:"
        )
        lines.extend(f"  {note}" for note in unread)
        lines.append("")
    if narrowed:
        # Name them, so a reader who suspects a miss knows the one word to
        # grep for by hand rather than distrusting the whole list.
        lines.append(
            "Also ordinary English, so searched only where a line marks it as code: "
            + ", ".join(sorted(narrowed))
            + "."
        )
        lines.append("")
    lines.append(
        "These are candidates, not findings: the mechanical half already ran in "
        "`check` mode. Read each line and decide whether it still states the truth."
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("mode", choices=("check", "candidates"))
    parser.add_argument("--root", type=Path, default=None, help="path to the repository")
    parser.add_argument(
        "--base",
        default="HEAD",
        help="candidates mode: diff from where HEAD forked from this revision",
    )
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parent.parent).resolve()

    if args.mode == "candidates":
        try:
            print(format_candidates(root, args.base))
        except GitUnanswered as silence:
            print(f"Cannot sweep: the diff against {args.base} could not be read.")
            print(f"  {silence}")
            print(
                "Nothing was swept. Name a base git can resolve and re-run - "
                "`git fetch origin` first where `origin/main` is missing."
            )
            return 1
        return 0

    report = analyze(root)
    print(format_check(report))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
