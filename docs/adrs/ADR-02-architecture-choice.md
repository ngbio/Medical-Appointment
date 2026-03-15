# ADR-02: Client–Server Architecture

## Status
Accepted

## Bối cảnh hệ thống

Hệ thống Medical Appointment được thiết kế như một ứng dụng web cho phép người dùng đặt lịch khám bệnh trực tuyến.

Nhiều loại người dùng khác nhau sẽ sử dụng hệ thống, bao gồm:

- Bệnh nhân
- Bác sĩ
- Lễ tân
- Quản trị viên

Những người dùng này sẽ truy cập hệ thống thông qua **trình duyệt web**. Vì vậy, hệ thống cần một kiến trúc cho phép client giao tiếp với server thông qua mạng để gửi request và nhận dữ liệu.

---

## Quyết định kiến trúc

Chúng tôi áp dụng **Client–Server Architecture**. Kiến trúc này bao gồm hai thành phần chính.

### Client

Client được xây dựng dưới dạng **Web User Interface sử dụng React**.

Chức năng của client bao gồm:

- Hiển thị giao diện người dùng  
- Xử lý tương tác của người dùng  
- Gửi request đến backend API  
- Hiển thị dữ liệu nhận được từ server  

### Server

Server được xây dựng bằng **Django REST Framework**.

Chức năng của server bao gồm:

- Xử lý các HTTP request từ client  
- Thực hiện logic nghiệp vụ  
- Truy cập và quản lý dữ liệu trong database  
- Trả dữ liệu về client dưới dạng JSON  

Client và server giao tiếp với nhau thông qua **HTTP/HTTPS và REST API**.

---

## Lý do lựa chọn

Kiến trúc client–server được lựa chọn vì:

- Tách biệt giao diện và logic  
- Hỗ trợ nhiều client  
- Dễ phát triển giao diện  
- Phù hợp với ứng dụng web hiện đại  

---

## Hệ quả

### Tích cực

- Tách biệt rõ frontend và backend  
- Dễ mở rộng giao diện người dùng  
- Hỗ trợ nhiều loại client  
- Dễ bảo trì và phát triển  

### Tiêu cực

- Phụ thuộc vào kết nối mạng  
- Cần thiết kế API rõ ràng  
- Có thêm overhead giao tiếp HTTP