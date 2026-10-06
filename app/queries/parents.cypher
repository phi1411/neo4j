MATCH (:Shape:ProjectEntity {dataset:$dataset,id:$shape_id})-[:IS_A]->(p:Shape:ProjectEntity {dataset:$dataset})
RETURN DISTINCT p{.id,.name} AS shape ORDER BY shape.id;
