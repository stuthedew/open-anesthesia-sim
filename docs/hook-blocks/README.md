# Guard refusals

Each file here holds the guard refusals that one branch's `bin/docket record`
copied, one line per refusal (`PL-SG93`). The file is named for the branch, so
two branches never write the same file. `hook_input.deny` writes each line to a
log on the machine that ran the session, and `tools/hook_blocks.py copy` copies
the lines that no file here holds yet. `python3 tools/hook_blocks.py count`
prints how many refusals each guard and rule made, how many bursts they make
and in how many sessions. A burst is a refusal and the retries that followed it
within two minutes, from the same guard and rule in the same session
(`PL-8RGF`).

A line is the time in UTC to the microsecond, the session id, the guard's name
and the rule that refused, separated by tabs. The command is never logged,
because a command can carry a token. Since 2026-11-03 the gate-status guard's
rule names the gate it read, as `status-swallowed:make check`, so a refused gate
can be told from a command the guard only took for one. A guard run by hand, with no session id in
its input, is not logged. The email guard refuses through `screen` in
`tools/pr_body_check.py`, which logs its refusals through
`hook_input.deny` as well, under the rule `email-address` (`PL-HHKC`).

The counts are a floor, and the floor is lowest for the guards that fire after
`bin/docket record`: `push-check-guard` and `gate-status-guard`. Their late refusals reach this directory only when a
later record on the same machine copies them, and a container that ends after
one pull request loses them.
