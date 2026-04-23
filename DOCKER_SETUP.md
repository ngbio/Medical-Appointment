# Docker & Docker Compose Setup

Để chạy project với Docker:

## Yêu cầu
- Docker Desktop cài đặt
- MySQL chạy trên máy host (localhost:3306)
- Database `medicaldb` đã tạo
- User MySQL: `root` / Password: `root`

## Cách chạy

### 1. Build image
```bash
docker-compose build
```

### 2. Chạy container
```bash
docker-compose up -d
```

### 3. Kiểm tra logs
```bash
docker-compose logs -f backend
```

### 4. Migrate database (nếu cần nha)
```bash
docker-compose exec backend python manage.py migrate
```

### 5. Tạo superuser (nếu cần nha)
```bash
docker-compose exec backend python manage.py createsuperuser
```

### 6. Dừng container
```bash
docker-compose down
```

## Thông tin 

- **Backend URL**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **Database**: MySQL trên localhost:3306 (medicaldb)
- **MySQL User**: root / Password: root


## Ghi chú
- Docker container kết nối tới MySQL trên host thông qua `host.docker.internal` (Windows)
- Frontend folder được mount để Django có thể access templates và static files
- Settings.py đã được cấu hình để kết nối tới MySQL với credentials: root/root
- Static files được mount qua volume

