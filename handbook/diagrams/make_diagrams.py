#!/usr/bin/env python3
"""Generate every diagram as an SVG file in diagrams/svg/.

    python3 make_diagrams.py            # write all SVGs
    python3 make_diagrams.py --sheet    # also write build/diagram_sheet.pdf for a visual check
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import figs_a  # noqa: E402
import figs_b  # noqa: E402

OUT = HERE / "svg"


def main():
    OUT.mkdir(exist_ok=True)
    registry = {**figs_a.REGISTRY, **figs_b.REGISTRY}
    for name, fn in registry.items():
        fn().save(OUT / f"{name}.svg")
    print(f"wrote {len(registry)} diagrams to {OUT}")
    if "--sheet" in sys.argv:
        from weasyprint import HTML
        build = HERE.parent / "build"
        build.mkdir(exist_ok=True)
        parts = []
        for name in registry:
            svg = (OUT / f"{name}.svg").read_text(encoding="utf-8")
            parts.append(f'<div style="break-inside: avoid; margin-bottom: 8mm"><p style="font: 9pt sans-serif">'
                         f'{name}</p><div style="width: 176mm">{svg}</div></div>')
        css = "@page { size: A4; margin: 15mm 17mm } svg { width: 100%; height: auto }"
        html = f"<html><head><style>{css}</style></head><body>{''.join(parts)}</body></html>"
        HTML(string=html, base_url=str(HERE.parent)).write_pdf(str(build / "diagram_sheet.pdf"))
        print("wrote", build / "diagram_sheet.pdf")


if __name__ == "__main__":
    main()
