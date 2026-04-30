# Medical-Appointment

## Mô tả

Hệ thống **Medical Appointment** là nền tảng đặt lịch khám bệnh trực tuyến, cho phép bệnh nhân dễ dàng tìm kiếm bác sĩ theo chuyên khoa, lựa chọn khung giờ phù hợp và thực hiện đặt lịch một cách nhanh chóng. Đồng thời, hệ thống hỗ trợ quản lý lịch làm việc của bác sĩ, lưu trữ hồ sơ bệnh nhân và cung cấp chức năng nhắc lịch thông qua email nhằm giảm thiểu tình trạng quên lịch khám.

Hệ thống phục vụ 4 nhóm người dùng chính:
- **Bệnh nhân**: Đăng ký/đăng nhập, tạo và quản lý hồ sơ, đặt lịch khám, xem lịch sử khám chữa bệnh
- **Bác sĩ**: Xem lịch làm việc, khám bệnh, xem thông tin và lịch sử khám của bệnh nhân
- **Lễ tân**: Đặt lịch khám thay cho bệnh nhân, xem thông tin và lịch sử khám của bệnh nhân
- **Admin**: Quản lý bác sĩ, chuyên khoa (CRUD), quản lý thông tin người dùng

## Thành viên nhóm

| STT | Họ tên | MSSV |
|----|--------|------|
| 1 | Ngô Hoàng Kiều Trang | 2354050141 |
| 2 | Trần Văn Trạng | 2351050185 |
| 3 | Nguyễn Thanh Thuận | 2351010203 |

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Django REST Framework (RESTful API) |
| Frontend | JavaScript, HTML, CSS |
| Database | MySQL |
| Message Queue | RabbitMQ + Celery (xử lý bất đồng bộ, gửi email nhắc lịch) |
| Containerization | Docker, Docker Compose |

## Kiến trúc

Hệ thống được xây dựng theo sự kết hợp của các mẫu kiến trúc sau:

- **Client–Server Architecture**: Client (trình duyệt web sử dụng HTML, JavaScript) giao tiếp với backend thông qua REST API (Django REST Framework)
- **Monolithic Architecture**: Toàn bộ backend được triển khai trong một ứng dụng duy nhất, phân chia thành các module rõ ràng:
  - Module quản lý người dùng (User Management)
  - Module quản lý bệnh nhân (Patient Management)
  - Module quản lý bác sĩ và chuyên khoa (Doctor & Specialization Management)
  - Module quản lý lịch khám (Appointment Scheduling)
  - Module hồ sơ bệnh án (Medical Record Management)
  - Module thông báo (Notification / Email Reminder)
- **Layered Architecture**: Backend áp dụng phân tầng Presentation – Business Logic – Data Access giúp tách biệt trách nhiệm giữa các thành phần
- **Event-driven (Message Queue)**: Sử dụng RabbitMQ để xử lý bất đồng bộ các tác vụ gửi email nhắc lịch, tách biệt xử lý nền khỏi luồng request chính

## Cài đặt và chạy

### Yêu cầu

- Docker Desktop đã cài đặt
- MySQL đang chạy trên máy host tại `localhost:3306`
- Database `medicaldb` đã được tạo
- MySQL User: `root` / Password: `root`

### Chạy với Docker Compose

**1. Build image**
```bash
docker-compose build
```

**2. Chạy container**
```bash
docker-compose up -d
```

**3. Kiểm tra logs**
```bash
docker-compose logs -f backend
```

**4. Migrate database (nếu cần)**
```bash
docker-compose exec backend python manage.py migrate
```

**5. Tạo superuser (nếu cần)**
```bash
docker-compose exec backend python manage.py createsuperuser
```

**6. Dừng container**
```bash
docker-compose down
```

> **Ghi chú:**
> - Docker container kết nối tới MySQL trên host thông qua `host.docker.internal` (Windows)
> - Frontend folder được mount để Django có thể access templates và static files
> - `settings.py` đã được cấu hình kết nối tới MySQL với credentials: `root/root`
> - Static files được mount qua volume

### Truy cập

| Dịch vụ | URL |
|---|---|
| API endpoints | https://medical-appointment-q26y.onrender.com/swwagger/ |
| Frontend | https://medical-appointment-q26y.onrender.com/index/ |
| Django Admin | https://medical-appointment-q26y.onrender.com/admin/ |
| Database | MySQL tại `localhost:3306` (database: `medicaldb`) |

## Demo
[![Watch the video](/docs/demo/demo.png)](/docs/demo/Demo.mp4)

## Tài liệu

- Báo cáo đồ án: `KTPM_TEAM2_REPORT_B3.pdf`
