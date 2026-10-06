"""Tổng hợp bằng chứng Phase 4 và kiểm tra Neo4j chỉ đọc; không seed/migration."""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app  # noqa: E402
from scripts.phase2 import digest, graph, verify  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    baseline = json.loads((ROOT / "docs/PHASE_3_BASELINE.json").read_text(encoding="utf-8"))
    ui = json.loads((ROOT / "docs/PHASE_4_UI_RESULTS.json").read_text(encoding="utf-8"))
    assert ui["status"] == "PASS" and ui["checks"] and not ui["unexpected_console_errors"]
    assert all(c["status"] == "PASS" for c in ui["checks"])
    names = {c["name"] for c in ui["checks"]}
    required = {"dashboard_stats", "taxonomy_counts", "shapes_count", "HV_properties", "HV_ancestors",
                "HV_C05_AND", "HV_depth_1", "HV_depth_2", "HV_depth_3", "shape_404_UI", "invalid_shape_UI",
                "Neo4j_unavailable_UI", "Flask_unavailable_UI", "graph_edge_click", "graph_node_click"}
    required.update(f"Q{i:02d}_run_success" for i in range(1, 16))
    assert required <= names, "Missing required browser evidence"
    suites = ET.parse(ROOT / "docs/PHASE_4_PYTEST.xml").getroot()
    tests = list(suites.iter("testcase"))
    assert len(tests) >= 91 and not any(list(suites.iter(tag)) for tag in ("failure", "error", "skipped"))
    app = create_app()
    db = app.extensions["neo4j"]
    try:
        db.verify()
        validations, demos = verify(db.driver, db.database)
        snapshot = graph(db.driver, db.database)
        dataset_hash = digest(snapshot)
        assert dataset_hash == baseline["dataset_sha256"]
        assert digest(graph(db.driver, db.database, False)) == baseline["outside_sha256"]
        secret = app.config["NEO4J_PASSWORD"]
        for folder in ("app", "scripts", "tests", "docs", "database"):
            for path in (ROOT / folder).rglob("*"):
                if "vendor" in path.parts:
                    continue  # Mã bên thứ ba kiểm tra bằng manifest, không phải source riêng.
                if path.is_file() and path.suffix in {".py", ".js", ".html", ".css", ".json", ".md", ".xml", ".cypher"}:
                    assert secret not in path.read_text(encoding="utf-8"), "Credential found in authored source/report"
        database = db.database
    finally:
        db.close()
    http_checks = []
    for path in ("/", "/shapes", "/shapes/HV", "/graph", "/queries", "/about", "/api/health", "/api/stats"):
        with urlopen("http://127.0.0.1:5000" + path, timeout=20) as response:
            assert response.status == 200
            http_checks.append({"path": path, "status": 200})
    vendor = ROOT / "app/static/vendor/vis-network"
    manifest = json.loads((vendor / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["files"].items():
        assert hashlib.sha256((vendor / name).read_bytes()).hexdigest() == expected
    images = [{"file": str(p.relative_to(ROOT)).replace("\\", "/"),
               "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((ROOT / "docs/images").glob("*.jpg"))]
    assert len(images) >= 10 and all((ROOT / item["file"]).read_bytes().startswith(b"\xff\xd8") for item in images)
    report = {
        "status": "PASS", "checked_at": datetime.now(timezone(timedelta(hours=7))).isoformat(),
        "database": database, "base_url": "http://127.0.0.1:5000", "api_contract_changed": False,
        "pytest": {"passed": len(tests), "failed": 0, "skipped": 0},
        "browser": {"passed": len(ui["checks"]), "query_passed": 15, "unexpected_console_errors": 0,
                    "viewports": ui["viewports"], "evidence_file": "docs/PHASE_4_UI_RESULTS.json"},
        "phase2": {"nodes": len(snapshot["nodes"]), "relationships": len(snapshot["relationships"]),
                   "validation_passed": len(validations), "query_passed": len(demos),
                   "dataset_sha256": dataset_hash, "dataset_unchanged": True,
                   "outside_dataset_unchanged": True, "seed_executed": False},
        "http": http_checks, "local_dependency": {"package": "vis-network", "version": manifest["version"], "integrity_check": "PASS"},
        "credential_scan": "PASS", "screenshots": images, "validations": validations,
    }
    (ROOT / "docs/PHASE_4_RESULTS.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("validations", "screenshots")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"PHASE 4 REVIEW FAILED: {type(error).__name__}", file=sys.stderr)
        sys.exit(1)
