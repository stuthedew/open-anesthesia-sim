---
id: PL-R6Y4
title: Format numbers and money by the reader's region through Babel, with the precision table's own patterns and typed input read in the same region
status: untriaged
feature: localization
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/main.py
added: 2026-11-22
---

**Problem.** Format numbers and money by the reader's region through Babel, with the precision table's own patterns and typed input read in the same region

`PL-SRP7` (the localization research) § 2 has the sources and the measurements behind this item.

**Scope.**

1. Set one display region at start: the system's region, unless the reader changed it in the Settings window of `PL-TLW6`. Pass that one region to `QLocale.setDefault()`, so that spin boxes read and print typed values in it, and to Babel, which `app/formatting.py` uses for every displayed number. A German reader then sees "1,5 %".
2. Pass the module's own pattern from its precision table to every Babel call. Measured on 2026-11-22: `format_decimal(1.23456, locale="en_US")` returned `"1.235"` on Babel's default pattern, so a default would decide a clinical value's digits.
3. Format money with Babel's `format_currency`, which takes the number of decimals from the currency, and show the currency's ISO code. Never use `QLocale.toCurrencyString()`. Measured on 2026-11-22 with PySide6 6.11.2: `QLocale("ja_JP").toCurrencyString(1099.98, "USD")` returned `"USD1,100"`. `PL-7R8S` (cost shown as money to the cent) holds the same rule.
4. Add a test that, for each region the app supports, Qt and Babel give the same decimal and grouping characters. Qt 6.11 carries CLDR 48.2 and Babel 2.18.0 carries CLDR 47.
5. Keep every stored file and log in one fixed number format, whatever the region.
6. Never let the region choose the unit of a patient's weight or of a drug amount. These stay metric, as the NCC MERP recommendation adopted 2018-10-25 says.

**Dependency.** Babel is a new runtime dependency. It is pure Python and carries its own copy of the CLDR data.

**Not in v0.7.0.** The owner said on 2026-11-22 that localization need not be built now (project owner, 2026-11-22).

**Generator check.** A one-off: planned work that the localization research (`PL-SRP7`) recommends, not a cause of other items.
