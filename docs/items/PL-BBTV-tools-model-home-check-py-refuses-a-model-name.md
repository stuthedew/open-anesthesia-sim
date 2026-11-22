---
id: PL-BBTV
title: tools/model_home_check.py refuses a model name inside a cited web address, such as Anthropic's prompting-guide pages, so each item citing one needs an exception
priority: P3
effort: S
status: done
classes: defect
feature: standing-weight
milestone: v0.6.20
touches: tools/model_home_check.py, tests/unit/test_model_home_check.py
deferred-from: v0.7.0 - a new problem: tools/model_home_check.py was added by PL-0XDM (#1791, 2b8a3e8f, 2026-10-25) after the freeze; a workflow check that changes nothing a learner sees
added: 2026-11-21
closed: 2026-11-22
pr: 2224
payoff: a session that cites a model prompting guide in an open item is not refused, and the exceptions list stops growing by one entry per citing item
tests: tests/unit/test_model_home_check.py::test_an_open_item_citing_a_guide_named_for_a_model_passes, tests/unit/test_model_home_check.py::test_a_model_id_beside_a_web_address_is_still_refused
---

**Problem.** tools/model_home_check.py refuses a model name inside a cited web address, such as Anthropic's prompting-guide pages, so each item citing one needs an exception

**Why it matters.** `PL-LY24`'s count found 4 of `tools/model_home_check.py`'s 5 CI refusals were model names inside the web address of a cited Anthropic prompting guide, such as the guide for Claude Sonnet 5, in `PL-J1ZM` and `PL-BFHK`. A citation is not an instruction about which model to use. `PL-J1ZM` was answered by adding the item to `COPIES`, so each later citation of the guides needs another exception.

**What to do.** Leave a model id inside a web address out of the check, and test it with the two guide addresses.

**Done when.** An open item that cites the guide addresses passes the check without an entry in `COPIES`, and an id outside an address is still refused.

**Checked 2026-11-22.** `MODEL_ID_RE` in `tools/model_home_check.py` still matches a model id anywhere in a file, inside a web address too, and the check leaves no address out. It passes today only because both items that cite the guides are closed: `PL-J1ZM` was dropped and `PL-BFHK` is done. So the `COPIES` entry for `PL-J1ZM` now excuses a closed item, which the check skips anyway, and the work can remove it.

**Generator check.** The fact misread is which text in a file is a choice of model and which is part of a cited address. No head states it. The nearest, `PL-KR6M` (which Markdown blocks hold a literal), is about whole blocks rather than one token. This is a one-off.

**Done 2026-11-22.** `tools/model_home_check.py` removes every web address (`WEB_ADDRESS_RE`) before it searches for a model id, and the `COPIES` entry for `PL-J1ZM` is gone. Two tests pin the guide addresses passing and an id beside an address still refused. Files checked for statements about what the check reads: the module docstring, `docs/apparatus.md` and `CLAUDE.md`; only the docstring described it, and it now names the exception.
