MATCH (s:Shape:ProjectEntity {dataset:$dataset})
WHERE s.search_name CONTAINS $search
RETURN s{.id,.name,.definition,.search_name,.display_order} AS shape
ORDER BY s.display_order,s.id LIMIT $limit;
