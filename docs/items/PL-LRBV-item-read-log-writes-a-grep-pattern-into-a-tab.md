---
id: PL-LRBV
title: item_read_log writes a Grep pattern into a tab-separated record stripping only tabs and newlines, so a pattern holding a carriage return splits the record and item_reads.parse_log keeps the target cut short; latent
priority: P3
effort: S
status: done
classes: defect
touches: .claude/hooks/item_read_log.py, tools/item_reads.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-05
pr: 1364
payoff: Every id a session searched for reaches the read-log counts, instead of the ids after a stray carriage return vanishing with no sign in the report
verify: grep -q 'def test_a_carriage_return_in_a_pattern_does_not_split_the_record' tests/unit/test_item_read_log.py
---

**Problem.** item_read_log writes a Grep pattern into a tab-separated record stripping only tabs and newlines, so a pattern holding a carriage return splits the record and item_reads.parse_log keeps the target cut short; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

`item_read_log.py`:132 strips `\t` and `\n` from what it writes, and `item_reads.parse_log` (91) splits records with `splitlines()`, which also breaks at `\r`: a target `PL-K7QX\rPL-B1D0` comes back as `PL-K7QX`. Not a member of `PL-R417`. Latent.

**Reproduced 2026-10-04, at triage.** On Python 3.11.15, against `main` at `8cc0698d`: `.claude/hooks/item_read_log.py`, run with `CLAUDE_PROJECT_DIR` pointed at a scratch directory, was handed a Grep payload whose pattern is `PL-K7QX`, a carriage return, then `PL-B1C2`. It wrote the record's last two fields as `Grep\tPL-K7QX\rPL-B1C2\n`, the `\r` raw, and `item_reads.parse_log` over that log returned one row whose target is `PL-K7QX`, the tail line holding `PL-B1C2` dropped for having one field. `Path.read_text` already turns that `\r` into a newline, so splitting on `\n` after it would not repair the reader.

**Why it matters.** `tools/item_reads.py` turns this log into the numbers the store's design arguments rest on - how many items sessions open, and whether a citation edge is ever followed - and a Grep pattern is arbitrary text a session typed. A record cut at a carriage return loses every id after it, and `parse_log` drops the fragment line without a word, so the counts come out low while the report reads as complete. Latent: no recorded pattern holds one.

**Generator check.** A member of `PL-4YVK`: where one line ends in line-oriented text, which `str.splitlines()` breaks at more characters than the item-read log does. With `PL-139L` and `PL-PK4B` before it, four items misread that fact and no head stated it, so it was recorded as a generator at triage, 2026-10-04.

**Done when.** A Grep pattern holding a carriage return, or any other character `str.splitlines` breaks at, comes back from `item_reads.parse_log` as one record whose target keeps every id, whether the hook replaces each such character as it does a tab and a newline or the reader reads the log with `newline=""` and splits on `\n` alone. `test_a_carriage_return_in_a_pattern_does_not_split_the_record` in `tests/unit/test_item_read_log.py`, beside `test_a_tab_in_a_pattern_does_not_shift_the_columns`, writes such a record through the hook and reads both ids back.
