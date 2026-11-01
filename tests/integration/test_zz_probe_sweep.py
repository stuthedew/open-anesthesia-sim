from __future__ import annotations

from PySide6.QtWidgets import QApplication, QWidget

from anesthesia_sim.layout.tree import Area, AreaId, areas_in
from tests.integration.test_layout_adapter import (
    _BIG,
    _column,
    _host_sized,
    _layout,
    _row,
    _splitters,
    _VIEW,
    application,  # noqa: F401
    hosts,  # noqa: F401
)


def _big(n: int) -> Area:
    return Area(AreaId(n), _BIG)


def _small(n: int) -> Area:
    return Area(AreaId(n), _VIEW)


_LAYOUTS = {
    "col2": (_column((0.5, 0.5), _big(1), _big(2)), 3),
    "col2_skew": (_column((0.8, 0.2), _big(1), _big(2)), 3),
    "col3": (_column((0.4, 0.3, 0.3), _big(1), _big(2), _big(3)), 4),
    "col_of_rows": (_column((0.5, 0.5), _row((0.5, 0.5), _big(1), _big(2)), _row((0.3, 0.7), _big(3), _big(4))), 5),
    "row_of_cols": (_row((0.6, 0.4), _column((0.5, 0.5), _big(1), _big(2)), _column((0.7, 0.3), _big(3), _small(4))), 5),
    "col_row_col": (_column((0.7, 0.3), _row((0.6, 0.4), _column((0.5, 0.5), _big(1), _big(2)), _big(3)), _big(4)), 5),
}


def test_probe_sweep(application, hosts) -> None:
    problems = []
    for name, (tree, nid) in _LAYOUTS.items():
        model = _layout(tree, nid)
        for w in (180, 260, 340, 420, 520, 640, 800, 1000):
            for h in (180, 240, 300, 360, 420, 480, 560, 700):
                host, c = _host_sized(application, hosts, model, (w, h))
                fit = c._fit
                least = c.minimumSizeHint()
                ts = tuple(e.area_id for e in fit.too_small)
                # stability of repeated settles
                seen = [ts]
                for _ in range(3):
                    c._settle(c._drawn)
                    application.processEvents()
                    seen.append(tuple(e.area_id for e in c._fit.too_small))
                if len(set(seen)) > 1:
                    problems.append((name, w, h, "unstable", seen))
                fit = c._fit
                for area in areas_in(tree):
                    f = c.frame(area.id)
                    b = fit.bounds[area.id]
                    if (f.minimumWidth(), f.minimumHeight()) != (b.width_px, b.height_px):
                        problems.append((name, w, h, "minsize", area.id, f.minimumSize().toTuple(), b))
                    n = f.too_small_notice
                    if area.id in {e.area_id for e in fit.too_small} and n is not None and n.isVisible():
                        frame_ok = f.height() >= f.minimumHeight() and f.width() >= f.minimumWidth()
                        for lab in (n.title_label, n.body_label):
                            if lab.height() < lab.heightForWidth(lab.width()):
                                problems.append((name, w, h, "clipped", area.id, lab.objectName() or lab.text()[:20],
                                                 lab.size().toTuple(), lab.heightForWidth(lab.width()),
                                                 "frame", f.size().toTuple(), "min", f.minimumSize().toTuple(),
                                                 "fitarea", fit.apportionment.areas[area.id], "frame_ok", frame_ok,
                                                 "win_ok", w >= least.width() and h >= least.height()))
                host.close()
    for p in problems:
        print("PROBLEM", p)
    print("COUNT", len(problems))
