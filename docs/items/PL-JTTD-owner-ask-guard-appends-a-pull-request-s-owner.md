---
id: PL-JTTD
title: owner_ask_guard appends a pull request's Owner-ask line to every thread message and edit while the checkout's branch holds an Owner-read record, including after the owner has said Merge, so replies on #2022 (2026-11-04, 17:19-17:25Z) repeated an ask he had already answered; it stops only once the pull request merges
status: untriaged
added: 2026-11-04
---

**Problem.** owner_ask_guard appends a pull request's Owner-ask line to every thread message and edit while the checkout's branch holds an Owner-read record, including after the owner has said Merge, so replies on #2022 (2026-11-04, 17:19-17:25Z) repeated an ask he had already answered; it stops only once the pull request merges

**Observed 2026-11-04.** Stuart said "Merge" on #2022 at 17:18:58Z, and the thread armed auto-merge at 17:19Z. Three later messages in the thread "Finish the copy editor items", one of them an edit made to remove the line, came back with the Owner-ask line appended (`PL-X4MD`). Stuart then asked "Didn't I say merge already?" The guard keys on the branch's commit records, which cannot hold the owner's word, so it has no way to see that the ask was answered. The lines were removed only after the merge deleted the branch. A fix needs some record of the answer that the guard can read, such as the pull request being armed after the hold.
