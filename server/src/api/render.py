import svgwrite
import time
from typing import Sequence, Tuple, Union

from src.api.schemas import LinePath, CurvePath, Dot

DotTuple = Tuple[float, float]

def render_kolam(
    dots: Sequence[DotTuple],
    paths: Sequence[Union[LinePath, CurvePath]]
) -> str:
    """
    Renders the Kolam as an SVG with black dots and black lines/curves.
    """
    filename = f"img/{time.time()}_kolam.svg"
    dwg = svgwrite.Drawing(filename, profile="tiny")
    dwg.viewbox(0, 0, 500, 500)

    print(f"Rendering {len(dots)} dots and {len(paths)} paths to {filename}")

    # draw dots (already black)
    for x, y in dots:
        dwg.add(dwg.circle(center=(x, y), r=3, fill="black"))

    # draw paths (updated to black stroke)
    for path in paths:
        if isinstance(path, LinePath):
            dwg.add(dwg.line(
                start=(path.p1.x, path.p1.y),
                end=(path.p2.x, path.p2.y),
                stroke="black",  # CHANGED from "blue" to "black"
                stroke_width=2
            ))
        elif isinstance(path, CurvePath):
            dwg.add(dwg.path(
                d=f"M{path.p1.x},{path.p1.y} Q{path.ctrl.x},{path.ctrl.y} {path.p2.x},{path.p2.y}",
                stroke="black",  # CHANGED from "red" to "black"
                fill="none",
                stroke_width=2
            ))

    dwg.save()
    return filename

def reconstruct_paths(path_data):
    paths = []
    for path in path_data:
        if path["type"] == "line":
            paths.append(LinePath(
                p1=Dot(**path["p1"]),
                p2=Dot(**path["p2"])
            ))
        elif path["type"] == "curve":
            paths.append(CurvePath(
                p1=Dot(**path["p1"]),
                ctrl=Dot(**path["ctrl"]),
                p2=Dot(**path["p2"])
            ))
    return paths