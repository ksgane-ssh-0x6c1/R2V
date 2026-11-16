"""Compare polygon simplification methods on identical traced contours.

Run with ``python benchmark.py``. Results are written to results/ as JSON and CSV.
"""
import csv
import json
import random
import statistics
import time
from pathlib import Path

import numpy as np
from PIL import Image

from simplifier import simplify_closed, visvalingam_closed
from synthetic_generator import generate_synthetic_raster
from tracer import mask_to_loops


OUTPUT_DIR = Path("results")
WIDTH, HEIGHT = 1024, 768
REPEATS = 5
RDP_TOLERANCE = 1.0
VISVALINGAM_AREA_THRESHOLD = 1.0


def run_benchmark():
    """Run each simplifier on exactly the same synthetic contour set."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    random.seed(0)

    image_path = OUTPUT_DIR / "benchmark_input.png"
    generate_synthetic_raster(str(image_path), WIDTH, HEIGHT, filled=True)
    with Image.open(image_path) as source:
        image = source.convert("RGB")
    mask = np.asarray(image.convert("L")) < 250

    trace_start = time.perf_counter()
    loops = mask_to_loops(mask)
    trace_seconds = time.perf_counter() - trace_start
    input_vertices = sum(len(loop) for loop in loops)

    methods = {
        "no_simplification": lambda loop: list(loop),
        "douglas_peucker": lambda loop: simplify_closed(loop, RDP_TOLERANCE),
        "visvalingam_whyatt": lambda loop: visvalingam_closed(
            loop, VISVALINGAM_AREA_THRESHOLD
        ),
    }
    parameters = {
        "no_simplification": {},
        "douglas_peucker": {"distance_tolerance_pixels": RDP_TOLERANCE},
        "visvalingam_whyatt": {
            "triangle_area_threshold_pixels_squared": VISVALINGAM_AREA_THRESHOLD
        },
    }

    rows = []
    for name, simplify in methods.items():
        run_times = []
        output_vertices = 0
        for _ in range(REPEATS):
            start = time.perf_counter()
            simplified = [simplify(loop) for loop in loops]
            run_times.append(time.perf_counter() - start)
            output_vertices = sum(len(loop) for loop in simplified)

        reduction = (
            100.0 * (input_vertices - output_vertices) / input_vertices
            if input_vertices else 0.0
        )
        rows.append({
            "algorithm": name,
            "parameters": parameters[name],
            "median_simplification_seconds": statistics.median(run_times),
            "input_loops": len(loops),
            "input_vertices": input_vertices,
            "output_vertices": output_vertices,
            "vertex_reduction_percent": reduction,
            "runs": REPEATS,
        })

    report = {
        "project": "R2V",
        "benchmark": "closed_contour_simplification",
        "dataset": {
            "name": "seeded_synthetic_raster",
            "seed": 0,
            "width": WIDTH,
            "height": HEIGHT,
            "loops": len(loops),
            "vertices": input_vertices,
        },
        "protocol": {
            "repeats": REPEATS,
            "reported_timing": "median wall-clock time; tracing is shared and excluded from per-algorithm timings",
            "trace_seconds": trace_seconds,
        },
        "results": rows,
        "caveat": "This initial benchmark reports runtime and vertex reduction, not geometric fidelity. Do not interpret it as a quality ranking.",
    }

    json_path = OUTPUT_DIR / "benchmark_summary.json"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    csv_path = OUTPUT_DIR / "benchmark_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "algorithm", "median_simplification_seconds", "input_loops",
            "input_vertices", "output_vertices", "vertex_reduction_percent", "runs",
        ])
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in writer.fieldnames})

    print(f"Shared contour set: {len(loops)} loops, {input_vertices} vertices")
    for row in rows:
        print(
            f"{row['algorithm']:20s} median={row['median_simplification_seconds']:.6f}s "
            f"vertices={row['output_vertices']} "
            f"reduction={row['vertex_reduction_percent']:.1f}%"
        )
    print(f"Wrote {json_path} and {csv_path}")


if __name__ == "__main__":
    run_benchmark()
