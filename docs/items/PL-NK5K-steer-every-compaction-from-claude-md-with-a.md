---
id: PL-NK5K
title: Steer every compaction from CLAUDE.md with a Compact Instructions section, so the summary keeps the sources cited, the routes refuted, and which claims were verified
status: untriaged
feature: compaction-reset
touches: CLAUDE.md
added: 2026-09-25
---

**Problem.** Compaction writes its summary from a fixed prompt. Claude Code
2.1.282's, read from the binary, asks for nine sections:
- requests and intent;
- technical concepts;
- files and code;
- errors and fixes;
- problem solving;
- all user messages;
- pending tasks;
- current work;
- the next step.

None asks for the sources behind a conclusion, the routes weighed and refuted,
or which claims were checked and which inferred. Those three are most of
what this project's design rounds produce.

**Measured on the first live compaction, 2026-09-25.**
- The summary kept both user messages.
- It dropped 12 of the 20 references the session's review had cited. The 8
  it kept were the ones the edits touched, `PL-H253`'s among them.
- Nothing needed was lost, because `PL-YJG1`'s externalize-first step had put
  the sources in its item file. The summary is still no carrier to rely on
  for them.

**What is available.**
- The same prompt tells the summarizer to follow "additional summarization
  instructions provided in the included context", with a `## Compact
  Instructions` section as its example.
- `CLAUDE.md` is in that context, and
  [best practices](https://code.claude.com/docs/en/best-practices) recommends
  customizing compaction there.
- A few lines would steer every compaction, manual or automatic, with no
  focus text typed.

**Held by the generator pause.** It is a new rule, and `CLAUDE.md` § "What
this project is" holds those while any item carries `generator: live`. A
request from the project owner lifts that for this item (`PL-6Q9L`). It is
resident growth too, so it names what it replaces.

**Done when.**
- `CLAUDE.md` carries the section.
- The next compaction keeps the item ids in play, the sources cited and the
  routes refuted.
- It also marks each carried conclusion as verified or inferred.
