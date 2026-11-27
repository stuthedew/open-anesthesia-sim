---
id: PL-8NDZ
title: Scope v0.8.0, the patient on the five-compartment model, in ROADMAP.md and file its build items
priority: P2
effort: M
status: done
classes: planning
feature: patient-model
touches: ROADMAP.md, docs/items, docs/features.toml
added: 2026-11-27
closed: 2026-11-27
payoff: v0.8.0 has a scope and build items a session can pick, so the patient work can start once Gate 4 clears
verify: grep -qF '## v0.8.0 - the patient, on the five-compartment model' ROADMAP.md
---

**Problem.** Scope v0.8.0, the patient on the five-compartment model, in ROADMAP.md and file its build items

**Why it matters.** The project owner approved the v0.8.0 scope on 2026-11-27
in the scoping thread, after the research recorded in
`/mnt/project-files/v0.8.0/scoping.md`. Until the section is in `ROADMAP.md`
and its items exist, no session can pick up the work.

**What was decided** (all project owner, 2026-11-27, ratified):

1. The model moves from Eger's four-compartment form to his five-compartment
   form, before compartment sizes become editable. This was chosen over
   editable compartments on the four-compartment model, and over age and
   weight alone.
2. Age and weight are the patient inputs. Sex, height and body composition are
   not, chosen over keeping sex as an input with no sourced effect.
3. The patient is an adult, 18 or older, chosen over children from 1 year on an
   adult body scaled by weight. Children get a later line on the roadmap.

**Sources read in full for the scope:** Hendrickx and De Wolf 2008 (*Modern
Anesthetics*, pp. 163-166); Eger and Saidman 2005 (*Anesth Analg* 100:1020-33,
Table 3 and Figures 4-5); Yasuda et al. 1991 (*Anesth Analg* 72:316-24);
Mapleson 1996 (*Br J Anaesth* 76:179-85); Davis and Mapleson 1981 (*Br J
Anaesth* 53:399-405); Cameron et al. 1984, LeDez and Lerman 1987, Taylor and
Lerman 1991 and Lerman et al. 1994 for ages under 1 year. All are in the
private reference corpus (pull request 2 there).

**Done when.** `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model" exists with its goal, Required scope, definition of done
and out-of-scope list; the timeline rows for v0.8.0 and Beyond are updated;
planned-milestone item 30 says what v0.8.0 takes and what is left; and the
build items are filed under `feature: patient-model`.

**Generator check.** None: filed by the v0.8.0 scoping round from its approved scope, not by a finding.
