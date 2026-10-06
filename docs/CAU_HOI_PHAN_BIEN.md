# Câu hỏi phản biện

## 1. Vì sao chọn Neo4j cho dataset nhỏ?

Trọng tâm là quan hệ: phân loại nhiều cấp, đa kế thừa và tính chất dùng chung. Neo4j giúp truy vấn đường đi để giải thích tính chất. Không chọn vì dữ liệu lớn hoặc vì đã chứng minh tốc độ vượt SQL.

## 2. SQL có làm được không?

Có. Có thể dùng bảng Shape, Property, Condition, bảng liên kết và truy vấn đệ quy. Project chọn graph để biểu diễn trực tiếp và duyệt các quan hệ, chưa có benchmark so sánh.

## 3. Vì sao Property là node thay vì chuỗi trong Shape?

Một mệnh đề được nhiều Shape và Condition dùng chung. Node có ID ổn định, mô tả và nguồn, hỗ trợ truy vấn giao tính chất và các hình có cùng tính chất mà không so chuỗi mô tả trùng lặp.

## 4. Vì sao Condition là node?

Một dấu hiệu có ngữ cảnh và nhiều giả thiết, cần được nhóm thành một quy tắc có tên và giải thích. Condition nối tới ngữ cảnh bằng REQUIRES_SHAPE và tới các giả thiết bằng REQUIRES_PROPERTY.

## 5. IS_A có ý nghĩa và hướng gì?

Shape đặc biệt IS_A Shape tổng quát. Ví dụ HV → HCN. Đây là quan hệ phân loại, không phải “tương tự” hoặc quan hệ giữa các hình có toạ độ cụ thể.

## 6. Neo4j có tự hiểu kế thừa không?

Không. Kế thừa là quy ước của project. Cypher duyệt IS_A, tìm HAS_PROPERTY tại chính hình và các tổ tiên, rồi hợp kết quả. Không có cơ chế suy luận tự động chỉ vì cạnh mang tên IS_A.

## 7. Vì sao Hình vuông có hai cha?

Hình vuông đồng thời thoả định nghĩa Hình chữ nhật và Hình thoi. Hai cạnh IS_A lưu trực tiếp sự đa kế thừa; Q09/Q15 trả được hai đường phân loại hoặc giải thích.

## 8. Vì sao không lưu mọi Property trực tiếp vào HV?

Sao chép sẽ làm dư dữ liệu và khó cập nhật khi tính chất lớp cha đổi. HV có 0 HAS_PROPERTY trực tiếp nhưng 12 tính chất hiệu lực do query kế thừa tính lúc đọc.

## 9. DISTINCT dùng để làm gì?

Cùng Property hoặc tổ tiên có thể được tới qua hai nhánh. DISTINCT tránh trả trùng tên tính chất hoặc loại hình. Riêng Q15 giữ hai path vì đó là hai đường giải thích khác nhau.

## 10. AND/OR của Condition hoạt động thế nào?

Trong một Condition, ngữ cảnh và tất cả Property cần đồng thời đúng (AND). Các Condition của cùng Shape là các dấu hiệu đủ thay thế (OR). Ứng dụng chỉ hiển thị cấu trúc tri thức, chưa đánh giá tự động tập giả thiết.

## 11. Vì sao hình thang có đúng một cặp song song?

Đây là quy ước taxonomy đã chọn để tách nhánh Hình thang và Hình bình hành. Các nguồn dùng “ít nhất một cặp” có thể phân loại khác. Project nêu rõ quy ước và không thêm HBH IS_A HT hoặc HCN IS_A HTC.

## 12. Hai đường chéo bằng nhau có đủ nhận biết hình chữ nhật?

Không khi chỉ biết hình là tứ giác. Hình thang cân cũng có đường chéo bằng nhau. C_HCN_03 cần ngữ cảnh Hình bình hành và giả thiết đường chéo bằng nhau.

## 13. HAS_PROPERTY khác REQUIRES_PROPERTY thế nào?

HAS_PROPERTY khai báo tính chất đúng cho một Shape. REQUIRES_PROPERTY nêu giả thiết trong một dấu hiệu nhận biết. Không dùng các cạnh này thay thế nhau hoặc kế thừa Condition như Property.

## 14. Vì sao không cho nhập Cypher tự do trên web?

