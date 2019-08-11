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

def slices(segments):
    """Returns list of slices through a path. Each slice is defined by two points on the path, where a line connects.
       Returns list of intersectionpairs:
       (((Tpath1, segpath1, tpath1), (Tline1, segline1, tline1)),
        ((Tpath2, segpath2, tpath2), (Tline2, segline2, tline2)))
    """
    b = segments.bbox()
    size = math.sqrt((b[1]-b[0])**2+(b[3]-b[2])**2)

    normals = [Line(s.point(i)-s.normal(i)*1e-15, s.point(i)+size*s.normal(i))
               for s in segments
               for i in (1e-20, .5)]

    # Normals are not defined at t = 0 and t=1!!! Hack around...
    intersections = [(collapse_close_intersections(segments.intersect(normal)), normal) for normal in normals]
    groupedintersectionpairs = [[(intersectionline[0], intersectionline[1], normal)]
                                for intersectionline, normal in intersections
                                if len(intersectionline) >= 2]    
    
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

    filtered = []
    for entry in sorted(centerpoints, key=lambda entry: entry[2].real):
        if not path.path_encloses_pt(entry[2], b[0]+1j*b[2]-1-1j, full):
            continue
        if filtered and misctools.isclose(filtered[-1][2], entry[2]):
            continue
        filtered.append(entry)
    return filtered

def ordered_centerpoints(segments):
    points = centerpoints(segments)

    dmean = array([d for d, i, p in points]).mean()
    dstd = array([d for d, i, p in points]).std()

    orderedcenterpoints = sorted(
        [(i[0][0][0], d, i, p) for d, i, p in points]
        + [(i[1][0][0], d, i, p) for d, i, p in points],
        key = lambda a: a[0])

    clusters = []
    cluster = []
    for T, d, i, p in orderedcenterpoints:
        if d > dmean - dstd:
            if cluster:
                clusters.append(cluster)
                cluster = []
        else:
            cluster.append((T, d, i, p))
    if cluster:
        clusters.append(cluster)
        cluster = []

    clusters = sorted([array([T for T, d, i, p in cluster]).mean() for cluster in clusters])
    first = clusters[0]
    last = clusters[1]
    if last - first < .5:
        first, last = last, first

    if first < last:
        orderedcenterpointsnocopies = [(L, d, i, p) for (L, d, i, p) in orderedcenterpoints
                                       if L >= first and L <=last]
    else:
        orderedcenterpointsnocopies = ([(L, d, i, p)
                                        for (L, d, i, p) in orderedcenterpoints
                                        if L >= first] +
                                       [(L, d, i, p)
                                        for (L, d, i, p) in orderedcenterpoints
                                        if L <= last])
    return orderedcenterpointsnocopies


def centerline(segments):
    orderedcenterpointsnocopies = ordered_centerpoints(segments)
    return Path(*(Line(orderedcenterpointsnocopies[i][3], orderedcenterpointsnocopies[i-1][3])
                  for i in range(1, len(orderedcenterpointsnocopies))))

def centercurve(segments, smoothing=0.3):
    orderedcenterpointsnocopies = ordered_centerpoints(segments)

    points = [p[3] for p in orderedcenterpointsnocopies]

    return approximate_bezier.approximate_bezier(points, smoothing=smoothing)
