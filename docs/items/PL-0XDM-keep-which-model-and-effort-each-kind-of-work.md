---
id: PL-0XDM
title: Keep which model and effort each kind of work uses in one extensible table, and use no Fable unless the owner names it
priority: P2
effort: M
status: done
classes: refactor
feature: one-source-of-truth
touches: docket.toml, subprojects/docket/src/docket/config.py, tools/, tests/unit/, subprojects/docket/tests/, .claude/, docs/maintainer.md, docs/apparatus.md, subprojects/docket/README.md
deferred-from: v0.7.0 - filed 2026-10-25 after the gate froze, at the owner's request in the workflow lane, and built at once outside the gate's scope
added: 2026-10-25
closed: 2026-10-25
pr: 1791
payoff: a change of model or effort for any kind of work is one edit to docket.toml, and no stale copy can send a session to a model the owner has ruled out
verify: grep -q '^\[models\]' docket.toml
---

**Problem.** Which model and which effort a piece of work uses is written in many places, and none of them reads another. `docs/maintainer.md` § "Match model capability to the work" said `use your strongest model` means Fable 5.1. `tools/model_doc_review.py` named Fable as `REVIEW_MODEL`, and `tools/headless_worker.py` names Opus 5.5 as `WORKER_MODEL`. `.claude/agents/Explore.md` sets `model: opus`. `.claude/settings.json` sets `effortLevel`, and maintainer.md and `.claude/rules/apparatus-standard.md` repeat that level. No check holds any of these copies to another. A session recommended a Fable run on 2026-10-25 because an item written before the owner's change still prescribed Fable.

**The owner's rules** (project owner, 2026-10-25). "Nothing should be using fable anymore unless I specifically say." "Make things that say which model and effort to use use a single source of truth as well." "Model single source of truth will need to be extendible because may end up wanting this model or strength for this arbitrary category(ies) and a different default."

**Why it matters.** A model or effort named in a stale copy is followed by whichever session reads that copy first. The owner pays for a model they have ruled out, or work runs below the bar they set for it, and nothing reports the disagreement.

**The design.** A `[models]` table in `docket.toml` is the one home. docket and the tools already read that file.

- `default` names a model and an effort.
- `excluded` lists the models nothing uses unless the owner names one for that work. Fable 5.1 is listed first.
- `[[models.rule]]` entries are overrides, read in order. The first entry whose `match` holds wins. Each entry sets `model`, `effort` or both, and a key it leaves out falls back to `default`.
- A `match` table may name any category. The reader supplies the facts it knows, such as an item's `class`, `lane`, `feature`, `status` and `size`, or a `role` such as `worker`, `review`, `exploration` or `delegable`. A rule matches only when every key it names has the value given. A new category or override is a data edit, with no code change.
- `[models.areas]` names code areas by path, such as `simulator = ["src/anesthesia_sim/core/", "src/anesthesia_sim/data/"]` and `ui = ["src/anesthesia_sim/app/"]`. An item's areas are those that any path in its `touches` falls under. A rule with `match = { area = "ui" }` holds when the item's areas include `ui`. A session working on files with no item passes the paths it changes instead. The owner's example (2026-10-25): "simulator code x model and y strength, UI code model A effort B".
- An item can touch more than one area, or match several rules in other ways. The first matching rule in file order wins, as in `model-evidence.toml`, so the table lists its most demanding rule first. An item touching both `core/` and the UI then takes the simulator's model and effort when the simulator rule comes first. The table's own comment says so, and a test holds one such item to that answer.
- `bin/docket` and the tools ask one reader for a model and an effort, with the facts they hold. `bin/docket next` prints the model it names, replacing the bare words "use your strongest model".
- `.claude/settings.json`'s `effortLevel` and `.claude/agents/Explore.md`'s `model:` cannot read the table, because the harness reads them. `tools/config_home_check.py` holds each one to its value in the table, and does the same for the prose copies in `docs/maintainer.md`.
- A new check refuses a model id in a tracked file outside the table, except in records (closed items, `docs/worker-runs/`, `docs/session-ledger.tsv`, release notes and pull request bodies), test expected values and the copies `config_home_check` holds. It refuses an `excluded` model's id in any tracked file that is not a record.

**Done when.** The table exists and is the only place a current model or effort choice is stated. Every reader goes through it. Changing `default` or adding a rule changes what `bin/docket next`, the headless worker and the review tool use, with no other edit. The check refuses a model id written anywhere else, and refuses Fable's id outside the records.

**Generator check.** The misread fact is which model and effort the owner wants for a kind of work. It had no single home, so each copy aged on its own. This item gives it one home and a check, which is the fix the `one-source-of-truth` feature asks for. It is one instance, not a generator.

**Built, 2026-10-25.** `docket.model_choice` reads the table, and `docket.config` loads it as `Config.models`. Its readers are these.

- `bin/docket next` and `show` print the chosen model and effort beside the model flag, such as "use your strongest model, claude-opus-5-5 at high effort". The flag's words stay, because the flag is the rule and the table is the answer to it.
- `tools/headless_worker.py` asks for each item as the role `worker`, and `--model` is now an override. A project with no table is refused before any spend.
- `tools/model_doc_review.py` asks as the role `review`, and takes the list price from `[models.prices]`, at half for a batch. A model with no price is refused.

`tools/config_home_check.py` holds three copies to the table: `effortLevel` in `.claude/settings.json`, the effort in `docs/maintainer.md` § "Match effort to the standard the work is held to", and `model:` in `.claude/agents/Explore.md`. `tools/model_home_check.py` is the new check, run bare in `make check` and in the quality job. The other prose copies were rewritten to point at the table rather than held to it: `docs/maintainer.md` § "Which model each flag means" and `.claude/rules/apparatus-standard.md`. Neither the release notes nor pull request bodies are tracked files, so the check does not read them. `PL-5S71`'s brief no longer names Fable's id, and it records the refused run.

One part of the design is not built: a session working with no item passing the paths it changes. No reader does that today, so it waits for the first one.
