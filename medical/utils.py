from flask_mail import Message
from medical import app, mail
from datetime import datetime, timedelta
from medical.models import Appointment, AppointmentStatus


def send_email(to, subject, body):
    # Gửi email
    with app.app_context():
        msg = Message(subject=subject, recipients=[to], body=body)

        mail.send(msg)


def get_upcoming_appointments(minutes=10):
    now = datetime.now()

    end = now + timedelta(minutes=minutes)

    return Appointment.query.filter(Appointment.start_at >= now, Appointment.start_at <= end, Appointment.status.in_(
        [AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING])).all()


def send_appointment_reminders():
    appointments = get_upcoming_appointments(minutes=10)  # nhắc trước 10 phút

    for appt in appointments:
        send_email(appt.patient.email, "Nhắc nhở lịch khám",
                   f"Xin chào {appt.patient.full_name},\n" f"Bạn có lịch hẹn với bác sĩ {appt.doctor.user.full_name} vào {appt.start_at}.\n" "Vui lòng đến đúng giờ!")
