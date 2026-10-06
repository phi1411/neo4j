import pytest

from app import create_app
from scripts.phase2 import digest, graph


@pytest.fixture(scope="session")
def app():
    application = create_app({"TESTING": True})
    db = application.extensions["neo4j"]
    db.verify()  # Nếu Neo4j thật chưa sẵn sàng: fail, không skip hay chuyển mock.
    before = digest(graph(db.driver, db.database))
    yield application
    after = digest(graph(db.driver, db.database))
    db.close()
    assert after == before, "Backend/integration tests changed the dataset"


@pytest.fixture()
def client(app):
    return app.test_client()


def data(response):
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    return body["data"]
