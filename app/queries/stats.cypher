MATCH (n:ProjectEntity {dataset:$dataset})
WITH count(n) AS total_nodes,
     sum(CASE WHEN n:Shape THEN 1 ELSE 0 END) AS shapes,
     sum(CASE WHEN n:Property THEN 1 ELSE 0 END) AS properties,
     sum(CASE WHEN n:Condition THEN 1 ELSE 0 END) AS conditions
OPTIONAL MATCH (:ProjectEntity {dataset:$dataset})-[r]->(:ProjectEntity {dataset:$dataset})
RETURN total_nodes,{Shape:shapes,Property:properties,Condition:conditions} AS node_counts,
       count(r) AS total_relationships,collect(type(r)) AS relationship_types;
