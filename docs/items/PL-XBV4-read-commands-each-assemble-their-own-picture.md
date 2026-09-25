---
id: PL-XBV4
title: Read commands each assemble their own picture of the world - the store from the working tree, holds from refs, some after a fetch and some not, a failed fetch discarded, the forge asked by one command only - so each answers from a different moment and none says which
priority: P2
effort: L
status: ready
classes: defect, infra
feature: one-snapshot
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-snapshot batch
added: 2026-09-25
payoff: every docket read says which moment it answered from, so a failed or skipped fetch, or a working tree behind origin/main, stops passing for a fresh answer in every command at once
verify: grep -q 'def test_every_read_command_names_what_its_snapshot_rests_on' subprojects/docket/tests/test_cli.py
root-cause-of: PL-8Z1T, PL-Y48N, PL-D1P5, PL-QSGX, PL-HVLJ
generator: live - nothing records which moment a read answered from: vcs.fetch_remote returns None, and next, show, flight and the digest never fetch or date their refs, so each new read command picks its own sources again; three members were reproduced on 2026-09-25 beside two open since 2026-09-19 and 2026-09-21
misread: How fresh the refs, working tree and forge state a read command answered from are
---

**Problem.** Read commands each assemble their own picture of the world - the store from the working tree, holds from refs, some after a fetch and some not, a failed fetch discarded, the forge asked by one command only - so each answers from a different moment and none says which

The simulation's violations V3, V4, V5, V7 and the cross-command audit's contradictions share one shape: two commands, or one command's two inputs, read different moments. `fetch_remote` swallows failure while `claiming._git` reports it; `next`/`show` read items from the working tree while holds come from refs; only `flight` asks the forge, and its contract lists open pull requests only, so merged, closed and never-opened are indistinguishable. PL-4Q9B (closed 2026-09-19) was the head for the remote-refs half, and its six members are still open.

**Why it matters.** The members are one mechanism; fixed one at a time, each fix leaves the mechanism in place to hand over the next.

**Done when.** One snapshot type (fetch result, origin/main vs working tree, refs, forge states open/merged/closed or unknown) built once per command and read by every read command, each of which prints what the snapshot rests on when it is not a fresh fetch; the members close against it and the regression suite item holds them.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Added 2026-09-25: PL-HVLJ.** `doc_check` reads the tags git holds, fetched now, against `ROADMAP.md` in a working tree that is behind `origin/main`, so any branch errors the moment a release merges and is tagged. It fired on `PL-P0FP`'s own branch after `v0.5.11` (#1003) was tagged, filed 2026-09-21 and still open.

**Membership, triaged 2026-09-25 against 46954a81.** Five members share the `misread:` fact: `PL-8Z1T` (a failed fetch discarded, so `branch` says `current with origin/main`), `PL-Y48N` (a working tree behind a fetched `origin/main` offers an item it closed), `PL-D1P5` (`next`, `show`, `flight` and the digest never fetch or date their refs), `PL-QSGX` (`flight` never fetches) and `PL-HVLJ` (tags fetched ahead of the working tree). The first three were reproduced that day in scratch clones, and each brief says what it showed. Five others filed here are left to the fact their reader actually misread, none of which is freshness: `PL-X3NY` to `PL-7TVT`'s (whether a branch's holder is still live), where it was already a member; `PL-8BR0` to `PL-GHHW`'s (whether the base already holds a branch's change), filed once that head had closed; `PL-53Y6` to `PL-QHCW`'s (whether and where a release was cut), as its own brief says; `PL-LFNK` to `PL-PVW2`'s (two spellings of "is this item only on a branch"); and `PL-140X` is a one-off. The forge dimension in **Done when.** served `PL-X3NY` and `PL-8BR0`; whether the snapshot still carries it is the working session's call.

**Generator check.** A head, and live: the fact is which moment the refs, working tree and fetch a read command answered from belong to, and no function records it. `vcs.fetch_remote` returns `None`, and only `branch --no-fetch` and `stranded --no-fetch` say they read the last fetch. Its remote-refs half is `PL-4Q9B`'s fact (done 2026-09-19, six members still `ready`), and all five members were filed on or since the day that head closed, so this is its mechanism still producing, recorded at the wider altitude.
