MATCH (s:Shape:ProjectEntity {dataset:$dataset})
RETURN s{.id,.name,.definition,.search_name,.display_order} AS shape
ORDER BY s.display_order,s.id;
