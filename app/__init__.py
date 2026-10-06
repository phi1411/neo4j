import atexit

from flask import Flask
from werkzeug.exceptions import HTTPException

from app.config import load_config
from app.db import Neo4jDatabase
from app.errors import APIError, failure
from app.queries import demo_queries
from app.routes.api import api
from app.routes.web import web
from app.services.graph_service import GraphService
from app.services.query_service import QueryService
from app.services.shape_service import ShapeService
from app.services.stats_service import StatsService


def create_app(overrides=None, *, env_file=None):
    app = Flask(__name__)
    app.config.update(load_config(env_file))
    if overrides:
        app.config.update(overrides)
    app.json.ensure_ascii = False
    db = Neo4jDatabase(app.config)
    app.extensions["neo4j"] = db
    # Đóng một lần khi tiến trình kết thúc, không teardown driver sau mỗi request.
    atexit.register(db.close)
    demos = demo_queries()
    shapes = ShapeService(db)
    app.extensions["services"] = {"shapes": shapes, "graphs": GraphService(db, demos),
                                  "queries": QueryService(db, shapes, demos), "stats": StatsService(db)}
    try:
        db.verify()
    except APIError as error:
        # Server vẫn lên để health trả lỗi thật; không thay thế bằng dữ liệu fallback.
        app.logger.warning("Neo4j startup check: %s", error.code)
    app.register_blueprint(api)
    app.register_blueprint(web)

    @app.errorhandler(APIError)
    def api_error(error):
        return failure(error)

    @app.errorhandler(HTTPException)
    def http_error(error):
        code = "NOT_FOUND" if error.code == 404 else "HTTP_ERROR"
        message = "Không tìm thấy endpoint." if error.code == 404 else "Yêu cầu HTTP không hợp lệ."
        return failure(APIError(code, message, error.code))

    @app.errorhandler(Exception)
    def unexpected_error(error):
        # Chỉ log tên loại lỗi, không stack trace/message chứa dữ liệu riêng.
        app.logger.error("Application error: %s", type(error).__name__)
        return failure(APIError("INTERNAL_ERROR", "Ứng dụng gặp lỗi xử lý yêu cầu.", 500))

    return app
