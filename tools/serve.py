"""Serve dist/ locally as the CDN would, for the site's dev server.

    python tools/publish.py build
    python tools/serve.py            # http://localhost:8790/commentary/latest.json

Then point the site at it: PUBLIC_COMMENTARY_BASE=http://localhost:8790/commentary
in apps/web/.env.local of the site repository.
"""

from __future__ import annotations

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "dist"


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, format: str, *args) -> None:  # quiet, except errors
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(format, *args)


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8790
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(ROOT)))
    print(f"serving {ROOT} at http://localhost:{port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
