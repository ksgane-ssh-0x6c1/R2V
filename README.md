# Raster → Vector

    pip install -r requirements.txt
    python server.py            # open http://localhost:8000

Files
- `tracer.py` – quantise → exact pixel-edge boundary tracing → SVG
- `simplifier.py` – Douglas-Peucker (open + closed paths)
- `server.py` – stdlib HTTP server (`POST /api/vectorize`, `GET /api/sample`)
- `static/index.html` – drag-and-drop UI with live parameters + SVG download
- `synthetic_generator.py`, `benchmark.py` – test image generator and timing script
