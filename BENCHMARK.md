# Benchmark Protocol

## Scope

This initial benchmark compares polygon simplification methods on a shared set of closed contours extracted from one deterministic synthetic raster. It is not a comparison of complete raster-to-vector systems.

## Compared methods

- **No simplification:** reference point count and timing baseline.
- **Douglas–Peucker:** distance-based simplification, with tolerance reported in pixels.
- **Visvalingam–Whyatt:** area-based iterative vertex removal, with triangle-area threshold reported in square pixels.

Both simplifiers receive the same contour loops from the same tracer. Their parameters have different units, so the current settings are illustrative rather than a parameter-equivalent quality comparison.

## Protocol

Run:

```bash
python benchmark.py
```

The script fixes the synthetic generator seed at 0, uses a 1024×768 image, and repeats each simplifier five times. It reports the median wall-clock simplification time, input/output vertex totals, and vertex reduction. Shared tracing time is reported separately. Results are saved to `results/benchmark_summary.json` and `results/benchmark_results.csv`.

## Interpretation and limitations

The current benchmark does not measure geometric fidelity, raster reconstruction quality, or variation across seeds and image families. Therefore it can compare runtime and point-count reduction for this specific sample, but it cannot support a claim that one algorithm is better overall. The two simplifiers also use different parameter units; meaningful quality/complexity comparisons should sweep parameters and compare methods at matched fidelity or matched output size.

For research publication, extend the protocol with multiple deterministic dataset families, several seeds, hardware and software version capture, fidelity measures such as symmetric Hausdorff distance and raster IoU, additional established baselines, and uncertainty/statistical reporting. Keep generated results and exact commands with the paper artifact.
