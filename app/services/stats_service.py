from collections import Counter

from app.queries import load


class StatsService:
    def __init__(self, db):
        self.db = db

    def get(self):
        row = self.db.read(load("stats.cypher"))[0]
        return {"node_counts": row["node_counts"], "total_nodes": row["total_nodes"],
                "relationship_counts": dict(sorted(Counter(row["relationship_types"]).items())),
                "total_relationships": row["total_relationships"]}
