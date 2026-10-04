---
id: PL-0779
title: docket new and docket set write a command-line value holding a newline verbatim and exit 0, leaving a file the next check refuses; latent
priority: P2
effort: S
status: ready
classes: defect
feature: front-matter-round-trip
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/model.py, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: a line break typed into a title or field is refused where it is typed, instead of landing as a stray line the next check refuses or as a second status line that hides an open item from list and next
verify: grep -q 'def test_new_and_set_refuse_a_value_holding_a_newline' subprojects/docket/tests/test_cli.py
---

**Problem.** docket new and docket set write a command-line value holding a newline verbatim and exit 0, leaving a file the next check refuses; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

A title or field value passed with an embedded newline is written as it stands at exit 0, and the next `bin/docket check` flags the file, so the refusal arrives after the write rather than instead of it. Not a member of `PL-R417`: the writer's validation, not a reader. Latent: no capture has passed one.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`, in a scratch store run with `--items` and `--no-git`: `bin/docket new $'first line\nsecond line'` exited 0 and wrote `title: first line` with `second line` at column zero under it, and the next `bin/docket check` exited 1 on "front-matter line(s) 'second line' belong to no field". `bin/docket set` on a clean capture with `--payoff $'first half\nsecond half'` did the same at exit 0. With `--payoff $'buys a thing\nstatus: done'` it exited 0 having written a second `status: done` line under the real `status: untriaged`; `list` then showed no open item, `show` read the item as `done`, and only `check` objected, with a repeated `status` key and "marked done but records no `closed` date".

**Why it matters.** `cmd_set` promises to apply "every rule `docket check` would apply a moment later" at the moment of writing, but it runs `analyze` over the in-memory `Item`, where a newline is one more character, and never over the lines `_front_matter_pairs` will split the written file into; `cmd_new` checks nothing of the kind. So the refusal arrives at the next `check` or `make check`, after the file is on disk, and the repair is a hand edit. A second line shaped like `key: value` is worse than a stray line: it writes a field nobody asked for, and the injected `status: done` above took an open item out of `list` and `next` until somebody ran `check`.

**Generator check.** An instance of `PL-9HD1`'s fact, the item front-matter value grammar: where a field's value ends and which spellings it may take, filed after that head closed on 2026-09-21. The writers never consult the grammar the reader holds, so they write a value it refuses. One of three such instances, with `PL-LNDJ` and `PL-WJM4`, recorded under `PL-HXJY` as a generator whose fix did not hold.

**Done when.** `bin/docket new` and `bin/docket set` refuse a title or field value holding a newline before anything is written: a non-zero exit, a message naming the field, and no file created or changed, so neither command can leave a file the next `check` refuses. `test_new_and_set_refuse_a_value_holding_a_newline` in `subprojects/docket/tests/test_cli.py` drives both commands with such a value, one of them a second line reading `status: done`, and asserts the exit, the message and the untouched store.
