from svgpathtools import *
from numpy import *
import IPython.display
import struct
import hashlib
import numpy

def displaysvg(*arg, **kw):
    if "filename" not in kw:
        kw["filename"]="test.svg"
    wsvg(*arg, **kw)
    with open(kw["filename"], "rb") as f:
        data = f.read()
    IPython.display.display(IPython.display.SVG(data=data))
    
def marker(point, size=1):
    return path.bbox2path(point.real-size, point.real+size, point.imag-size, point.imag+size)

def nonlinspace(l, u, n, init=b''):
    maxuint = struct.unpack(">I", b"\xff\xff\xff\xff")[0]
    m = hashlib.md5()
    m.update(init)
    res = numpy.zeros(n)
    for i in range(0, n):
        m.update(b'\0')
        res[i] = l + (u-l) * float(struct.unpack(">I", m.digest()[:4])[0]) / maxuint
    return sort(res)
