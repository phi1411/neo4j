// Seed độc lập, dataset cố định quadrilateral-v1.
// Sinh từ bốn file JSON bằng scripts/phase2.py build-seed.
// Không DELETE/DROP; MERGE theo (dataset, id).

// Seed Shape
UNWIND [{id: "TQ", name: "Tứ giác", definition: "Đa giác lồi, không suy biến có bốn cạnh trong mặt phẳng.", search_name: "tu giac", display_order: 1, source_ref: "https://mathworld.wolfram.com/Quadrilateral.html"},
{id: "HT", name: "Hình thang", definition: "Tứ giác có đúng một cặp cạnh đối song song, theo quy ước phân loại loại trừ của project.", search_name: "hinh thang", display_order: 2, source_ref: "project:docs/PHASE_1_PHAN_TICH.md#2"},
{id: "HTC", name: "Hình thang cân", definition: "Hình thang có hai góc kề một đáy bằng nhau.", search_name: "hinh thang can", display_order: 3, source_ref: "https://mathworld.wolfram.com/IsoscelesTrapezoid.html"},
{id: "HBH", name: "Hình bình hành", definition: "Tứ giác có hai cặp cạnh đối song song.", search_name: "hinh binh hanh", display_order: 4, source_ref: "https://mathworld.wolfram.com/Parallelogram.html"},
{id: "HCN", name: "Hình chữ nhật", definition: "Tứ giác có bốn góc vuông; bao gồm trường hợp đặc biệt là hình vuông.", search_name: "hinh chu nhat", display_order: 5, source_ref: "https://mathworld.wolfram.com/Rectangle.html"},
{id: "HTHOI", name: "Hình thoi", definition: "Tứ giác có bốn cạnh bằng nhau; bao gồm trường hợp đặc biệt là hình vuông.", search_name: "hinh thoi", display_order: 6, source_ref: "https://mathworld.wolfram.com/Rhombus.html"},
{id: "HV", name: "Hình vuông", definition: "Tứ giác có bốn cạnh bằng nhau và bốn góc vuông.", search_name: "hinh vuong", display_order: 7, source_ref: "https://mathworld.wolfram.com/Square.html"}] AS row
MERGE (n:Shape {dataset: 'quadrilateral-v1', id: row.id})
SET n:ProjectEntity
SET n += row;

