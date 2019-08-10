import math
from svgpathtools import *
from numpy import *

def slices(segments):
    """Returns list of slices through a path. Each slice is defined by two points on the path, where a line connects.
       Returns list of intersectionpairs:
       (((Tpath1, segpath1, tpath1), (Tline1, segline1, tline1)),
        ((Tpath2, segpath2, tpath2), (Tline2, segline2, tline2)))
    """
    b = segments.bbox()
    size = math.sqrt((b[1]-b[0])**2+(b[3]-b[2])**2)

    normals = [Line(s.point(i)+size*s.normal(i), s.point(i)-size*s.normal(i))
               for s in segments
               for i in linspace(1e-20, 1-1e-16, 3)]

    # Normals are not defined at t = 0 and t=1!!! Hack around...
    def intersectionsort(i):
        ((T1, seg1, t1), (T2, seg2, t2)) = i
        return T2
    intersections = [sorted(segments.intersect(normal), key=intersectionsort) for normal in normals]
    groupedintersectionpairs = [[(intersectionline[i*2], intersectionline[i*2+1])
                                 for i in range(len(intersectionline)//2)]
                                for intersectionline in intersections]
    return [intersectionpair
            for group in groupedintersectionpairs
            for intersectionpair in group]

def centerpoints(segments):

    """Calculates a list of center points inside a shape as well as a
       likeliehood for each point of being at the end of the shape (a
       corner). Returns list of:
       (distance, intersectionpair, centerpoint_coord)
       where distance is in ]0,1[, and close to 0 means corner
    """
    intersectionpairs = slices(segments)
    
    def distance(a, b):
        return math.sqrt((sin(a*2*pi) - sin(b*2*pi))**2 + (cos(a*2*pi) - cos(b*2*pi))**2)/2

    intersectionpairswithdistance = sorted([(distance(intersectionpair[0][0][0], intersectionpair[1][0][0]), intersectionpair)
                                            for intersectionpair in intersectionpairs],
                                           key=lambda p: p[0])

    centerpoints = [(distance,
                     intersectionpair,
                     (segments.point(intersectionpair[0][0][0])
                      + segments.point(intersectionpair[1][0][0])) / 2)
                    for distance, intersectionpair in intersectionpairswithdistance]

    full = Path(*segments)
    if not full.isclosed():
        full.append(Line(full.end, full.start))

    b = segments.bbox()

    return [(d, i, p) for (d, i, p) in centerpoints
            if path.path_encloses_pt(p, b[0]+1j*b[2]-1-1j, full)]
