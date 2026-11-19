# R2V: Benchmarking Raster-to-Vector Conversion

R2V is a compact research prototype for converting raster images into vector paths while preserving shape fidelity and offering a reproducible benchmark pipeline. The project implements an end-to-end raster-to-vector workflow: raster quantization, boundary tracing, path simplification, and SVG export.

## Project framing

This repository is structured as a benchmark-oriented prototype for evaluating a raster-to-vector pipeline in a reproducible and extensible way. It is designed for:

- algorithmic experimentation on boundary extraction and polygon simplification
- controlled benchmark execution on synthetic raster inputs
- reproducible reporting of runtime and geometric complexity
- demonstration through a lightweight interactive web frontend

The underlying method combines:

1. image quantization or binary thresholding,
2. exact pixel-edge boundary tracing,
3. closed-loop simplification via Douglas-Peucker,
4. SVG generation for rendering and downstream processing.

## Research objective

The core question is whether a simple exact-tracing pipeline can preserve shape fidelity while substantially reducing the number of points required to represent raster boundaries. The repository is intentionally small and transparent so that the trade-off between fidelity and simplification cost can be measured without the overhead of a large production stack.

## Benchmark contribution

The repository includes a benchmark workflow that measures:

- tracing time
- simplification cost
- total SVG generation time
- resulting path and point counts
- final output dimensions and complexity

This makes the project suitable as a benchmark paper prototype or a starting point for a research artifact, especially for studies on vectorization quality, simplification quality, or contour extraction efficiency.

## Quick start

```bash
pip install -r requirements.txt
python server.py
```

Then open:

- http://localhost:8000

## Files

- `tracer.py` — quantization, exact boundary tracing, and SVG export
- `simplifier.py` — Douglas-Peucker simplification for open and closed paths
- `server.py` — local HTTP API for interactive vectorization
- `static/index.html` — browser-based UI for parameter exploration
- `synthetic_generator.py` — synthetic raster generation for controlled experiments
- `benchmark.py` — benchmark harness for tracing and simplification timing
- `test_tracer.py` — regression tests for SVG output behavior

## Benchmark protocol

The project includes a synthetic benchmark workflow intended to emulate controlled research conditions:

```bash
python benchmark.py
```

The script generates a synthetic raster, traces its boundaries, simplifies the loops, and writes a summary to `results/benchmark_summary.json`.

This benchmark is intentionally lightweight and reproducible, making it suitable for early-stage studies and paper prototypes.

## Reproduction and extension

To treat this repository as a research prototype, researchers can extend it in several directions:

- add more benchmark scenes and datasets
- evaluate against baseline vectorization methods
- compute quality metrics such as fidelity, IoU, and point reduction
- compare simplification tolerance settings and color quantization levels
- package results as plots, tables, or a paper appendix

## Citation-style summary

`R2V` is a minimal benchmark prototype for raster-to-vector conversion based on exact contour tracing and geometric simplification. It is designed to support reproducible experimentation and early research validation in the domain of vectorization quality and efficiency.

## License

This repository is intended for research and experimentation. Add a license before public release or formal publication.


#BENCHMARK.md# Benchmark protocol for R2V## ObjectiveR2V is designed to benchmark a compact raster-to-vector pipeline that traces pixel-edge boundaries and simplifies them into SVG paths. The aim is to measure the relationship between:- fidelity to the original raster shape,- number of retained polygon vertices,- runtime cost of tracing and simplification,- and the final vector output size.## Benchmark workflowThe core benchmark is implemented in `benchmark.py`.### Pipeline1. Generate a synthetic raster image with known geometry.2. Convert it to a grayscale or color mask.3. Trace exact object boundaries using `mask_to_loops`.4. Simplify the resulting loops with Douglas-Peucker.5. Emit SVG output and record pipeline metrics.### Metrics collected- tracing time- simplification time- total time- loop count- vertex count before and after simplification- output image dimensions- SVG byte size## Reproducible command```bashpython benchmark.py```## Expected outputThe script prints a summary, and it also writes a structured JSON report to:```bashresultsbenchmark_summary.json```This output can be us \ned as a research artifact for plots, tables, or appendix material.## Suggested extensionsFor a paper-ready benchmark, consider adding:- multiple synthetic scene families- real image test sets- baseline comparisons to alternative vectorization methods- quality metrics such as Hausdorff distance or IoU- area and perimeter preservation statistics- parameter sweeps across tolerance and quantization settings## Benchmark philosophyThis repository is intentionally small and transparent so its benchmark can be reproduced easily. That makes it suitable as a prototype research project or a foundation for a more extensive experimental study.
