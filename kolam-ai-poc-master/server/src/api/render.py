import svgwrite
import time
from typing import Sequence, Tuple, Union

from src.api.schemas import LinePath, CurvePath

DotTuple = Tuple[float, float]

def render_kolam(
    dots: Sequence[DotTuple],
    paths: Sequence[Union[LinePath, CurvePath]]
) -> str:
    filename = f"img/{time.time()}_kolam.svg"
    dwg = svgwrite.Drawing(filename, profile="tiny")
    dwg.viewbox(0, 0, 500, 500)

    # draw dots
    for x, y in dots:
        dwg.add(dwg.circle(center=(x, y), r=3, fill="black"))

    # draw paths
    for path in paths:
        if isinstance(path, LinePath):
            dwg.add(dwg.line(
                start=(path.p1.x, path.p1.y),
                end=(path.p2.x, path.p2.y),
                stroke="blue",
                stroke_width=2
            ))
        elif isinstance(path, CurvePath):
            dwg.add(dwg.path(
                d=f"M{path.p1.x},{path.p1.y} Q{path.ctrl.x},{path.ctrl.y} {path.p2.x},{path.p2.y}",
                stroke="red",
                fill="none",
                stroke_width=2
            ))

    dwg.save()
    return filename
