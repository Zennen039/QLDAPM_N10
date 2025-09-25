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