from pydantic import BaseModel
from typing import Literal, Union

class Dot(BaseModel):
    x: float
    y: float

class LinePath(BaseModel):
    type: Literal["line"] = "line"
    p1: Dot
    p2: Dot

class CurvePath(BaseModel):
    type: Literal["curve"] = "curve"
    p1: Dot
    ctrl: Dot
    p2: Dot

Path = Union[LinePath, CurvePath]

class KolamRequest(BaseModel):
    dots: list[Dot]
    paths: list[Path]
