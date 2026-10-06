from app.errors import APIError
from app.queries import load


class ShapeService:
    def __init__(self, db):
        self.db = db

    def list(self):
        return [r["shape"] for r in self.db.read(load("shapes.cypher"))]

    def get(self, shape_id):
        rows = self.db.read(load("shape.cypher"), {"shape_id": shape_id})
        if not rows:
            raise APIError("SHAPE_NOT_FOUND", "Không tìm thấy loại hình này.", 404)
        return rows[0]["shape"]

    def parents(self, shape_id):
        return [r["shape"] for r in self.db.read(load("parents.cypher"), {"shape_id": shape_id})]

    def ancestors(self, shape_id):
        return [{**r["shape"], "distance": r["distance"]}
                for r in self.db.read(load("ancestors.cypher"), {"shape_id": shape_id})]

    def properties(self, shape_id):
        rows = self.db.read(load("properties.cypher"), {"shape_id": shape_id})
        return [{**r["property"], "direct": r["direct"], "inherited": r["inherited"],
                 "declared_at": sorted(r["declared_at"], key=lambda s: s["id"]),
                 "inheritance_paths": sorted(r["inheritance_paths"], key=lambda p: p["shape_ids"])} for r in rows]

    def conditions(self, shape_id):
        rows = self.db.read(load("conditions.cypher"), {"shape_id": shape_id})
        return [{"condition_id": r["condition"]["id"],
                 **{k: v for k, v in r["condition"].items() if k != "id"},
                 "required_shape": r["required_shape"],
                 "required_properties": sorted(r["required_properties"], key=lambda p: p["id"])} for r in rows]

    def detail(self, shape_id):
        shape = self.get(shape_id)
        properties = self.properties(shape_id)
        return {"shape": shape, "direct_parents": self.parents(shape_id),
                "ancestors": self.ancestors(shape_id), "effective_properties": properties,
                "direct_properties": [p for p in properties if p["direct"]],
                "conditions": self.conditions(shape_id), "condition_combination": "OR"}

    def search(self, normalized, limit):
        return [r["shape"] for r in self.db.read(load("search.cypher"), {"search": normalized, "limit": limit})]
