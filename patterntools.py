from svgpathtools import *
from numpy import *
import IPython.display

def displaysvg(*arg, **kw):
    if "filename" not in kw:
        kw["filename"]="test.svg"
    wsvg(*arg, **kw)
    with open(kw["filename"], "rb") as f:
        data = f.read()
    IPython.display.display(IPython.display.SVG(data=data))
    
def marker(point, size=1):
    return path.bbox2path(point.real-size, point.real+size, point.imag-size, point.imag+size)
