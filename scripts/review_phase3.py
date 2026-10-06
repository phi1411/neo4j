"""Kiểm tra bảo toàn Phase 2 và tổng hợp bằng chứng Phase 3; không seed."""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import dotenv_values
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.phase2 import digest, graph, verify  # noqa: E402


def main():
    baseline = json.loads((ROOT / "docs/PHASE_3_BASELINE.json").read_text(encoding="utf-8"))
    cfg = dotenv_values(ROOT / ".env")
    with GraphDatabase.driver(cfg["NEO4J_URI"], auth=(cfg["NEO4J_USER"], cfg["NEO4J_PASSWORD"])) as driver:
        driver.verify_connectivity()
        validations, demo_results = verify(driver, cfg["NEO4J_DATABASE"])
        snapshot = graph(driver, cfg["NEO4J_DATABASE"])
        after_hash = digest(snapshot)
        assert after_hash == baseline["dataset_sha256"], "Dataset changed during Phase 3"
        assert digest(graph(driver, cfg["NEO4J_DATABASE"], False)) == baseline["outside_sha256"], "Outside dataset changed"
    suites = ET.parse(ROOT / "docs/PHASE_3_PYTEST.xml").getroot()
    tests = list(suites.iter("testcase"))
    assert tests and not list(suites.iter("failure")) and not list(suites.iter("error")) and not list(suites.iter("skipped"))
    http = json.loads((ROOT / "docs/PHASE_3_HTTP_RESULTS.json").read_text(encoding="utf-8"))
    assert http["status"] == "PASS" and http["failed"] == 0
    secret = cfg["NEO4J_PASSWORD"]
    leaks = []
    for folder in ("app", "scripts", "tests", "docs", "database"):
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and path.suffix in {".py", ".json", ".md", ".cypher", ".xml", ".txt"}:
                if secret in path.read_text(encoding="utf-8"):
                    leaks.append(str(path.relative_to(ROOT)))
    assert not leaks, "Credentials found outside local .env; paths withheld from report"
    # App nguồn chỉ dùng query đã duyệt; tuyệt đối không khởi động lại seed/schema.
    report = {
        "status": "PASS", "checked_at": datetime.now(timezone(timedelta(hours=7))).isoformat(),
        "database": cfg["NEO4J_DATABASE"], "dataset": "quadrilateral-v1",
        "pytest": {"passed": len(tests), "failed": 0, "skipped": 0,
                   "integration": sum("test_api_integration" in t.get("classname", "") for t in tests),
                   "unit": sum("test_units" in t.get("classname", "") for t in tests)},
        "http": {"base_url": http["base_url"], "passed": http["passed"], "failed": http["failed"]},
        "phase2": {"nodes": len(snapshot["nodes"]), "relationships": len(snapshot["relationships"]),
                   "validation_passed": len(validations), "query_passed": len(demo_results),
                   "hash_before": baseline["dataset_sha256"], "hash_after": after_hash,
                   "dataset_unchanged": True, "outside_dataset_unchanged": True, "seed_executed": False},
        "credential_scan": "PASS", "validations": validations,
    }
    (ROOT / "docs/PHASE_3_RESULTS.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "validations"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"PHASE 3 REVIEW FAILED: {type(error).__name__}", file=sys.stderr)
        sys.exit(1)
