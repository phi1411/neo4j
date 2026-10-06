MATCH (:Shape:ProjectEntity {dataset:$dataset,id:$shape_id})-[:HAS_CONDITION]->(c:Condition:ProjectEntity {dataset:$dataset})
MATCH (c)-[:REQUIRES_SHAPE]->(base:Shape:ProjectEntity {dataset:$dataset})
MATCH (c)-[:REQUIRES_PROPERTY]->(p:Property:ProjectEntity {dataset:$dataset})
RETURN c{.id,.name,.statement,.logic,.explanation,.source_ref} AS condition,
       base{.id,.name} AS required_shape,
       collect(DISTINCT p{.id,.name,.category,.description,.notation}) AS required_properties
ORDER BY condition.id;
