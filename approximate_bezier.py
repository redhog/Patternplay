# Basic algorithm from
# https://medium.com/@francoisromain/smooth-a-svg-path-with-cubic-bezier-curves-e37b49d46c74

import math
from svgpathtools import * 
from numpy import *

def line_to_magnitude_angle(a, b):
    dx = b.real - a.real
    dy = b.imag - a.imag
    return math.sqrt(dx**2 + dy**2), math.atan2(dy, dx)

def control_point(current, previous, nxt, reverse=False, smoothing = 0.1):
    """Position of a control point 
    current: current point coordinates
    previous: previous point coordinates
    nxt: next point coordinates
    reverse: sets the direction
    smoothing: smoothing ratio
    returns control point coordinates
    """
    # When 'current' is the first or last point of the array
    # 'previous' or 'next' don't exist.
    # Replace with 'current'
    p = previous
    n = nxt
    if p is None: p = current
    if n is None: n = current
    # Properties of the opposed-line
    magnitude, angle = line_to_magnitude_angle(p, n)
    # If is end-control-point, add PI to the angle to go backward
    angle = angle + (pi if reverse else 0)
    magnitude = magnitude * smoothing
    # The control point position is relative to the current point
    x = current.real + cos(angle) * magnitude
    y = current.imag + sin(angle) * magnitude
    return x+1j*y

def bezier_segment(i, a, smoothing):
    """Create a single bezier curve segment
    i: index of current point in the array
    a: array of point coordinates
    returns 'C x2,y2 x1,y1 x,y': SVG cubic bezier
    """
    ap2 = a[i-2] if i >= 2 else None
    ap1 = a[i-1] if i >= 1 else None
    point = a[i]
    an1 = a[i+1] if i+1 <= len(a) else None
    start_control_point = control_point(ap1, ap2, point, smoothing=smoothing)
    end_control_point = control_point(point, ap1, an1, True, smoothing=smoothing)
    return "C " + " ".join("%s,%s" % (p.real, p.imag)
                           for p in (start_control_point, end_control_point, point))

def approximate_bezier(points, smoothing=0.1):
    return parse_path(
        ("M %s,%s " % (points[0].real, points[0].imag))
        + " ".join(bezier_segment(i, points, smoothing=.5)
                   for i in range(1, len(points)-1)))
