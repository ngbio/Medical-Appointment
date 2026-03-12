# ADR-06: Message Queue for Asynchronous Processing
## Status
Accepted

## Bối cảnh hệ thống
Hệ thống quản lý lịch khám cần gửi email thông báo cho bệnh nhân trong một số trường hợp, chẳng hạn như email xác nhận lịch khám hoặc email nhắc lịch trước thời điểm diễn ra cuộc hẹn. Ví dụ: 

| Thời gian lịch khám | Thời gian nhắc lịch |
|---------------------|---------------------|
| 9:00 | 8:00 |
| 15:30| 14:30 |

Ban đầu, việc gửi email nhắc lịch có thể được thực hiện trực tiếp trong “Appointment API” ngay khi tạo lịch hẹn. Tuy nhiên, đây cũng chính là nguyên nhân dẫn đến một số vấn đề về hiệu năng và khả năng mở rộng của hệ thống khi áp dụng vào thực tế:

- Thời gian phản hồi của API có thể bị chậm do phải xử lý thêm tác vụ gửi email cùng một request.

- Request có thể bị “block” nếu dịch vụ email phản hồi chậm hoặc gặp lỗi. Vì trong thời gian chờ email service phản hồi, luồng xử lý của server vẫn bị chiếm dụng, làm giảm khả năng xử lý các request khác của hệ thống.

- Khó mở rộng hệ thống khi số lượng thông báo tăng lên đáng kể.

- Khó quản lý và thực hiện  cơ chế retry khi việc gửi email thất bại.

Chính vì những vấn đề đó mà hệ thống cần có một cơ chế xử lý background tasks nhằm tách biệt việc gửi thông báo khỏi luồng xử lý chính của API. Từ đó, cải thiện hiệu năng và khả năng mở rộng của hệ thống.

## Quyết định kiến trúc
Để giải quyết các vấn đề trên, chúng tôi quyết định áp dụng kiến trúc Broker để xử lý các tác vụ thông báo theo cơ chế bất đồng bộ (asynchronous processing). Trong kiến trúc này, các thành phần của hệ thống không giao tiếp trực tiếp với nhau mà thông qua một Message Broker đóng vai trò trung gian. Message Broker chịu trách nhiệm tiếp nhận, lưu trữ và phân phối các messages từ các thành phần producer đến các thành phần consumer.

Trong phạm vi của hệ thống Medical Appointment, chúng tôi lựa chọn RabbitMQ làm message broker để triển khai cơ chế message queue cho việc xử lý notification. Với kiến trúc xử lý thông báo như sau:

**1. Appointment API**

**2. Message Producer**

**3. Message Queue (RabbitMQ)**

**4. Notification Worker**

**5. Email Service**

### Quy trình hoạt động chi tiết

1. Khi một cuộc hẹn (appointment) được tạo (bệnh nhân đặt lịch khám), hệ thống sẽ tính toán thời điểm nhắc lịch (reminder_time) dựa trên thời gian khám.

2. Appointment API lúc này sẽ gửi một sự kiện thông báo (notification event) vào RabbitMQ thông qua Message Producer.

3. Notification Worker sẽ lắng nghe và nhận message từ message queue.

4. Khi đến thời điểm nhắc lịch (reminder_time), Worker sẽ thực hiện gửi email thông qua Email Service.

5. RabbitMQ sử dụng  AMQP protocol để truyền message giữa producer và worker.

Với cách tiếp cận mới, chúng tôi muốn tách biệt tác vụ gửi email khỏi request chính của hệ thống để tăng khả năng mở rộng cũng như khắc phục những vấn đề đã đề cập đến trong mô hình trước đây.

## Lý do lựa chọn

Trong kiến trúc Message Queue, RabbitMQ được lựa chọn làm message broker dựa trên những lý do sau:

**1. Hỗ trợ xử lý bất đồng bộ:** RabbitMQ cho phép xử lý các tác vụ nền như gửi email hoặc thông báo mà không ảnh đến thời gian phản hồi của API.

**2. Độ tin cậy cao:** RabbitMQ cung cấp nhiều cơ chế đảm bảo độ tin cậy của message, bao gồm: Message persistence, Message acknowledgment, Retry mechanisms. Các cơ chế này giúp đảm bảo thông báo sẽ không bị mất trong trường hợp worker gặp lỗi hoặc hệ thống bị gián đoạn.

**3. Phù hợp với Django framework ở Backend:** RabbitMQ tích hợp tốt với Celery framework để xử lý background tasks trong các hệ thống sử dụng Django.

**4. Cải thiện hiệu năng hệ thống:** Việc xử lý notification thông qua message queue giúp giảm tải cho backend khi phải xử lý quá nhiều tác vụ trong cùng một request, từ đó cải thiện tốc độ phản hồi của API.

## Hệ quả:
### Tích cực:
- Cải thiện hiệu năng tổng thể của hệ thống.

- Cho phép xử lý background tasks hiệu quả.

- Tăng khả năng scalability khi số lượng thông báo tăng.

- Giảm sự phụ thuộc trực tiếp giữa các thành phần trong hệ thống thông qua cơ chế message broker.

- Tránh việc block API requests do các tác vụ gửi email.

### Tiêu cực:
- Làm tăng độ phức tạp của kiến trúc hệ thống.

- Cần triển khai và quản lý thêm một message broker.

- Cần giám sát và theo dõi hoạt động của message queue và workers để đảm bảo hệ thống hoạt động ổn định.

*Ngày quyết định: 12/03/2026*
