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

**Evidence on what summaries lose, checked against the sources 2026-09-25.**
- Anthropic's guidance: "overly aggressive compaction can result in the loss
  of subtle but critical context whose importance only becomes apparent
  later" (Rajasekaran P, et al., *Effective context engineering for AI
  agents*, Anthropic Engineering, 29 Sep 2025,
  https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- In book-length summaries, leaving things out is the main error, not making
  them up:
  - 2.1% (Claude 3 Opus) to 11.5% of claims were unfaithful;
  - 52% to 84.6% of summaries were criticised for omitting important
    information (Kim Y, et al., *FABLES*, COLM 2024, arXiv:2404.01261).
- A running summary, updated chunk by chunk, made 840 coherence errors to
  353 for hierarchical merging with GPT-4, and omission was the commonest
  error in both. The running summary kept more detail, and for Claude 2 with
  large chunks the gap vanished (Chang Y, et al., *BooookScore*, ICLR 2024,
  arXiv:2310.00785).
- For SWE-bench Verified agents (Lindenbauer T, et al., *The Complexity Trap*,
  NeurIPS 2025 DL4C workshop, arXiv:2508.21433):
  - LLM summaries made one model's runs 15% longer than hiding old tool
    output, which the authors read as summaries masking failure signals;
  - for the same model, they cut the solve rate from 40.4% to 31.4%;
  - hiding old tool output matched summarisation's solve rate at about half
    the raw agent's cost.
- A fresh prompt carrying the same information recovered nearly all of the
  multi-turn loss, and restating it inside the conversation recovered only
  part. The researchers assembled that prompt; no model wrote it (Laban P, et
  al., arXiv:2505.06120).
- Counterweight, from everyday chat without tools: user turns kept verbatim,
  with assistant turns cut to one-sentence summaries, often matched full
  context at about 8x less of it (Huang JY, et al., *Do LLMs Benefit From
  Their Own Words?*, COLM 2026, arXiv:2602.24287). Claude Code's compaction
  prompt keeps every user message too.
