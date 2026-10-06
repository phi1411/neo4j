"""CLI thao tác Neo4j thật cho Phase 2. Không có dữ liệu thay thế/offline."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import dotenv_values
from neo4j import GraphDatabase, unit_of_work
from neo4j.graph import Node, Path as GraphPath, Relationship

ROOT = Path(__file__).resolve().parents[1]
DATASET = "quadrilateral-v1"
DOMAIN_LABELS = {"Shape", "Property", "Condition"}


def read_json(name):
    return json.loads((ROOT / "database" / name).read_text(encoding="utf-8"))


def catalogs():
    return {"Shape": read_json("shapes.json"), "Property": read_json("properties.json"),
            "Condition": read_json("conditions.json")}, read_json("relationships.json")


def literal(value):
    if isinstance(value, dict):
        return "{" + ", ".join(f"{key}: {literal(val)}" for key, val in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ",\n".join(literal(val) for val in value) + "]"
    return json.dumps(value, ensure_ascii=False)


def generate_seed():
    data, links = catalogs()
    chunks = ["// Seed độc lập, dataset cố định quadrilateral-v1.\n"
              "// Sinh từ bốn file JSON bằng scripts/phase2.py build-seed.\n"
              "// Không DELETE/DROP; MERGE theo (dataset, id).\n"]
    for label, rows in data.items():
        fields = [{k: v for k, v in row.items() if k not in {"target", "context", "properties"}}
                  for row in rows]
        chunks.append(f"// Seed {label}\nUNWIND {literal(fields)} AS row\n"
                      f"MERGE (n:{label} {{dataset: '{DATASET}', id: row.id}})\n"
                      "SET n:ProjectEntity\nSET n += row;\n")
    chunks.append(f"// Phân loại trực tiếp\nUNWIND {literal(links['taxonomy'])} AS pair\n"
                  f"MATCH (a:Shape:ProjectEntity {{dataset: '{DATASET}', id: pair[0]}})\n"
                  f"MATCH (b:Shape:ProjectEntity {{dataset: '{DATASET}', id: pair[1]}})\n"
                  "MERGE (a)-[:IS_A]->(b);\n")
    pairs = [[shape, prop] for shape, props in links["declarations"].items() for prop in props]
    chunks.append(f"// Tính chất trực tiếp\nUNWIND {literal(pairs)} AS pair\n"
                  f"MATCH (s:Shape:ProjectEntity {{dataset: '{DATASET}', id: pair[0]}})\n"
                  f"MATCH (p:Property:ProjectEntity {{dataset: '{DATASET}', id: pair[1]}})\n"
                  "MERGE (s)-[:HAS_PROPERTY]->(p);\n")
    for rel_type, label, pairs in [
        ("HAS_CONDITION", "Shape", [[c["target"], c["id"]] for c in data["Condition"]]),
        ("REQUIRES_SHAPE", "Shape", [[c["id"], c["context"]] for c in data["Condition"]]),
        ("REQUIRES_PROPERTY", "Property", [[c["id"], p] for c in data["Condition"] for p in c["properties"]]),
    ]:
        from_label, to_label = ("Shape", "Condition") if rel_type == "HAS_CONDITION" else ("Condition", label)
        chunks.append(f"// {rel_type}\nUNWIND {literal(pairs)} AS pair\n"
                      f"MATCH (a:{from_label}:ProjectEntity {{dataset: '{DATASET}', id: pair[0]}})\n"
                      f"MATCH (b:{to_label}:ProjectEntity {{dataset: '{DATASET}', id: pair[1]}})\n"
                      f"MERGE (a)-[:{rel_type}]->(b);\n")
    (ROOT / "database" / "seed.cypher").write_text("\n".join(chunks), encoding="utf-8")
    print("seed.cypher generated from approved catalogs")


def statements(text):
    """Tách statement, giữ dấu ; và // trong chuỗi Cypher/URL."""
    result, buffer, quote, i = [], [], None, 0
    while i < len(text):
        ch = text[i]
        if quote:
            buffer.append(ch)
            if ch == "\\" and i + 1 < len(text):
                i += 1
                buffer.append(text[i])
            elif ch == quote:
                quote = None
        elif ch in "'\"`":
            quote = ch
            buffer.append(ch)
        elif text[i:i + 2] == "//":
            i = text.find("\n", i)
            if i == -1:
                break
            buffer.append("\n")
        elif ch == ";":
            if "".join(buffer).strip():
                result.append("".join(buffer).strip())
            buffer = []
        else:
            buffer.append(ch)
        i += 1
    if "".join(buffer).strip():
        result.append("".join(buffer).strip())
    return result


