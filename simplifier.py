"""
simplifier.py
Path simplification for raster-to-vector conversion (Douglas-Peucker).
"""
import numpy as np


def rdp(points, tolerance=1.0):
    """Douglas-Peucker on an OPEN polyline (iterative, no recursion limit)."""
    pts = np.asarray(points, dtype=float)
    n = len(pts)
    if n < 3:
        return [tuple(p) for p in pts.tolist()]
    keep = np.zeros(n, dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        seg = pts[b] - pts[a]
        rel = pts[a + 1:b] - pts[a]
        length = np.hypot(seg[0], seg[1])
        if length == 0:
            d = np.hypot(rel[:, 0], rel[:, 1])
        else:
            d = np.abs(seg[0] * rel[:, 1] - seg[1] * rel[:, 0]) / length
        i = int(np.argmax(d))
        if d[i] > tolerance:
            k = a + 1 + i
            keep[k] = True
            stack.append((a, k))
            stack.append((k, b))
    return [tuple(p) for p in pts[keep].tolist()]


def simplify_closed(points, tolerance=1.0):
    """Douglas-Peucker for a CLOSED loop: split at the point farthest from
    the first vertex so both halves are well-conditioned."""
    n = len(points)
    if n < 4:
        return list(points)
    pts = np.asarray(points, dtype=float)
    j = int(np.argmax(np.hypot(*(pts - pts[0]).T)))
    first = rdp(pts[:j + 1], tolerance)
    second = rdp(np.vstack([pts[j:], pts[:1]]), tolerance)
    return first[:-1] + second[:-1]


def simplify_paths(paths, tolerance=1.0):
    """Simplify a list of open paths."""
    return [rdp(p, tolerance) if len(p) > 2 else list(p) for p in paths]


if __name__ == "__main__":
    sample = [(0, 0), (1, 0.1), (2, -0.1), (3, 0), (4, 4)]
    print("Original  :", sample)
    print("Simplified:", simplify_paths([sample], tolerance=0.5))
