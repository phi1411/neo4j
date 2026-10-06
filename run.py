"""Chạy backend demo cục bộ; không seed hoặc sửa database khi khởi động."""
import argparse

from app import create_app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    app = create_app()
    try:
        app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False)
    finally:
        app.extensions["neo4j"].close()