Web phục vụ demo các truy vấn đọc đã duyệt. Whitelist 15 query và tham số được kiểm tra giúp giới hạn phạm vi, tránh lệnh sửa/xoá dữ liệu. Muốn thử query tự viết thì dùng Neo4j Query/Browser với quyền phù hợp.

## 15. Constraint có vai trò gì?

Ba unique constraint bảo đảm cặp (dataset, id) không trùng trong từng label Shape, Property, Condition. Constraint không tự kiểm tra chu trình hoặc nội dung toán học; các việc đó cần validation và kiểm tra catalog.

## 16. Index dùng làm gì?

Index hỗ trợ tra cứu theo các thuộc tính có cấu trúc. Project có bốn index ONLINE, gồm ba index hỗ trợ constraint và một index tra cứu tên chuẩn hoá. Không khẳng định index luôn tăng tốc CONTAINS; cần xem query plan nếu đo hiệu năng.

## 17. MERGE khác CREATE như thế nào?

CREATE luôn tạo node/cạnh mới. MERGE tìm mẫu khớp hoặc tạo nếu chưa có. Project MERGE theo ID ổn định và dùng constraint; SET cập nhật mô tả sau khi ghép node. Không MERGE theo toàn bộ mô tả dễ thay đổi.

## 18. Seed idempotent là gì?

Chạy lại seed vẫn có cùng dataset, không tạo bản sao node/cạnh. Các lần kiểm thử đã xác nhận 44/79, không tạo thêm entity và snapshot không đổi. SET vẫn có thể được thực thi, nên không đồng nghĩa seed không làm thao tác ghi.

## 19. Tại sao cần dataset và ProjectEntity?

Chúng xác định phạm vi project khi đọc hoặc seed trong database có thể chứa dữ liệu khác. ID duy nhất theo (dataset, id), traversal kiểm tra node nằm trong dataset. Việc kiểm thử cũng so snapshot dữ liệu ngoài project.

## 20. Graph lân cận có giống tập tổ tiên không?

Không. Lân cận duyệt mọi loại cạnh theo cả hai hướng ở độ sâu 1–3 và lấy các cạnh giữa node được chọn. Nó gồm cả Condition, Property và tiền đề. Tổ tiên chỉ theo IS_A tới lớp tổng quát.

## 21. Q09 có dùng shortestPath không?

Không. Query liệt kê đường IS_A trong giới hạn 1–6 cạnh. Với taxonomy hiện tại, hai đường TQ tới HV đều dài ba cạnh và cũng ngắn nhất. Không suy rộng thành thuật toán tìm đường ngắn nhất cho mọi graph.

## 22. Nếu thêm loại hình mới thì làm gì?

Thêm Shape với ID ổn định vào catalog, bổ sung IS_A/Property/Condition có căn cứ, sinh lại seed rồi kiểm tra validation và expected result. Cần cập nhật số liệu, giới hạn traversal nếu cần, ảnh và tài liệu; không chỉ thêm một card frontend.

## 23. Nếu Neo4j dừng thì web có dùng dữ liệu giả không?

Không. API trả lỗi 503 phù hợp và giao diện báo lỗi kết nối, xoá kết quả cũ của truy vấn. Cấu hình nằm trong .env; tài liệu và response không công bố mật khẩu.

## 24. Hạn chế lớn nhất hiện tại?

Chỉ bảy loại tứ giác lồi, tri thức được nhập có chủ đích, không nhận dạng ảnh/toạ độ và không là theorem prover. Flask đang phục vụ demo cục bộ; chưa có cấu hình production hay chức năng sửa dữ liệu qua web.

## 25. Có thể mở rộng thành hệ chuyên gia không?

Có thể dùng Condition làm nền tảng nhưng phải xây thêm bộ suy luận, biểu diễn dữ kiện đầu vào, kiểm tra đủ giả thiết, quản lý nguồn và giải thích kết luận. Neo4j tự nó không chứng minh các định lý hình học.

## 26. Kết quả được xác nhận bằng gì?

Neo4j thật có 44 node/79 relationship, 20 validation và 15 query PASS. Vòng cuối có 92 pytest, 41 HTTP và kiểm tra browser. Báo cáo nằm trong docs; không coi screenshot là phép đo hiệu năng hoặc bằng chứng cho mọi test.
