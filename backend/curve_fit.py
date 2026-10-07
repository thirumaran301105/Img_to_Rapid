"""Fits long straight lines and true circular arcs to a dense path.

A drawing made of thousands of 0.3 mm MoveL steps is slow on an ABB controller (it cannot process that many
instructions per second, so the robot crawls) and the curves come out faceted. Straight runs become one MoveL and
curves become MoveC arcs, so the same shape needs a fraction of the instructions and is smoother.

Op format for one stroke: {"start": (x, y), "segs": [("L", (x, y)) | ("C", (via_x, via_y), (x, y)), ...]}
"""
import math

import numpy as np

WINDOW = 1500                     # how many points ahead to consider
STEP = 0.4                        # mm: the path is resampled this finely before fitting, so deviation is checked between vertices too
MIN_SWEEP = math.radians(6)       # flatter than this is a straight line, not an arc
MAX_SWEEP = math.radians(150)     # one MoveC never covers more than this
MIN_RADIUS = 2.0                  # mm


def circle3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-9:
        return None
    a2, b2, c2 = ax * ax + ay * ay, bx * bx + by * by, cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def _dev_line(P, i, j):
    if j - i < 2:
        return 0.0
    a, d = P[i], P[j] - P[i]
    L = math.hypot(d[0], d[1])
    q = P[i + 1:j] - a
    if L < 1e-9:
        return float(np.hypot(q[:, 0], q[:, 1]).max())
    return float((np.abs(q[:, 0] * d[1] - q[:, 1] * d[0]) / L).max())


def _arc(P, i, j, tol):
    """(mid_index, centre, radius) if P[i..j] is one clean arc, else None."""
    if j - i < 3:
        return None
    m = (i + j) // 2
    c = circle3(P[i], P[m], P[j])
    if c is None:
        return None
    (cx, cy), R = c
    if R < MIN_RADIUS or R > 5000:
        return None
    seg = P[i:j + 1]
    if np.abs(np.hypot(seg[:, 0] - cx, seg[:, 1] - cy) - R).max() > tol:
        return None
    ang = np.unwrap(np.arctan2(seg[:, 1] - cy, seg[:, 0] - cx))
    d = np.diff(ang)
    if not MIN_SWEEP <= abs(ang[-1] - ang[0]) <= MAX_SWEEP or not (np.all(d >= -1e-3) or np.all(d <= 1e-3)):
        return None
    if math.hypot(*(P[j] - P[i])) < 1.0 or math.hypot(*(P[m] - P[i])) < 0.5 or math.hypot(*(P[j] - P[m])) < 0.5:
        return None
    return m


def _longest(i, n, ok):
    """Largest j > i with ok(j), by bisection (ok(i + 1) is assumed true)."""
    hi = min(n - 1, i + WINDOW)
    if ok(hi):
        return hi
    lo = i + 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo


def _densify(P, step=STEP):
    out = [P[0]]
    for a, b in zip(P[:-1], P[1:]):
        k = max(1, int(math.ceil(math.hypot(*(b - a)) / step)))
        out += [a + (b - a) * t / k for t in range(1, k + 1)]
    return np.array(out)


def _longest_arc(P, i, n, tol):
    """(j, mid) for the longest single arc starting at i, or (i, None)."""
    lim = min(n - 1, i + WINDOW)
    lo = i + 6
    if lo > lim or _arc(P, i, lo, tol) is None:
        return i, None
    step = 6
    while lo < lim:
        nxt = min(lo + step, lim)
        if _arc(P, i, nxt, tol) is not None:
            lo, step = nxt, step * 2
            continue
        hi = nxt
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if _arc(P, i, mid, tol) is not None:
                lo = mid
            else:
                hi = mid
        break
    return lo, _arc(P, i, lo, tol)


def fit_stroke(P, tol):
    P = _densify(np.asarray(P, float))
    n = len(P)
    cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    segs, i = [], 0
    while i < n - 1:
        jl = _longest(i, n, lambda j: _dev_line(P, i, j) <= tol)
        ja, mid = (i, None) if jl >= n - 1 else _longest_arc(P, i, n, tol)
        if mid is not None and cum[ja] - cum[i] > 1.15 * (cum[jl] - cum[i]):
            segs.append(("C", tuple(np.round(P[mid], 2)), tuple(np.round(P[ja], 2))))
            i = ja
        else:
            segs.append(("L", tuple(np.round(P[jl], 2))))
            i = jl
    return {"start": tuple(np.round(P[0], 2)), "segs": segs}


def lines_to_ops(strokes):
    return [{"start": tuple(np.round(s[0], 2)), "segs": [("L", tuple(np.round(p, 2))) for p in s[1:]]} for s in strokes]


def _sample_arc(s, v, e, step=1.0):
    c = circle3(s, v, e)
    if c is None:
        return [e]
    (cx, cy), R = c
    a0, am, a1 = (math.atan2(p[1] - cy, p[0] - cx) for p in (s, v, e))
    wrap = lambda x: (x + math.pi) % (2 * math.pi) - math.pi
    d1, dm = wrap(a1 - a0), wrap(am - a0)
    if dm > 0 and d1 <= 0:
        d1 += 2 * math.pi
    elif dm < 0 and d1 >= 0:
        d1 -= 2 * math.pi
    k = max(2, int(math.ceil(abs(d1) * R / step)))
    pts = [(cx + R * math.cos(a0 + d1 * t / k), cy + R * math.sin(a0 + d1 * t / k)) for t in range(1, k)]
    return pts + [e]


def ops_to_polyline(op, step=1.0):
    pts, cur = [op["start"]], op["start"]
    for sg in op["segs"]:
        if sg[0] == "L":
            pts.append(sg[1]); cur = sg[1]
        else:
            pts += _sample_arc(cur, sg[1], sg[2], step); cur = sg[2]
    return np.array(pts, float)
