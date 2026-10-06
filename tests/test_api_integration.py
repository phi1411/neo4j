import json
import socket
from pathlib import Path

import pytest

from app import create_app
from app.errors import APIError
from tests.conftest import data

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[1]
EXPECTED = json.loads((ROOT / "database/expected_results.json").read_text(encoding="utf-8"))


def test_health(client):
    result = data(client.get("/api/health"))
    assert result == {"flask": "running", "neo4j": "connected", "database": "quadrilateral", "dataset": "quadrilateral-v1"}


def test_stats_real_counts(client, app):
    result = data(client.get("/api/stats"))
    assert result["node_counts"] == {"Shape": 7, "Property": 19, "Condition": 18}
    assert result["relationship_counts"] == {"IS_A": 7, "HAS_PROPERTY": 17, "HAS_CONDITION": 18,
                                               "REQUIRES_SHAPE": 18, "REQUIRES_PROPERTY": 19}
    assert result["total_nodes"] == 44 and result["total_relationships"] == 79
    actual = app.extensions["neo4j"].read("MATCH (n:ProjectEntity {dataset:$dataset}) RETURN count(n) AS total")[0]["total"]
    assert result["total_nodes"] == actual


def test_shapes(client):
    shapes = data(client.get("/api/shapes"))
    assert [s["id"] for s in shapes] == ["TQ", "HT", "HTC", "HBH", "HCN", "HTHOI", "HV"]
    assert all({"id", "name", "definition", "search_name", "display_order"} <= set(s) for s in shapes)


def test_square_detail_and_inheritance(client):
    result = data(client.get("/api/shapes/HV"))
    assert result["shape"]["name"] == "Hình vuông"
    assert {s["id"] for s in result["direct_parents"]} == {"HCN", "HTHOI"}
    assert {s["id"] for s in result["ancestors"]} == {"HCN", "HTHOI", "HBH", "TQ"}
    assert not {"HT", "HTC"} & {s["id"] for s in result["ancestors"]}
    assert {p["id"] for p in result["effective_properties"]} == set(EXPECTED["Q02"])
    assert result["direct_properties"] == []
    assert len(result["effective_properties"]) == 12
    by_id = {p["id"]: p for p in result["effective_properties"]}
    assert [s["id"] for s in by_id["DIAGONALS_EQUAL"]["declared_at"]] == ["HCN"]
    assert [s["id"] for s in by_id["DIAGONALS_PERPENDICULAR"]["declared_at"]] == ["HTHOI"]
    assert [s["id"] for s in by_id["FOUR_SIDES"]["declared_at"]] == ["TQ"]
    diagonal = by_id["DIAGONALS_BISECT_EACH_OTHER"]
    assert [s["id"] for s in diagonal["declared_at"]] == ["HBH"]
    assert {tuple(p["shape_ids"]) for p in diagonal["inheritance_paths"]} == {
        ("HV", "HCN", "HBH"), ("HV", "HTHOI", "HBH")}
    assert all(p["inherited"] and not p["direct"] for p in result["effective_properties"])


def test_property_endpoint_direct_and_inherited(client):
    properties = data(client.get("/api/shapes/HCN/properties"))
    assert len(properties) == 9
    assert {p["id"] for p in properties if p["direct"]} == {"FOUR_RIGHT_ANGLES", "DIAGONALS_EQUAL"}
    assert sum(p["inherited"] for p in properties) == 7


def test_condition_structure_and_or(client):
    result = data(client.get("/api/shapes/HV/conditions"))
    assert result["combination"] == "OR"
    assert len(result["items"]) == 5
    assert all(c["logic"] == "AND" and c["required_shape"] and c["required_properties"] for c in result["items"])
    dual = next(c for c in result["items"] if c["condition_id"] == "C_HV_05")
    assert dual["required_shape"]["id"] == "TQ"
    assert {p["id"] for p in dual["required_properties"]} == {"FOUR_EQUAL_SIDES", "FOUR_RIGHT_ANGLES"}
    rectangle = data(client.get("/api/shapes/HCN/conditions"))["items"]
    criterion = next(c for c in rectangle if c["condition_id"] == "C_HCN_03")
    assert criterion["required_shape"]["id"] == "HBH"
    assert [p["id"] for p in criterion["required_properties"]] == ["DIAGONALS_EQUAL"]


