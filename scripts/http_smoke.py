"""Kiểm thử backend qua HTTP thật; server run.py phải đang chạy."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:5000")
    parser.add_argument("--report", type=Path, default=ROOT / "docs/PHASE_3_HTTP_RESULTS.json",
                        help="Đường dẫn báo cáo; dùng file riêng để giữ bằng chứng các phase trước.")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    expected = json.loads((ROOT / "database/expected_results.json").read_text(encoding="utf-8"))
    private = dotenv_values(ROOT / ".env").get("NEO4J_PASSWORD", "")
    checks = []

    def call(name, path, validate=None, status=200, body=None):
        payload = None if body is None else json.dumps(body).encode()
        req = Request(base + path, data=payload, headers={"Content-Type": "application/json"} if payload else {})
        try:
            with urlopen(req, timeout=20) as response:
                actual_status, raw = response.status, response.read()
        except HTTPError as error:
            actual_status, raw = error.code, error.read()
        assert actual_status == status, f"{name}: unexpected HTTP status {actual_status}"
        text = raw.decode("utf-8")
        assert not private or private not in text, "Credential exposed by HTTP response"
        assert "NEO4J_PASSWORD" not in text and "Traceback" not in text, "Unsafe HTTP response"
        content = json.loads(text)
        assert content["success"] is (status == 200), f"{name}: incorrect success flag"
        if status == 200:
            evidence = validate(content["data"]) if validate else {}
        else:
            assert {"code", "message"} <= set(content["error"])
            evidence = {"error_code": content["error"]["code"]}
        checks.append({"name": name, "method": "GET" if payload is None else "POST", "path": path,
                       "http_status": actual_status, "status": "PASS", "evidence": evidence,
                       "response_sha256": hashlib.sha256(raw).hexdigest()})
        print(name, actual_status, "PASS")

    def health(result):
        assert result["flask"] == "running" and result["neo4j"] == "connected"
        assert result["database"] == "quadrilateral" and result["dataset"] == "quadrilateral-v1"
        return result

    def stats(result):
        assert result["total_nodes"] == 44 and result["total_relationships"] == 79
        assert result["node_counts"] == {"Shape": 7, "Property": 19, "Condition": 18}
        return result

    def shapes(result):
        ids = [s["id"] for s in result]
        assert ids == ["TQ", "HT", "HTC", "HBH", "HCN", "HTHOI", "HV"]
        return {"shape_ids": ids}

    def detail(result):
        assert result["shape"]["id"] == "HV"
        assert {s["id"] for s in result["direct_parents"]} == {"HCN", "HTHOI"}
        assert {s["id"] for s in result["ancestors"]} == {"HCN", "HTHOI", "HBH", "TQ"}
        assert {p["id"] for p in result["effective_properties"]} == set(expected["Q02"])
        return {"shape_id": "HV", "parents": 2, "ancestors": 4, "effective_properties": 12}

    def properties(result):
        assert len(result) == 12
        item = next(p for p in result if p["id"] == "DIAGONALS_EQUAL")
        assert [s["id"] for s in item["declared_at"]] == ["HCN"]
        return {"count": len(result), "diagonals_equal_declared_at": "HCN"}

    def conditions(result):
        assert result["combination"] == "OR" and len(result["items"]) == 5
        assert all(c["logic"] == "AND" for c in result["items"])
        criterion = next(c for c in result["items"] if c["condition_id"] == "C_HV_05")
        assert {p["id"] for p in criterion["required_properties"]} == {"FOUR_EQUAL_SIDES", "FOUR_RIGHT_ANGLES"}
        return {"conditions": 5, "combination": "OR", "rule_logic": "AND"}

    def ancestors(result):
        ids = sorted(s["id"] for s in result)
        assert ids == sorted(expected["Q04"])
        return {"shape_ids": ids}

    def search(result):
        assert [s["id"] for s in result["results"]] == ["HV"]
        return {"shape_ids": ["HV"]}

    def graph(result, counts):
        actual = {"nodes": len(result["nodes"]), "relationships": len(result["edges"])}
        assert actual == counts
        node_ids = {n["id"] for n in result["nodes"]}
        assert all(e["from"] in node_ids and e["to"] in node_ids for e in result["edges"])
        return actual

    call("health", "/api/health", health)
    call("stats", "/api/stats", stats)
    call("shapes", "/api/shapes", shapes)
    call("square_detail", "/api/shapes/HV", detail)
    call("properties", "/api/shapes/HV/properties", properties)
    call("conditions", "/api/shapes/HV/conditions", conditions)
    call("ancestors", "/api/shapes/HV/ancestors", ancestors)
    for text in ("Hình vuông", "hình vuông", "hinh vuong", "HINH VUONG", "VUONG", "vuong"):
        call("search_" + text, "/api/search?" + urlencode({"q": text}), search)
    call("taxonomy", "/api/graph/taxonomy", lambda r: graph(r, {"nodes": 7, "relationships": 7}))
    for depth in (1, 2, 3):
        call(f"neighborhood_{depth}", f"/api/graph/neighborhood/HV?depth={depth}",
             lambda r, depth=depth: graph(r, expected["Q14"][str(depth)]))

    def catalog(result):
        ids = [q["id"] for q in result]
        assert ids == [f"Q{i:02d}" for i in range(1, 16)]
        return {"query_ids": ids}
    call("query_catalog", "/api/queries", catalog)

    def demo(result, query_id):
        rows = result["rows"]
        if query_id in {"Q02", "Q10", "Q11"}:
            assert sorted(r["property_id"] for r in rows) == sorted(expected[query_id])
        elif query_id in {"Q03", "Q04", "Q05", "Q06", "Q07", "Q08", "Q12"}:
            assert sorted(r["shape_id"] for r in rows) == sorted(expected[query_id])
        elif query_id in {"Q09", "Q15"}:
            assert sorted(r["node_ids"] for r in rows) == sorted(expected[query_id])
        elif query_id == "Q13":
            assert rows == expected[query_id]
        elif query_id == "Q01":
            graph(result["graph"], {"nodes": 44, "relationships": 79})
        elif query_id == "Q14":
            graph(result["graph"], expected["Q14"]["3"])
        return {"query_id": query_id, "rows": len(rows), "expected_matched": True}

    for number in range(1, 16):
        code = f"Q{number:02d}"
        call(code, f"/api/queries/{code}", lambda r, code=code: demo(r, code))
    call("query_post", "/api/queries/Q14", lambda r: graph(r["graph"], expected["Q14"]["2"]),
         body={"shape_id": "HV", "depth": 2})
    for name, path, status in [("missing_shape", "/api/shapes/UNKNOWN", 404),
                               ("missing_query", "/api/queries/Q99", 404),
                               ("depth_0", "/api/graph/neighborhood/HV?depth=0", 400),
                               ("depth_4", "/api/graph/neighborhood/HV?depth=4", 400),
                               ("empty_search", "/api/search?q=", 400),
                               ("dataset_override", "/api/queries/Q06?dataset=other", 400)]:
        call(name, path, status=status)
    call("arbitrary_cypher_rejected", "/api/queries/Q14", status=400, body={"cypher": "MATCH (n) DETACH DELETE n"})
    report = {"status": "PASS", "transport": "real HTTP", "base_url": base,
              "checked_at": datetime.now(timezone(timedelta(hours=7))).isoformat(), "checks": checks,
              "passed": len(checks), "failed": 0}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"REAL HTTP PASS: {len(checks)} checks; no credentials in response/report")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"HTTP CHECK FAILED: {type(error).__name__}; xem bước kiểm tra gần nhất.", file=sys.stderr)
        sys.exit(1)
