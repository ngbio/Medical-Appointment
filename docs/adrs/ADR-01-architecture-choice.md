# ADR-01: Monolithic Architecture

## Status
Accepted

## Bối cảnh hệ thống

Hệ thống Medical Appointment được xây dựng nhằm hỗ trợ việc đặt lịch khám bệnh trực tuyến giữa bệnh nhân và bác sĩ. Hệ thống cho phép bệnh nhân tìm kiếm bác sĩ theo chuyên khoa, lựa chọn thời gian khám phù hợp và đặt lịch khám thông qua nền tảng trực tuyến.

Ngoài chức năng đặt lịch khám, hệ thống còn hỗ trợ quản lý thông tin bệnh nhân, quản lý lịch làm việc của bác sĩ và lưu trữ hồ sơ bệnh án.

Các chức năng chính của hệ thống bao gồm:

- Xác thực và phân quyền người dùng  
- Quản lý hồ sơ bệnh nhân  
- Quản lý bác sĩ và chuyên khoa  
- Tìm kiếm bác sĩ theo chuyên khoa và ngày khám  
- Đặt và quản lý lịch khám bệnh  
- Quản lý lịch làm việc của bác sĩ  
- Quản lý hồ sơ bệnh án  
- Gửi email nhắc lịch khám (có thể sử dụng mock email)

Các tác nhân chính của hệ thống bao gồm:

- Patient (Bệnh nhân)  
- Doctor (Bác sĩ)  
- Receptionist (Lễ tân)  
- Administrator (Quản trị viên)

Trong phạm vi của đồ án, hệ thống không yêu cầu triển khai nhiều services độc lập hoặc xử lý khối lượng request ở quy mô rất lớn. Do đó, việc lựa chọn một kiến trúc đơn giản, dễ phát triển và dễ triển khai là phù hợp với mục tiêu của hệ thống.

---

## Quyết định kiến trúc

Chúng tôi quyết định áp dụng **Monolithic Architecture** cho hệ thống Medical Appointment để đáp ứng những yêu cầu và mục tiêu như trên.

Trong kiến trúc này, toàn bộ backend của hệ thống được triển khai dưới dạng **một ứng dụng duy nhất (single backend application)**. Tất cả các chức năng của hệ thống được tổ chức thành các module bên trong cùng một codebase và được triển khai trong cùng một môi trường chạy.

Các module chính của hệ thống bao gồm:

- Module quản lý người dùng (User Management)
- Module quản lý bệnh nhân (Patient Management)
- Module quản lý bác sĩ và chuyên khoa (Doctor & Specialization Management)
- Module quản lý lịch khám (Appointment Scheduling)
- Module hồ sơ bệnh án (Medical Record Management)
- Module thông báo (Notification / Email Reminder)

---

## Lý do lựa chọn

### 1. Đơn giản trong phát triển

Kiến trúc monolithic giúp việc phát triển trở nên đơn giản hơn vì tất cả các thành phần nằm trong cùng một ứng dụng. Có thể phát triển, kiểm thử và debug hệ thống dễ dàng hơn.

### 2. Dễ triển khai

Toàn bộ hệ thống có thể được triển khai như một dịch vụ backend duy nhất mà không cần đến các cơ chế phức tạp.

### 3. Phù hợp với quy mô hệ thống

Với quy mô của hệ thống đặt lịch khám trong đồ án, kiến trúc monolithic hoàn toàn đủ khả năng đáp ứng các yêu cầu chức năng.

### 4. Giảm độ phức tạp vận hành

So với microservices, kiến trúc monolithic giúp tránh được các vấn đề phức tạp như:

- giao tiếp giữa nhiều service  
- quản lý nhiều service độc lập  
- debugging hệ thống phân tán  
- độ trễ mạng giữa các service  

---

## Hệ quả

### Tích cực

- Kiến trúc đơn giản, dễ hiểu  
- Phát triển và triển khai nhanh  
- Dễ debug và kiểm thử  
- Không cần quản lý nhiều service  
- Hạ tầng triển khai đơn giản hơn  

### Tiêu cực

- Khó mở rộng riêng lẻ từng module  
- Khi hệ thống lớn lên có thể khó bảo trì hơn  
- Lỗi ở một phần có thể ảnh hưởng toàn bộ hệ thống