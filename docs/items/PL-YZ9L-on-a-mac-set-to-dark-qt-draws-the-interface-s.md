---
id: PL-YZ9L
title: On a Mac set to Dark, Qt draws the interface's lettering heavier than under Light, though the interface declares light colours
status: untriaged
added: 2026-11-11
---

**Problem.** On a Mac set to the Dark appearance, the interface's lettering
is drawn slightly heavier than under Light. The interface declares its own
light colours whatever the host is set to (`PL-KRZW`), so its lettering is
dark on a light surface under both appearances and should be drawn the same.

**Evidence.** `PL-BVC5`'s comparison window, run on the owner's Mac on
2026-11-11, recorded the same five buttons under Light and under Dark. 960
pixels differed across the five buttons, with a largest colour step of 72 of
255. Every differing pixel was in the lettering, and the buttons drawn
without lettering were identical. A style sheet's buttons and a custom
style's buttons differed in the same way.

**Cause, read from Qt's source.** `QCoreTextFontEngine::imageForGlyph`
(`src/gui/text/coretext/qfontengine_coretext.mm`, tag `v6.11.0`, read on
2026-11-11) draws each letter with a black fill unless the platform's colour
scheme is Dark, and with a white fill when it is. Its comment says that
macOS's font smoothing "adjusts its dilation (stem darkening) parameters
based on the fill color". Qt chooses the fill by the host's appearance, and
the interface's surfaces do not follow that appearance.

**Not yet known.** Whether the difference can be seen at life size, and
whether it changes how a value reads. The measurement was at one device
pixel per pixel, enlarged four times.

**One route to try.** Tell Qt or macOS that this application's appearance
is Light, so that the text drawing agrees with the declared colours.
`qt_widgets.declare_application_colours` records that
`styleHints().setColorScheme` was ignored on 2026-09-20 in the container.
Nobody has tried it on a Mac.
