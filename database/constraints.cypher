// Uniqueness trong phạm vi dataset; không áp đặt ID toàn cục lên project khác.
// Chạy từng statement trong database quadrilateral; không chạy ở system.
CREATE CONSTRAINT quadrilateral_shape_id IF NOT EXISTS
FOR (n:Shape) REQUIRE (n.dataset, n.id) IS UNIQUE;

CREATE CONSTRAINT quadrilateral_property_id IF NOT EXISTS
FOR (n:Property) REQUIRE (n.dataset, n.id) IS UNIQUE;

CREATE CONSTRAINT quadrilateral_condition_id IF NOT EXISTS
FOR (n:Condition) REQUIRE (n.dataset, n.id) IS UNIQUE;
