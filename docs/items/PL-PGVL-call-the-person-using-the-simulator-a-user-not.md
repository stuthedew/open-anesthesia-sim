---
id: PL-PGVL
title: Call the person using the simulator a user, not a learner, student or trainee, and describe the simulator as general-purpose simulation software that can be used for teaching rather than as a teaching tool
priority: P2
effort: M
status: ready
classes: docs
touches: README.md, pyproject.toml, CLAUDE.md, docs/MODEL.md, docs/INTERFACE.md, docs/ARCHITECTURE.md, docs/VERIFICATION.md, docs/PARAMETERS.md, .claude/rules/plain-writing.md, .claude/rules/ui-reader.md, .claude/rules/document-readers.md, .claude/rules/instruction-writing.md
added: 2026-11-27
payoff: a reader of the documentation and the interface meets a general-purpose simulator used by anyone, with teaching as one use, rather than a teaching tool for trainees
---

**Problem.** Call the person using the simulator a user, not a learner, student or trainee, and describe the simulator as general-purpose simulation software that can be used for teaching rather than as a teaching tool

**Why it matters.** The project owner, 2026-11-27: "Can we scrub learner terminology everywhere in references. At least as primary audience. This is supposed to be general purpose simulation software that can be used for learning", and "It certainly can be used as a teaching tool. But that's like saying solid works is a teaching tool for engineering students because it's used in their courses" (project owner, 2026-11-27). The tree names the learner as the person using the simulator in about 700 places outside closed item briefs: the interface specification, the code's docstrings and test names, the rules that say who reads an interface string, and the queue's payoff lines. `README.md`, `pyproject.toml` and `docs/MODEL.md` describe the simulator as a teaching simulator.

**Done when.**

1. The person using the simulator is called "the user" (or "a user", "users") in every live document, rule, skill, docstring, comment, test name and open item brief, where it was "the learner", "a student" or "a trainee" used as the name of that person.
2. Each statement of who the simulator is for or what it is (`README.md`, `pyproject.toml`, `docs/MODEL.md`, `.claude/rules/plain-writing.md`'s reader table, `.claude/rules/document-readers.md`, `.claude/rules/ui-reader.md`, `CLAUDE.md`'s safety-critical standard) describes it as general-purpose simulation software, and names teaching as one use where it fits.
3. Records stay as written: closed item briefs, `docs/releases/`, `docs/pr-bodies/`, `docs/ci-runs.tsv` and dated reports under `docs/prose-review/`, under `.claude/rules/citation-drift.md`'s rule that a closed record says what was true when it was written.
4. "Resident" in the sense of an instruction loaded at launch, and residents named as the participants of a usability test, stay, because neither names the audience.

**Out of scope here.** The `ROADMAP.md` section for v0.8.0, which another thread is scoping on 2026-11-27.

**Open question for the owner: the in-app use statement.** The disclaimer at the foot of the window opens "Educational simulation only." `docs/VERIFICATION.md` § "Class C is an engineering bar, not a regulatory status" rests the argument that the simulator is not a medical device on FDA's list of software functions that are not devices. Read 2026-11-27 that list's relevant heading is "2. Software functions that are intended for health care professionals to use as educational tools for medical training or to reinforce training previously received", with "Games that simulate various cardiac arrest scenarios to train health professionals in advanced cardiopulmonary resuscitation (CPR) skills" as an example. The page gives no example of general-purpose simulation software that is not about a specific patient; its deciding language is that a function is "not intended for use in the diagnosis of disease or other conditions ... by facilitating a health professional's assessment of a specific patient" ([FDA, Examples of Software Functions That Are NOT Medical Devices](https://www.fda.gov/medical-devices/device-software-functions-including-mobile-medical-applications/examples-software-functions-are-not-medical-devices), content current as of 09/29/2022). So this item leaves the use statement, `docs/MODEL.md` § "What the simulator is for" and the regulatory paragraph as they are until the owner decides whether the use statement should stop naming education.

**Generator check.** One-off: the owner reframed who the simulator is for on 2026-11-27. The wording it replaces was each session copying the term the documents already used, which this change removes at its source, the reader tables in `.claude/rules/plain-writing.md` and `.claude/rules/ui-reader.md`.
