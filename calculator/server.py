"""Local HTTP server: the calculation API and the built Vue frontend."""

import json
import socketserver
import threading
from dataclasses import asdict
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from calculator.engine import CalculationError, calculate
from calculator.facts import find_fact
from calculator.history import History

HOST = "127.0.0.1"
MAX_BODY_BYTES = 64 * 1024


class CalculatorServer(ThreadingHTTPServer):
    def __init__(self, address, static_dir):
        super().__init__(address, partial(_Handler, directory=str(static_dir)))
        self.history = History()
        self.history_lock = threading.Lock()

    def server_bind(self):
        # HTTPServer.server_bind does a reverse DNS lookup that can take seconds.
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]


class _Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/history":
            self._send_json(200, {"history": self._history_entries()})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/calculate":
            self._send_json(404, {"error": "Not found"})
            return

        # Requiring JSON makes browsers preflight cross-site requests, and the
        # preflight fails, so other websites can't drive this local server.
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "Expected JSON"})
            return

        expression = self._read_expression()
        if expression is None:
            self._send_json(400, {"error": "Invalid request"})
            return

        try:
            result = calculate(expression)
        except CalculationError as error:
            self._send_json(422, {"error": str(error)})
            return

        with self.server.history_lock:
            self.server.history.add(expression, result)
        self._send_json(
            200,
            {
                "result": result,
                "fact": find_fact(result),
                "history": self._history_entries(),
            },
        )

    def do_DELETE(self):
        if self.path != "/api/history":
            self._send_json(404, {"error": "Not found"})
            return

        with self.server.history_lock:
            self.server.history.clear()
        self._send_json(200, {"history": []})

    def log_message(self, format, *args):
        pass

    def _read_expression(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            return None
        if not 0 < length <= MAX_BODY_BYTES:
            return None

        try:
            body = json.loads(self.rfile.read(length))
        except ValueError:
            return None

        expression = body.get("expression") if isinstance(body, dict) else None
        return expression if isinstance(expression, str) else None

    def _history_entries(self):
        with self.server.history_lock:
            return [asdict(entry) for entry in self.server.history]

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