def blocks(filename, prefix):
    text = (ROOT / "database" / filename).read_text(encoding="utf-8")
    pieces = re.split(rf"(?m)^// @{prefix} ([A-Z]\d{{2}})\s*$", text)
    result = []
    for i in range(1, len(pieces), 2):
        queries = statements(pieces[i + 1])
        if len(queries) != 1:
            raise ValueError(f"{pieces[i]} must have exactly one statement")
        result.append((pieces[i], queries[0]))
    return result


def key(node):
    labels = sorted(DOMAIN_LABELS.intersection(node.labels))
    return f"{labels[0] if labels else 'Other'}:{node.get('id')}"


def encode(value):
    if isinstance(value, Node):
        return {"key": key(value), "labels": sorted(value.labels), "properties": dict(value)}
    if isinstance(value, Relationship):
        return {"source": key(value.start_node), "type": value.type, "target": key(value.end_node),
                "properties": dict(value)}
    if isinstance(value, GraphPath):
        return {"nodes": [key(n) for n in value.nodes], "types": [r.type for r in value.relationships]}
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def query(driver, db, cypher, params=None):
    with driver.session(database=db) as session:
        return session.execute_read(lambda tx: [encode(r.data()) for r in tx.run(cypher, params or {})])


def graph(driver, db, project=True):
    where = "n.dataset = $dataset" if project else "n.dataset IS NULL OR n.dataset <> $dataset"
    with driver.session(database=db) as session:
        nodes = session.execute_read(lambda tx: [
            {"key": key(r["n"]), "labels": sorted(r["n"].labels), "properties": dict(r["n"])}
            for r in tx.run(f"MATCH (n) WHERE {where} RETURN n", dataset=DATASET)])
        condition = "a.dataset = $dataset OR b.dataset = $dataset" if project else "NOT (coalesce(a.dataset, '') = $dataset OR coalesce(b.dataset, '') = $dataset)"
        edges = session.execute_read(lambda tx: [
            {"source": key(r["a"]), "type": r["type"], "target": key(r["b"]), "properties": r["props"]}
            for r in tx.run(f"MATCH (a)-[r]->(b) WHERE {condition} RETURN a, b, type(r) AS type, properties(r) AS props", dataset=DATASET)])
    sortkey = lambda row: json.dumps(row, ensure_ascii=False, sort_keys=True)
    return {"nodes": sorted(nodes, key=sortkey), "relationships": sorted(edges, key=sortkey)}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def expected_graph():
    data, links = catalogs()
    nodes = []
    for label, rows in data.items():
        for row in rows:
            props = {k: v for k, v in row.items() if k not in {"target", "context", "properties"}}
            nodes.append({"key": f"{label}:{row['id']}", "labels": sorted([label, "ProjectEntity"]),
                          "properties": {**props, "dataset": DATASET}})
    triples = [(f"Shape:{a}", "IS_A", f"Shape:{b}") for a, b in links["taxonomy"]]
    triples += [(f"Shape:{s}", "HAS_PROPERTY", f"Property:{p}") for s, ps in links["declarations"].items() for p in ps]
    for c in data["Condition"]:
        triples += [(f"Shape:{c['target']}", "HAS_CONDITION", f"Condition:{c['id']}"),
                    (f"Condition:{c['id']}", "REQUIRES_SHAPE", f"Shape:{c['context']}")]
        triples += [(f"Condition:{c['id']}", "REQUIRES_PROPERTY", f"Property:{p}") for p in c["properties"]]
    edges = [{"source": a, "type": t, "target": b, "properties": {}} for a, t, b in triples]
    sortkey = lambda row: json.dumps(row, ensure_ascii=False, sort_keys=True)
    return {"nodes": sorted(nodes, key=sortkey), "relationships": sorted(edges, key=sortkey)}


def apply_file(driver, db, filename):
    queries = statements((ROOT / "database" / filename).read_text(encoding="utf-8"))
    # Seed trong một transaction: lỗi bất kỳ statement nào thì rollback toàn bộ seed.
    with driver.session(database=db) as session:
        @unit_of_work(timeout=30)
        def write(tx):
            counters = []
            for cypher in queries:
                summary = tx.run(cypher).consume()
                counters.append({k: getattr(summary.counters, k) for k in
                                 ("nodes_created", "relationships_created", "properties_set", "constraints_added", "indexes_added")})
            return counters
        result = session.execute_write(write)
    print(filename, json.dumps(result))
    return result


def neighbors(expected, center, depth):
    selected = {center}
    for _ in range(depth):
        selected |= {e["target"] for e in expected["relationships"] if e["source"] in selected} | {
            e["source"] for e in expected["relationships"] if e["target"] in selected}
    # Q14 trả induced graph trên tập node đạt được, không chỉ cạnh tình cờ có trong path.
    edges = [e for e in expected["relationships"] if e["source"] in selected and e["target"] in selected]
    return selected, edges


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}: actual={actual!r}, expected={expected!r}")


