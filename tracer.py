"""
tracer.py
Raster -> vector (SVG) conversion.

Pipeline:
  1. (optional) downscale
  2. colour quantisation (median cut) or black/white threshold
  3. for every colour layer: exact pixel-edge boundary tracing -> closed loops
  4. Douglas-Peucker simplification of every loop
  5. SVG output with source transparency (optionally smoothed with quadratic curves)
"""
import numpy as np
from PIL import Image
from simplifier import simplify_closed

# directions in screen coordinates (y down), clockwise: E, S, W, N
_DX = (1, 0, -1, 0)
_DY = (0, 1, 0, -1)


def mask_to_loops(mask):
    """Trace the outlines of a boolean mask.

    Returns a list of closed loops [(x, y), ...] in pixel-corner coordinates.
    Outer boundaries run clockwise, holes counter-clockwise, so a single path
    with fill-rule="evenodd" renders holes correctly.
    """
    m = np.pad(mask.astype(bool), 1)
    f = m[1:-1, 1:-1]
    up, down = m[:-2, 1:-1], m[2:, 1:-1]
    left, right = m[1:-1, :-2], m[1:-1, 2:]

    out = {}  # start vertex -> list of outgoing directions still unused

    def add(sel, dx, dy, d):
        rs, cs = np.nonzero(sel)
        for x, y in zip((cs + dx).tolist(), (rs + dy).tolist()):
            out.setdefault((x, y), []).append(d)

    add(f & ~up,    0, 0, 0)  # top edge,    heading east
    add(f & ~right, 1, 0, 1)  # right edge,  heading south
    add(f & ~down,  1, 1, 2)  # bottom edge, heading west
    add(f & ~left,  0, 1, 3)  # left edge,   heading north

    loops = []
    while out:
        start = next(iter(out))
        cur, pd = start, None
        pts = []
        while True:
            dirs = out[cur]
            if pd is None or len(dirs) == 1:
                nd = dirs[0]
            else:  # pinch point: prefer right turn, then straight, then left
                nd = next(d for d in ((pd + 1) % 4, pd, (pd - 1) % 4) if d in dirs)
            dirs.remove(nd)
            if not dirs:
                del out[cur]
            if nd != pd:
                pts.append(cur)
            pd = nd
            cur = (cur[0] + _DX[nd], cur[1] + _DY[nd])
            if cur == start:
                break
        loops.append(pts)
    return loops


def _area(pts):
    a = np.asarray(pts, dtype=float)
    x, y = a[:, 0], a[:, 1]
    return abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2


def _fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def loop_to_d(pts, smooth=False):
    n = len(pts)
    if not smooth or n < 3:
        return "M" + " L".join(f"{_fmt(x)} {_fmt(y)}" for x, y in pts) + "Z"
    mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    sx, sy = mid(pts[-1], pts[0])
    d = [f"M{_fmt(sx)} {_fmt(sy)}"]
    for i in range(n):
        mx, my = mid(pts[i], pts[(i + 1) % n])
        d.append(f"Q{_fmt(pts[i][0])} {_fmt(pts[i][1])} {_fmt(mx)} {_fmt(my)}")
    return "".join(d) + "Z"


def vectorize(img, mode="color", colors=64, threshold=128, tolerance=0.0,
              min_area=0, smooth=False, max_dim=2000):
    """Convert a PIL image to an SVG string. Returns (svg, stats)."""
    img = img.convert("RGBA")
    ow, oh = img.size
    if max(img.size) > max_dim:
        s = max_dim / max(img.size)
        img = (img.convert("RGBa")
               .resize((max(1, round(ow * s)), max(1, round(oh * s))),
                       Image.Resampling.LANCZOS)
               .convert("RGBA"))
    w, h = img.size
    rgba = np.asarray(img)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]
    visible = alpha > 0

    if mode == "bw":
        gray = np.asarray(img.convert("L"))
        foreground = gray < threshold
        layers = []
        for color, color_mask in (
            ("#000000", foreground),
            ("#ffffff", ~foreground),
        ):
            color_mask &= visible
            layers.extend(
                (color, int(a) / 255, color_mask & (alpha == a))
                for a in np.unique(alpha[color_mask])
            )
        background = None
    else:
        colors = int(max(2, min(64, colors)))
        rgb_for_quantization = rgb.copy()
        if np.any(~visible):
            visible_pixels = rgb[visible]
            if len(visible_pixels):
                rgb_for_quantization[~visible] = visible_pixels[0]
        rgb_image = Image.fromarray(rgb_for_quantization)
        q = rgb_image.quantize(
            colors=colors,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.NONE,
        )
        idx = np.asarray(q)
        pal = q.getpalette()
        n = len(pal) // 3
        counts = np.bincount(idx[visible], minlength=n)
        hexes = ["#%02x%02x%02x" % tuple(pal[i * 3:i * 3 + 3]) for i in range(n)]
        layers = []
        for i in np.flatnonzero(counts):
            color_mask = (idx == i) & visible
            layers.extend(
                (hexes[i], int(a) / 255, color_mask & (alpha == a))
                for a in np.unique(alpha[color_mask])
            )
        background = None

    parts, n_paths, n_points = [], 0, 0
    for color, opacity, mask in layers:
        d_parts = []
        for loop in mask_to_loops(mask):
            if len(loop) < 3 or _area(loop) < min_area:
                continue
            simp = simplify_closed(loop, tolerance)
            if len(simp) < 3:
                continue
            d_parts.append(loop_to_d(simp, smooth))
            n_points += len(simp)
        if d_parts:
            n_paths += len(d_parts)
            opacity_text = f"{opacity:.6f}".rstrip("0").rstrip(".")
            opacity_attr = f' fill-opacity="{opacity_text}"' if opacity < 1 else ""
            parts.append(
                f'<path fill="{color}"{opacity_attr} fill-rule="evenodd" '
                f'd="{"".join(d_parts)}"/>'
            )

    background_rect = (
        f'<rect width="{w}" height="{h}" fill="{background}"/>'
        if background is not None else ""
    )
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ow}" height="{oh}" '
           f'viewBox="0 0 {w} {h}">'
           + background_rect + "".join(parts) + "</svg>")
    return svg, {"width": ow, "height": oh, "layers": len(parts),
                 "paths": n_paths, "points": n_points, "svg_bytes": len(svg)}
