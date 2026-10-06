"""Một driver/app, session/transaction theo request; chỉ expose thao tác đọc."""
from urllib.parse import urlsplit

from neo4j import GraphDatabase, unit_of_work
from neo4j.exceptions import AuthError, ConfigurationError, DriverError, Neo4jError, ServiceUnavailable, SessionExpired

from app.config import DATASET
from app.errors import APIError


def translate_error(exc):
    # Không dùng str(exc): driver exception có thể chứa URI, query hoặc thông tin riêng.
    if isinstance(exc, AuthError) or (isinstance(exc, Neo4jError) and "Security" in (exc.code or "")):
        return APIError("NEO4J_AUTH_ERROR", "Không thể xác thực với Neo4j. Kiểm tra cấu hình cục bộ.", 503)
    if isinstance(exc, ConfigurationError):
        return APIError("CONFIGURATION_ERROR", "Cấu hình Neo4j không hợp lệ. Kiểm tra file .env.", 503)
    if isinstance(exc, (ServiceUnavailable, SessionExpired, DriverError, OSError)):
        return APIError("NEO4J_UNAVAILABLE", "Không thể kết nối Neo4j. Kiểm tra instance đang chạy.", 503)
    return APIError("NEO4J_QUERY_ERROR", "Truy vấn Neo4j không thực hiện được.", 500)


class Neo4jDatabase:
    def __init__(self, config):
        self.database = config.get("NEO4J_DATABASE") or None
        self.driver = None
        self.query_timeout = config["NEO4J_QUERY_TIMEOUT"]
        self._config_error = None
        required = ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "NEO4J_DATABASE")
        if any(not config.get(key) for key in required):
            self._config_error = APIError("CONFIGURATION_ERROR", "Thiếu cấu hình Neo4j trong .env.", 503)
            return
        try:
            uri = urlsplit(config["NEO4J_URI"])
            if uri.username is not None or uri.password is not None or not uri.hostname:
                raise ValueError("Invalid connection URI")
            if self.database == "system":
                raise ValueError("System database is not an application database")
            self.driver = GraphDatabase.driver(
                config["NEO4J_URI"], auth=(config["NEO4J_USER"], config["NEO4J_PASSWORD"]),
                connection_timeout=config["NEO4J_CONNECTION_TIMEOUT"],
                connection_acquisition_timeout=config["NEO4J_CONNECTION_TIMEOUT"],
                max_transaction_retry_time=config["NEO4J_MAX_RETRY_TIME"],
            )
        except (ValueError, TypeError, ConfigurationError):
            self._config_error = APIError("CONFIGURATION_ERROR", "Cấu hình Neo4j không hợp lệ. Kiểm tra file .env.", 503)

    def _require_driver(self):
        if self._config_error:
            raise self._config_error
        if self.driver is None:
            raise APIError("NEO4J_UNAVAILABLE", "Kết nối Neo4j đã đóng.", 503)

    def verify(self):
        self._require_driver()
        try:
            self.driver.verify_connectivity()
            # Kiểm tra cả database mục tiêu, không chỉ khả năng tới instance.
            self.read("WITH $dataset AS dataset RETURN 1 AS connection_check")
        except APIError:
            raise
        except (Neo4jError, DriverError, OSError) as exc:
            raise translate_error(exc) from None

    def read(self, cypher, parameters=None):
        self._require_driver()
        # Dataset không do request lựa chọn, kể cả khi caller truyền nhầm parameter.
        params = {**(parameters or {}), "dataset": DATASET}
        try:
            with self.driver.session(database=self.database, default_access_mode="READ") as session:
                @unit_of_work(timeout=self.query_timeout)
                def run(tx):
                    # dict(record) giữ kiểu Node/Relationship/Path, khác Record.data().
                    return [dict(record) for record in tx.run(cypher, params)]
                return session.execute_read(run)
        except (Neo4jError, DriverError, OSError) as exc:
            raise translate_error(exc) from None

    def close(self):
        if self.driver is not None:
            self.driver.close()
            self.driver = None
