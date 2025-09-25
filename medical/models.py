from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, Time, Enum, Float, ForeignKey
from medical import app, db
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as RoleEnum
from flask_login import UserMixin


class UserRole(RoleEnum):
    PATIENT = 1
    DOCTOR = 2
    ADMIN = 3


class AppointmentStatus(RoleEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    CANCELED = "canceled"
    COMPLETED = "completed"


class PaymentMethod(RoleEnum):
    VNPAY = "vnpay"
    MOMO = "momo"


class PaymentStatus(RoleEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    address = Column(String(300), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(50), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    phone = Column(String(15), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(300), nullable=False)
    avatar = Column(String(250), nullable=True)
    user_role = Column(Enum(UserRole), default=UserRole.PATIENT)
    created_date = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    # Quan hệ
    patient_profile = relationship('PatientProfile', backref='user', uselist=False, lazy='joined',
                                   cascade='all, delete-orphan')
    doctor_profile = relationship('DoctorProfile', backref='user', uselist=False, lazy='joined',
                                  cascade='all, delete-orphan')
    appointments_as_patient = relationship('Appointment', backref='patient', lazy='selectin')

    def __str__(self):
        return self.full_name


class PatientProfile(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=True)
    blood_type = Column(String(5), nullable=True)
    insurance_number = Column(String(50), nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    allergies = Column(Text, nullable=True)
    chronic_diseases = Column(Text, nullable=True)
    disease_description = Column(Text, nullable=True)
    test_results = Column(Text, nullable=True)
    created_date = Column(DateTime, default=datetime.now)
    files = relationship('MedicalFile', backref='personal_file_test', lazy='joined', cascade='all, delete-orphan')


class Specialty(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    doctors = relationship('DoctorProfile', backref='specialty', lazy='selectin')

    def __str__(self):
        return self.name


class Hospital(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    address = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    doctors = relationship('DoctorProfile', backref='hospital', lazy='selectin')

    def __str__(self):
        return self.name


class DoctorProfile(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, unique=True)
    academic_degree = Column(String(100), nullable=False)
    license_file = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    specialty_id = Column(Integer, ForeignKey(Specialty.id), nullable=False)
    hospital_id = Column(Integer, ForeignKey(Hospital.id), nullable=True)
    schedules = relationship('Schedule', backref='doctor', lazy='selectin', cascade='all, delete-orphan')
    appointments_as_doctor = relationship('Appointment', backref='doctor', lazy='selectin')


class Schedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    doctor_id = Column(Integer, ForeignKey(DoctorProfile.id), nullable=False)
    appointments = relationship('Appointment', backref='schedule', lazy='selectin')


class Appointment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    reason = Column(String(255), nullable=False)
    cancel_reason = Column(String(255), nullable=True)
    fee = Column(Float, default=10000)
    created_date = Column(DateTime, default=datetime.now)
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    doctor_id = Column(Integer, ForeignKey(DoctorProfile.id), nullable=False)
    schedule_id = Column(Integer, ForeignKey(Schedule.id), nullable=True)
    medical_record = relationship('MedicalRecord', backref='appointment', lazy='joined', uselist=False,
                                  cascade='all, delete-orphan')
    payment = relationship('Payment', backref='appointment', lazy='joined', uselist=False, cascade='all, delete-orphan')
    rating = relationship('Rating', backref='appointment', lazy='joined', uselist=False, cascade='all, delete-orphan')


class MedicalRecord(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    diagnosis = Column(Text, nullable=True)
    test_results = Column(Text, nullable=True)
    symptoms = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    created_date = Column(DateTime, default=datetime.now)
    appointment_id = Column(Integer, ForeignKey(Appointment.id), unique=True)
    files = relationship('MedicalFile', backref='medical_record', lazy='joined', cascade='all, delete-orphan')


class MedicalFile(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_profile_id = Column(Integer, ForeignKey(PatientProfile.id), nullable=True)
    medical_record_id = Column(Integer, ForeignKey(MedicalRecord.id), nullable=True)
    file_url = Column(String(255), nullable=False)
    uploaded_date = Column(DateTime, default=datetime.now)


class Payment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.MOMO)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(String(100), nullable=True)
    created_date = Column(DateTime, default=datetime.now)
    appointment_id = Column(Integer, ForeignKey(Appointment.id), unique=True)


class Rating(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    stars = Column(Integer, nullable=False)
    comment = Column(String(255), nullable=True)
    doctor_reply = Column(String(255), nullable=True)
    created_date = Column(DateTime, default=datetime.now)
    patient_id = Column(Integer, ForeignKey(User.id), nullable=False)
    doctor_id = Column(Integer, ForeignKey(DoctorProfile.id), nullable=False)
    appointment_id = Column(Integer, ForeignKey(Appointment.id), unique=True)


class Notification(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    type = Column(String(150), default='GENERAL')
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # import hashlib
        #
        # u = User(full_name='Nguyễn Vân Anh', address='HCM', date_of_birth='2003-07-18', gender='Nữ', username='zennen',
        #          email='nguyenvananh9606@gmail.com', phone='0932694738',
        #          avatar='https://res.cloudinary.com/dvn6qzq9o/image/upload/v1713096443/Deen-Mustachio_lxrcg7.png',
        #          password=str(hashlib.md5('admin'.encode('utf-8')).hexdigest()),
        #          user_role=UserRole.ADMIN)
        #
        # u1 = User(full_name='Ngô Hoài Kiều Trinh', address='HCM', date_of_birth='2004-09-09', gender='Nữ',
        #           username='tina',
        #           email='2254052086trinh@ou.edu.vn', phone='0359526055',
        #           avatar='https://res.cloudinary.com/dvn6qzq9o/image/upload/v1713096443/Deen-Mustachio_lxrcg7.png',
        #           password=str(hashlib.md5('admin'.encode('utf-8')).hexdigest()),
        #           user_role=UserRole.ADMIN)
        #
        # u2 = User(full_name='Nguyễn Thị Thùy Dương', address='HCM', date_of_birth='2003-08-11', gender='Nữ',
        #           username='daisy',
        #           email='2251012044duong@ou.edu.vn', phone='0387499939',
        #           avatar='https://res.cloudinary.com/dvn6qzq9o/image/upload/v1713096461/61577e5045247.595ecab320c61_gydemz.png',
        #           password=str(hashlib.md5('admin'.encode('utf-8')).hexdigest()),
        #           user_role=UserRole.ADMIN)
        #
        # db.session.add_all([u, u1, u2])
        #
        # db.session.commit()
