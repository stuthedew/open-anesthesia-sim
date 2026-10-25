# Guard refusals

Each file here holds the guard refusals that one branch's `bin/docket record`
copied, one line per refusal (`PL-SG93`). The file is named for the branch, so
two branches never write the same file. `hook_input.deny` writes each line to a
log on the machine that ran the session, and `tools/hook_blocks.py copy` copies
the lines that no file here holds yet. `python3 tools/hook_blocks.py count`
prints how many refusals each guard and rule made, and in how many sessions.

A line is the time in UTC to the microsecond, the session id, the guard's name
and the rule that refused, separated by tabs. The command is never logged,
because a command can carry a token. A guard run by hand, with no session id in
its input, is not logged. `pr-body-email-guard.sh` refuses through
`tools/pr_body_check.py --screen`, which logs its refusals through
`hook_input.deny` as well, under the rule `email-address` (`PL-HHKC`).

The counts are a floor, and the floor is lowest for the guards that fire after
`bin/docket record`: `push-check-guard`, `gate-status-guard` and
`direct-merge-guard`. Their late refusals reach this directory only when a
later record on the same machine copies them, and a container that ends after
one pull request loses them.
