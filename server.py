"""
server.py  -  tiny stdlib HTTP server: serves the frontend + /api/vectorize.

    pip install pillow numpy
    python server.py          # then open http://localhost:8000
"""
import io
import json
import os
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from PIL import Image

from tracer import vectorize
from synthetic_generator import generate_synthetic_raster

ROOT = os.path.dirname(os.path.abspath(__file__))
MAX_UPLOAD = 20 * 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            with open(os.path.join(ROOT, "static", "index.html"), "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if path == "/api/sample":
            buf = io.BytesIO()
            generate_synthetic_raster(buf, 640, 480, filled=True)
            return self._send(200, buf.getvalue(), "image/png")
        self._send(404, {"error": "not found"})

    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/api/vectorize":
            return self._send(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            if not 0 < n <= MAX_UPLOAD:
                return self._send(400, {"error": "empty or too large upload (20 MB max)"})
            img = Image.open(io.BytesIO(self.rfile.read(n)))
            img.load()
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            t = time.time()
            svg, stats = vectorize(
                img,
                mode=q.get("mode", "color"),
                colors=int(q.get("colors", 64)),
                threshold=int(q.get("threshold", 128)),
                tolerance=float(q.get("tolerance", 0)),
                min_area=float(q.get("min_area", 0)),
                smooth=q.get("smooth") == "1",
                max_dim=int(q.get("max_dim", 2000)),
            )
            stats["ms"] = round((time.time() - t) * 1000)
            self._send(200, {"svg": svg, "stats": stats})
        except Exception as e:  # bad image, bad params...
            self._send(400, {"error": f"{type(e).__name__}: {e}"})

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Raster-to-Vector running at http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
