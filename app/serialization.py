"""Định danh graph ổn định theo label/ID nghiệp vụ, không dùng internal ID."""
from neo4j.graph import Node, Path, Relationship

PUBLIC_FIELDS = {
    "Shape": {"id", "name", "definition", "search_name", "display_order", "source_ref"},
    "Property": {"id", "name", "category", "description", "notation", "source_ref"},
    "Condition": {"id", "name", "statement", "explanation", "logic", "source_ref"},
}


def node_json(node):
    kind = next(label for label in PUBLIC_FIELDS if label in node.labels)
    return {"id": f"{kind}:{node['id']}", "entity_id": node["id"], "label": node["name"], "type": kind,
            "properties": {field: node[field] for field in sorted(PUBLIC_FIELDS[kind]) if field in node}}


def edge_json(edge):
    source, target = node_json(edge.start_node)["id"], node_json(edge.end_node)["id"]
    return {"id": f"{source}|{edge.type}|{target}", "from": source, "to": target,
            "type": edge.type, "label": edge.type}


def graph_json(nodes, edges):
    ns = {n["id"]: n for n in (node_json(node) for node in nodes)}
    es = {e["id"]: e for e in (edge_json(edge) for edge in edges)}
    return {"nodes": [ns[k] for k in sorted(ns)], "edges": [es[k] for k in sorted(es)]}


def result_json(rows):
    nodes, edges = {}, {}

    def encode(value):
        if isinstance(value, Node):
            item = node_json(value)
            nodes[item["id"]] = item
            return item
        if isinstance(value, Relationship):
            encode(value.start_node)
            encode(value.end_node)
            item = edge_json(value)
            edges[item["id"]] = item
            return item
        if isinstance(value, Path):
            return {"nodes": [encode(n) for n in value.nodes], "edges": [encode(e) for e in value.relationships]}
        if isinstance(value, dict):
            return {key: encode(val) for key, val in value.items()}
        if isinstance(value, (tuple, list)):
            return [encode(val) for val in value]
        return value

    encoded = [encode(row) for row in rows]
    return {"rows": encoded, "graph": {"nodes": [nodes[k] for k in sorted(nodes)], "edges": [edges[k] for k in sorted(edges)]}}
