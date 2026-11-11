"""
benchmark.py
Times the real R2V pipeline (tracing + simplification) on synthetic images.
"""
import time
from PIL import Image
from synthetic_generator import generate_synthetic_raster
from tracer import mask_to_loops, vectorize
from simplifier import simplify_closed
import numpy as np


def run_benchmark():
    print("Starting R2V benchmark...")
    path = generate_synthetic_raster("test_raster.png", 1024, 768, filled=True)
    img = Image.open(path).convert("RGB")

    t = time.time()
    mask = np.asarray(img.convert("L")) < 250
    loops = mask_to_loops(mask)
    t_trace = time.time() - t

    t = time.time()
    simp = [simplify_closed(l, 1.0) for l in loops]
    t_simp = time.time() - t

    t = time.time()
    svg, stats = vectorize(img, mode="color", colors=8)
    t_full = time.time() - t

    print(f"Tracing (1 mask)    : {t_trace:.4f}s  ({len(loops)} loops, "
          f"{sum(map(len, loops))} vertices)")
    print(f"Simplification      : {t_simp:.4f}s  ({sum(map(len, simp))} vertices left)")
    print(f"Full pipeline (8 col): {t_full:.4f}s  -> {stats}")

    import os
    os.remove(path)


if __name__ == "__main__":
    run_benchmark()
