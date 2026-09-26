---
id: PL-R5RF
title: gate-status-guard.sh reads a backslash-newline line continuation as a separator, so a pipefail gate whose command is continued onto a second line is refused although it keeps the status
status: untriaged
feature: one-answer
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
added: 2026-09-26
---

**Problem.** gate-status-guard.sh reads a backslash-newline line continuation as a separator, so a pipefail gate whose command is continued onto a second line is refused although it keeps the status

**Found 2026-09-26 while working `PL-GVFC`**, by piping each command as a hook
payload into `bash .claude/hooks/gate-status-guard.sh`. This one is refused,
and it keeps the status - `pipefail` is set, and the second line is still the
`pytest` command:

    set -o pipefail; uv run pytest -q \
      tests/unit/x.py 2>&1 | tail -5

The same command on one line passes. The hook replaces every newline with
` ; ` before tokenising (line 97), so the backslash-newline pair becomes an
escaped space followed by a `;`, and the walk reads `uv run pytest -q` as a
gate whose status the `;` hands to the next segment.

**Why it matters.** A correct spelling costs a retry, and the refusal message
blames a `;` the command does not contain - the shape `PL-1SFZ` records as
teaching a session that the refusal can be wrong.

**Done when.** A line ending in a backslash continues the command in
`gate-status-guard.sh`, and the command above passes, pinned in
`tests/unit/test_gate_status_guard.py`.

**Generator check.** An instance of `PL-PVW2`'s fact: how a shell command
splits. Since `PL-GVFC` the floor guard removes each backslash-newline before
it turns newlines into separators, and uses this hook's lexer settings
otherwise, so the two hooks now differ by that one line. The one splitter
`PL-PVW2` builds for the hooks to import should take it, which fixes this
item with it.