// Seed Property
UNWIND [{id: "FOUR_SIDES", name: "Có bốn cạnh", category: "structure", description: "Đường biên của tứ giác gồm bốn đoạn thẳng nối bốn đỉnh liên tiếp.", notation: "AB, BC, CD, DA", source_ref: "https://mathworld.wolfram.com/Quadrilateral.html"},
{id: "ANGLE_SUM_360", name: "Tổng bốn góc trong bằng 360°", category: "angle", description: "Áp dụng cho tứ giác lồi không suy biến trong mặt phẳng.", notation: "∠A + ∠B + ∠C + ∠D = 360°", source_ref: "https://mathworld.wolfram.com/Quadrilateral.html"},
{id: "EXACTLY_ONE_PARALLEL_PAIR", name: "Có đúng một cặp cạnh đối song song", category: "side", description: "Quy ước hình thang loại trừ của project: một cặp cạnh đối song song, cặp còn lại không song song.", notation: "AB ∥ CD và AD không song song BC (hoặc đổi cặp)", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#2"},
{id: "LEG_ADJACENT_ANGLES_SUPPLEMENTARY", name: "Hai góc kề cùng một cạnh bên bù nhau", category: "angle", description: "Với hai đáy AB ∥ CD, các góc trong cùng phía trên mỗi cạnh bên có tổng 180°.", notation: "∠A + ∠D = 180°; ∠B + ∠C = 180°", source_ref: "https://mathworld.wolfram.com/Trapezoid.html"},
{id: "LEGS_EQUAL", name: "Hai cạnh bên bằng nhau", category: "side", description: "Với hai đáy AB và CD đã chọn, hai cạnh bên là AD và BC.", notation: "AD = BC", source_ref: "https://mathworld.wolfram.com/IsoscelesTrapezoid.html"},
{id: "BASE_ANGLES_EQUAL", name: "Hai góc kề mỗi đáy bằng nhau", category: "angle", description: "Với AB ∥ CD, hai góc tại đáy AB bằng nhau và hai góc tại đáy CD bằng nhau.", notation: "∠A = ∠B; ∠D = ∠C", source_ref: "https://mathworld.wolfram.com/IsoscelesTrapezoid.html"},
{id: "DIAGONALS_EQUAL", name: "Hai đường chéo bằng nhau", category: "diagonal", description: "Độ dài hai đoạn nối các đỉnh đối diện bằng nhau; không tự nó đủ nhận biết hình chữ nhật.", notation: "AC = BD", source_ref: "https://mathworld.wolfram.com/Rectangle.html; https://mathworld.wolfram.com/IsoscelesTrapezoid.html"},
{id: "TWO_PARALLEL_PAIRS", name: "Có hai cặp cạnh đối song song", category: "side", description: "Cả hai cặp cạnh đối của tứ giác song song.", notation: "AB ∥ CD; AD ∥ BC", source_ref: "https://mathworld.wolfram.com/Parallelogram.html"},
{id: "OPPOSITE_SIDES_EQUAL", name: "Hai cặp cạnh đối bằng nhau", category: "side", description: "Mỗi cạnh bằng cạnh đối diện của nó.", notation: "AB = CD; AD = BC", source_ref: "https://mathworld.wolfram.com/Parallelogram.html"},
{id: "OPPOSITE_ANGLES_EQUAL", name: "Hai cặp góc đối bằng nhau", category: "angle", description: "Cả hai cặp góc đối của tứ giác có số đo bằng nhau.", notation: "∠A = ∠C; ∠B = ∠D", source_ref: "https://mathworld.wolfram.com/Parallelogram.html"},
{id: "ADJACENT_ANGLES_SUPPLEMENTARY", name: "Mọi cặp góc kề nhau bù nhau", category: "angle", description: "Mỗi cặp góc ở hai đỉnh liên tiếp có tổng 180°.", notation: "∠A + ∠B = ∠B + ∠C = ∠C + ∠D = ∠D + ∠A = 180°", source_ref: "https://mathworld.wolfram.com/Parallelogram.html"},
{id: "DIAGONALS_BISECT_EACH_OTHER", name: "Hai đường chéo chia đôi nhau", category: "diagonal", description: "Giao điểm của hai đường chéo là trung điểm của mỗi đường, không chỉ của một đường.", notation: "O = AC ∩ BD; OA = OC; OB = OD", source_ref: "https://mathworld.wolfram.com/Parallelogram.html"},
{id: "FOUR_RIGHT_ANGLES", name: "Có bốn góc vuông", category: "angle", description: "Bốn góc trong của tứ giác đều bằng 90°.", notation: "∠A = ∠B = ∠C = ∠D = 90°", source_ref: "https://mathworld.wolfram.com/Rectangle.html"},
{id: "FOUR_EQUAL_SIDES", name: "Có bốn cạnh bằng nhau", category: "side", description: "Độ dài bốn cạnh bằng nhau; không khẳng định các góc đều vuông.", notation: "AB = BC = CD = DA", source_ref: "https://mathworld.wolfram.com/Rhombus.html"},
{id: "DIAGONALS_PERPENDICULAR", name: "Hai đường chéo vuông góc", category: "diagonal", description: "Hai đường chéo tạo góc 90° tại giao điểm; không tự nó đủ nhận biết hình thoi.", notation: "AC ⟂ BD", source_ref: "https://mathworld.wolfram.com/Rhombus.html"},
{id: "DIAGONALS_BISECT_ANGLES", name: "Các đường chéo phân giác các góc", category: "diagonal_angle", description: "Mỗi đường chéo phân giác góc trong tại hai đầu của nó.", notation: "∠BAC = ∠CAD; ∠BCA = ∠ACD; ∠ABD = ∠DBC; ∠ADB = ∠BDC", source_ref: "https://mathworld.wolfram.com/Rhombus.html"},
{id: "THREE_RIGHT_ANGLES", name: "Có ít nhất ba góc vuông", category: "angle", description: "Giả thiết nhận biết; tổng góc 360° buộc góc thứ tư cũng vuông.", notation: "Ba trong bốn góc bằng 90°", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "HAS_RIGHT_ANGLE", name: "Có ít nhất một góc vuông", category: "angle", description: "Giả thiết nhận biết khi đã biết ngữ cảnh hình bình hành hoặc hình thoi.", notation: "Tồn tại một góc bằng 90°", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "ADJACENT_SIDES_EQUAL", name: "Có một cặp cạnh kề bằng nhau", category: "side", description: "Giả thiết nhận biết khi đã biết ngữ cảnh hình bình hành hoặc hình chữ nhật.", notation: "Ví dụ AB = BC", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"}] AS row
MERGE (n:Property {dataset: 'quadrilateral-v1', id: row.id})
SET n:ProjectEntity
SET n += row;

// Seed Condition
UNWIND [{id: "C_HT_01", name: "Nhận biết hình thang theo định nghĩa", statement: "Tứ giác có đúng một cặp cạnh đối song song là hình thang.", explanation: "Áp dụng định nghĩa hình thang loại trừ của project; hai cặp song song thuộc nhánh hình bình hành.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#2"},
{id: "C_HTC_01", name: "Nhận biết hình thang cân bằng góc ở đáy", statement: "Hình thang có hai góc kề mỗi đáy bằng nhau là hình thang cân.", explanation: "Trong hình thang, chỉ cần hai góc kề một đáy bằng nhau; tính bù trên cạnh bên suy ra cặp ở đáy còn lại cũng bằng nhau.", logic: "AND", source_ref: "https://mathworld.wolfram.com/IsoscelesTrapezoid.html"},
{id: "C_HTC_02", name: "Nhận biết hình thang cân bằng đường chéo", statement: "Hình thang có hai đường chéo bằng nhau là hình thang cân.", explanation: "Phải có giả thiết hình thang; tính bằng nhau của đường chéo xác định tính đối xứng giữa hai cạnh bên và hai góc ở đáy.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HBH_01", name: "Nhận biết hình bình hành bằng cạnh song song", statement: "Tứ giác có hai cặp cạnh đối song song là hình bình hành.", explanation: "Đúng theo định nghĩa hình bình hành.", logic: "AND", source_ref: "https://mathworld.wolfram.com/Parallelogram.html"},
{id: "C_HBH_02", name: "Nhận biết hình bình hành bằng cạnh bằng nhau", statement: "Tứ giác có hai cặp cạnh đối bằng nhau là hình bình hành.", explanation: "Đường chéo chia tứ giác thành hai tam giác bằng nhau theo cạnh-cạnh-cạnh; các góc so le trong suy ra hai cặp cạnh song song.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HBH_03", name: "Nhận biết hình bình hành bằng góc đối", statement: "Tứ giác có hai cặp góc đối bằng nhau là hình bình hành.", explanation: "Tổng góc 360° suy ra các góc kề bù nhau; đảo của tính chất góc trong cùng phía cho hai cặp cạnh song song.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HBH_04", name: "Nhận biết hình bình hành bằng trung điểm đường chéo", statement: "Tứ giác có hai đường chéo chia đôi nhau là hình bình hành.", explanation: "Các cặp tam giác đối đỉnh bằng nhau theo cạnh-góc-cạnh tại giao điểm; suy ra các cạnh đối song song.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HCN_01", name: "Nhận biết hình chữ nhật bằng ba góc vuông", statement: "Tứ giác có ít nhất ba góc vuông là hình chữ nhật.", explanation: "Tổng bốn góc bằng 360° nên góc còn lại bằng 90°.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HCN_02", name: "Nhận biết hình chữ nhật từ hình bình hành có góc vuông", statement: "Hình bình hành có một góc vuông là hình chữ nhật.", explanation: "Các góc đối bằng nhau và góc kề bù nhau khiến cả bốn góc đều vuông.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HCN_03", name: "Nhận biết hình chữ nhật từ hình bình hành có đường chéo bằng nhau", statement: "Hình bình hành có hai đường chéo bằng nhau là hình chữ nhật.", explanation: "Trong hình bình hành, các tam giác tạo bởi cạnh và hai đường chéo bằng nhau theo cạnh-cạnh-cạnh; góc kề bằng nhau và bù nhau nên bằng 90°.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HTHOI_01", name: "Nhận biết hình thoi bằng bốn cạnh", statement: "Tứ giác có bốn cạnh bằng nhau là hình thoi.", explanation: "Theo định nghĩa; hai cặp cạnh đối bằng nhau cũng đảm bảo đây là hình bình hành.", logic: "AND", source_ref: "https://mathworld.wolfram.com/Rhombus.html"},
{id: "C_HTHOI_02", name: "Nhận biết hình thoi từ hai cạnh kề", statement: "Hình bình hành có hai cạnh kề bằng nhau là hình thoi.", explanation: "Cạnh đối của hình bình hành bằng nhau nên một cặp cạnh kề bằng nhau dẫn tới cả bốn cạnh bằng nhau.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HTHOI_03", name: "Nhận biết hình thoi từ đường chéo vuông góc", statement: "Hình bình hành có hai đường chéo vuông góc là hình thoi.", explanation: "Đường chéo chia đôi nhau; các tam giác vuông tại giao điểm có hai cạnh góc vuông tương ứng bằng nhau, suy ra bốn cạnh bằng nhau.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HV_01", name: "Nhận biết hình vuông từ hai cạnh kề của hình chữ nhật", statement: "Hình chữ nhật có hai cạnh kề bằng nhau là hình vuông.", explanation: "Cạnh đối bằng nhau khiến cả bốn cạnh bằng nhau; bốn góc vuông đã có từ ngữ cảnh.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HV_02", name: "Nhận biết hình vuông từ đường chéo hình chữ nhật", statement: "Hình chữ nhật có hai đường chéo vuông góc là hình vuông.", explanation: "Hình chữ nhật là hình bình hành; đường chéo vuông góc suy ra hình thoi. Đồng thời là hình thoi và hình chữ nhật nên là hình vuông.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HV_03", name: "Nhận biết hình vuông từ góc vuông của hình thoi", statement: "Hình thoi có một góc vuông là hình vuông.", explanation: "Hình thoi là hình bình hành; một góc vuông suy ra bốn góc vuông. Bốn cạnh bằng nhau đã có từ ngữ cảnh.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HV_04", name: "Nhận biết hình vuông từ đường chéo bằng nhau của hình thoi", statement: "Hình thoi có hai đường chéo bằng nhau là hình vuông.", explanation: "Hình thoi là hình bình hành; đường chéo bằng nhau suy ra hình chữ nhật. Đồng thời bốn cạnh bằng nhau nên là hình vuông.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"},
{id: "C_HV_05", name: "Nhận biết hình vuông theo hai nhóm giả thiết đồng thời", statement: "Tứ giác có bốn cạnh bằng nhau và bốn góc vuông là hình vuông.", explanation: "Phải thỏa mãn đồng thời cả hai Property; nhiều dấu hiệu đủ khác nhau của HV được hiểu theo OR.", logic: "AND", source_ref: "project:docs/PHASE_1_PHAN_TICH.md#7"}] AS row
MERGE (n:Condition {dataset: 'quadrilateral-v1', id: row.id})
SET n:ProjectEntity
SET n += row;

// Phân loại trực tiếp
UNWIND [["HTC",
"HT"],
["HT",
"TQ"],
["HBH",
"TQ"],
["HCN",
"HBH"],
["HTHOI",
"HBH"],
["HV",
"HCN"],
["HV",
"HTHOI"]] AS pair
MATCH (a:Shape:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[0]})
MATCH (b:Shape:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[1]})
MERGE (a)-[:IS_A]->(b);

// Tính chất trực tiếp
UNWIND [["TQ",
"FOUR_SIDES"],
["TQ",
"ANGLE_SUM_360"],
["HT",
"EXACTLY_ONE_PARALLEL_PAIR"],
["HT",
"LEG_ADJACENT_ANGLES_SUPPLEMENTARY"],
["HTC",
"LEGS_EQUAL"],
["HTC",
"BASE_ANGLES_EQUAL"],
["HTC",
"DIAGONALS_EQUAL"],
["HBH",
"TWO_PARALLEL_PAIRS"],
["HBH",
"OPPOSITE_SIDES_EQUAL"],
["HBH",
"OPPOSITE_ANGLES_EQUAL"],
["HBH",
"ADJACENT_ANGLES_SUPPLEMENTARY"],
["HBH",
"DIAGONALS_BISECT_EACH_OTHER"],
["HCN",
"FOUR_RIGHT_ANGLES"],
["HCN",
"DIAGONALS_EQUAL"],
["HTHOI",
"FOUR_EQUAL_SIDES"],
["HTHOI",
"DIAGONALS_PERPENDICULAR"],
["HTHOI",
"DIAGONALS_BISECT_ANGLES"]] AS pair
MATCH (s:Shape:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[0]})
MATCH (p:Property:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[1]})
MERGE (s)-[:HAS_PROPERTY]->(p);

