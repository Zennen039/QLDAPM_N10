import cloudinary.uploader
from medical.models import *
from sqlalchemy import func
import hashlib
from flask_login import current_user
from medical.utils import send_email


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    un = User.query.filter_by(username=username, password=password)

    if role:
        un = un.filter(User.user_role == role)
    return un.first()


def add_user(full_name, username, address, gender, date_of_birth, phone, email, password, academic_degree=None,
             specialty_id=None, hospital_id=None, role=UserRole.PATIENT, avatar=None, license_file=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(full_name=full_name, phone=phone, email=email, username=username, address=address,
             gender=gender, date_of_birth=date_of_birth, password=password, user_role=role)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')
    db.session.add(u)
    db.session.flush()

    if role == UserRole.DOCTOR:
        if not license_file or not academic_degree or not specialty_id:
            raise ValueError("Bác sĩ cần cung cấp đầy đủ thông tin giấy phép, học vị, chuyên khoa.")
        d = DoctorProfile(user_id=u.id, academic_degree=academic_degree, specialty_id=specialty_id,
                          hospital_id=hospital_id, is_verified=False)
        if license_file:
            res = cloudinary.uploader.upload(license_file)
            d.license_file = res.get('secure_url')
        db.session.add(d)
        # Gửi thông báo cho admin khi có bác sĩ mới đăng ký
        admin_user = User.query.filter_by(user_role=UserRole.ADMIN).first()

        if admin_user:
            add_notification(admin_user.id, f"Bác sĩ mới đăng ký: {full_name}. Vui lòng xác thực.", 'NEW_DOCTOR')
    elif role == UserRole.PATIENT:
        p = PatientProfile(user_id=u.id)
        db.session.add(p)
    db.session.commit()
    return u


def load_specialties():
    return Specialty.query.all()


def load_hospitals():
    return Hospital.query.all()


def get_specialty_by_id(specialty_id):
    return Specialty.query.get(specialty_id)


def get_hospital_by_id(hospital_id):
    return Hospital.query.get(hospital_id)


def add_specialty(name, description):
    sp = Specialty(name=name, description=description)
    db.session.add(sp)
    db.session.commit()
    return sp


def update_specialty(specialty_id, name=None, description=None):
    sp = Specialty.query.get(specialty_id)

    if sp:
        if name:
            sp.name = name
        if description:
            sp.description = description
        db.session.commit()
    return sp


def delete_specialty(specialty_id):
    sp = Specialty.query.get(specialty_id)

    if sp:
        db.session.delete(sp)
        db.session.commit()
    return sp


def add_hospital(name, address, description):
    hp = Hospital(name=name, address=address, description=description)
    db.session.add(hp)
    db.session.commit()
    return hp


def update_hospital(hospital_id, name=None, address=None, description=None):
    hp = Hospital.query.get(hospital_id)

    if hp:
        if name:
            hp.name = name
        if address:
            hp.address = address
        if description:
            hp.description = description
        db.session.commit()
    return hp


def delete_hospital(hospital_id):
    hp = Hospital.query.get(hospital_id)

    if hp:
        db.session.delete(hp)
        db.session.commit()
    return hp


def get_all_doctors(verified=None, specialty_id=None, academic_degree=None):
    q = DoctorProfile.query.join(User)

    if verified is not None:
        q = q.filter(DoctorProfile.is_verified == verified)
    if specialty_id:
        q = q.filter(DoctorProfile.specialty_id == specialty_id)
    if academic_degree:
        q = q.filter(DoctorProfile.academic_degree == academic_degree)
    return q.all()


def verify_doctor(doctor_id):
    d = DoctorProfile.query.get(doctor_id)

    if d:
        d.is_verified = True
        add_notification(d.user_id, "Tài khoản bác sĩ của bạn đã được quản trị viên xác thực.",
                         type='DOCTOR_VERIFICATION')
        db.session.commit()
    return d


def reject_doctor(doctor_id, reason=None, delete=False):
    d = DoctorProfile.query.get(doctor_id)

    if not d:
        return None

    if delete:
        # Xóa file license thì trên Cloudinary
        if d.license_file:
            public_id = d.license_file.rsplit("/", 1)[-1].split(".")[0]

            try:
                cloudinary.uploader.destroy(public_id)
            except:
                pass
        # Xoá DoctorProfile
        db.session.delete(d)
        # Xoá luôn User
        u = User.query.get(d.user_id)

        if u:
            db.session.delete(u)
        db.session.commit()
        return True
    else:
        # Chỉ từ chối, không xoá
        d.is_verified = False

        if reason:
            add_notification(d.user_id, f"Tài khoản bác sĩ của bạn đã bị từ chối. Lý do: {reason}",
                             type='DOCTOR_VERIFICATION')
        db.session.commit()
    return True


def get_patient_profile(user_id):
    return PatientProfile.query.filter_by(user_id=user_id).first()


def get_ratings_by_patient(user_id):
    return Rating.query.join(Appointment).filter(Appointment.patient_id == user_id).all()


def get_patient_files(patient_profile_id):
    return MedicalFile.query.filter_by(patient_profile_id=patient_profile_id).all()


def update_patient_info(user_id, full_name=None, date_of_birth=None, gender=None, avatar=None, address=None, phone=None,
                        email=None, blood_type=None, insurance_number=None, emergency_contact=None, allergies=None,
                        chronic_diseases=None, disease_description=None, test_results=None, file=None):
    u = User.query.get(user_id)
    p = PatientProfile.query.filter_by(user_id=user_id).first()

    if not u:
        return None
    if not p:
        p = PatientProfile(user_id=user_id)
        db.session.add(p)
    if full_name:
        u.full_name = full_name
    if date_of_birth:
        u.date_of_birth = date_of_birth
    if gender:
        u.gender = gender
    if address:
        u.address = address
    if phone:
        u.phone = phone
    if email:
        u.email = email
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')
    # Cập nhật PatientProfile
    if blood_type is not None:
        p.blood_type = blood_type
    if insurance_number is not None:
        p.insurance_number = insurance_number
    if emergency_contact is not None:
        p.emergency_contact = emergency_contact
    if allergies is not None:
        p.allergies = allergies
    if chronic_diseases is not None:
        p.chronic_diseases = chronic_diseases
    if disease_description is not None:
        p.disease_description = disease_description
    if test_results is not None:
        p.test_results = test_results
    if file:
        res = cloudinary.uploader.upload(file)
        f = MedicalFile(patient_profile_id=p.id, file_url=res.get('secure_url'))
        db.session.add(f)
    db.session.commit()
    return u


def get_medical_record(appointment_id):
    return MedicalRecord.query.filter_by(appointment_id=appointment_id).first()


def get_medical_records_for_patient(patient_id):
    return MedicalRecord.query.join(Appointment).filter(Appointment.patient_id == patient_id).all()


def update_medical_record(appointment_id, diagnosis=None, test_results=None, symptoms=None, medical_history=None,
                          file=None):
    mr = MedicalRecord.query.filter_by(appointment_id=appointment_id).first()

    if not mr:
        mr = MedicalRecord(appointment_id=appointment_id)
        db.session.add(mr)
        db.session.flush()
    if diagnosis:
        mr.diagnosis = diagnosis
    if test_results:
        mr.test_results = test_results
    if symptoms:
        mr.symptoms = symptoms
    if medical_history:
        mr.medical_history = medical_history
    if file:
        res = cloudinary.uploader.upload(file)
        f = MedicalFile(medical_record_id=mr.id, file_url=res.get('secure_url'))
        db.session.add(f)
    db.session.commit()
    return mr


def delete_medical_record(appointment_id):
    mr = MedicalRecord.query.filter_by(appointment_id=appointment_id).first()

    if mr:
        db.session.delete(mr)
        db.session.commit()
    return mr


def delete_patient_file(file_id):
    f = MedicalFile.query.get(file_id)

    if f and f.patient_profile_id:
        db.session.delete(f)
        db.session.commit()
        return True
    return False


def get_doctor_profile(user_id):
    return DoctorProfile.query.filter_by(user_id=user_id).first()


def update_doctor_info(user_id, full_name=None, date_of_birth=None, gender=None, avatar=None, address=None,
                       phone=None, email=None, academic_degree=None, specialty_id=None, hospital_id=None,
                       license_file=None):
    u = User.query.get(user_id)
    d = DoctorProfile.query.filter_by(user_id=user_id).first()

    if not u or not d:
        return None
    # Cập nhật user
    if full_name:
        u.full_name = full_name
    if date_of_birth:
        u.date_of_birth = date_of_birth
    if gender:
        u.gender = gender
    if address:
        u.address = address
    if phone:
        u.phone = phone
    if email:
        u.email = email
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')
    # Cập nhật DoctorProfile
    if academic_degree:
        d.academic_degree = academic_degree
    if specialty_id:
        d.specialty_id = specialty_id
    if hospital_id:
        d.hospital_id = hospital_id
    if license_file:
        res = cloudinary.uploader.upload(license_file)
        d.license_file = res.get('secure_url')
        d.is_verified = False  # Cập nhật license mới => cần admin xác thực lại
        admin_user = User.query.filter_by(user_role=UserRole.ADMIN).first()

        if admin_user:
            add_notification(admin_user.id, f"Bác sĩ {u.full_name} cập nhật giấy phép hành nghề. Vui lòng xác thực.",
                             'DOCTOR_VERIFICATION')
    db.session.commit()
    return u


def get_schedule_by_id(schedule_id):
    return Schedule.query.get(schedule_id)


def get_schedules_by_doctor(doctor_id):
    return Schedule.query.filter_by(doctor_id=doctor_id).order_by(Schedule.date, Schedule.start_time).all()


def add_schedule(doctor_id, date, start_time, end_time):
    # Kiểm tra trùng lịch làm việc của bác sĩ
    overlapping = Schedule.query.filter(Schedule.doctor_id == doctor_id,
                                        Schedule.date == date,
                                        Schedule.start_time < end_time,
                                        Schedule.end_time > start_time).first()
    if overlapping:
        return None  # Trùng lịch làm việc
    s = Schedule(doctor_id=doctor_id, date=date, start_time=start_time, end_time=end_time)
    db.session.add(s)
    db.session.commit()
    return s


def update_schedule(schedule_id, date=None, start_time=None, end_time=None, is_available=None):
    s = Schedule.query.get(schedule_id)

    if not s:
        return None

    # Kiểm tra trùng lịch mới (nếu đổi giờ)
    new_date = date or s.date
    new_start = start_time or s.start_time
    new_end = end_time or s.end_time

    overlapping = Schedule.query.filter(Schedule.doctor_id == s.doctor_id, Schedule.id != schedule_id,
                                        Schedule.date == new_date, Schedule.start_time < new_end,
                                        Schedule.end_time > new_start).first()
    if overlapping:
        return None  # Trùng lịch

    s.date = new_date
    s.start_time = new_start
    s.end_time = new_end

    if is_available is not None:
        s.is_available = is_available

    db.session.commit()
    return s


def reschedule(appointment_id, new_start_at, new_end_at, new_schedule_id):
    appt = Appointment.query.get(appointment_id)

    if not appt:
        return None

    # Kiểm tra trùng giờ mới
    overlapping = Appointment.query.filter(Appointment.doctor_id == appt.doctor_id, Appointment.id != appointment_id,
                                           Appointment.status.in_(
                                               [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
                                           Appointment.start_at < new_end_at,
                                           Appointment.end_at > new_start_at).first()

    if overlapping:
        return None  # trùng lịch

    # Nếu appointment hiện có schedule thì set lại schedule đó khả dụng
    if appt.schedule_id:
        old_schedule = Schedule.query.get(appt.schedule_id)

        if old_schedule:
            old_schedule.is_available = True

    # Cập nhật appointment
    appt.start_at = new_start_at
    appt.end_at = new_end_at
    appt.schedule_id = new_schedule_id
    appt.status = AppointmentStatus.RESCHEDULED

    # Set schedule mới thành không khả dụng
    if new_schedule_id:
        new_schedule = Schedule.query.get(new_schedule_id)

        if new_schedule:
            new_schedule.is_available = False

    db.session.commit()

    # Gửi notification cho bệnh nhân
    add_notification(appt.patient_id, f"Lịch hẹn của bạn với bác sĩ {appt.doctor.user.full_name} đã được thay đổi.",
                     type='APPOINTMENT')
    # Gửi email cho bệnh nhân
    send_email(appt.patient.email, "Lịch hẹn đã thay đổi",
               f"Xin chào {appt.patient.full_name},\n\n" f"Lịch hẹn với bác sĩ {appt.doctor.user.full_name} đã được thay đổi sang {new_start_at}.\n"
               "Vui lòng kiểm tra lại thông tin trên hệ thống.")
    return appt


def delete_schedule(schedule_id):
    sch = Schedule.query.get(schedule_id)

    if sch and not sch.appointments:
        db.session.delete(sch)
        db.session.commit()
        return True
    return False  # Không thể xóa lịch đã có cuộc hẹn


def search_doctors(kw=None, specialty_id=None, hospital_id=None, academic_degree=None, page=1):
    q = DoctorProfile.query.join(User).outerjoin(Hospital).outerjoin(Specialty).filter(
        DoctorProfile.is_verified == True)

    if kw:
        q = q.filter(User.full_name.contains(kw))
    if specialty_id:
        q = q.filter(DoctorProfile.specialty_id == specialty_id)
    if hospital_id:
        q = q.filter(DoctorProfile.hospital_id == hospital_id)
    if academic_degree:
        q = q.filter(DoctorProfile.academic_degree == academic_degree)

    page_size = app.config.get('PAGE_SIZE')
    start = (page - 1) * page_size
    q = q.slice(start, start + page_size)
    return q.all()


def count_doctors(kw=None, specialty_id=None, hospital_id=None, academic_degree=None):
    q = DoctorProfile.query.join(User).outerjoin(Hospital).outerjoin(Specialty).filter(
        DoctorProfile.is_verified == True)

    if kw:
        q = q.filter(User.full_name.contains(kw))
    if specialty_id:
        q = q.filter(DoctorProfile.specialty_id == specialty_id)
    if hospital_id:
        q = q.filter(DoctorProfile.hospital_id == hospital_id)
    if academic_degree:
        q = q.filter(DoctorProfile.academic_degree == academic_degree)
    return q.count()


def get_appointment_by_id(appointment_id):
    return Appointment.query.get(appointment_id)


def get_appointments_for_doctor(doctor_id):
    return Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.start_at.desc()).all()


def get_appointments_for_patient(patient_id):
    return Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.start_at.desc()).all()


def book_appointment(patient_id, doctor_id, start_at, end_at, reason, schedule_id):
    overlapping = Appointment.query.filter(Appointment.doctor_id == doctor_id,
                                           Appointment.status.in_(
                                               [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
                                           Appointment.start_at < end_at, Appointment.end_at > start_at).first()
    if overlapping:
        return None

    ba = Appointment(patient_id=patient_id, doctor_id=doctor_id, start_at=start_at,
                     end_at=end_at, reason=reason, schedule_id=schedule_id)
    db.session.add(ba)
    db.session.commit()

    # Cập nhật lịch làm việc thành không khả dụng
    sc = Schedule.query.get(schedule_id)

    if sc:
        sc.is_available = False
        db.session.commit()

    # Notification cho bác sĩ
    add_notification(ba.doctor.user_id,
                     f"Bạn có lịch hẹn mới từ bệnh nhân {ba.patient.full_name}.",
                     type='APPOINTMENT')

    # Gửi email xác nhận cho bệnh nhân
    send_email(ba.patient.email, "Xác nhận lịch khám",
               f"Bạn đã đặt lịch với bác sĩ {ba.doctor.user.full_name} vào {start_at}.")

    return ba


def complete_appointment(appointment_id):
    ap = Appointment.query.get(appointment_id)

    if ap:
        ap.status = AppointmentStatus.COMPLETED
        db.session.commit()
        add_notification(ap.patient_id, f"Lịch hẹn {ap.id} đã hoàn thành.", type='APPOINTMENT')
        send_email(ap.patient.email, "Hoàn thành lịch hẹn",
                   f"Xin chào {ap.patient.full_name}, lịch hẹn với bác sĩ {ap.doctor.user.full_name} đã hoàn thành.")
        return ap
    return None


def update_appointment_status(appointment_id, status, cancel_reason=None):
    ua = Appointment.query.get(appointment_id)

    if ua:
        ua.status = status

        if status == AppointmentStatus.CONFIRMED:
            db.session.commit()
            add_notification(ua.patient_id, f"Lịch hẹn {ua.id} đã được bác sĩ xác nhận.", type='APPOINTMENT')
            send_email(ua.patient.email, "Xác nhận lịch hẹn",
                       f"Xin chào {ua.patient.full_name}, lịch hẹn với bác sĩ {ua.doctor.user.full_name} đã được xác nhận.")

        if status == AppointmentStatus.CANCELED:
            ua.cancel_reason = cancel_reason
            # Đặt lại lịch làm việc thành khả dụng
            if ua.schedule:
                ua.schedule.is_available = True
            db.session.commit()
            # Gửi thông báo cho bệnh nhân
            add_notification(ua.patient_id, f"Lịch hẹn {ua.id} đã bị hủy. Lý do: {cancel_reason}",
                             type='APPOINTMENT')
            # Gửi email cho bệnh nhân
            send_email(ua.patient.email, "Hủy lịch hẹn",
                       f"Xin chào {ua.patient.full_name},\n\n" f"Lịch hẹn với bác sĩ {ua.doctor.user.full_name} vào {ua.start_at} đã bị hủy.\n"
                       f"Lý do: {cancel_reason if cancel_reason else 'Không có lý do cụ thể.'}")
        else:
            db.session.commit()
    return ua


def add_payment(appointment_id, payment_method, total_price=None, transaction_id=None):
    existing = Payment.query.filter_by(appointment_id=appointment_id).first()

    if existing:
        return existing

    appt = Appointment.query.get(appointment_id)

    if not total_price:
        total_price = appt.fee
    pa = Payment(appointment_id=appointment_id, payment_method=payment_method,
                 total_price=total_price, transaction_id=transaction_id)
    db.session.add(pa)
    db.session.commit()

    # Thông báo cho bác sĩ
    add_notification(pa.appointment.doctor.user_id,
                     f"Lịch hẹn {appointment_id} đã được tạo yêu cầu thanh toán.",
                     type='PAYMENT')

    return pa


def update_payment_status(payment_id, status, transaction_id=None):
    up = Payment.query.get(payment_id)

    if up:
        up.status = status
        up.transaction_id = transaction_id
        db.session.commit()

        if status == PaymentStatus.SUCCESS:
            send_email(up.appointment.patient.email, "Thanh toán thành công",
                       f"Lịch hẹn {up.appointment.id} với bác sĩ {up.appointment.doctor.user.full_name} đã thanh toán thành công.")
        elif status == PaymentStatus.FAILED:
            send_email(up.appointment.patient.email, "Thanh toán thất bại",
                       f"Lịch hẹn {up.appointment.id} với bác sĩ {up.appointment.doctor.user.full_name} thanh toán thất bại. Vui lòng thử lại.")
    return up


def add_rating(appointment_id, stars, comment, patient_id, doctor_id):
    apmt = Appointment.query.get(appointment_id)

    if not apmt or apmt.status != AppointmentStatus.COMPLETED:
        return None
    r = Rating(appointment_id=appointment_id, stars=stars, comment=comment, patient_id=patient_id, doctor_id=doctor_id)
    db.session.add(r)
    db.session.commit()

    doctor = DoctorProfile.query.get(doctor_id)

    if doctor:
        add_notification(doctor.user_id,
                         f"Bạn nhận được đánh giá mới từ bệnh nhân {current_user.full_name}.",
                         type='RATING')
    return r


def get_completed_appointments_by_patient(patient_id):
    return Appointment.query.filter_by(patient_id=patient_id, status=AppointmentStatus.COMPLETED).all()


def get_ratings_for_doctor(doctor_id):
    return Rating.query.join(Appointment).filter(Appointment.doctor_id == doctor_id).all()


def doctor_reply_rating(rating_id, reply):
    r = Rating.query.get(rating_id)

    if r:
        r.doctor_reply = reply
        db.session.commit()
    return r


def get_doctor_statistics(doctor_id):
    total_patients = db.session.query(func.count(Appointment.id)).filter(Appointment.doctor_id == doctor_id,
                                                                         Appointment.status == AppointmentStatus.COMPLETED).scalar()
    common_diseases = db.session.query(Appointment.reason, func.count(Appointment.reason)).filter(
        Appointment.doctor_id == doctor_id).group_by(Appointment.reason).order_by(
        func.count(Appointment.reason).desc()).all()

    appointment_stats = db.session.query(
        func.date_format(Appointment.start_at, '%Y-%m'),
        func.count(Appointment.id)
    ).filter(
        Appointment.doctor_id == doctor_id
    ).group_by(func.date_format(Appointment.start_at, '%Y-%m')).all()

    recent_appointments = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.start_at.desc()).limit(
        5).all()

    return {"total_patients": total_patients, "common_diseases": common_diseases,
            "appointment_stats": appointment_stats, "recent_appointments": recent_appointments}


def get_admin_statistics():
    total_appointments = db.session.query(func.count(Appointment.id)).scalar()
    total_users = db.session.query(func.count(User.id)).scalar()
    total_revenue = db.session.query(func.coalesce(func.sum(Payment.total_price), 0)).scalar()

    revenue_by_month = db.session.query(
        func.date_format(Payment.created_date, '%Y-%m'),
        func.coalesce(func.sum(Payment.total_price), 0)
    ).filter(
        Payment.status == PaymentStatus.SUCCESS
    ).group_by(func.date_format(Payment.created_date, '%Y-%m')).all()

    recent_appointments = Appointment.query.order_by(Appointment.start_at.desc()).limit(5).all()

    patients = User.query.filter_by(user_role=UserRole.PATIENT).all()

    return {"total_appointments": total_appointments, "total_users": total_users, "total_revenue": total_revenue,
            "revenue_by_month": revenue_by_month, "recent_appointments": recent_appointments, "patients": patients}


def get_notifications(user_id):
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_date.desc()).all()


def add_notification(user_id, content, type='GENERAL'):
    n = Notification(user_id=user_id, content=content, type=type)
    db.session.add(n)
    db.session.commit()
    return n


def mark_notification_read(notification_id):
    n = Notification.query.get(notification_id)

    if n:
        n.is_read = True
        db.session.commit()
    return n
