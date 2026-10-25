# Guard refusals

Each file here holds one session's refusals by the guard hooks under
`.claude/hooks/`, one line per refusal (`PL-SG93`). `hook_input.deny` writes
each line to a log on the machine that ran the session, and
`tools/hook_blocks.py copy` copies the lines here when `bin/docket record`
writes a pull request's number. `python3 tools/hook_blocks.py count` prints
how many refusals each guard and rule made, and in how many sessions.

A line is the time in UTC, the session id, the guard's name and the rule that
refused, separated by tabs. The command is never logged, because a command can
carry a token. A session that ends before it records a pull request loses its
lines, so the counts are a floor, not a total.