def verify(driver, db):
    params = {"dataset": DATASET, "shape_id": "HV", "depth": 3}
    expected = expected_graph()
    assert_equal(graph(driver, db), expected, "Full graph IDs/labels/properties/relationships")
    validations = []
    for code, cypher in blocks("validation.cypher", "validation"):
        rows = query(driver, db, cypher, params)
        assert_equal(rows, [{"violations": 0}], code)
        validations.append({"id": code, "status": "PASS", "violations": 0})
        print(code, "PASS")
    results, expectations = [], read_json("expected_results.json")
    for code, cypher in blocks("demo_queries.cypher", "query"):
        with driver.session(database=db) as session:
            # Không dùng Record.data() trước encode: nó làm mất kiểu graph của Node/Path.
            rows = session.execute_read(lambda tx: [encode(dict(r)) for r in tx.run(cypher, params)])
        if code == "Q01":
            assert_equal(len(rows[0]["nodes"]), 44, code)
            assert_equal(len(rows[0]["relationships"]), 79, code)
        elif code in {"Q02", "Q10", "Q11"}:
            assert_equal(sorted(r["property_id"] for r in rows), sorted(expectations[code]), code)
            if code == "Q02":
                by_id = {r["property_id"]: r for r in rows}
                assert_equal(by_id["DIAGONALS_EQUAL"]["declared_at"], ["HCN"], "DIAGONALS_EQUAL source")
                assert_equal(by_id["DIAGONALS_BISECT_EACH_OTHER"]["declared_at"], ["HBH"], "DIAGONALS_BISECT source")
        elif code in {"Q03", "Q04", "Q05", "Q06", "Q07", "Q08", "Q12"}:
            assert_equal(sorted(r["shape_id"] for r in rows), sorted(expectations[code]), code)
        elif code in {"Q09", "Q15"}:
            assert_equal(sorted(r["node_ids"] for r in rows), sorted(expectations[code]), code)
        elif code == "Q13":
            assert_equal(rows, expectations[code], code)
        elif code == "Q14":
            checks = []
            for depth in (1, 2, 3):
                with driver.session(database=db) as session:
                    actual = session.execute_read(lambda tx: [encode(dict(r)) for r in tx.run(cypher, {**params, "depth": depth})])[0]
                ns, es = neighbors(expected, "Shape:HV", depth)
                assert_equal({n["key"] for n in actual["nodes"]}, ns, f"Q14 depth {depth} nodes")
                actual_edges = sorted((e["source"], e["type"], e["target"]) for e in actual["relationships"])
                expect_edges = sorted((e["source"], e["type"], e["target"]) for e in es)
                assert_equal(actual_edges, expect_edges, f"Q14 depth {depth} edges")
                assert_equal({"nodes": len(ns), "relationships": len(es)}, expectations[code][str(depth)], f"Q14 depth {depth} frozen counts")
                checks.append({"depth": depth, "nodes": len(ns), "relationships": len(es), "status": "PASS"})
            results.append({"id": code, "status": "PASS", "depth_checks": checks, "rows": rows})
            print(code, "PASS", json.dumps(checks))
            continue
        results.append({"id": code, "status": "PASS", "rows": rows})
        print(code, "PASS", "rows=" + str(len(rows)))
    assert_equal(len(results), 15, "15 query results")
    return validations, results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["connect", "build-seed", "schema", "seed", "finish", "verify"])
    args = parser.parse_args()
    if args.action == "build-seed":
        generate_seed()
        return
    cfg = dotenv_values(ROOT / ".env")
    required = ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "NEO4J_DATABASE")
    if any(not cfg.get(k) for k in required):
        raise ValueError("Missing connection fields in .env; credentials are never printed")
    db = cfg["NEO4J_DATABASE"]
    # Guard tránh vô tình chọn system hoặc database mặc định chứa dữ liệu khác.
    if db != "quadrilateral":
        raise ValueError("Phase 2 runner requires the dedicated quadrilateral database")
    with GraphDatabase.driver(cfg["NEO4J_URI"], auth=(cfg["NEO4J_USER"], cfg["NEO4J_PASSWORD"]), connection_timeout=10) as driver:
        driver.verify_connectivity()
        assert_equal(query(driver, db, "RETURN 1 AS connection_check"), [{"connection_check": 1}], "Connection")
        print("AUTHENTICATED TARGET CONNECTION PASS")
        if args.action == "connect":
            print(json.dumps(query(driver, db, "CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition")))
        elif args.action == "schema":
            apply_file(driver, db, "constraints.cypher")
            apply_file(driver, db, "indexes.cypher")
            query(driver, db, "CALL db.awaitIndexes(30)")
        elif args.action == "seed":
            before_external = graph(driver, db, project=False)
            first_counters = apply_file(driver, db, "seed.cypher")
            assert_equal(graph(driver, db, project=False), before_external, "Outside dataset preservation")
            first = graph(driver, db)
            assert_equal(first, expected_graph(), "First seed full graph")
            evidence = {"snapshot": first, "sha256": digest(first), "outside_snapshot": before_external,
                        "outside_sha256": digest(before_external), "counters": first_counters}
            (ROOT / "docs" / "seed_first_run.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
            print("FIRST SEED PASS: nodes=44 relationships=79")
        elif args.action == "verify":
            # Chỉ đọc: kiểm thử lại khi chỉnh expected/chú thích mà không seed lần ba.
            validations, results = verify(driver, db)
            path = ROOT / "docs" / "PHASE_2_RESULTS.json"
            report = json.loads(path.read_text(encoding="utf-8"))
            assert_equal(digest(graph(driver, db)), report["second_sha256"], "Read-only recheck snapshot")
            first = json.loads((ROOT / "docs" / "seed_first_run.json").read_text(encoding="utf-8"))
            assert_equal(graph(driver, db, project=False), first["outside_snapshot"], "Read-only outside preservation")
            report.update(validations=validations, queries=results,
                          checked_at=datetime.now(timezone(timedelta(hours=7))).isoformat())
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print("READ-ONLY RECHECK PASS: no third seed")
        elif args.action == "finish":
            first = json.loads((ROOT / "docs" / "seed_first_run.json").read_text(encoding="utf-8"))
            assert_equal(graph(driver, db), first["snapshot"], "First snapshot before second seed")
            # Validation trước seed lần hai; không che lỗi bằng việc seed lại sửa dữ liệu.
            for code, cypher in blocks("validation.cypher", "validation"):
                assert_equal(query(driver, db, cypher, {"dataset": DATASET}), [{"violations": 0}], code)
            second_counters = apply_file(driver, db, "seed.cypher")
            second = graph(driver, db)
            assert_equal(second, first["snapshot"], "Idempotence full graph snapshot")
            assert_equal(sum(c["nodes_created"] + c["relationships_created"] for c in second_counters), 0, "Idempotence no new entities")
            assert_equal(graph(driver, db, project=False), first["outside_snapshot"], "Outside dataset preservation")
            validations, results = verify(driver, db)
            components = query(driver, db, "CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition")
            schema = {"constraints": query(driver, db, "SHOW CONSTRAINTS YIELD name, type, labelsOrTypes, properties WHERE name STARTS WITH 'quadrilateral_' RETURN name, type, labelsOrTypes, properties ORDER BY name"),
                      "indexes": query(driver, db, "SHOW INDEXES YIELD name, type, state WHERE name STARTS WITH 'quadrilateral_' RETURN name, type, state ORDER BY name")}
            assert_equal(len(schema["constraints"]), 3, "Constraint count")
            assert_equal(len(schema["indexes"]), 4, "Index count including constraint backing indexes")
            assert_equal({i["state"] for i in schema["indexes"]}, {"ONLINE"}, "Index state")
            report = {"status": "PASS", "database": db, "dataset": DATASET,
                      "checked_at": datetime.now(timezone(timedelta(hours=7))).isoformat(), "components": components,
                      "nodes": len(second["nodes"]), "relationships": len(second["relationships"]),
                      "node_counts": {label: sum(label in n["labels"] for n in second["nodes"]) for label in sorted(DOMAIN_LABELS)},
                      "relationship_counts": {t: sum(e["type"] == t for e in second["relationships"]) for t in sorted({e["type"] for e in second["relationships"]})},
                      "schema": schema, "first_seed_counters": first["counters"], "second_seed_counters": second_counters,
                      "idempotent": True, "first_sha256": first["sha256"], "second_sha256": digest(second),
                      "outside_dataset_unchanged": True, "validations": validations, "queries": results}
            path = ROOT / "docs" / "PHASE_2_RESULTS.json"
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print("PHASE 2 PASS: report saved; no passwords recorded")


def report_failure(exc):
    # Chỉ công bố loại lỗi; thông báo driver có thể chứa URI hoặc cấu hình riêng.
    print(f"PHASE 2 FAILED ({type(exc).__name__}); kiểm tra cấu hình và kết nối Neo4j.", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Không in cấu hình/traceback có dữ liệu kết nối.
        report_failure(exc)
        sys.exit(1)
