# ADR-05: Relational Database for Persistent Data Storage

  ## **Status:** `Accepted`

## Bối cảnh hệ thống

Hệ thống đặt lịch khám cần lưu trữ nhiều loại dữ liệu cốt lõi có mối quan hệ chặt chẽ với nhau, bao gồm:

  * User accounts 
  * Patient profiles
  * Doctor information & schedules
  * Appointments 
  * Medical records 

Các thực thể dữ liệu này có tính liên kết cao. Ví dụ:

  * Một bệnh nhân có thể có nhiều lịch khám.
  * Một bác sĩ sẽ tiếp nhận nhiều lịch khám.
  * Mỗi lịch khám lại được liên kết trực tiếp với một hồ sơ bệnh án.

Do đó, hệ thống bắt buộc phải sử dụng một giải pháp cơ sở dữ liệu có khả năng:

  * Quản lý tốt các mối quan hệ giữa các thực thể dữ liệu.
  * Đảm bảo tính nhất quán của dữ liệu.
  * Hỗ trợ giao dịch chặt chẽ để tránh xung đột khi đặt lịch.

## Quyết định kiến trúc

Chúng tôi quyết định lựa chọn Relational Database Management System (RDBMS) cho hệ thống lưu trữ bền vững. Cụ thể, hệ thống sẽ sử dụng MySQL làm cơ sở dữ liệu chính.

Phía Backend được xây dựng bằng Django, sử dụng Django làm lớp trung gian để tương tác với cơ sở dữ MySQL. Việc sử dụng Django ORM cho phép ánh xạ tự động các object/model trong code sang các bảng trong database.

Bảng ánh xạ Model dự kiến:

| Django Model | Database Table |
| :--- | :--- |
| `User` | `users` |
| `Patient` | `patients` |
| `Doctor` | `doctors` |
| `Appointment` | `appointments` |
| `MedicalRecord` | `medical_records` |

## Các phương án đã đánh giá

Trước khi đưa ra quyết định, chúng tôi đã đánh giá 3 tùy chọn cơ sở dữ liệu phổ biến nhất dựa trên đặc thù của dự án:

| Tùy chọn Database | Phân loại | Ưu điểm | Nhược điểm |
| :--- | :--- | :--- | :--- |
| MySQL / PostgreSQL | Relational Database | - Hỗ trợ cấu trúc dữ liệu quan hệ tốt.<br>- Đảm bảo ACID transactions.<br>- Tích hợp hoàn hảo với Django ORM. | - Schema cứng nhắc, đòi hỏi migration khi có thay đổi cấu trúc so với NoSQL. |
| MongoDB | Document (NoSQL) Database | - Schema cực kỳ linh hoạt.<br>- Phù hợp với các định dạng dữ liệu phi cấu trúc. | - Khó quản lý các mối quan hệ chéo phức tạp.<br>- Khả năng hỗ trợ transaction hạn chế hơn RDBMS. |
| Redis | In-memory Database | - Tốc độ đọc/ghi dữ liệu cực kỳ nhanh. | - Không phù hợp cho lưu trữ dữ liệu vĩnh viễn (persistent storage).<br>- Thường chỉ dùng làm caching hoặc message broker. |

## Cơ sở phân tích và lựa chọn

Quyết định chọn MySQL được đưa ra dựa trên 4 lý do cốt lõi sau:

*  Phù hợp với mô hình dữ liệu quan hệ: Hệ thống mạng lưới dữ liệu dày đặc (Patient → Appointment, Doctor → Appointment, Appointment → MedicalRecord). Database quan hệ giúp quản lý các Foreign Keys và cấu trúc này một cách tối ưu nhất.
*  Hỗ trợ Transaction mạnh mẽ: Các thao tác quan trọng (như khi user bấm đặt lịch khám) đòi hỏi tính nhất quán dữ liệu tuyệt đối (Data Consistency). MySQL hỗ trợ ACID transactions, giúp ngăn chặn tình trạng sai lệch hoặc mất mát dữ liệu khi có nhiều truy vấn xảy ra đồng thời.
*  Tương thích tốt với Backend Framework: Django ORM được thiết kế để làm việc hiệu quả với MySQL. Nó cho phép định nghĩa các Models bằng Python, tự động generate database schema, và thực hiện các câu lệnh query phức tạp dễ dàng mà không cần viết SQL raw.
*  Độ tin cậy và Cộng đồng: MySQL là hệ quản trị CSDL phổ biến, tài liệu phong phú, dễ dàng triển khai, đồng thời có cộng đồng hỗ trợ khổng lồ giúp giảm thiểu rủi ro trong quá trình phát triển.

## Hệ quả 

### Tích cực:

  * Đảm bảo tính toàn vẹn và nhất quán của dữ liệu đặt lịch khám.
  * Quản lý các luồng dữ liệu có tính quan hệ (relational data) hiệu quả, dễ dàng query chéo.
  * Tăng tốc độ phát triển nhờ sự tích hợp sâu giữa MySQL và Django ORM.
  * Dễ bảo trì và mở rộng đội ngũ phát triển vì công nghệ phổ biến.

### Tiêu cực:

  * Việc thay đổi cấu trúc bảng (schema changes) cần phải cẩn trọng hơn và luôn đi kèm với quá trình database migration.
  * Nếu hệ thống phát triển quá lớn, việc scale ngang của MySQL sẽ phức tạp hơn so với các giải pháp NoSQL.
