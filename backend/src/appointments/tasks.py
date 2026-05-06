from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from appointments.models import Appointment, AppointmentStatus
from django.utils import timezone
from datetime import timedelta, datetime
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
        slot_dt = datetime.combine(
            appointment.time_slot.schedule.work_date,
            appointment.time_slot.start_time,
        )
        if timezone.is_naive(slot_dt):
            slot_dt = timezone.make_aware(slot_dt, timezone.get_current_timezone())
        slot_display = timezone.localtime(slot_dt).strftime('%d/%m/%Y %H:%M')

        subject = f'Nhắc nhở: Lịch hẹn với {doctor_name}'
        message = f'''
        Xin chào {appointment.patient.user.fullname},
        
        Đây là nhắc nhở về lịch hẹn của bạn:
        - Bác sĩ: {doctor_name}
        - Thời gian: {slot_display}
        
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
        now = timezone.localtime()
        tomorrow = now + timedelta(hours=24)

        candidates = Appointment.objects.filter(
            time_slot__schedule__work_date__gte=now.date(),
            time_slot__schedule__work_date__lte=tomorrow.date(),
            status=AppointmentStatus.BOOKED,
        )

        count = 0
        for appointment in candidates:
            slot_dt = datetime.combine(
                appointment.time_slot.schedule.work_date,
                appointment.time_slot.start_time,
            )
            if timezone.is_naive(slot_dt):
                slot_dt = timezone.make_aware(slot_dt, timezone.get_current_timezone())
            if now <= slot_dt <= tomorrow:
                send_appointment_reminder.delay(appointment.id)
                count += 1

        logger.info(f"Sent reminders for {count} appointments")
        return f"Reminders sent for {count} appointments"
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
            time_slot__schedule__work_date__lt=one_year_ago.date(),
            status__in=[AppointmentStatus.CANCELED, AppointmentStatus.COMPLETED]
        )
        count = old_appointments.count()
        old_appointments.delete()
        logger.info(f"Deleted {count} old appointments")
        return f"Deleted {count} old appointments"
    except Exception as exc:
        logger.error(f"Error in cleanup_old_appointments: {exc}")
        return f"Error: {exc}"
