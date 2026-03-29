from datetime import datetime, timedelta
from ..models import TimeSlot, DoctorSchedule

def generate_timeslots(schedule: DoctorSchedule):
    SLOT_DURATION = 30  # Duration of each time slot in minutes
    start = datetime.combine(schedule.work_date, schedule.start_time)
    end = datetime.combine(schedule.work_date, schedule.end_time)

    slots = []

    current_time = start
    while current_time + timedelta(minutes=SLOT_DURATION) <= end:
        slot = TimeSlot(
            schedule=schedule,
            start_time=current_time.time(),
            end_time=(current_time + timedelta(minutes=SLOT_DURATION)).time()
        )
        slots.append(slot)
        current_time += timedelta(minutes=SLOT_DURATION)

    TimeSlot.objects.bulk_create(slots)

if __name__ == "__main__":
    # Example usage
    schedule = DoctorSchedule.objects.first()  # Get a schedule to generate time slots for
    if schedule:
        generate_timeslots(schedule)