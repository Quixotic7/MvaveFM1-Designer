#!/usr/bin/env python3
"""Dev server for the FM-1 designer, with a save endpoint for scripted PNG exports.

  tools/serve.py [--port 8765] [--out docs]

Serves the designer directory over HTTP (needed for `?design=URL` loading: browsers block
fetch() from file:// pages). POST /save?name=X.png writes the request body to <out>/X.png, so

  http://localhost:8765/?design=examples/choralroot-fm1.json&export=screens&post=/save

renders the design's ticked states and saves the sheet without a download dialog
(`export=plate` for the faceplates; `name=` overrides the file name).
"""
import argparse
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--out", default="docs", help="where POST /save writes (relative to the designer root)")
    args = ap.parse_args()
    out = os.path.join(ROOT, args.out)
    os.makedirs(out, exist_ok=True)

    class H(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)

        def do_POST(self):
            u = urlparse(self.path)
            if u.path != "/save":
                self.send_error(404)
                return
            name = os.path.basename(parse_qs(u.query).get("name", ["export.png"])[0]) or "export.png"
            n = int(self.headers.get("Content-Length", "0"))
            data = self.rfile.read(n)
            with open(os.path.join(out, name), "wb") as f:
                f.write(data)
            body = f"saved {name} ({len(data)} bytes)".encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            print(body.decode(), flush=True)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

    print(f"designer at http://localhost:{args.port}/  (saving exports to {out})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), H).serve_forever()


if __name__ == "__main__":
    main()
