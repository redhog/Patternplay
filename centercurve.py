import math
from svgpathtools import *
from numpy import *
import approximate_bezier

def _intersectionsort(i):
    ((T1, seg1, t1), (T2, seg2, t2)) = i
    return T2
def sort_intersections(intersections):
    return sorted(intersections, key=_intersectionsort)

def collapse_close_intersections(intersections):
    intersections = sort_intersections(intersections)
    out = []
    for i in range(0, len(intersections)):
        if out and misctools.isclose(out[-1][1][0], intersections[i][1][0]):
            continue
        out.append(intersections[i])
    return out

def centerline(P, resolution=10):
    lines = []
    res = []
    respath = []
    respoint = None
    for T in linspace(0, 1, len(P) * resolution):
        p = P.point(T)
        n = P.normal(T)
        l = Line(p - n * 1e-10, p + n*200)
        lines.append(l)
        intersections = collapse_close_intersections(P.intersect(l))
        if len(intersections) < 2:
            continue
        ((T1, seg1, t1), (T2, seg2, t2)) = intersections[1]
        if T1 < T:
            respoint = None
            if respath:
                res.append(Path(*respath))
            respath = []
            continue
        centerp = (p + P.point(T1)) / 2
        if respoint is not None:
            s = Line(respoint, centerp)
            if P.intersect(s):
                respoint = None
                if respath:
                    res.append(Path(*respath))
                respath = []
                continue
            respath.append(s)
        respoint = centerp
    if respath:
        res.append(Path(*respath))
    return res


def centercurve(P, resolution=10, smoothing=0.3):
    return [
        approximate_bezier.approximate_bezier(
            [l[0].start] + [s.end for s in l],
            smoothing=smoothing)
        for l in centerline(P, resolution)]
