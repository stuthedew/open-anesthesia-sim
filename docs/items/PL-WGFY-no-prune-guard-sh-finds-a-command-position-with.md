---
id: PL-WGFY
title: no-prune-guard.sh finds a command position with its own regex rather than a shell split, so a ';' inside a quoted argument reads as a separator: on 2026-09-26 it refused a Bash call whose only 'git fetch --prune' was single-quoted text passed to a for loop
priority: P2
effort: M
status: done
classes: defect
feature: one-answer
touches: .claude/hooks/no-prune-guard.sh, .claude/hooks/shell_split.py, .claude/hooks/gate-status-guard.sh, .claude/hooks/floor-interpreter-guard.sh, tests/unit/test_no_prune_guard.py, docs/items/PL-PVW2-predicates-the-apparatus-asks-repeatedly-which.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; a member of PL-PVW2, its last
added: 2026-09-26
closed: 2026-09-26
pr: 1088
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

**Built 2026-09-26, in #1088.** The guard reads `shell_split.commands`, and
each of its four shapes is a `git` command whose words include the shape's own
in order: `fetch` then a prune flag, `remote` then `prune`, `remote update
--prune`, and `config` then a prune setting. The move had to keep three things
the regex had, by design or by accident:

- **A command in `( )`, `$( )` or `<( )` is a command.** The regex took `(` for
  a command position, so `echo "$(git remote prune origin)"` was refused, and
  `commands` also reads the commands of a `$( )` inside double quotes, whose
  text the splitter keeps in the quoted word.
- **A command bash would refuse is still read as far as it goes.** Bash runs
  every line before the one it cannot finish, so `git fetch --prune` followed by
  a line with an unclosed quote prunes. `segments` answers None there, which the
  gate and floor guards fail open on; `commands` returns what it read, which is
  what `command_text` kept its raw remainder for. `command_text` had no other
  caller and is gone.
- **Where a command's words start is one answer.** `shell_split.command_words`
  replaced the copy the gate and floor guards each held, so this guard drops a
  `{` and a `!` as they do: `{ git fetch --prune; }` and `! git fetch --prune`,
  which the regex let through, are refused.

Seven new cases fail on the hook as it stood - the five above and the two
openers - and the substitution and syntax-error cases pass on both, pinned so
the move cannot lose them. Two older misses the four shapes never covered are
filed: `PL-R17X` for pruning spellings git documents beyond them, and
`PL-0X0G` for a reserved word such as `do` or `time` in front of a command,
which all three guards read as its name.
