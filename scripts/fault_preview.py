"""Server kiểm thử UI mất Neo4j; driver thật tới cổng trống, không tắt DB project."""
import argparse
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app  # noqa: E402


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    # Giữ socket không listen trong suốt lần chạy để cổng không bị ứng dụng khác chiếm.
    with socket.socket() as endpoint:
        endpoint.bind(("127.0.0.1", 0))
        app = create_app({"NEO4J_URI": f"bolt://127.0.0.1:{endpoint.getsockname()[1]}",
                          "NEO4J_CONNECTION_TIMEOUT": 0.5, "NEO4J_MAX_RETRY_TIME": 0.0})
        try:
            app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False)
        finally:
            app.extensions["neo4j"].close()