// HAS_CONDITION
UNWIND [["HT",
"C_HT_01"],
["HTC",
"C_HTC_01"],
["HTC",
"C_HTC_02"],
["HBH",
"C_HBH_01"],
["HBH",
"C_HBH_02"],
["HBH",
"C_HBH_03"],
["HBH",
"C_HBH_04"],
["HCN",
"C_HCN_01"],
["HCN",
"C_HCN_02"],
["HCN",
"C_HCN_03"],
["HTHOI",
"C_HTHOI_01"],
["HTHOI",
"C_HTHOI_02"],
["HTHOI",
"C_HTHOI_03"],
["HV",
"C_HV_01"],
["HV",
"C_HV_02"],
["HV",
"C_HV_03"],
["HV",
"C_HV_04"],
["HV",
"C_HV_05"]] AS pair
MATCH (a:Shape:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[0]})
MATCH (b:Condition:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[1]})
MERGE (a)-[:HAS_CONDITION]->(b);

// REQUIRES_SHAPE
UNWIND [["C_HT_01",
"TQ"],
["C_HTC_01",
"HT"],
["C_HTC_02",
"HT"],
["C_HBH_01",
"TQ"],
["C_HBH_02",
"TQ"],
["C_HBH_03",
"TQ"],
["C_HBH_04",
"TQ"],
["C_HCN_01",
"TQ"],
["C_HCN_02",
"HBH"],
["C_HCN_03",
"HBH"],
["C_HTHOI_01",
"TQ"],
["C_HTHOI_02",
"HBH"],
["C_HTHOI_03",
"HBH"],
["C_HV_01",
"HCN"],
["C_HV_02",
"HCN"],
["C_HV_03",
"HTHOI"],
["C_HV_04",
"HTHOI"],
["C_HV_05",
"TQ"]] AS pair
MATCH (a:Condition:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[0]})
MATCH (b:Shape:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[1]})
MERGE (a)-[:REQUIRES_SHAPE]->(b);

