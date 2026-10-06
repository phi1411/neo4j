from flask import Blueprint, current_app, request

from app.config import DATASET
from app.errors import APIError, failure, success
from app.validation import integer, normalize_search, shape_id

api = Blueprint("api", __name__, url_prefix="/api")


def service(name):
    return current_app.extensions["services"][name]


def arguments(allowed=()):
    if set(request.args) - set(allowed) or any(len(request.args.getlist(k)) != 1 for k in request.args):
        raise APIError("UNKNOWN_PARAMETER", "Tham số không được hỗ trợ hoặc bị lặp.")
    return request.args.to_dict()


def existing_id(value):
    normalized = shape_id(value)
    service("shapes").get(normalized)
    return normalized


@api.get("/health")
def health():
    arguments()
    db = current_app.extensions["neo4j"]
    data = {"flask": "running", "neo4j": "connected", "database": db.database, "dataset": DATASET}
    try:
        db.verify()
    except APIError as error:
        data["neo4j"] = "unavailable"
        return failure(error, data)
    return success(data)


@api.get("/stats")
def stats():
    arguments()
    return success(service("stats").get())


@api.get("/shapes")
def shapes():
    arguments()
    return success(service("shapes").list())


@api.get("/shapes/<value>")
def detail(value):
    arguments()
    return success(service("shapes").detail(shape_id(value)))


@api.get("/shapes/<value>/properties")
def properties(value):
    arguments()
    return success(service("shapes").properties(existing_id(value)))


@api.get("/shapes/<value>/conditions")
def conditions(value):
    arguments()
    return success({"combination": "OR", "items": service("shapes").conditions(existing_id(value))})


@api.get("/shapes/<value>/ancestors")
def ancestors(value):
    arguments()
    return success(service("shapes").ancestors(existing_id(value)))


@api.get("/search")
def search():
    args = arguments({"q", "limit"})
    normalized = normalize_search(args.get("q", ""))
    limit = integer(args.get("limit", 10), "limit", 1, 50)
    return success({"normalized_query": normalized, "limit": limit,
                    "results": service("shapes").search(normalized, limit)})


@api.get("/graph/taxonomy")
def taxonomy():
    arguments()
    return success(service("graphs").taxonomy())


@api.get("/graph/neighborhood/<value>")
def neighborhood(value):
    args = arguments({"depth"})
    depth = integer(args.get("depth", 1), "depth", 1, 3)
    return success(service("graphs").neighborhood(existing_id(value), depth))


@api.get("/queries")
def queries():
    arguments()
    return success(service("queries").list())


@api.route("/queries/<query_id>", methods=["GET", "POST"])
def run_query(query_id):
    if request.method == "POST":
        arguments()
        submitted = request.get_json() if request.get_data() else {}
        if not isinstance(submitted, dict):
            raise APIError("INVALID_BODY", "Nội dung JSON phải là một object tham số.")
    else:
        # QueryService xác thực whitelist, parameter schema và giá trị.
        submitted = arguments(request.args.keys())
    return success(service("queries").run(query_id, submitted))
