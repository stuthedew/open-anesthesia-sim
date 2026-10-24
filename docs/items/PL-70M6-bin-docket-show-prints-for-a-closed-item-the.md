---
id: PL-70M6
title: bin/docket show prints, for a closed item, the sessions that worked it, as one more section of the whole item that the existing command already prints: each session's model, effort, served model and cost, joined from docs/session-ledger.tsv through the item's pull request
priority: P2
effort: S
status: ready
classes: session-cost, infra
feature: model-evidence
touches: subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md
added: 2026-10-19
payoff: one item reads whole in bin/docket show, and the model review joins items to sessions through the same function instead of re-deriving the join each month
verify: grep -rq 'session-ledger.tsv' subprojects/docket/src/docket && grep -q 'session-ledger' subprojects/docket/README.md
recurrences: 2026-10-24 PL-YF16
---

**Problem.** bin/docket show prints, for a closed item, the sessions that worked it, as one more section of the whole item that the existing command already prints: each session's model, effort, served model and cost, joined from docs/session-ledger.tsv through the item's pull request.

`bin/docket show` already exists and prints everything about one item: its
fields, its brief and its history. This item adds one section to that output.
It does not add a command. The owner noted on 2026-10-19 that the old title
read as if `show` were a new command for model and effort. The section's
heading, "Sessions that worked it", is a placeholder name, and it is what
says what the lines are (placeholder, 2026-10-19).

**Why it matters.** On 2026-10-19 the project owner asked why a closed item does
not carry its model and effort directly. The facts belong to a session, not an
item. On 2026-10-19, 1,877 closed items joined to 916 sessions, about two items
per session. A session also keeps spending after the commit that closes its
item, for example on CI fixes and review rounds. So the ledger (`PL-92ZN`)
stores each session once. What the owner wanted from the per-item form is a
reading in which one item shows everything about it. A join at read time gives
that without a second copy of the facts.

The join is item, then its `pr:`, then the squash commit on `main` whose
subject ends `(#N)`, then that commit's `Claude-Session:` trailers, then
`docs/pr-bodies/` as the fallback, then the ledger rows. The model review
(`PL-63CB`) needs the same join every month. Writing it once in `docket`
follows `CLAUDE.md` § "Architecture and development discipline" (a shared fact
has one source of truth). It is data access, not analysis, so it does not
reopen the owner's refusal of a committed analysis tool recorded on `PL-92ZN`.

**Done when.** `bin/docket show` prints, under a closed item and below a
heading that names the section, one line per joined session: session id, last served model, effort level and cost in USD.
It says so plainly when the item has no `pr:`, when no session joins, or when
a joined session has no ledger row. It must never print an empty list as if
the item had no sessions. `bin/docket show`'s help text names the section, so a reader of
`bin/docket --help` or `bin/docket show --help` learns that it is where to find
which model and effort worked an item (project owner, 2026-10-19). A
function in `docket` exposes the join for the model review to call. A test covers the joined, unjoined and missing-row cases, and
`subprojects/docket/README.md` documents the file it reads.

**Generator check.** Asked for by the project owner on 2026-10-19 as a
follow-on to `PL-92ZN`; a one-off, not an instance of a head.

**Worked.** The join is a new module, `subprojects/docket/src/docket/sessions.py`: `read_ledger`, `item_sessions` (the function the model review calls) and `format_item_sessions`. The git read is a new `vcs.squash_message`, beside `merged_pull_requests`, because `tools/fact_home_check.py` keeps git reads in `vcs`. Decisions the brief left open:

- **Where the section prints.** After the brief, as the last section of `show`'s output, and only for a `done` or `dropped` item. An open item prints no section at all.
- **What a line holds.** The session id, the last served model, the effort level and the cost rounded to the cent. Where `configured_model` differs from `last_served_model`, the line adds "(configured X)", because the title names both the model and the served model. `user_switched_model` and the token counts are not printed.
- **Session ids.** Read from every `claude.ai/code/session_...` link in the squash commit's whole message, as `PL-92ZN`'s result section asks, not only from `Claude-Session:` lines. A bare `session_` word is not read, because prose about sessions contains it.
- **The fallback.** `docs/pr-bodies/<N>.md` is read when the squash commit names no session, when no squash commit is found, when git declines, and under `--no-git`. The record path reuses `vcs.RECORDS`.
- **Which commit counts.** Only a squash subject ending `(#N)`, chosen by `vcs.subject_pull_request`. A `Merge pull request #N` commit is not taken, because it carries no pull request body. When nothing is found, `squash_message` declines instead of answering "none" if the checkout is shallow, cannot say whether it is shallow, or guessed its default branch.
- **The ledger parse.** The file is split on tabs and newlines, not read with `csv`, because two titles hold unescaped double quotes. A ledger missing one of the five columns it reads is refused, and each session's line then says the ledger was not read.
- **Names.** The heading constant is `sessions.SECTION_HEADING`, because `markdown.HEADING` already exists and the one-definition rule refuses a second. `show`'s help text and a new epilog name the section, so `bin/docket --help` and `bin/docket show --help` both mention it.
- **The cost.** It is printed to the cent only when it is plain decimal digits (`sessions.COST_RE`). Any other value is reported as not a number, and an empty one as not recorded. `decimal` is not used, because `test_portability` does not allow it in `docket`.
- **An added test entry.** `subprojects/docket/tests/test_vcs_silence.py` requires every public `vcs` read that takes a runner to be in its sweep. I added a `squash_message` entry that reads the fixture's `(#4)` squash commit. No existing entry or assertion changed.
- **Tests.** A new file, `subprojects/docket/tests/test_sessions.py`, with scratch git repositories and ledger rows written in the test. Seven cases: joined plus a missing row, the body-record fallback, no `pr:` and an unmatched pull request (including a body-only `(#12)` mention and `(#120)`), a missing ledger, an open item, a direct call to `item_sessions`, and a ledger missing columns. The shallow-clone decline has no test.

**Blocked.** The item's `verify:` command exits 0, but `make check` exits 2 on this host. On the final tree, pytest reported "2 failed, 10103 passed, 3 skipped". Both failures are in `tests/unit/test_makefile_reference.py`: `test_the_makefile_readers_read_generated_makefiles_as_make_does` and `test_the_makefile_readers_read_the_tracked_makefile_as_make_does`. Each fails with "AssertionError: /usr/bin/make is GNU Make 3.81; the comparison needs version 4 or newer". This diff does not touch the Makefile or that test. `PL-TSH9`, which is closed, records this as the Mac host's tooling. The work above is complete and committed. It needs `make check` run on a host whose `make` is GNU Make 4 or newer before it can be accepted.
