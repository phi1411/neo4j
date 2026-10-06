from app.errors import APIError
from app.serialization import result_json
from app.validation import integer, shape_id

TITLES = [
    ("Toàn bộ graph", "Xem các node và relationship trong dataset của project."),
    ("Tính chất của một hình", "Tổng hợp tính chất trực tiếp, kế thừa và nguồn khai báo."),
    ("Cha trực tiếp", "Tìm các loại hình tổng quát nối bằng một cạnh IS_A."),
    ("Mọi tổ tiên", "Duyệt IS_A nhiều cấp và loại kết quả trùng do đa kế thừa."),
    ("Trường hợp đặc biệt của hình bình hành", "Tìm hình chữ nhật, hình thoi và hình vuông qua traversal."),
    ("Bốn cạnh bằng nhau", "Tìm các loại hình luôn có bốn cạnh bằng nhau, gồm kế thừa."),
    ("Bốn góc vuông", "Tìm các loại hình luôn có bốn góc vuông."),
    ("Đường chéo bằng nhau", "Tìm các nhánh chia sẻ tính chất đường chéo bằng nhau."),
    ("Đường phân loại từ tứ giác", "Xem các đường IS_A từ tứ giác tới hình được chọn."),
    ("Tính chất chung vuông và chữ nhật", "Lấy giao hai tập tính chất hiệu lực."),
    ("Tính chất chung vuông và thoi", "Lấy giao hai tập tính chất hiệu lực."),
    ("Hai tính chất đường chéo đồng thời", "Tìm hình có đường chéo vuông góc AND chia đôi nhau."),
    ("Thống kê cạnh theo loại hình", "Đếm cạnh trực tiếp theo loại và theo chiều vào/ra."),
    ("Graph lân cận", "Tìm node trong bán kính 1–3 và mọi cạnh nội bộ giữa chúng."),
    ("Giải thích nguồn tính chất", "Xem hai đường kế thừa tính chất chia đôi đường chéo của hình vuông."),
]
SHAPE_QUERIES = {"Q02", "Q03", "Q04", "Q09", "Q14"}


class QueryService:
    def __init__(self, db, shapes, demos):
        self.db, self.shapes, self.demos = db, shapes, demos

    def definition(self, query_id):
        if query_id not in self.demos:
            raise APIError("QUERY_NOT_FOUND", "Query không nằm trong danh sách Q01–Q15.", 404)
        index = int(query_id[1:]) - 1
        schema = {}
        if query_id in SHAPE_QUERIES:
            schema["shape_id"] = {"type": "string", "default": "HV", "pattern": "^[A-Z][A-Z0-9_]{0,31}$"}
        if query_id == "Q14":
            schema["depth"] = {"type": "integer", "default": 3, "enum": [1, 2, 3]}
        return {"id": query_id, "title": TITLES[index][0], "description": TITLES[index][1], "parameter_schema": schema}

    def list(self):
        return [self.definition(code) for code in sorted(self.demos)]

    def run(self, query_id, submitted):
        definition = self.definition(query_id)
        schema = definition["parameter_schema"]
        if set(submitted) - set(schema):
            raise APIError("UNKNOWN_PARAMETER", "Query nhận tham số không được hỗ trợ.")
        params = {}
        if "shape_id" in schema:
            params["shape_id"] = shape_id(submitted.get("shape_id", "HV"))
        if "depth" in schema:
            params["depth"] = integer(submitted.get("depth", 3), "depth", 1, 3)
        # Validate đầy đủ trước khi kiểm tra hình/tới database.
        if "shape_id" in params:
            self.shapes.get(params["shape_id"])
        rows = self.db.read(self.demos[query_id], params)
        return {"query_id": query_id, "title": definition["title"], "parameters": params,
                "cypher": self.demos[query_id], **result_json(rows)}
