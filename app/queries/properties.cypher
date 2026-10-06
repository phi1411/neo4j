MATCH path=(s:Shape:ProjectEntity {dataset:$dataset,id:$shape_id})-[:IS_A*0..6]->(owner:Shape)
      -[:HAS_PROPERTY]->(p:Property)
WHERE all(n IN nodes(path) WHERE n.dataset=$dataset AND n:ProjectEntity)
WITH s,p,collect(DISTINCT owner{.id,.name}) AS declared_at,
     collect(DISTINCT {shape_ids:[n IN nodes(path)[..-1] | n.id],
                       shape_names:[n IN nodes(path)[..-1] | n.name]}) AS inheritance_paths
RETURN p{.id,.name,.category,.description,.notation,.source_ref} AS property,
       any(owner IN declared_at WHERE owner.id=s.id) AS direct,
       any(owner IN declared_at WHERE owner.id<>s.id) AS inherited,
       declared_at,inheritance_paths
ORDER BY property.id;
