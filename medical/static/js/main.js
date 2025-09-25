function rejectDoctor(doctorId) {
  if (confirm("Bạn chắc chắn muốn từ chối / xoá bác sĩ này?")) {
    const modal = new bootstrap.Modal(document.getElementById(`rejectModal${doctorId}`));
    modal.show();
  }
}

function submitReject(doctorId) {
  const reason = document.getElementById(`reason${doctorId}`).value;

  fetch(`/api/reject_doctors/${doctorId}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason, delete: true })
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
    if (data.status === "success") {
      document.getElementById(`doctors${doctorId}`).remove();
      bootstrap.Modal.getInstance(document.getElementById(`rejectModal${doctorId}`)).hide();
    }
  })
  .catch(err => console.error("Lỗi:", err));
}

function pay() {
  const method = document.getElementById('payment_method').value;

  if (!confirm("Bạn chắc chắn thanh toán không?")) return;

  fetch(`/api/patient/{{ appointment.id }}/pay`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ payment_method: method })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 200) {
      alert("Thanh toán thành công!");
      location.href = "{{ url_for('patient_dashboard') }}";
    } else {
      alert("Lỗi: " + data.message);
    }
  })
  .catch(err => alert("Có lỗi xảy ra: " + err));
}

function retryPayment(appointmentId) {
  if (!confirm("Bạn muốn thanh toán lại?")) return;

  fetch(`/api/patient/${appointmentId}/pay`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ payment_method: 'Giả lập' })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 200) {
      alert("Thanh toán thành công!");
      location.reload();
    } else {
      alert("Lỗi: " + data.message);
    }
  })
  .catch(err => alert("Có lỗi xảy ra: " + err));
}

function markRead(id) {
  fetch(`/notis/${id}/read`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 200) {
      location.reload();
    } else {
      alert("Lỗi: " + data.message);
    }
  })
  .catch(err => alert("Có lỗi xảy ra: " + err));
}