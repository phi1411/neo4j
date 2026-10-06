import pytest
from neo4j.exceptions import AuthError, ConfigurationError, ServiceUnavailable

from app import create_app
from app.db import translate_error
from app.errors import APIError
from app.validation import integer, normalize_search, shape_id

pytestmark = pytest.mark.unit


def test_vietnamese_search_normalization():
    assert normalize_search("  ĐƯỜNG chéo  ") == "duong cheo"
    assert normalize_search("HÌNH VUÔNG") == "hinh vuong"


@pytest.mark.parametrize("value", [None, "", "   ", "\u0301", "x" * 201])
def test_invalid_search(value):
    with pytest.raises(APIError):
        normalize_search(value)


@pytest.mark.parametrize("value", [True, False, 0, 4, -1, 1.5, "1.0", "0000", "abc", None])
def test_depth_type_validation(value):
    with pytest.raises(APIError):
        integer(value, "depth", 1, 3)


def test_shape_id_validation():
    assert shape_id(" hv ") == "HV"
    with pytest.raises(APIError):
        shape_id("HV') MATCH (n)")


@pytest.mark.parametrize("exc,code", [(AuthError("private diagnostic"), "NEO4J_AUTH_ERROR"),
                                     (ConfigurationError("private diagnostic"), "CONFIGURATION_ERROR"),
                                     (ServiceUnavailable("private diagnostic"), "NEO4J_UNAVAILABLE")])
def test_driver_error_mapping_sanitizes_details(exc, code):
    error = translate_error(exc)
    assert error.code == code and error.status == 503
    assert "private diagnostic" not in error.message


def test_missing_configuration_keeps_health_available(tmp_path, monkeypatch):
    for name in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "NEO4J_DATABASE"):
        monkeypatch.delenv(name, raising=False)
    app = create_app({"TESTING": True}, env_file=tmp_path / "missing.env")
    try:
        client = app.test_client()
        response = client.get("/api/health")
        assert response.status_code == 503
        assert response.get_json()["error"]["code"] == "CONFIGURATION_ERROR"
        assert response.get_json()["data"]["flask"] == "running"
        assert client.get("/api/stats").status_code == 503
    finally:
        app.extensions["neo4j"].close()


def test_unexpected_http_error_does_not_expose_message(monkeypatch, tmp_path):
    app = create_app({"TESTING": True, "NEO4J_PASSWORD": ""}, env_file=tmp_path / "missing.env")
    def fail():
        raise RuntimeError("private diagnostic including credentials")
    monkeypatch.setattr(app.extensions["services"]["stats"], "get", fail)
    try:
        response = app.test_client().get("/api/stats")
        assert response.status_code == 500
        assert response.get_json()["error"]["code"] == "INTERNAL_ERROR"
        assert "private diagnostic" not in response.get_data(as_text=True)
    finally:
        app.extensions["neo4j"].close()