// REQUIRES_PROPERTY
UNWIND [["C_HT_01",
"EXACTLY_ONE_PARALLEL_PAIR"],
["C_HTC_01",
"BASE_ANGLES_EQUAL"],
["C_HTC_02",
"DIAGONALS_EQUAL"],
["C_HBH_01",
"TWO_PARALLEL_PAIRS"],
["C_HBH_02",
"OPPOSITE_SIDES_EQUAL"],
["C_HBH_03",
"OPPOSITE_ANGLES_EQUAL"],
["C_HBH_04",
"DIAGONALS_BISECT_EACH_OTHER"],
["C_HCN_01",
"THREE_RIGHT_ANGLES"],
["C_HCN_02",
"HAS_RIGHT_ANGLE"],
["C_HCN_03",
"DIAGONALS_EQUAL"],
["C_HTHOI_01",
"FOUR_EQUAL_SIDES"],
["C_HTHOI_02",
"ADJACENT_SIDES_EQUAL"],
["C_HTHOI_03",
"DIAGONALS_PERPENDICULAR"],
["C_HV_01",
"ADJACENT_SIDES_EQUAL"],
["C_HV_02",
"DIAGONALS_PERPENDICULAR"],
["C_HV_03",
"HAS_RIGHT_ANGLE"],
["C_HV_04",
"DIAGONALS_EQUAL"],
["C_HV_05",
"FOUR_EQUAL_SIDES"],
["C_HV_05",
"FOUR_RIGHT_ANGLES"]] AS pair
MATCH (a:Condition:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[0]})
MATCH (b:Property:ProjectEntity {dataset: 'quadrilateral-v1', id: pair[1]})
MERGE (a)-[:REQUIRES_PROPERTY]->(b);
