"""Simple proxy server: serves frontend static files and proxies /api to backend."""
import http.server
import socketserver
import urllib.request
import urllib.parse
import os

PORT = 3001
BACKEND_URL = "http://127.0.0.1:8000"
DIST_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def send_error(self, code, message=None, explain=None):
        """Override to serve index.html for SPA routes instead of 404."""
        if code == 404 and not self.path.startswith("/api/"):
            # SPA fallback: serve index.html
            index_path = os.path.join(DIST_DIR, "index.html")
            if os.path.isfile(index_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(index_path, "rb") as f:
                    self.wfile.write(f.read())
                return
        super().send_error(code, message, explain)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self._proxy("GET")
        return super().do_GET()

    def do_HEAD(self):
        if self.path.startswith("/api/"):
            return self._proxy("HEAD")
        return super().do_HEAD()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self._proxy("POST")
        self.send_error(404)

    def do_PUT(self):
        if self.path.startswith("/api/"):
            return self._proxy("PUT")
        self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            return self._proxy("DELETE")
        self.send_error(404)

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        if self.path.startswith("/api/"):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.send_header("Access-Control-Max-Age", "86400")
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

    def _proxy(self, method):
        parsed = urllib.parse.urlparse(self.path)
        backend_path = "/api" + parsed.path[len("/api"):]
        if parsed.query:
            backend_path += "?" + parsed.query
        url = BACKEND_URL + backend_path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req = urllib.request.Request(url, data=body, method=method)
        # Forward all relevant headers
        if "Authorization" in self.headers:
            req.add_header("Authorization", self.headers["Authorization"])
        if "Content-Type" in self.headers:
            req.add_header("Content-Type", self.headers["Content-Type"])

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()
            self.wfile.write(err_body)


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print(f"  Frontend: static files from {DIST_DIR}")
        print(f"  API proxy: /api/* -> {BACKEND_URL}/api/*")
        httpd.serve_forever()
