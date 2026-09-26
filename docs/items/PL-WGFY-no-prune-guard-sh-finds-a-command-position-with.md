---
id: PL-WGFY
title: no-prune-guard.sh finds a command position with its own regex rather than a shell split, so a ';' inside a quoted argument reads as a separator: on 2026-09-26 it refused a Bash call whose only 'git fetch --prune' was single-quoted text passed to a for loop
priority: P2
effort: M
status: ready
classes: defect
feature: one-answer
touches: .claude/hooks/no-prune-guard.sh, .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a member of PL-PVW2, its last
added: 2026-09-26
payoff: a Bash call carrying a prune only as quoted text - a loop over command strings, a commit message - runs instead of being refused, and every guard reads where a command starts from the one splitter, which lets PL-PVW2 close
verify: grep -q 'def test_a_quoted_separator_starts_no_command' tests/unit/test_no_prune_guard.py
---

**Problem.** no-prune-guard.sh finds a command position with its own regex rather than a shell split, so a ';' inside a quoted argument reads as a separator: on 2026-09-26 it refused a Bash call whose only 'git fetch --prune' was single-quoted text passed to a for loop

**Reproduced 2026-09-26 against `aca9fcde`**, by piping each command as a hook
payload into `bash .claude/hooks/no-prune-guard.sh`. All five are refused, and
none of them prunes anything:

    for c in 'git fetch origin; git fetch --prune' 'x'; do echo "$c"; done
    echo 'a; git fetch --prune'
    echo "a; git fetch --prune"
    git commit -m 'never fetch with --prune'
    git commit -m "a; git remote prune origin"

The four patterns anchor at `(?:^|[;&|\n(])` in the text
`shell_split.command_text` returns, which keeps quoted text as written, so a
`;` inside quotes reads as a separator; and each pattern then runs across
quotes, so the words of a commit message read as a command's flags.

**Why it matters.** A refusal of a command that prunes nothing costs a session
a retry, and one that refuses prose about its own subject teaches the session
that the refusal can be wrong, the lesson `PL-1SFZ` records. It is also
`PL-PVW2`'s last open member: this guard's regex is a second answer to where a
shell command starts, beside the splitter the other two guards import, and the
next hook can copy it.

**Done when.** The prune guard reads the commands `.claude/hooks/shell_split.py`
finds and matches its four shapes on their words, so a separator or a flag
inside quoted text starts nothing, pinned in `tests/unit/test_no_prune_guard.py`
as `test_a_quoted_separator_starts_no_command`. Every prune it refuses today is
still refused, including one inside a `$( )`, quoted or not, and one on a line
before a syntax error, which bash runs before it stops.

**Generator check.** An instance of `PL-PVW2`'s fact, how a shell command
splits, and its last open member: `#1087` put all three Bash guards on one
splitter and left this guard's command position to its own regex, as
`PL-PVW2`'s brief records.
