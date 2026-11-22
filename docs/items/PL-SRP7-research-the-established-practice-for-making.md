---
id: PL-SRP7
title: Research the established practice for making the interface localizable, so that a later build can translate its text and format numbers, dates and money for the reader's region without rework (owner, 2026-11-22)
priority: P3
effort: M
status: done
classes: planning
feature: preferences-store
touches: src/anesthesia_sim/app/formatting.py
added: 2026-11-22
closed: 2026-11-22
pr: 2210
payoff: the project knows how to make the interface translatable and regional before more strings and formatters are written in a way that would need rework
---

**Problem.** Research the established practice for making the interface localizable, so that a later build can translate its text and format numbers, dates and money for the reader's region without rework (owner, 2026-11-22)

The owner asked on 2026-11-22, while setting the rule that display units live in one Settings window (`PL-TLW6`): "don't need to implement now but research best practice for allowing localization" (project owner, 2026-11-22). The interface's strings are English literals in `src/anesthesia_sim/app/`, held word for word by `tests/integration/approved_interface_strings.json`, and numbers are formatted by hand in `app/formatting.py`.

**Why it matters.** Text, number formats and units that are built into the code now become a rewrite later. Knowing the established route first, such as Qt's own translation tools and the Unicode CLDR locale data, lets each new string and formatter be written so translation and regional formats can be added without touching the clinical values.

**Done when.** The brief records, from sources read in the session, the established practice for a Qt for Python application: how strings are marked and translated, how numbers, dates and money follow the reader's region, how units fit with the Settings window of `PL-TLW6`, and what this project would have to change in how it writes strings and formatters today. It ends with a recommendation for the owner, with no code changed.

**Generator check.** A one-off: research the owner asked for.

**Findings (2026-11-22).** Each source below was read in this session, and each entry says how much of it was read. Each value marked "measured" was produced in this session by the installed PySide6 6.11.2 or by Babel 2.18.0 in a scratch environment.

**1. How the text is marked and translated.**

