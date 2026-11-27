---
id: PL-VT87
title: Check each refusal and halt notice that a user reads for what to do next, now that a refusal must say it (NUREG-0700 guideline 2.7.3-1)
priority: P3
effort: S
status: done
classes: ux
feature: interface-design-review
touches: src/anesthesia_sim/app/preferences.py, src/anesthesia_sim/app/agent_cost.py, src/anesthesia_sim/app/simulation_view.py, docs/INTERFACE.md, tests/unit/test_preferences.py
added: 2026-11-27
closed: 2026-11-27
pr: 2332
filed-pr: 2330
payoff: a user who meets a refused setting or a halted run is told how to go on, not only what went wrong
tests: tests/unit/test_preferences.py::test_the_notice_of_refused_preferences_says_what_the_reader_can_do
---

**Problem.** Check each refusal and halt notice that a user reads for what to do next, now that a refusal must say it (NUREG-0700 guideline 2.7.3-1)

**Where this comes from.** `PL-HWZK` added to
`.claude/rules/sources-and-docstrings.md` that a refusal a user reads also says
what to do next, such as the range a setting must fall in or the action that
clears the state. The existing messages were written to the earlier rule, which
asked for the condition, the value that failed it and where to read why.

**What to do.** List every string under `src/anesthesia_sim/app/` and
`src/anesthesia_sim/core/supported_ranges.py` that a user reads when a setting
is refused or a run halts. Mark each one that already says what to do next,
and reword each one that does not.

**Why it matters.** A refused setting or a halted run that names only the
problem leaves the user to work out the remedy, which NUREG-0700 Rev. 3
guideline 2.7.3-1 asks the message to give.

**Done when.** Every such message names the next step, and this item lists the
ones that were changed.

**Generator check.** One-off: the rule that these messages now miss was
written on 2026-11-27.

**Built 2026-11-27.** Every string under `src/anesthesia_sim/app/` that a user
reads when a setting, a branch, a price or a preference is refused, or when a
run halts, was read. `core/supported_ranges.py` writes its messages for a
developer, and `setting_refusal_for_a_user` in `app/dashboard_frame.py` rewords
them before a user sees one, so the user's texts are all in `app/`.

Already say what to do next, and left alone:

1. The setting refusals in `app/dashboard_frame.py`.
   `REFUSED_SETTING_OUTSIDE_RANGE_TEMPLATE` with `SETTING_LIMIT_REASONS` gives
   the range the setting must fall in, and `REFUSED_SETTING_NOTICE_TEMPLATE`
   says the run keeps its previous setting.
2. The refusals on a stopped run, which end with
   `SUPPORTED_LIMIT_SETTING_WAY_OUT_TEXT` or `RESET_SETTING_WAY_OUT_TEXT`.
3. Every halt banner (`FAILURE_NOTICE_TEMPLATE`, the three undrawn-failure
   templates, `REJECTED_ACCOUNTING_NOTICE_TEMPLATE`,
   `SUPPORTED_LIMIT_NOTICE_TEMPLATE`), which end with `{exit}`: Reset, a
   branch, or closing and reopening the application when Reset was refused
   (`REFUSED_RESET_WAY_OUT_TEXT`).
4. The branch refusals in `app/controller.py`, which name an earlier point or
   the trunk to branch from instead.
5. The price entry refusals, which give the form required, such as "such as
   20.47" or "such as USD", and `NO_PRICE_TEXT` and `REFUSED_PRICE_TEXT` in
   `app/agent_cost.py`.

Changed:

1. `refusals_notice` in `app/preferences.py`, which the agent cost View shows.
   Before: "some preferences in {path} were refused and are not used: the price
   at agent_prices[1]: {error}; ...". On the owner's word on 2026-11-27 ("Can
   you say which preferences rather than 'some preferences' check best
   practices"), it now names each refused preference first, then why in
   brackets, then where the file is and what to do: "These saved preferences
   were refused and are not used: your isoflurane price (...); the agent cost
   unit (...). They are saved in {path}. Set them again in this View, or
   discard the refused entries below." A price that gives no agent as text is
   named by its place, such as "price entry 4 in the file". The sources are
   the Nielsen Norman Group's "Error-Message Guidelines" ("Concisely and
   precisely describe the issue", and hide codes such as `agent_prices[1]`
   except for diagnosis) and the GOV.UK Design System's error summary, which
   lists each error separately. Both pages were read on 2026-11-27.
   `simulation_view.py` drops the "Also," it joined the notice with after an
   unsaved-change notice.
