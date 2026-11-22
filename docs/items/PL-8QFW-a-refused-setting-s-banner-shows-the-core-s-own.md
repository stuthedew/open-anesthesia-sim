---
id: PL-8QFW
title: A refused setting's banner shows the core's own message, so a learner reads the setting by its Python name, as in 'Setting refused — delivered_concentration_percent exceeds the vaporizer maximum (50% requested, 5% maximum)'
status: untriaged
added: 2026-11-22
---

**Problem.** A refused setting's banner shows the core's own message, so a learner reads the setting by its Python name, as in 'Setting refused — delivered_concentration_percent exceeds the vaporizer maximum (50% requested, 5% maximum)'

**Found on 2026-11-22** while extending the approved-wording test to the states only an event brings up (`PL-4G79`). With isoflurane running, the delivered concentration handler given 50% shows this banner:

"Setting refused — delivered_concentration_percent exceeds the vaporizer maximum (50% requested, 5% maximum). The simulation is unchanged and still running its previous setting."

`refused_setting_notice` in `app/dashboard_frame.py` formats `REFUSED_SETTING_TEMPLATE` with the `SimulationConfigurationError` itself, and `core/validation.py` writes that message with the parameter's Python name, for a developer. `.claude/rules/plain-writing.md` says a string a learner reads holds no software term.

**Why it matters.** The banner is conditional text that a learner acts on. "delivered_concentration_percent" is readable, but it is a code name, and other settings' names may be less so. The value and the limit in the message are correct.

**Done when.** The banner names the setting in the learner's words (the dial's own label), and keeps the value and the limit. The developer's message stays available in the log or the exception. The approved-wording list records the new banner.
