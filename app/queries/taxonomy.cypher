MATCH (s:Shape:ProjectEntity {dataset:$dataset})
WITH collect(s) AS nodes
OPTIONAL MATCH (:Shape:ProjectEntity {dataset:$dataset})-[r:IS_A]->(:Shape:ProjectEntity {dataset:$dataset})
RETURN nodes,collect(r) AS edges;
