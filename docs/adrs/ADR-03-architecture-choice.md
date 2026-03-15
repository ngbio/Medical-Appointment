# ADR-03: Layered Architecture

## Status
Accepted

## Bối cảnh hệ thống

Backend của hệ thống phải xử lý nhiều nghiệp vụ khác nhau như:

- Nhận request từ client  
- Thực hiện logic nghiệp vụ  
- Truy cập và thao tác dữ liệu trong database  
- Kiểm tra và xử lý dữ liệu  

Nếu tất cả các chức năng này được triển khai trong cùng một lớp hoặc cùng một module, code backend sẽ nhanh chóng trở nên phức tạp và khó bảo trì.

Các phần logic nghiệp vụ, xử lý request và truy cập dữ liệu có thể bị trộn lẫn với nhau, dẫn đến việc hệ thống khó mở rộng và khó kiểm thử.

Do đó, hệ thống cần một cách tổ chức backend rõ ràng để **phân tách trách nhiệm giữa các phần khác nhau của hệ thống**.

---

## Quyết định kiến trúc

Backend được tổ chức theo **Layered Architecture** gồm ba tầng chính.

### Presentation Layer

Chịu trách nhiệm giao tiếp trực tiếp với client thông qua REST API.

- Nhận request HTTP từ client  
- Định nghĩa các REST API endpoints  
- Kiểm tra dữ liệu đầu vào  
- Trả response cho client  

### Business Logic Layer

Chịu trách nhiệm xử lý toàn bộ logic nghiệp vụ của hệ thống, đóng vai trò trung gian giữa Presentation Layer và Data Access Layer.

- Xử lý logic nghiệp vụ của hệ thống  
- Quản lý việc đặt lịch khám  
- Kiểm tra lịch trống của bác sĩ  
- Áp dụng các quy tắc nghiệp vụ  

### Data Access Layer

Chịu trách nhiệm truy cập và thao tác dữ liệu trong database.

- Tương tác với Database thông qua ORM  
- Thực hiện CRUD operations  
- Lưu trữ và truy xuất dữ liệu hệ thống  

---

## Lý do lựa chọn

- **Phân tách trách nhiệm:** Mỗi tầng có nhiệm vụ riêng, giúp hệ thống rõ ràng và dễ quản lý.  

- **Giảm sự phụ thuộc giữa các module:** Thay đổi ở tầng dữ liệu sẽ ít ảnh hưởng đến các tầng khác.  

- **Dễ kiểm thử:** Có thể kiểm thử từng tầng riêng biệt.  

- **Hỗ trợ mở rộng hệ thống:** Khi hệ thống phát triển, có thể thêm các module mới mà không làm ảnh hưởng đến kiến trúc chung.  

---

## Hệ quả

### Tích cực

- Code backend có cấu trúc rõ ràng  
- Dễ bảo trì và mở rộng hệ thống  
- Dễ debug và kiểm thử từng tầng  
- Giảm sự phụ thuộc giữa các thành phần của hệ thống  

### Tiêu cực

- Có thể làm tăng số lượng lớp trong hệ thống  
- Cần nhiều code tổ chức hơn