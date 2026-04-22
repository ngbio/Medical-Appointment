from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from users.models import User
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email_confirmation(self, user_id, confirmation_url):
    """
    Gửi email xác nhận đăng ký
    """
    try:
        user = User.objects.get(id=user_id)
        subject = 'Xác nhận đăng ký tài khoản'
        message = f'''
        Xin chào {user.fullname},
        
        Vui lòng xác nhận email của bạn bằng cách nhấp vào link sau:
        {confirmation_url}
        
        Trân trọng,
        Medical Appointment Team
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Confirmation email sent to {user.email}")
        return f"Email sent to {user.email}"
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
    except Exception as exc:
        logger.error(f"Error sending email: {exc}")
        # Retry sau 60 giây
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, reset_url):
    """
    Gửi email đặt lại mật khẩu
    """
    try:
        user = User.objects.get(id=user_id)
        subject = 'Đặt lại mật khẩu'
        message = f'''
        Xin chào {user.fullname},
        
        Bạn yêu cầu đặt lại mật khẩu. Vui lòng nhấp vào link sau:
        {reset_url}
        
        Link này sẽ hết hạn sau 24 giờ.
        
        Trân trọng,
        Medical Appointment Team
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {user.email}")
        return f"Email sent to {user.email}"
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
    except Exception as exc:
        logger.error(f"Error sending email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def sync_user_data(user_id):
    """
    Task ví dụ: Đồng bộ dữ liệu user
    """
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Syncing data for user: {user.username}")
        # Làm gì đó...
        return f"User {user.username} data synced"
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"

