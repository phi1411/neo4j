// Chạy với :param dataset => 'quadrilateral-v1'
// Mỗi kiểm tra phải trả một dòng violations=0. Không sửa/xóa dữ liệu.

// @validation V01
// Trùng ID trong cùng label/dataset.
UNWIND ['Shape','Property','Condition'] AS kind
MATCH (n:ProjectEntity {dataset: $dataset}) WHERE kind IN labels(n)
WITH kind, n.id AS id, count(*) AS copies WHERE copies > 1
RETURN count(*) AS violations;

// @validation V02
// Trùng relationship theo đầu nguồn, loại cạnh, đầu đích.
MATCH (a:ProjectEntity {dataset: $dataset})-[r]->(b:ProjectEntity {dataset: $dataset})
WITH a, b, type(r) AS kind, count(*) AS copies WHERE copies > 1
RETURN count(*) AS violations;

// @validation V03
// Orphan xét tất cả loại cạnh nội bộ, không chỉ HAS_PROPERTY.
MATCH (n:ProjectEntity {dataset: $dataset})
WHERE NOT EXISTS { MATCH (n)--(:ProjectEntity {dataset: $dataset}) }
RETURN count(n) AS violations;

// @validation V04
// Self-loop ở mọi loại cạnh.
MATCH (n:ProjectEntity {dataset: $dataset})-[r]->(n)
RETURN count(r) AS violations;

// @validation V05
// Chu trình có hướng IS_A. Validation trên dataset nhỏ; demo traversal vẫn có giới hạn.
MATCH path=(s:Shape:ProjectEntity {dataset: $dataset})-[:IS_A*1..]->(s)
WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN count(DISTINCT s) AS violations;

// @validation V06
// Tập cạnh taxonomy phải khớp đúng bảy cặp, kiểm tra cả thiếu và thừa.
CALL () {
  UNWIND [['HTC','HT'],['HT','TQ'],['HBH','TQ'],['HCN','HBH'],['HTHOI','HBH'],['HV','HCN'],['HV','HTHOI']] AS pair
  OPTIONAL MATCH (:Shape:ProjectEntity {dataset: $dataset, id: pair[0]})-[r:IS_A]->(:Shape:ProjectEntity {dataset: $dataset, id: pair[1]})
  WITH pair, r WHERE r IS NULL RETURN pair AS bad
  UNION ALL
  MATCH (a:Shape:ProjectEntity {dataset: $dataset})-[:IS_A]->(b:Shape:ProjectEntity {dataset: $dataset})
  WHERE NOT [a.id,b.id] IN [['HTC','HT'],['HT','TQ'],['HBH','TQ'],['HCN','HBH'],['HTHOI','HBH'],['HV','HCN'],['HV','HTHOI']]
  RETURN [a.id,b.id] AS bad
}
RETURN count(*) AS violations;

// @validation V07
// Hai cạnh bị loại khỏi mô hình phải không tồn tại.
MATCH (a:Shape:ProjectEntity {dataset: $dataset})-[r:IS_A]->(b:Shape:ProjectEntity {dataset: $dataset})
WHERE [a.id,b.id] IN [['HBH','HT'],['HCN','HTC']]
RETURN count(r) AS violations;

// @validation V08
// Nhãn và trường chung bắt buộc.
MATCH (n:ProjectEntity {dataset: $dataset})
WHERE size([l IN labels(n) WHERE l IN ['Shape','Property','Condition']]) <> 1
   OR trim(coalesce(n.id,'')) = '' OR trim(coalesce(n.name,'')) = ''
   OR trim(coalesce(n.source_ref,'')) = ''
RETURN count(n) AS violations;

// @validation V09
// Trường bắt buộc theo loại và logic AND của Condition.
MATCH (n:ProjectEntity {dataset: $dataset})
WHERE (n:Shape AND (trim(coalesce(n.definition,'')) = '' OR trim(coalesce(n.search_name,'')) = '' OR n.display_order IS NULL))
   OR (n:Property AND (trim(coalesce(n.category,'')) = '' OR trim(coalesce(n.description,'')) = '' OR trim(coalesce(n.notation,'')) = ''))
   OR (n:Condition AND (trim(coalesce(n.statement,'')) = '' OR trim(coalesce(n.explanation,'')) = '' OR coalesce(n.logic,'') <> 'AND'))
RETURN count(n) AS violations;

// @validation V10
// Kiểu relationship và label hai đầu phải đúng schema.
MATCH (a)-[r]->(b)
WHERE a.dataset = $dataset OR b.dataset = $dataset
WITH a,b,r,
  CASE type(r)
    WHEN 'IS_A' THEN a:Shape AND b:Shape
    WHEN 'HAS_PROPERTY' THEN a:Shape AND b:Property
    WHEN 'HAS_CONDITION' THEN a:Shape AND b:Condition
    WHEN 'REQUIRES_SHAPE' THEN a:Condition AND b:Shape
    WHEN 'REQUIRES_PROPERTY' THEN a:Condition AND b:Property
    ELSE false
  END AS valid
WHERE NOT valid RETURN count(r) AS violations;

// @validation V11
// Không có cạnh nối qua ranh giới dataset project.
MATCH (a)-[r]->(b)
WHERE (coalesce(a.dataset,'') = $dataset) <> (coalesce(b.dataset,'') = $dataset)
RETURN count(r) AS violations;

