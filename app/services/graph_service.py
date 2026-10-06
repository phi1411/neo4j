from app.queries import load
from app.serialization import graph_json


class GraphService:
    def __init__(self, db, demos):
        self.db, self.demos = db, demos

    def taxonomy(self):
        row = self.db.read(load("taxonomy.cypher"))[0]
        return graph_json(row["nodes"], row["edges"])

    def neighborhood(self, shape_id, depth):
        # Tái sử dụng nguyên Q14 đã kiểm thử; không sao chép/tạo graph JSON tĩnh.
        row = self.db.read(self.demos["Q14"], {"shape_id": shape_id, "depth": depth})[0]
        return {"shape_id": shape_id, "depth": depth, **graph_json(row["nodes"], row["relationships"])}
