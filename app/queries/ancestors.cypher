MATCH path=(:Shape:ProjectEntity {dataset:$dataset,id:$shape_id})-[:IS_A*1..6]->(a:Shape)
WHERE all(n IN nodes(path) WHERE n.dataset=$dataset AND n:ProjectEntity)
RETURN a{.id,.name} AS shape,min(length(path)) AS distance
ORDER BY distance,shape.id;
