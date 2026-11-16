# R2V: Raster-to-Vector Research Prototype

R2V is a small, extensible prototype for studying raster boundary tracing and polygon simplification. It converts raster images into SVG paths using color quantization or thresholding, exact pixel-edge boundary tracing, and polygon simplification.

The repository currently includes an **initial comparative benchmark for polygon simplification**. It compares no simplification, Douglas–Peucker, and Visvalingam–Whyatt on the same deterministic synthetic contour set. This is a useful starting point, not yet a comprehensive benchmark or evidence that one method is better: the current report measures runtime and vertex reduction, but not geometric fidelity.

## Run the benchmark

```bash
pip install -r requirements.txt
python benchmark.py
```

The script prints the per-algorithm median simplification time and vertex reduction. It writes:

- `results/benchmark_summary.json` — protocol, dataset metadata, parameters, and results
- `results/benchmark_results.csv` — tabular results for analysis

Timing is repeated five times; the median is reported. All algorithms operate on the exact same traced loops, and tracing time is recorded separately rather than charged to any one simplifier. The synthetic input uses seed 0. For publishable results, repeat across multiple seeds and image families, report hardware/software details, and include fidelity metrics and established baselines.

## Current scope and limitations

This benchmark compares **simplification algorithms**, not complete raster-to-vector systems. It does not yet compare alternative tracing/vectorization methods, evaluate Hausdorff distance or raster reconstruction quality, or provide statistical analysis across a broad dataset. A paper-quality study should add those elements before making performance or quality claims.

## Interactive demo

```bash
python server.py
```

Open <http://localhost:8000> for the local web interface.

## Implementation

- `tracer.py` — quantization, exact pixel-edge boundary tracing, and SVG output
- `simplifier.py` — Douglas–Peucker and Visvalingam–Whyatt closed-loop simplifiers
- `synthetic_generator.py` — synthetic raster generation
- `benchmark.py` — comparative simplification benchmark
- `test_tracer.py` — SVG behavior regression tests
- `static/index.html` — local browser interface
