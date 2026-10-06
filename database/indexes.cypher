// Dùng cho lọc theo dataset + tìm kiếm tiền tố đã chuẩn hóa dấu/chữ hoa.
// Không tạo lại các index được uniqueness constraints tạo tự động.
CREATE INDEX quadrilateral_shape_search IF NOT EXISTS
FOR (n:Shape) ON (n.dataset, n.search_name);