def test_ancestors_endpoint(client):
    assert {s["id"] for s in data(client.get("/api/shapes/HV/ancestors"))} == {"HCN", "HTHOI", "HBH", "TQ"}


@pytest.mark.parametrize("keyword", ["hinh vuong", "Hình vuông", "VUONG", "  hình   VUÔNG  "])
def test_search_variants(client, keyword):
    result = data(client.get("/api/search", query_string={"q": keyword}))
    assert [s["id"] for s in result["results"]] == ["HV"]


def test_search_limit_and_no_match(client):
    assert len(data(client.get("/api/search?q=hinh&limit=2"))["results"]) == 2
    assert data(client.get("/api/search?q=khong_co_hinh"))["results"] == []


def test_taxonomy_real_graph(client):
    result = data(client.get("/api/graph/taxonomy"))
    assert len(result["nodes"]) == 7 and len(result["edges"]) == 7
    links = {(e["from"], e["to"]) for e in result["edges"]}
    assert links == {("Shape:HTC", "Shape:HT"), ("Shape:HT", "Shape:TQ"), ("Shape:HBH", "Shape:TQ"),
                     ("Shape:HCN", "Shape:HBH"), ("Shape:HTHOI", "Shape:HBH"), ("Shape:HV", "Shape:HCN"), ("Shape:HV", "Shape:HTHOI")}
    assert all(e["type"] == "IS_A" for e in result["edges"])


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_neighborhood_matches_q14(client, depth):
    result = data(client.get(f"/api/graph/neighborhood/HV?depth={depth}"))
    expected = EXPECTED["Q14"][str(depth)]
    assert len(result["nodes"]) == expected["nodes"]
    assert len(result["edges"]) == expected["relationships"]
    query = data(client.get(f"/api/queries/Q14?shape_id=HV&depth={depth}"))["graph"]
    assert result["nodes"] == query["nodes"] and result["edges"] == query["edges"]


def test_query_catalog(client):
    catalog = data(client.get("/api/queries"))
    assert [q["id"] for q in catalog] == [f"Q{i:02d}" for i in range(1, 16)]
    assert all({"id", "title", "description", "parameter_schema"} <= set(q) for q in catalog)
    assert next(q for q in catalog if q["id"] == "Q14")["parameter_schema"]["depth"]["enum"] == [1, 2, 3]


@pytest.mark.parametrize("query_id", [f"Q{i:02d}" for i in range(1, 16)])
def test_all_15_whitelist_queries_execute_real_neo4j(client, query_id):
    result = data(client.get(f"/api/queries/{query_id}"))
    rows = result["rows"]
    assert result["query_id"] == query_id and "$dataset" in result["cypher"]
    if query_id in {"Q02", "Q10", "Q11"}:
        assert sorted(row["property_id"] for row in rows) == sorted(EXPECTED[query_id])
    elif query_id in {"Q03", "Q04", "Q05", "Q06", "Q07", "Q08", "Q12"}:
        assert sorted(row["shape_id"] for row in rows) == sorted(EXPECTED[query_id])
    elif query_id in {"Q09", "Q15"}:
        assert sorted(row["node_ids"] for row in rows) == sorted(EXPECTED[query_id])
    elif query_id == "Q13":
        assert rows == EXPECTED[query_id]
    elif query_id == "Q01":
        assert len(result["graph"]["nodes"]) == 44 and len(result["graph"]["edges"]) == 79
    elif query_id == "Q14":
        assert len(result["graph"]["nodes"]) == 39 and len(result["graph"]["edges"]) == 71


def test_post_query_parameters(client):
    result = data(client.post("/api/queries/Q14", json={"shape_id": "HCN", "depth": 1}))
    assert result["parameters"] == {"shape_id": "HCN", "depth": 1}
    assert any(n["id"] == "Shape:HCN" for n in result["graph"]["nodes"])


