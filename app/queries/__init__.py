"""Đọc query cố định từ file; không nhận đường dẫn hay Cypher do request gửi."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMO_FILE = ROOT.parents[1] / "database" / "demo_queries.cypher"


def load(name):
    return (ROOT / name).read_text(encoding="utf-8").strip().removesuffix(";")


def demo_queries():
    sections = re.split(r"(?m)^// @query (Q\d{2})\s*$", DEMO_FILE.read_text(encoding="utf-8"))
    result = {}
    for index in range(1, len(sections), 2):
        code = sections[index]
        result[code] = "\n".join(line for line in sections[index + 1].splitlines()
                                   if not line.lstrip().startswith("//")).strip().removesuffix(";")
    expected = {f"Q{i:02d}" for i in range(1, 16)}
    if set(result) != expected:
        raise RuntimeError("Demo query catalog does not match the approved whitelist")
    return result
