"""Cấu hình chỉ đọc; thông tin đăng nhập không được đưa vào response/log."""
import os
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
DATASET = "quadrilateral-v1"


def load_config(env_file=None):
    values = dotenv_values(env_file if env_file is not None else ROOT / ".env")
    fields = ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "NEO4J_DATABASE")
    return {
        **{key: os.environ.get(key, values.get(key, "")) for key in fields},
        "NEO4J_CONNECTION_TIMEOUT": 5.0,
        "NEO4J_QUERY_TIMEOUT": 10.0,
        "NEO4J_MAX_RETRY_TIME": 2.0,
        "MAX_CONTENT_LENGTH": 16 * 1024,
        "TESTING": False,
    }
