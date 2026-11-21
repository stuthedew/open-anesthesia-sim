---
id: PL-BBTV
title: tools/model_home_check.py refuses a model name inside a cited web address, such as Anthropic's prompting-guide pages, so each item citing one needs an exception
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** tools/model_home_check.py refuses a model name inside a cited web address, such as Anthropic's prompting-guide pages, so each item citing one needs an exception

**Why it matters.** `PL-LY24`'s count found 4 of `tools/model_home_check.py`'s 5 CI refusals were model names inside the web address of a cited Anthropic prompting guide, such as the guide for Claude Sonnet 5, in `PL-J1ZM` and `PL-BFHK`. A citation is not an instruction about which model to use. `PL-J1ZM` was answered by adding the item to `COPIES`, so each later citation of the guides needs another exception.

**What to do.** Leave a model id inside a web address out of the check, and test it with the two guide addresses.

**Done when.** An open item that cites the guide addresses passes the check without an entry in `COPIES`, and an id outside an address is still refused.
