---
id: PL-XBV4
title: Read commands each assemble their own picture of the world - the store from the working tree, holds from refs, some after a fetch and some not, a failed fetch discarded, the forge asked by one command only - so each answers from a different moment and none says which
status: untriaged
feature: one-snapshot
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-09-25
root-cause-of: PL-8Z1T, PL-Y48N, PL-D1P5, PL-LFNK, PL-8BR0, PL-53Y6, PL-140X, PL-QSGX, PL-X3NY, PL-HVLJ
generator: live - PL-QSGX and PL-X3NY are open and the 2026-09-25 simulation reproduced seven more; every new read command assembles its own picture again
misread: How fresh the refs, working tree and forge state a read command answered from are
---

**Problem.** Read commands each assemble their own picture of the world - the store from the working tree, holds from refs, some after a fetch and some not, a failed fetch discarded, the forge asked by one command only - so each answers from a different moment and none says which

The simulation's violations V3, V4, V5, V7 and the cross-command audit's contradictions share one shape: two commands, or one command's two inputs, read different moments. `fetch_remote` swallows failure while `claiming._git` reports it; `next`/`show` read items from the working tree while holds come from refs; only `flight` asks the forge, and its contract lists open pull requests only, so merged, closed and never-opened are indistinguishable. PL-4Q9B (closed 2026-09-19) was the head for the remote-refs half, and its six members are still open.

**Why it matters.** The members are one mechanism; fixed one at a time, each fix leaves the mechanism in place to hand over the next.

**Done when.** One snapshot type (fetch result, origin/main vs working tree, refs, forge states open/merged/closed or unknown) built once per command and read by every read command, each of which prints what the snapshot rests on when it is not a fresh fetch; the members close against it and the regression suite item holds them.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Added 2026-09-25: PL-HVLJ.** `doc_check` reads the tags git holds, fetched now, against `ROADMAP.md` in a working tree that is behind `origin/main`, so any branch errors the moment a release merges and is tagged. It fired on `PL-P0FP`'s own branch after `v0.5.11` (#1003) was tagged, filed 2026-09-21 and still open.
