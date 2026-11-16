"""
simplifier.py
Polygon simplification methods used by the R2V benchmark.
"""
import heapq

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
    """Douglas-Peucker for a CLOSED loop."""
    n = len(points)
    if n < 4:
        return list(points)
    pts = np.asarray(points, dtype=float)
    j = int(np.argmax(np.hypot(*(pts - pts[0]).T)))
    first = rdp(pts[:j + 1], tolerance)
    second = rdp(np.vstack([pts[j:], pts[:1]]), tolerance)
    return first[:-1] + second[:-1]


def visvalingam_closed(points, area_threshold=1.0):
    """Simplify a closed loop using Visvalingam-Whyatt triangle areas.

    Vertices are removed in ascending effective-area order while their local
    triangle area is at most ``area_threshold``. At least three vertices are
    retained. The input loop is expected not to repeat its first point at the
    end, matching ``tracer.mask_to_loops`` output.
    """
    pts = [tuple(point) for point in points]
    n = len(pts)
    if n <= 3:
        return pts

    previous = [(i - 1) % n for i in range(n)]
    following = [(i + 1) % n for i in range(n)]
    alive = [True] * n
    versions = [0] * n
    heap = []

    def triangle_area(i):
        a, b, c = pts[previous[i]], pts[i], pts[following[i]]
        return abs((a[0] - c[0]) * (b[1] - a[1]) -
                   (a[0] - b[0]) * (c[1] - a[1])) / 2.0

    for i in range(n):
        heapq.heappush(heap, (triangle_area(i), i, versions[i]))

    remaining = n
    while remaining > 3 and heap:
        area, i, version = heapq.heappop(heap)
        if not alive[i] or version != versions[i]:
            continue
        if area > area_threshold:
            break

        left, right = previous[i], following[i]
        alive[i] = False
        following[left] = right
        previous[right] = left
        remaining -= 1

        for neighbor in (left, right):
            versions[neighbor] += 1
            heapq.heappush(
                heap, (triangle_area(neighbor), neighbor, versions[neighbor])
            )

    start = next(i for i, is_alive in enumerate(alive) if is_alive)
    result = []
    current = start
    while True:
        result.append(pts[current])
        current = following[current]
        if current == start:
            break
    return result


def simplify_paths(paths, tolerance=1.0):
    """Simplify a list of open paths with Douglas-Peucker."""
    return [rdp(path, tolerance) if len(path) > 2 else list(path) for path in paths]


if __name__ == "__main__":
    sample = [(0, 0), (1, 0.1), (2, -0.1), (3, 0), (4, 4)]
    print("Original  :", sample)
    print("Simplified:", simplify_paths([sample], tolerance=0.5))
