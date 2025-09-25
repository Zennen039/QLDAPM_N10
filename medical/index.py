from flask import render_template, request, redirect, url_for, flash, jsonify
from medical import app, login, mail, scheduler
from medical.models import *
from medical.utils import send_appointment_reminders
import dao
import math
import hashlib
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message


# Điều hướng tới trang chủ
@app.route("/")
def homepage():
    return render_template("home/homepage.html")


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


# Form đăng nhập
@app.route("/login", methods=["GET", "POST"])
def login_page():
    err_msg = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        u = dao.auth_user(username=username, password=password)

        if u:
            login_user(u)

            if u.user_role == UserRole.DOCTOR and (not u.doctor_profile or not u.doctor_profile.is_verified):
                flash("Tài khoản bác sĩ chưa được xác thực!", "danger")
                logout_user()
                return redirect(url_for("login_page"))
            else:
                next = request.args.get("next")
                return redirect(next if next else "/")
        else:
            err_msg = "Tên đăng nhập hoặc mật khẩu không đúng!"
    return render_template("account/login.html", err_msg=err_msg)


@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    ps = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email không tồn tại trong hệ thống!", "danger")
        else:
            token = ps.dumps(email, salt="reset-password")
            reset_url = url_for("reset_password", token=token, _external=True)
            msg = Message("Đặt lại mật khẩu", recipients=[email])
            msg.body = f"Nhấp vào link sau để đặt lại mật khẩu: {reset_url}\n(Liên kết có hiệu lực trong 30 phút)"
            mail.send(msg)
            flash("Vui lòng kiểm tra email để đặt lại mật khẩu!", "info")
            return redirect(url_for("login_page"))
    return render_template("account/forgot_password.html")


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    ps = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    try:
        email = ps.loads(token, salt="reset-password", max_age=1800)  # 30 phút
    except SignatureExpired:
        flash("Link đặt lại mật khẩu đã hết hạn!", "danger")
        return redirect(url_for("forgot_password"))
    except BadSignature:
        flash("Link không hợp lệ!", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            flash("Mật khẩu xác nhận không khớp!", "danger")
            return redirect(url_for("reset_password", token=token))
        u = User.query.filter_by(email=email).first()

        if u:
            u.password = str(hashlib.md5(new_password.encode('utf-8')).hexdigest())
            db.session.commit()
            flash("Đặt lại mật khẩu thành công, vui lòng đăng nhập lại!", "success")
            return redirect(url_for("login_page"))
    return render_template("account/reset_password.html")


# Form đăng ký
@app.route("/register", methods=["GET", "POST"])
def register_page():
    err_msg = None
    success_msg = None

    if request.method == "POST":
        full_name = request.form.get("full_name")
        address = request.form.get("address")
        email = request.form.get("email")
        date_of_birth = request.form.get("date_of_birth")
        gender = request.form.get("gender")
        phone = request.form.get("phone")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        avatar = request.files.get("avatar")
        role = request.form.get("user_role")
        license_file = request.files.get("license_file")
        academic_degree = request.form.get("academic_degree")
        specialty_id = request.form.get("specialty_id")
        hospital_id = request.form.get("hospital_id")

        if User.query.filter_by(username=username).first():
            err_msg = "Tên đăng nhập đã tồn tại!"
        elif password != confirm_password:
            err_msg = "Mật khẩu xác nhận không khớp!"
        else:
            user_role = UserRole[role] if role in UserRole.__members__ else UserRole.PATIENT

            try:
                dao.add_user(full_name=full_name, username=username, address=address, gender=gender,
                             date_of_birth=date_of_birth, phone=phone, email=email, password=password, role=user_role,
                             avatar=avatar, license_file=license_file, academic_degree=academic_degree,
                             specialty_id=specialty_id, hospital_id=hospital_id)
                flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
                return redirect(url_for("login_page"))
            except Exception as ex:
                err_msg = "Hệ thống đang gặp lỗi: " + str(ex)
    specialties = dao.load_specialties()
    hospitals = dao.load_hospitals()
    return render_template("account/register.html", err_msg=err_msg, success_msg=success_msg, specialties=specialties,
                           hospitals=hospitals)


@app.route("/list", methods=["GET"])
@login_required
def specialties_list():
    specialties = dao.load_specialties()
    return render_template("home/list.html", specialties=specialties)


@app.route("/hospital_list", methods=["GET"])
@login_required
def hospital_lists():
    hospitals = dao.load_hospitals()
    return render_template("home/hospital_list.html", hospitals=hospitals)


@app.route("/dashboard/admin")
@login_required
def admin_dashboard():
    if current_user.user_role != UserRole.ADMIN:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    stats = dao.get_admin_statistics()
    return render_template("admin/dashboard.html", stats=stats)


@app.route("/doctors_list", methods=["GET"])
@login_required
def admin_doctors():
    if current_user.user_role != UserRole.ADMIN:
        flash("Không có quyền!", "danger")
        return redirect(url_for("homepage"))
    doctors = dao.get_all_doctors()
    return render_template("admin/doctors_list.html", doctors=doctors)


@app.route("/admin/verify_doctors/<int:id>", methods=["POST"])
@login_required
def verify_doctors(id):
    if current_user.user_role != UserRole.ADMIN:
        flash("Không có quyền!", "danger")
        return redirect(url_for('homepage'))
    dao.verify_doctor(id)
    flash("Xác thực bác sĩ thành công!", "success")
    return redirect(url_for("admin_doctors"))


@app.route("/api/reject_doctors/<int:id>", methods=["DELETE"])
@login_required
def reject_doctors(id):
    if current_user.user_role != UserRole.ADMIN:
        flash("Không có quyền!", "danger")
        return redirect(url_for('homepage'))

    data = request.get_json(silent=True) or {}
    reason = data.get("reason")
    delete_flag = bool(data.get("delete"))

    if not reason:
        return jsonify({"status": "error", "message": "Cần có lý do!"}), 400

    ok = dao.reject_doctor(id, reason, delete=delete_flag)
    if not ok:
        return jsonify({"status": "error", "message": "Không tìm thấy bác sĩ"}), 404

    if delete_flag:
        return jsonify({"status": "success", "message": "Đã xoá tài khoản bác sĩ!"})
    else:
        return jsonify({"status": "success", "message": "Đã từ chối bác sĩ!"})


@app.route("/add_sp", methods=["GET", "POST"])
@login_required
def add_specialty():
    if current_user.user_role != UserRole.ADMIN:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name or not description:
            flash("Vui lòng nhập đầy đủ thông tin!", "danger")
        else:
            dao.add_specialty(name=name, description=description)
            flash("Thêm chuyên khoa thành công!", "success")
            return redirect(url_for("specialties_list"))
    return render_template("admin/add_sp.html")


@app.route("/edit_sp/<int:id>", methods=["GET", "POST"])
@login_required
def edit_specialty(id):
    if current_user.user_role != UserRole.ADMIN:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    specialty = dao.get_specialty_by_id(id)

    if not specialty:
        return "Không tìm thấy chuyên khoa!", 404

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        dao.update_specialty(id, name=name, description=description)
        flash("Cập nhật chuyên khoa thành công!", "success")
        return redirect(url_for("specialties_list"))
    return render_template("admin/edit_sp.html", specialty=specialty)


@app.route("/admin/delete_sp/<int:id>", methods=["POST"])
@login_required
def delete_specialty(id):
    if current_user.user_role != UserRole.ADMIN:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    dao.delete_specialty(id)
    flash("Xóa chuyên khoa thành công!", "success")
    return redirect(url_for("specialties_list"))


@app.route("/add_hosp", methods=["GET", "POST"])
@login_required
def add_hospital():
    if current_user.user_role != UserRole.ADMIN:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        description = request.form.get("description")

        if not name or not address or not description:
            flash("Vui lòng nhập đầy đủ thông tin!", "danger")
        else:
            dao.add_hospital(name=name, address=address, description=description)
            flash("Thêm bệnh viện thành công!", "success")
            return redirect(url_for("hospital_lists"))
    return render_template("admin/add_hosp.html")


@app.route("/edit_hosp/<int:id>", methods=["GET", "POST"])
@login_required
def edit_hospital(id):
    if current_user.user_role != UserRole.ADMIN:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    hospital = dao.get_hospital_by_id(id)

    if not hospital:
        return "Không tìm thấy bệnh viện!", 404

    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        description = request.form.get("description")
        dao.update_hospital(id, name=name, address=address, description=description)
        flash("Cập nhật bệnh viện thành công!", "success")
        return redirect(url_for("hospital_lists"))
    return render_template("admin/edit_hosp.html", hospital=hospital)


@app.route("/admin/delete_hosp/<int:id>", methods=["POST"])
@login_required
def delete_hospital(id):
    if current_user.user_role != UserRole.ADMIN:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    dao.delete_hospital(id)
    flash("Xóa bệnh viện thành công!", "success")
    return redirect(url_for("hospital_lists"))


@app.route("/dashboard/patient")
@login_required
def patient_dashboard():
    if current_user.user_role != UserRole.PATIENT:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    appointments = dao.get_appointments_for_patient(current_user.id)
    return render_template("patient/dashboard.html", appointments=appointments)


@app.route("/patient-profile")
@login_required
def patient_profile():
    if current_user.user_role != UserRole.PATIENT:
        flash("Chỉ bệnh nhân mới được truy cập!", "danger")
        return redirect(url_for("homepage"))
    profile = dao.get_patient_profile(current_user.id)
    return render_template("patient/profile.html", profile=profile, user=current_user)


@app.route("/update_profile", methods=["GET", "POST"])
@login_required
def update_patient_profile():
    if current_user.user_role != UserRole.PATIENT:
        flash("Chỉ bệnh nhân mới được truy cập!", "danger")
        return redirect(url_for("homepage"))

    profile = dao.get_patient_profile(current_user.id)

    if request.method == "POST":
        full_name = request.form.get("full_name")
        address = request.form.get("address")
        email = request.form.get("email")
        date_of_birth = request.form.get("date_of_birth")
        gender = request.form.get("gender")
        phone = request.form.get("phone")
        avatar = request.files.get("avatar")
        blood_type = request.form.get("blood_type")
        insurance_number = request.form.get("insurance_number")
        emergency_contact = request.form.get("emergency_contact")
        allergies = request.form.get("allergies")
        chronic_diseases = request.form.get("chronic_diseases")
        description = request.form.get("disease_description")
        test_results = request.form.get("test_results")
        file = request.files.get("file")
        dao.update_patient_info(current_user.id, full_name, date_of_birth, gender, avatar, address, phone, email,
                                blood_type, insurance_number, emergency_contact, allergies, chronic_diseases,
                                description, test_results, file)
        flash("Cập nhật thông tin cá nhân thành công!", "success")
        return redirect(url_for("patient_profile"))
    return render_template("patient/edit.html", profile=profile, user=current_user)


@app.route("/search_doctors", methods=["GET"])
@login_required
def search():
    if current_user.user_role != UserRole.PATIENT:
        flash("Chỉ bệnh nhân mới được tìm kiếm bác sĩ!", "danger")
        return redirect(url_for("homepage"))
    kw = request.args.get("kw")
    specialty_id = request.args.get("specialty_id")
    hospital_id = request.args.get("hospital_id")
    academic_degree = request.args.get("academic_degree")
    page = request.args.get("page", 1)
    sp = dao.load_specialties()
    h = dao.load_hospitals()
    doctors = dao.search_doctors(kw=kw, specialty_id=specialty_id, hospital_id=hospital_id,
                                 academic_degree=academic_degree, page=int(page))
    page_size = app.config.get('PAGE_SIZE', 5)
    total = dao.count_doctors(kw=kw, specialty_id=specialty_id, hospital_id=hospital_id,
                              academic_degree=academic_degree)
    return render_template("patient/search_doctor.html", doctors=doctors, pages=math.ceil(total / page_size),
                           specialties=sp, hospitals=h)


@app.route("/patient/appointments")
@login_required
def patient_appointments():
    if current_user.user_role != UserRole.PATIENT:
        flash("Chỉ bệnh nhân mới được truy cập!", "danger")
        return redirect(url_for("homepage"))
    appointments = dao.get_appointments_for_patient(current_user.id)
    return render_template('patient/appointments.html', appointments=appointments)


@app.route("/choose", methods=["GET"])
@login_required
def choose_doctor():
    if current_user.user_role != UserRole.PATIENT:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    doctors = dao.get_all_doctors()  # trả về danh sách bác sĩ
    return render_template("patient/choose.html", doctors=doctors)


@app.route("/patient/view_schedule/<int:doctor_id>")
@login_required
def view_doctor_schedule(doctor_id):
    if current_user.user_role != UserRole.PATIENT:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    doctor = dao.get_doctor_profile(doctor_id)

    if not doctor:
        flash("Không tìm thấy thông tin bác sĩ!", "danger")
        return redirect(url_for("homepage"))

    schedules = dao.get_schedules_by_doctor(doctor.id)

    return render_template(
        "patient/view_schedule.html", schedules=schedules, doctor=doctor)


@app.route("/patient/book_apmt/<int:doctor_id>", methods=["GET", "POST"])
@login_required
def book_appointment(doctor_id):
    if current_user.user_role != UserRole.PATIENT:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    doctor = dao.get_doctor_profile(doctor_id)

    if not doctor:
        flash("Không tìm thấy bác sĩ này!", "danger")
        return redirect(url_for("patient_dashboard"))

    schedules = dao.get_schedules_by_doctor(doctor.id)

    if request.method == "POST":
        start_at = request.form.get("start_at")
        end_at = request.form.get("end_at")
        reason = request.form.get("reason", "").strip()
        schedule_id = request.form.get("schedule_id")

        if not reason:
            flash("Vui lòng nhập lý do khám!", "danger")
            return redirect(url_for("book_appointment", doctor_id=doctor_id))
        dao.book_appointment(current_user.id, doctor.id, start_at, end_at, reason, schedule_id)
        flash("Đặt lịch hẹn khám thành công!", "success")
        return redirect(url_for("patient_appointments"))
    return render_template("patient/book_apmt.html", doctor=doctor, schedules=schedules)


@app.route("/doctor/cancel_apmt/<int:appointment_id>", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    if current_user.user_role != UserRole.DOCTOR:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    if request.method == "POST":
        cancel_reason = request.form.get("cancel_reason")
        dao.update_appointment_status(appointment_id, AppointmentStatus.CANCELED, cancel_reason=cancel_reason)
        flash("Hủy lịch hẹn thành công!", "success")
    return redirect(url_for("doctor_appointments"))


@app.route("/patient/<int:appointment_id>/pay", methods=["GET", "POST"])
@login_required
def payment(appointment_id):
    if current_user.user_role != UserRole.PATIENT:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == "POST":
        payment_method = request.form.get("payment_method")  # MOMO / VNPAY
        total_price = appointment.fee
        dao.add_payment(appointment_id, payment_method=payment_method, total_price=total_price)
        flash("Khởi tạo thanh toán thành công!", "success")
        return redirect(url_for("patient_dashboard"))
    return render_template("patient/pay.html", appointment=appointment)


@app.route("/patient/payments", methods=["GET"])
@login_required
def patient_payments():
    if current_user.user_role != UserRole.PATIENT:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    payments = (Payment.query.join(Appointment).filter(Appointment.patient_id == current_user.id).all())
    return render_template("patient/payments.html", payments=payments)


@app.route("/rating_lists", methods=["GET"])
@login_required
def rating_list():
    if current_user.user_role != UserRole.PATIENT:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    completed = dao.get_completed_appointments_by_patient(current_user.id)
    return render_template("patient/rating_lists.html", completed=completed)


@app.route("/patient/<int:appointment_id>/rating", methods=["GET", "POST"])
@login_required
def rating_appointment(appointment_id):
    if current_user.user_role != UserRole.PATIENT:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    appointment = dao.get_appointment_by_id(appointment_id)

    # Cho phép đánh giá nếu appointment thuộc về mình và đã COMPLETED
    if not appointment or appointment.patient_id != current_user.id or appointment.status != AppointmentStatus.COMPLETED:
        flash("Không thể đánh giá lịch hẹn này")
        return redirect(url_for("patient_dashboard"))

    if request.method == "POST":
        stars = int(request.form.get("stars"))
        comment = request.form.get("comment")
        dao.add_rating(appointment_id, stars=stars, comment=comment, patient_id=current_user.id,
                       doctor_id=appointment.doctor_id)
        flash("Đánh giá thành công!", "success")
        return redirect(url_for("patient_dashboard"))
    return render_template("patient/rating.html", appointment=appointment)


@app.route("/patient/my_ratings", methods=["GET"])
@login_required
def patient_ratings():
    if current_user.user_role != UserRole.PATIENT:
        flash("Không có quyền!", "danger")
        return redirect(url_for("homepage"))
    ratings = dao.get_ratings_by_patient(current_user.id)
    return render_template("patient/my_ratings.html", ratings=ratings)


@app.route("/dashboard/doctor")
@login_required
def doctor_dashboard():
    if current_user.user_role != UserRole.DOCTOR:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    appointments = dao.get_appointments_for_doctor(current_user.id)
    stats = dao.get_doctor_statistics(current_user.id)
    return render_template("doctor/dashboard.html", appointments=appointments, stats=stats)


@app.route("/doctor-profile")
@login_required
def view_doctor_profile():
    if current_user.user_role != UserRole.DOCTOR:
        flash("Chỉ bác sĩ mới được truy cập!", "danger")
        return redirect(url_for("homepage"))
    profile = dao.get_doctor_profile(current_user.id)
    return render_template("doctor/doctor_profile.html", profile=profile, user=current_user)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def update_doctor_profile():
    if current_user.user_role != UserRole.DOCTOR:
        flash("Chỉ bác sĩ mới được truy cập!", "danger")
        return redirect(url_for("homepage"))

    profile = dao.get_doctor_profile(current_user.id)

    if request.method == "POST":
        full_name = request.form.get("full_name")
        address = request.form.get("address")
        email = request.form.get("email")
        date_of_birth = request.form.get("date_of_birth")
        gender = request.form.get("gender")
        phone = request.form.get("phone")
        avatar = request.files.get("avatar")
        academic_degree = request.form.get("academic_degree")
        specialty_id = request.form.get("specialty_id")
        hospital_id = request.form.get("hospital_id")
        license_file = request.files.get("license_file")
        dao.update_doctor_info(current_user.id, full_name, date_of_birth, gender, avatar, address, phone, email,
                               academic_degree, specialty_id, hospital_id, license_file)
        flash("Cập nhật thông tin cá nhân thành công!", "success")
        return redirect(url_for("view_doctor_profile"))
    return render_template("doctor/edit_profile.html", profile=profile, user=current_user)


@app.route("/doctor/view_profile/<int:patient_id>", methods=["GET"])
@login_required
def view_patient_profile(patient_id):
    if current_user.user_role != UserRole.DOCTOR:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    profile = dao.get_patient_profile(patient_id)
    records = dao.get_medical_records_for_patient(patient_id)
    return render_template("doctor/view_profile.html", profile=profile, records=records)


@app.route("/schedule", methods=["GET"])
@login_required
def doctor_schedules():
    if current_user.user_role != UserRole.DOCTOR:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    doctor_profile = dao.get_doctor_profile(current_user.id)

    if not doctor_profile:
        flash("Bạn chưa có hồ sơ bác sĩ!", "danger")
        return redirect(url_for("homepage"))
    schedules = dao.get_schedules_by_doctor(doctor_profile.id)
    return render_template("doctor/schedule.html", schedules=schedules, doctor_profile=doctor_profile)


@app.route("/add_schedule", methods=["GET", "POST"])
@login_required
def doctor_add_schedules():
    if current_user.user_role != UserRole.DOCTOR:
        flash("Không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    doctor_profile = dao.get_doctor_profile(current_user.id)

    if not doctor_profile:
        flash("Bạn chưa có hồ sơ bác sĩ!", "danger")
        return redirect(url_for("homepage"))

    if request.method == "POST":
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        if not date or not start_time or not end_time:
            flash("Vui lòng nhập đầy đủ thông tin!", "danger")
        else:
            dao.add_schedule(doctor_profile.id, date, start_time, end_time)
            flash("Thêm lịch thành công!", "success")
            return redirect(url_for("doctor_schedules"))
    return render_template("doctor/add_schedule.html", doctor_profile=doctor_profile)


@app.route("/update_schedule/<int:id>", methods=["GET", "POST"])
@login_required
def doctor_update_schedules(id):
    if current_user.user_role != UserRole.DOCTOR:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    doctor_profile = dao.get_doctor_profile(current_user.id)

    if not doctor_profile:
        flash("Bạn chưa có hồ sơ bác sĩ!", "danger")
        return redirect(url_for("homepage"))

    schedule = dao.get_schedule_by_id(id)

    if not schedule or schedule.doctor_id != doctor_profile.id:
        flash("Không tìm thấy lịch của bạn!", "danger")
        return redirect(url_for("doctor_schedules"))

    if request.method == "POST":
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        dao.update_schedule(schedule_id=id, date=date, start_time=start_time, end_time=end_time)
        flash("Cập nhật lịch làm việc thành công!", "success")
        return redirect(url_for("doctor_schedules"))
    return render_template("doctor/update_schedule.html", schedule=schedule, doctor_profile=doctor_profile)


from datetime import datetime


@app.route("/doctor/reschedule/<int:appointment_id>", methods=["GET", "POST"])
@login_required
def reschedule_appointment(appointment_id):
    if current_user.user_role != UserRole.DOCTOR:
        flash("Không có quyền!", "danger")
        return redirect(url_for("homepage"))

    doctor_profile = dao.get_doctor_profile(current_user.id)

    if not doctor_profile:
        flash("Bạn chưa có hồ sơ bác sĩ!", "danger")
        return redirect(url_for("homepage"))

    appointment = Appointment.query.get(appointment_id)

    if not appointment or appointment.doctor_id != doctor_profile.id:
        flash("Bạn không có quyền chỉnh sửa lịch hẹn này!", "danger")
        return redirect(url_for("doctor_schedules"))

    if request.method == "POST":
        new_schedule_id = request.form.get("new_schedule_id")
        new_start_at = request.form.get("new_start_at")
        new_end_at = request.form.get("new_end_at")

        # Bắt buộc nhập thời gian
        if not new_start_at or not new_end_at:
            flash("Bạn phải chọn thời gian bắt đầu và kết thúc hợp lệ!", "danger")
            return redirect(request.url)

        new_start_at = datetime.fromisoformat(new_start_at)
        new_end_at = datetime.fromisoformat(new_end_at)

        if new_schedule_id:
            new_schedule_id = int(new_schedule_id)

        res = dao.reschedule(appointment_id, new_start_at, new_end_at, new_schedule_id)

        if not res:
            flash("Lịch hẹn mới trùng với lịch khác, vui lòng chọn khung giờ khác!", "danger")
            return redirect(request.url)
        flash("Thay đổi lịch hẹn thành công!", "success")
        return redirect(url_for("doctor_schedules"))
    return render_template("doctor/reschedule.html", appointment=appointment, doctor_profile=doctor_profile)


@app.route("/doctor/delete_schedule/<int:id>", methods=["POST"])
@login_required
def doctor_delete_schedules(id):
    if current_user.user_role != UserRole.DOCTOR:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))

    doctor_profile = dao.get_doctor_profile(current_user.id)

    if not doctor_profile:
        flash("Bạn chưa có hồ sơ bác sĩ!", "danger")
        return redirect(url_for("homepage"))

    schedule = dao.get_schedule_by_id(id)

    if not schedule or schedule.doctor_id != doctor_profile.id:
        flash("Bạn không có quyền xóa lịch này!", "danger")
        return redirect(url_for("doctor_schedules"))

    if dao.delete_schedule(id):
        flash("Xóa lịch làm việc thành công!", "success")
    else:
        flash("Không thể xóa lịch đã có cuộc hẹn!", "danger")
    return redirect(url_for("doctor_schedules"))


@app.route("/doctor/appointments", methods=["GET"])
@login_required
def doctor_appointments():
    if current_user.user_role != UserRole.DOCTOR:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    d = dao.get_doctor_profile(current_user.id)
    appointments = dao.get_appointments_for_doctor(d.id)
    return render_template('doctor/apmt.html', appointments=appointments)


@app.route("/doctor/confirm_appointments/<int:id>", methods=["POST"])
@login_required
def confirm_appointment(id):
    if current_user.user_role != UserRole.DOCTOR:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    dao.update_appointment_status(id, AppointmentStatus.CONFIRMED)
    flash("Đã xác nhận lịch hẹn!", "success")
    return redirect(url_for('doctor_appointments'))


@app.route("/doctor/complete_appointments/<int:id>", methods=["POST"])
@login_required
def complete_appointment(id):
    if current_user.user_role != UserRole.DOCTOR:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    dao.complete_appointment(id)
    return redirect(url_for('doctor_appointments'))


@app.route("/update_record/<int:appointment_id>", methods=["GET", "POST"])
@login_required
def doctor_update_record(appointment_id):
    if current_user.user_role != UserRole.DOCTOR:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect(url_for("homepage"))
    record = dao.get_medical_record(appointment_id)

    if request.method == "POST":
        diagnosis = request.form.get("diagnosis")
        test_results = request.form.get("test_results")
        symptoms = request.form.get("symptoms")
        medical_history = request.form.get("medical_history")
        file = request.files.get("file")
        dao.update_medical_record(appointment_id=appointment_id, diagnosis=diagnosis, test_results=test_results,
                                  symptoms=symptoms,
                                  medical_history=medical_history, file=file)
        flash("Cập nhật bệnh án thành công!", "success")
        return redirect(url_for("doctor_appointments"))
    return render_template("doctor/update_record.html", record=record)


@app.route("/view_ratings", methods=["GET"])
@login_required
def doctor_view_ratings():
    if current_user.user_role != UserRole.DOCTOR:
        flash("Không có quyền!", "danger")
        return redirect(url_for("homepage"))

    doctor = dao.get_doctor_profile(current_user.id)

    if not doctor:
        flash("Bạn chưa có hồ sơ bác sĩ!", "danger")
        return redirect(url_for("homepage"))
    rating = dao.get_ratings_for_doctor(doctor.id)
    return render_template("doctor/view_ratings.html", rating=rating)


@app.route("/doctor/reply_rating/<int:rating_id>", methods=["POST"])
@login_required
def doctor_reply(rating_id):
    if current_user.user_role != UserRole.DOCTOR:
        flash("Không có quyền!", "danger")
        return redirect(url_for("homepage"))
    reply = request.form.get("doctor_reply")
    dao.doctor_reply_rating(rating_id, reply)
    flash("Đã phản hồi đánh giá!", "success")
    return redirect(url_for("doctor_dashboard"))


@app.route("/stats/doctor")
@login_required
def doctor_statistics():
    if current_user.user_role != UserRole.DOCTOR:
        flash("Không có quyền!", "danger")
        return redirect(url_for("homepage"))
    doctor_profile = dao.get_doctor_profile(current_user.id)  # lấy doctor_profile trước
    stats = dao.get_doctor_statistics(doctor_profile.id)
    return render_template("doctor/stats.html", stats=stats)


@app.route("/stats/admin")
@login_required
def admin_statistics():
    if current_user.user_role != UserRole.ADMIN:
        flash("Không có quyền!", "danger")
        return redirect(url_for("homepage"))
    stats = dao.get_admin_statistics()
    return render_template("admin/stats.html", stats=stats)


@app.route('/notis', methods=["GET"])
@login_required
def notifications():
    notifs = dao.get_notifications(current_user.id)
    return render_template('admin/notifications.html', notifs=notifs)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@scheduler.scheduled_job('interval', minutes=2)
def reminder_job():
    with app.app_context():  # cần app context để query DB
        send_appointment_reminders()


scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