1. Qt for Python supports two routes, and its tutorial documents both (full text read: [Translating Applications](https://doc.qt.io/qtforpython-6/tutorials/basictutorial/translations.html)). The Qt route marks text with `self.tr()`, or with `QCoreApplication.translate()` outside a `QObject`. `pyside6-lupdate` collects the text into `.ts` files, a translator works in Qt Linguist, `pyside6-lrelease` compiles `.qm` files, and a `QTranslator` loads them at start. The gettext route marks text with `_()` and `ngettext()`, collects it into `.po` catalogues and compiles `.mo` files.
2. Qt's own dialog text, such as the buttons of a file dialog, is translated only by Qt's `qtbase` catalogue, which a `QTranslator` loads. The same tutorial loads that catalogue first and the application's own second. So an application that uses gettext for its own text still loads one `QTranslator`.
3. Python's `gettext` has `pgettext()` and `npgettext()` for a message that needs a context, since Python 3.8. A module must use the class-based interface rather than install `_` into the built-in names. A string that is marked in one place and translated later is marked with a no-op function such as `N_()`. Babel's `pybabel` extracts and compiles the catalogues (full text read: [gettext](https://docs.python.org/3/library/gettext.html)).
4. Qt's rules for writing translatable source apply whichever route is used (full text read: [Writing Source Code for Translation](https://doc.qt.io/qt-6/i18n-source-translation.html)). Do not build a sentence by joining words and values, because languages order them differently: put numbered or named placeholders in one whole message. Pass the count with a plural message so that each language picks its own plural form. Add a comment for the translator where the meaning is not obvious, and a disambiguating context where two identical English words mean different things.
5. An f-string cannot be translated. Python fills in its values before any translation call sees the text, so there is no fixed message to look up. A translatable message is a template, such as `"{agent} bottle volume must be more than 0 mL"`, filled in after translation.

**The route for this project is gettext.** `core/` may not import Qt (`tools/import_boundary_check.py`), and `core/` raises the refusal messages that a learner reads. So `self.tr()` and `QCoreApplication.translate()` cannot reach those messages, and gettext, which is in the standard library, can. One `QTranslator` loads Qt's own catalogue.

**2. How numbers, dates and money follow the reader's region.**

1. `QLocale` takes its data from Unicode CLDR v48.2 in Qt 6.11. `QLocale.system()` uses the decimal and grouping characters and the date and time formats from the system's settings on Windows and macOS. `QLocale.setDefault()` sets the locale that every default-constructed `QLocale` and every `%L` placeholder uses (read: the class description and the entries for `system()`, `c()`, `setDefault()`, `measurementSystem()` and `toCurrencyString()` in [QLocale](https://doc.qt.io/qt-6/qlocale.html)).
2. `QLocale.toCurrencyString()` is wrong for a currency that is not the region's own. Measured: `QLocale("ja_JP").toCurrencyString(1099.98, "USD")` returned `"USD1,100"`, rounding US dollars to whole units, because it takes the number of decimals from the region's currency, the yen. Babel's `format_currency(1099.98, "USD", locale="ja_JP")` returned `"$1,099.98"`, and `format_currency(1099.98, "JPY", locale="de_DE")` returned `"1.100 ¥"`. Babel takes the number of decimals from the currency, as its documentation says it does (read: `format_currency`, `format_decimal` and `parse_decimal` in [babel.numbers](https://babel.pocoo.org/en/latest/api/numbers.html)). `PL-TLW6` lets the reader choose a currency other than the region's, so money must be formatted by Babel, or from CLDR's currency data, and never by `QLocale`.
3. Babel rounds a number to its locale's pattern unless told otherwise. Measured: `format_decimal(1.23456, locale="en_US")` returned `"1.235"`. The documentation says that "by default the locale is allowed to truncate and round". The number of decimals shown is a safety decision that `app/formatting.py` makes from `docs/INTERFACE.md` § "Displayed precision". So every call must pass that module's own pattern, and no default pattern may decide a clinical value's digits.
4. The SI Brochure allows the point or the comma as the decimal marker, "that which is customary in the language and context concerned" (§ 5.4.4). It says that unit symbols are "mathematical entities and not abbreviations" (§ 5.2), and that unit names are treated as ordinary nouns (§ 5.3) (full text read: [SI Brochure, 9th edition, V4.01](https://www.bipm.org/en/publications/si-brochure)). So a symbol such as mL, L/min or % stays as it is in every language, a unit's full name is translated, and the decimal marker follows the region. A German reader sees "1,5 %".
5. Typed input must be read in the same region as the display. Measured: `QLocale("en_US").toDouble("1,5")` is refused, and `QLocale("de_DE").toDouble("1,5")` returns 1.5. A `QDoubleSpinBox` prints its value with `QWidget::locale()` (read: `textFromValue()` in [QDoubleSpinBox](https://doc.qt.io/qt-6/qdoublespinbox.html)), and Babel would format every other displayed number. Qt 6.11 carries CLDR 48.2 and Babel 2.18.0 carries CLDR 47 (measured with `babel.core.get_cldr_version()`). So a test must check, for each region the app supports, that the two give the same decimal and grouping characters.
6. Files and logs never follow the region. `preferences.json`, `workspaces.json` and every stored number stay in one fixed format, so a file written in one region reads the same in another.

**3. How units fit the one Settings window of `PL-TLW6`.**

1. Apple's guidance puts general, rarely changed options in the app's own settings window, opened from the App menu's Settings item or with Command-comma. It says to choose defaults that suit most people, and to respect systemwide settings rather than repeat them (full text read: [Settings](https://developer.apple.com/design/human-interface-guidelines/settings), from the page's published data). Qt places a `QAction` whose menu role is `PreferencesRole` "where the 'Preferences...' menu item is in the application menu" on macOS (read: the `MenuRole` entry of [QAction](https://doc.qt.io/qt-6/qaction.html)).
2. CLDR states the established model for "the region gives the default, and the reader can change it" (read: § "Unit Preferences" and § "Unit Preferences Overrides" of [UTS #35 Part 6](https://www.unicode.org/reports/tr35/tr35-info.html), CLDR 49, and [`units.xml`](https://raw.githubusercontent.com/unicode-org/cldr/main/common/supplemental/units.xml)). Each kind of quantity and use has a preferred unit by region. An explicit choice of unit overrides a choice of measurement system, which overrides a chosen region, which overrides the system's region.
3. So Settings stores only what the reader changed. A unit the reader never set is read from the region at every launch, so a reader who moves region gets the new default.
4. The language of the interface follows the system, and Settings has no language choice. The system already holds that choice, and Apple's guidance says not to repeat a systemwide setting.

**4. Clinical units.**

1. A region's default is not safe for every clinical quantity. CLDR's `units.xml` gives the pound as the United States unit for a person's weight. The NCC MERP recommendation adopted 2018-10-25 says that information system screens and device screens should "list or prompt for the patient's weight in metric units only" (full text read: [Recommendations to Weigh Patients and Document Metric Weights](https://www.nccmerp.org/recommendations-weigh-patients-and-document-metric-weights-ensure-accurate-medication-dosing-adopted)). So weight, doses and drug volumes never follow the region and never appear in Settings.
2. Some clinical units do differ by region, and CLDR has data for one of them. `units.xml` gives millimoles per litre for blood glucose in 68 regions, among them GB, CA, AU and NZ, and milligrams per decilitre everywhere else.
3. CLDR has no entry for a partial pressure in blood or gas, or for an agent's concentration. The claim that blood gas tensions are reported in kPa in the United Kingdom and in mmHg in the United States has no source read in this session. A PubMed search with two wordings found nothing, and the one article that a web search found was behind a browser check. The item that first shows a partial pressure finds that source and its regional table.
4. The rule that follows: a clinical unit becomes a Settings choice only where more than one unit is in published clinical use for it. Its regional default comes from a cited table. The conversion is written once and tested. The unit is printed beside every value, as `app/display_units.py` already does.

**5. What to change now in how text and formatters are written.**

The cost of waiting grows with the text. An `ast` count on `main` at `a7eb53f` finds 1,317 string literals of more than one word outside docstrings, and 755 f-strings, in `src/anesthesia_sim/`. Not all of them are learner-facing. Five habits cost nothing to adopt now and remove most of the later rewrite:

1. Write each message a learner reads as one whole sentence with named placeholders, never as fragments joined together.
2. Write a new learner-facing message as a template filled in with `str.format`, not as an f-string.
3. Turn a number into text only in `app/formatting.py`, which is already the rule, and never with a format specification elsewhere. The count finds 34 such specifications in `app/` and 30 in `core/`.
4. Take each unit from `DisplayUnit`, as now.
5. Write a message that depends on a count as one message per count form, never as a word with "s" added.

`tests/integration/approved_interface_strings.json` holds the English text word for word. It stays the check of the English text when translations exist, run with no catalogue loaded.

**Recommendation.** Make the interface localizable with gettext for the project's text, one `QTranslator` for Qt's own text, and Babel for numbers, dates and money. Set one display region at start, from the system unless the reader changed it in Settings, and pass that one region both to `QLocale.setDefault()` for typed input and to Babel for display. Format money by its currency's own decimals with its ISO code, and pass the project's own precision patterns to every number. Keep weight and drug amounts metric whatever the region. Adopt the five habits in section 5 for new text now. Build the rest when a translation or a non-US reader is planned. None of it is part of v0.7.0. `PL-S3VQ` (mark the text for translation) and `PL-R6Y4` (format numbers and money by region) hold the two pieces of work.
