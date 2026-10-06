// 15 truy vấn chạy trong database quadrilateral.
// Neo4j Query/Browser: khai báo bằng :params {dataset:'quadrilateral-v1',shape_id:'HV',depth:3}
// Runner scripts/phase2.py truyền tham số tương đương qua driver.
// IS_A*0..6 gồm chính hình; DISTINCT xử lý đa kế thừa.

// @query Q01
// Mục đích: xem toàn bộ graph của project, gồm cả node nếu có orphan.
// Expected: 44 node / 79 cạnh; node và relationship dùng được trong graph view.
MATCH (n:ProjectEntity {dataset: $dataset})
WITH collect(n) AS nodes
OPTIONAL MATCH (:ProjectEntity {dataset: $dataset})-[r]->(:ProjectEntity {dataset: $dataset})
RETURN nodes, collect(r) AS relationships;

// @query Q02
// Mục đích: tính chất hiệu lực của HV và lớp khai báo tính chất.
// Expected: 12 tính chất; DIAGONALS_EQUAL từ HCN, chia đôi nhau từ HBH.
MATCH inheritance=(s:Shape:ProjectEntity {dataset: $dataset, id: $shape_id})-[:IS_A*0..6]->(owner:Shape)
MATCH (owner)-[:HAS_PROPERTY]->(p:Property:ProjectEntity {dataset: $dataset})
WHERE all(n IN nodes(inheritance) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN p.id AS property_id, p.name AS property_name,
       collect(DISTINCT owner.id) AS declared_at
ORDER BY property_id;

// @query Q03
// Mục đích: cha trực tiếp của HV. Expected: HCN, HTHOI.
MATCH (:Shape:ProjectEntity {dataset: $dataset, id: $shape_id})-[:IS_A]->(parent:Shape:ProjectEntity {dataset: $dataset})
RETURN DISTINCT parent.id AS shape_id, parent.name AS shape_name ORDER BY shape_id;

// @query Q04
// Mục đích: mọi tổ tiên của HV. Expected: HBH, HCN, HTHOI, TQ; không HT/HTC.
MATCH path=(:Shape:ProjectEntity {dataset: $dataset, id: $shape_id})-[:IS_A*1..6]->(ancestor:Shape)
WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN DISTINCT ancestor.id AS shape_id, ancestor.name AS shape_name ORDER BY shape_id;

// @query Q05
// Mục đích: các trường hợp đặc biệt của HBH (không gồm chính HBH).
// Expected: HCN, HTHOI, HV.
MATCH path=(s:Shape:ProjectEntity {dataset: $dataset})-[:IS_A*1..6]->(:Shape:ProjectEntity {dataset: $dataset, id: 'HBH'})
WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN DISTINCT s.id AS shape_id, s.name AS shape_name ORDER BY shape_id;

// @query Q06
// Mục đích: hình có bốn cạnh bằng nhau, gồm kế thừa. Expected: HTHOI, HV.
MATCH path=(s:Shape:ProjectEntity {dataset: $dataset})-[:IS_A*0..6]->(:Shape)
      -[:HAS_PROPERTY]->(:Property:ProjectEntity {dataset: $dataset, id: 'FOUR_EQUAL_SIDES'})
WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN DISTINCT s.id AS shape_id, s.name AS shape_name ORDER BY shape_id;

// @query Q07
// Mục đích: hình có bốn góc vuông. Expected: HCN, HV.
MATCH path=(s:Shape:ProjectEntity {dataset: $dataset})-[:IS_A*0..6]->(:Shape)
      -[:HAS_PROPERTY]->(:Property:ProjectEntity {dataset: $dataset, id: 'FOUR_RIGHT_ANGLES'})
WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN DISTINCT s.id AS shape_id, s.name AS shape_name ORDER BY shape_id;

// @query Q08
// Mục đích: hình có đường chéo bằng nhau. Expected: HCN, HTC, HV.
// HTC và HCN khai báo độc lập; HV lấy qua HCN.
MATCH path=(s:Shape:ProjectEntity {dataset: $dataset})-[:IS_A*0..6]->(:Shape)
      -[:HAS_PROPERTY]->(:Property:ProjectEntity {dataset: $dataset, id: 'DIAGONALS_EQUAL'})
WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN DISTINCT s.id AS shape_id, s.name AS shape_name ORDER BY shape_id;

// @query Q09
// Mục đích: mọi đường phân loại từ TQ tới HV, duyệt ngược IS_A.
// Expected: TQ,HBH,HCN,HV và TQ,HBH,HTHOI,HV; mỗi đường 3 cạnh.
MATCH path=(:Shape:ProjectEntity {dataset: $dataset, id: 'TQ'})<-[:IS_A*1..6]-(:Shape:ProjectEntity {dataset: $dataset, id: $shape_id})
WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN path, [n IN nodes(path) | n.id] AS node_ids, length(path) AS edge_count
ORDER BY node_ids;

// @query Q10
// Mục đích: giao tập tính chất hiệu lực của HV và HCN. Expected: 9 Property.
MATCH leftPath=(:Shape:ProjectEntity {dataset: $dataset, id: 'HV'})-[:IS_A*0..6]->(:Shape)-[:HAS_PROPERTY]->(p:Property)
MATCH rightPath=(:Shape:ProjectEntity {dataset: $dataset, id: 'HCN'})-[:IS_A*0..6]->(:Shape)-[:HAS_PROPERTY]->(p)
WHERE all(n IN nodes(leftPath) WHERE n.dataset = $dataset AND n:ProjectEntity)
  AND all(n IN nodes(rightPath) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN DISTINCT p.id AS property_id, p.name AS property_name ORDER BY property_id;

// @query Q11
// Mục đích: giao tập tính chất hiệu lực của HV và HTHOI. Expected: 10 Property.
MATCH leftPath=(:Shape:ProjectEntity {dataset: $dataset, id: 'HV'})-[:IS_A*0..6]->(:Shape)-[:HAS_PROPERTY]->(p:Property)
MATCH rightPath=(:Shape:ProjectEntity {dataset: $dataset, id: 'HTHOI'})-[:IS_A*0..6]->(:Shape)-[:HAS_PROPERTY]->(p)
WHERE all(n IN nodes(leftPath) WHERE n.dataset = $dataset AND n:ProjectEntity)
  AND all(n IN nodes(rightPath) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN DISTINCT p.id AS property_id, p.name AS property_name ORDER BY property_id;

// @query Q12
// Mục đích: đường chéo vuông góc AND chia đôi nhau, không thay AND bằng OR.
// Expected: HTHOI, HV.
MATCH firstPath=(s:Shape:ProjectEntity {dataset: $dataset})-[:IS_A*0..6]->(:Shape)
      -[:HAS_PROPERTY]->(:Property {id: 'DIAGONALS_PERPENDICULAR'})
MATCH secondPath=(s)-[:IS_A*0..6]->(:Shape)
      -[:HAS_PROPERTY]->(:Property {id: 'DIAGONALS_BISECT_EACH_OTHER'})
WHERE all(n IN nodes(firstPath) WHERE n.dataset = $dataset AND n:ProjectEntity)
  AND all(n IN nodes(secondPath) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN DISTINCT s.id AS shape_id, s.name AS shape_name ORDER BY shape_id;

// @query Q13
// Mục đích: đếm cạnh trực tiếp đi vào/ra theo loại của từng Shape.
// Expected chi tiết được lưu độc lập trong expected_results.json; không đếm cạnh kế thừa như cạnh trực tiếp.
MATCH (s:Shape:ProjectEntity {dataset: $dataset})
OPTIONAL MATCH (s)-[outgoing]->(:ProjectEntity {dataset: $dataset})
WITH s, collect(type(outgoing)) AS out_types, count(outgoing) AS out_degree
OPTIONAL MATCH (:ProjectEntity {dataset: $dataset})-[incoming]->(s)
WITH s, out_types, out_degree, collect(type(incoming)) AS in_types, count(incoming) AS in_degree
RETURN s.id AS shape_id,
       size([t IN out_types WHERE t = 'IS_A']) AS outgoing_is_a,
       size([t IN out_types WHERE t = 'HAS_PROPERTY']) AS direct_property_count,
       size([t IN out_types WHERE t = 'HAS_CONDITION']) AS condition_count,
       size([t IN in_types WHERE t = 'IS_A']) AS incoming_is_a,
       size([t IN in_types WHERE t = 'REQUIRES_SHAPE']) AS incoming_requires_shape,
       in_degree, out_degree
ORDER BY shape_id;

// @query Q14
// Mục đích: node đạt được trong độ sâu 1–3 và các cạnh nội bộ giữa chúng (induced graph).
// Đây là lân cận không hướng, không phải taxonomy hay toàn bộ tập tính chất.
// HV: depth=1 có 8 node/11 cạnh; depth=2 có 23 node/43 cạnh; depth=3 có 39 node/71 cạnh.
// Depth=1 gồm 7 cạnh tới HV và 4 cạnh ngữ cảnh giữa các node lân cận.
MATCH path=(s:Shape:ProjectEntity {dataset: $dataset, id: $shape_id})
      -[:IS_A|HAS_PROPERTY|HAS_CONDITION|REQUIRES_SHAPE|REQUIRES_PROPERTY*0..3]-(neighbor)
WHERE $depth >= 1 AND $depth <= 3 AND length(path) <= $depth
  AND all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
WITH collect(DISTINCT neighbor) AS nodes
OPTIONAL MATCH (a:ProjectEntity {dataset: $dataset})-[r]->(b:ProjectEntity {dataset: $dataset})
WHERE a IN nodes AND b IN nodes
RETURN nodes, collect(DISTINCT r) AS relationships;

// @query Q15
// Mục đích: giải thích nguồn tính chất chia đôi đường chéo của HV.
// Expected: HV→HCN→HBH→Property và HV→HTHOI→HBH→Property; không đi qua Condition.
MATCH path=(:Shape:ProjectEntity {dataset: $dataset, id: 'HV'})-[:IS_A*0..6]->(owner:Shape)
      -[:HAS_PROPERTY]->(:Property {id: 'DIAGONALS_BISECT_EACH_OTHER'})
WHERE all(n IN nodes(path) WHERE n.dataset = $dataset AND n:ProjectEntity)
RETURN path, [n IN nodes(path) | n.id] AS node_ids, owner.id AS declared_at
ORDER BY node_ids;
