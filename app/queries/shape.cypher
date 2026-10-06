MATCH (s:Shape:ProjectEntity {dataset:$dataset,id:$shape_id})
RETURN s{.id,.name,.definition,.search_name,.display_order,.source_ref} AS shape;
