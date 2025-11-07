from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8080

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hello from Docker container on port 8080!")

if __name__ == "__main__":
    httpd = HTTPServer(("", PORT), Handler)
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