@pytest.mark.parametrize("path,status", [
    ("/api/shapes/UNKNOWN", 404), ("/api/shapes/UNKNOWN/properties", 404),
    ("/api/shapes/UNKNOWN/conditions", 404), ("/api/shapes/UNKNOWN/ancestors", 404),
    ("/api/graph/neighborhood/UNKNOWN", 404), ("/api/queries/Q99", 404),
    ("/api/queries/Q00", 404), ("/api/queries/DELETE", 404),
    ("/api/graph/neighborhood/HV?depth=0", 400), ("/api/graph/neighborhood/HV?depth=4", 400),
    ("/api/graph/neighborhood/HV?depth=1.5", 400), ("/api/graph/neighborhood/HV?depth=-1", 400),
    ("/api/graph/neighborhood/HV?depth=abc", 400), ("/api/graph/neighborhood/HV?depth=1&depth=2", 400),
    ("/api/search", 400), ("/api/search?q=", 400), ("/api/search?q=%20%20", 400),
    ("/api/search?q=hinh&limit=0", 400), ("/api/search?q=hinh&limit=51", 400),
    ("/api/queries/Q14?depth=4", 400), ("/api/queries/Q14?shape_id=UNKNOWN", 404),
    ("/api/queries/Q06?cypher=MATCH", 400), ("/api/queries/Q06?dataset=another", 400),
    ("/api/graph/neighborhood/HV?relationship_type=ANY", 400), ("/missing", 404),
])
def test_invalid_inputs_consistent_errors(client, path, status):
    response = client.get(path)
    assert response.status_code == status
    body = response.get_json()
    assert body["success"] is False and {"code", "message"} <= set(body["error"])
    assert "Traceback" not in response.get_data(as_text=True)


@pytest.mark.parametrize("payload", [{"cypher": "MATCH (n) DETACH DELETE n"}, {"dataset": "another"},
                                      {"depth": True}, {"depth": 1.5}, {"shape_id": []}, [], {"depth": "1" * 5000}])
def test_post_rejects_arbitrary_cypher_and_bad_types(client, payload):
    assert client.post("/api/queries/Q14", json=payload).status_code == 400


def test_injection_stays_a_search_parameter(client):
    before = data(client.get("/api/stats"))
    result = data(client.get("/api/search", query_string={"q": "') MATCH (n) DETACH DELETE n //"}))
    assert result["results"] == []
    assert data(client.get("/api/stats")) == before
    assert client.get("/api/shapes/HV%27").status_code == 400


def test_responses_do_not_expose_credentials(client, app):
    secret = app.config["NEO4J_PASSWORD"]
    for path in ["/api/health", "/api/stats", "/api/shapes/HV", "/api/queries/Q01", "/api/queries/Q99"]:
        body = client.get(path).get_data(as_text=True)
        safe = secret not in body and "NEO4J_PASSWORD" not in body and "bolt://" not in body
        assert safe, "A response exposed connection configuration"


def test_real_unavailable_connection_returns_503():
    # Gọi driver thật tới cổng không có server; không tắt instance đang phục vụ project.
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        closed_port = sock.getsockname()[1]
    app = create_app({"TESTING": True, "NEO4J_URI": f"bolt://127.0.0.1:{closed_port}",
                      "NEO4J_CONNECTION_TIMEOUT": 0.5, "NEO4J_MAX_RETRY_TIME": 0.0})
    try:
        with app.test_client() as client:
            for path in ("/api/health", "/api/stats", "/api/shapes/HV"):
                response = client.get(path)
                assert response.status_code == 503
                assert response.get_json()["error"]["code"] == "NEO4J_UNAVAILABLE"
                if path == "/api/health":
                    assert response.get_json()["data"]["flask"] == "running"
                    assert response.get_json()["data"]["neo4j"] == "unavailable"
    finally:
        app.extensions["neo4j"].close()


def test_actual_cypher_error_is_sanitized(app):
    with pytest.raises(APIError) as caught:
        app.extensions["neo4j"].read("WITH $dataset AS dataset RETURN nonexistent_variable")
    assert caught.value.code == "NEO4J_QUERY_ERROR" and caught.value.status == 500
    assert "nonexistent_variable" not in caught.value.message