// @validation V12
// Mỗi Condition có đúng một kết luận, một ngữ cảnh và ít nhất một giả thiết.
MATCH (c:Condition:ProjectEntity {dataset: $dataset})
WHERE size([(s:Shape)-[:HAS_CONDITION]->(c) WHERE s.dataset = $dataset | s]) <> 1
   OR size([(c)-[:REQUIRES_SHAPE]->(s:Shape) WHERE s.dataset = $dataset | s]) <> 1
   OR size([(c)-[:REQUIRES_PROPERTY]->(p:Property) WHERE p.dataset = $dataset | p]) < 1
RETURN count(c) AS violations;

// @validation V13
// C_HV_05 có đúng hai giả thiết AND; mọi Condition khác có đúng một Property.
MATCH (c:Condition:ProjectEntity {dataset: $dataset})
OPTIONAL MATCH (c)-[:REQUIRES_PROPERTY]->(p:Property:ProjectEntity {dataset: $dataset})
WITH c, collect(p.id) AS ids
WHERE (c.id = 'C_HV_05' AND (size(ids) <> 2 OR NOT 'FOUR_EQUAL_SIDES' IN ids OR NOT 'FOUR_RIGHT_ANGLES' IN ids))
   OR (c.id <> 'C_HV_05' AND size(ids) <> 1)
RETURN count(c) AS violations;

// @validation V14
// Mọi hình chuyên biệt phải có đường phân loại tới TQ.
MATCH (s:Shape:ProjectEntity {dataset: $dataset}) WHERE s.id <> 'TQ'
AND NOT EXISTS {
  MATCH path=(s)-[:IS_A*1..6]->(:Shape:ProjectEntity {dataset: $dataset,id:'TQ'})
  WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
}
RETURN count(s) AS violations;

// @validation V15
// Số lượng node theo label và relationship theo loại.
MATCH (n:ProjectEntity {dataset: $dataset})
WITH collect(n) AS ns
OPTIONAL MATCH (:ProjectEntity {dataset: $dataset})-[r]->(:ProjectEntity {dataset: $dataset})
WITH ns, collect(type(r)) AS ts
RETURN CASE WHEN size(ns)=44
  AND size([n IN ns WHERE n:Shape])=7 AND size([n IN ns WHERE n:Property])=19 AND size([n IN ns WHERE n:Condition])=18
  AND size(ts)=79 AND size([t IN ts WHERE t='IS_A'])=7
  AND size([t IN ts WHERE t='HAS_PROPERTY'])=17 AND size([t IN ts WHERE t='HAS_CONDITION'])=18
  AND size([t IN ts WHERE t='REQUIRES_SHAPE'])=18 AND size([t IN ts WHERE t='REQUIRES_PROPERTY'])=19
  THEN 0 ELSE 1 END AS violations;

// @validation V16
// Node gắn dataset project phải có nhãn ProjectEntity.
MATCH (n {dataset: $dataset}) WHERE NOT n:ProjectEntity RETURN count(n) AS violations;

// @validation V17
// Không đồng thời kế thừa đúng một cặp và hai cặp cạnh song song.
MATCH path=(s:Shape:ProjectEntity {dataset: $dataset})-[:IS_A*0..6]->(:Shape)-[:HAS_PROPERTY]->(p:Property)
WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
WITH s,collect(DISTINCT p.id) AS ids
WHERE 'EXACTLY_ONE_PARALLEL_PAIR' IN ids AND 'TWO_PARALLEL_PAIRS' IN ids
RETURN count(s) AS violations;

// @validation V18
// Tập ID Shape chính xác, không chỉ kiểm tra số lượng.
MATCH (s:Shape:ProjectEntity {dataset: $dataset})
WITH collect(s.id) AS ids
RETURN CASE WHEN size(ids)=7 AND all(id IN ['TQ','HT','HTC','HBH','HCN','HTHOI','HV'] WHERE id IN ids)
THEN 0 ELSE 1 END AS violations;

// @validation V19
// HTC và HCN khai báo độc lập tính chất đường chéo bằng nhau; HV không sao chép HAS_PROPERTY.
CALL () {
  UNWIND ['HTC','HCN'] AS id
  OPTIONAL MATCH (:Shape:ProjectEntity {dataset:$dataset,id:id})-[r:HAS_PROPERTY]->(:Property:ProjectEntity {dataset:$dataset,id:'DIAGONALS_EQUAL'})
  WITH id,r WHERE r IS NULL RETURN id AS bad
  UNION ALL
  MATCH (:Shape:ProjectEntity {dataset:$dataset,id:'HV'})-[r:HAS_PROPERTY]->(:Property:ProjectEntity {dataset:$dataset})
  RETURN 'HV' AS bad
}
RETURN count(*) AS violations;

// @validation V20
// Ba Property chỉ dùng cho giả thiết phải vẫn có cạnh REQUIRES_PROPERTY.
UNWIND ['THREE_RIGHT_ANGLES','HAS_RIGHT_ANGLE','ADJACENT_SIDES_EQUAL'] AS id
OPTIONAL MATCH (:Condition:ProjectEntity {dataset:$dataset})-[r:REQUIRES_PROPERTY]->(:Property:ProjectEntity {dataset:$dataset,id:id})
WITH id,count(r) AS refs WHERE refs=0 RETURN count(*) AS violations;
