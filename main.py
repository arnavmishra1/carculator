import sys
import threading
import webbrowser
from pathlib import Path

from calculator.server import HOST, CalculatorServer

PORT = 8765
FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"


def main():
    if not (FRONTEND_DIR / "index.html").exists():
        sys.exit("Frontend not built. Run: npm --prefix frontend run build")

    try:
        server = CalculatorServer((HOST, PORT), FRONTEND_DIR)
    except OSError as error:
        sys.exit(f"Could not start on port {PORT}: {error.strerror}")

    url = f"http://{HOST}:{PORT}"
    print(f"Calculator running at {url} (Ctrl+C to stop)")
    threading.Timer(0.2, webbrowser.open, [url]).start()

    with server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