2. `PRICE_PER_ML_NOT_SHOWN_TEXT` gains "Check them below."
3. `COST_NOT_COMPUTED_TEXT` gained "Check your price for {agent} below." Then,
   on the owner's word on 2026-11-27 ("Should say whether too large and
   separate too small"), it was split in two. `COST_TOO_LARGE_TEXT` covers a
   cost that overflows or is too large to hold to its minor unit, and
   `COST_TOO_SMALL_TEXT` a cost that underflows to zero. Their present wording
   is in the next paragraph. `test_a_cost_too_large_and_a_cost_too_small_each_say_which` in
   `tests/unit/test_agent_cost.py` checks both sentences as written.

Left without a step, because the user can do nothing about the cause in the
application: `COST_NOT_CONVERTED_TEXT`, shown when the run's delivered amount
could not be converted to liquid or is withheld (`DeliveredShown.liquid_ml`),
which no price can repair, and `unsaved_preferences_notice`, whose
cause is the file system's refusal and whose message already says the change
lasts until the application closes.

The wording follows NUREG-0700 Rev. 3 guideline 2.7.3-1 and the Siemens iX
guidance on error messages, both quoted in
`.claude/rules/sources-and-docstrings.md` and read for `PL-HWZK`. No sentence
changes what a value means, so no clinician decision is asked.

Regression test: `test_the_notice_of_refused_preferences_says_what_the_reader_can_do`
in `tests/unit/test_preferences.py`. Run against `preferences.py` from HEAD
before the change (`git show HEAD:src/anesthesia_sim/app/preferences.py`, then
`pytest tests/unit/test_preferences.py -k says_what_the_reader`), the first
version of the test failed on its `startswith` assertion, because the old
notice began "some preferences" in lower case. The audit's mutation run then
showed that one refused entry cannot catch a wrong separator between reasons,
so the test now refuses three entries and compares the whole notice; a mutant
that joins them with "XX; XX" fails it.

**Plain-language rewrite, 2026-11-27.** The owner asked of the texts above "Are
these best practice in terms of technical writing for humans?". Checked
against the published guides, they were not, in three ways. Reasons were
written from the code's view, such as "an agent price's agent is a str, not
int". The file's full path sat in the middle of the main sentence. "Too large
to compute" described what the software could not do rather than what the user
had entered. The guides read on 2026-11-27 were the Microsoft Windows
error-message guidelines (learn.microsoft.com/en-us/windows/win32/uxguide/mess-error:
write "in terms of user actions or goals, not in terms of what the software is
unhappy with", "Avoid technical jargon", be specific with "names, locations,
and values", and keep full file paths out of the main instruction), the
Nielsen Norman Group's "Error-Message Guidelines", the GOV.UK Design System's
error summary, and GitLab Pajamas on error messages ("concise, specific, and
consistent").

What changed:

1. `refusals_notice` opens "These saved settings could not be used:", then
   lists one refused entry per line, each led by its name in the View's words,
   such as "Your isoflurane price:" or "How agent amounts are shown:", and
   the reason in the user's terms. It ends with the step and then the file's
   location: "Set them again in this View, or discard the refused entries
   below. They are saved in {path}."
2. Each price-entry reason names the field in the View's words and the value:
   "the bottle price must be a number above zero, and it is 0", "the currency
   must be a three-letter code in capital letters, such as USD, and it is
   'usd'", "the date must be written as year-month-day, such as 2008-03-05".
   `_require_above_zero` in `app/preferences.py` gives the bottle price and
   volume one wording. A refused display unit names the choices and the one
   the View shows instead.
3. The cost texts say what the user can check: "No cost: at your price, the
   {agent} would cost more than the simulator can show. Check the bottle price
   and volume below for a typing error." `COST_TOO_SMALL_TEXT` says "less
   than". `PRICE_PER_ML_NOT_SHOWN_TEXT` says the price per mL is "too large or
   too small to use" and asks for the same check.

The message given when the whole preferences file is unreadable still
describes the file's keys in its own terms. `PL-W312` records it, because that
text is not one this item's inventory listed.

**Docs checked at close-out.** `docs/INTERFACE.md` § "A cost at the reader's
price" (updated, with the steps each case names), `docs/MODEL.md` (no mention of
these texts), `README.md` (none), `docs/VERIFICATION.md` (none).
