from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from appointments.models import Appointment
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_appointment_confirmation(self, appointment_id):
    """
    Gửi email xác nhận lịch hẹn
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        user_email = appointment.patient.user.email
        doctor_name = appointment.doctor.user.fullname
        
        subject = f'Xác nhận lịch hẹn với {doctor_name}'
        message = f'''
        Xin chào {appointment.patient.user.fullname},
        
        Lịch hẹn của bạn đã được xác nhận:
        - Bác sĩ: {doctor_name}
        - Thời gian: {appointment.time_slot}
        - Trạng thái: {appointment.status}
        
        Vui lòng đến đúng giờ.
        
        Trân trọng,
        Medical Appointment Team
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Appointment confirmation sent for appointment {appointment_id}")
        return f"Appointment confirmation sent"
    except Appointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} not found")
        return f"Appointment {appointment_id} not found"
    except Exception as exc:
        logger.error(f"Error sending appointment confirmation: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_appointment_reminder(self, appointment_id):
    """
    Gửi reminder 24h trước cuộc hẹn
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        user_email = appointment.patient.user.email
        doctor_name = appointment.doctor.user.fullname
        
        subject = f'Nhắc nhở: Lịch hẹn với {doctor_name} vào ngày mai'
        message = f'''
        Xin chào {appointment.patient.user.fullname},
        
        Đây là nhắc nhở về lịch hẹn của bạn:
        - Bác sĩ: {doctor_name}
        - Thời gian: {appointment.time_slot}
        
        Vui lòng đến đúng giờ và chuẩn bị các tài liệu cần thiết.
        
        Trân trọng,
        Medical Appointment Team
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Appointment reminder sent for appointment {appointment_id}")
        return f"Appointment reminder sent"
    except Appointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} not found")
        return f"Appointment {appointment_id} not found"
    except Exception as exc:
        logger.error(f"Error sending appointment reminder: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def send_appointment_reminders():
    """
    Task chạy định kỳ (via Celery Beat): 
    Gửi reminder cho tất cả appointment trong 24h tới
    """
    try:
        now = timezone.now()
        tomorrow = now + timedelta(hours=24)
        
        # Lấy tất cả appointments trong 24h tới mà chưa gửi reminder
        appointments = Appointment.objects.filter(
            time_slot__gte=now,
            time_slot__lte=tomorrow,
            status='confirmed'
        )
        
        for appointment in appointments:
            send_appointment_reminder.delay(appointment.id)
        
        logger.info(f"Sent reminders for {appointments.count()} appointments")
        return f"Reminders sent for {appointments.count()} appointments"
    except Exception as exc:
        logger.error(f"Error in send_appointment_reminders: {exc}")
        return f"Error: {exc}"


@shared_task
def cleanup_old_appointments():
    """
    Task chạy định kỳ: Xóa hoặc archive appointments cũ
    """
    try:
        # Ví dụ: Archive appointments cũ hơn 1 năm
        one_year_ago = timezone.now() - timedelta(days=365)
        old_appointments = Appointment.objects.filter(
            time_slot__lt=one_year_ago,
            status__in=['cancelled', 'completed']
        )
        count = old_appointments.count()
        old_appointments.delete()
        logger.info(f"Deleted {count} old appointments")
        return f"Deleted {count} old appointments"
    except Exception as exc:
        logger.error(f"Error in cleanup_old_appointments: {exc}")
        return f"Error: {exc}"

