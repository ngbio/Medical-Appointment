const state = {
  specialtyId: null,
  doctorId: null,
  doctorName: '',
  date: null,
  dateLabel: '',
  scheduleId: null,
  slotId: null,
  slotTime: '',
};

function showAlert(msg) {
  const el = document.getElementById('alert-appointment');
  el.textContent = msg;
  el.classList.remove('d-none');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  setTimeout(() => el.classList.add('d-none'), 6000);
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('vi-VN', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric' });
}

/*Data Loading*/
async function loadSpecialties() {
  const res = await authFetch('/specialties/');
  const data = await res.json();

  const sel = document.getElementById("specialty-select");
  sel.innerHTML = '<option selected disabled value="">— Chọn chuyên khoa —</option>';

  (data.results || data).forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.name;
    sel.appendChild(opt);
  });
}


async function loadDoctors(specialtyId = '') {
  let url = '/doctors/';
  if (specialtyId) url += `?speciality_id=${specialtyId}`;

  try {
    const res = await authFetch(url);
    const data = await res.json();

    const sel = document.getElementById('doctor-select');

    sel.innerHTML = '<option selected disabled value="">— Chọn bác sĩ —</option>';

    (data.results || data).forEach(d => {
      const opt = document.createElement("option");
      opt.value = d.id;
      opt.textContent = d.fullname;
      sel.appendChild(opt);
    });

  } catch {
    showAlert('Không tải được danh sách bác sĩ');
  }
}

async function onSpecialtyChange(sel) {
  state.specialtyId = sel.value;

  await loadDoctors(state.specialtyId);

  resetAfterDoctor();
}

async function onDoctorChange(sel) {
  const opt = sel.options[sel.selectedIndex];
  state.doctorId = sel.value;
  state.doctorName = opt.textContent;
  // UI
  state.date = null;
  state.scheduleId = null;
  state.slotId = null;

  document.getElementById('timeslot-empty').classList.remove('d-none');
  document.getElementById('timeslot-content').classList.add('d-none');
  document.getElementById('btn-confirm').disabled = true;

  await loadDates(state.doctorId);
}

async function loadDates(doctorId) {
  const sel = document.getElementById('select-date');
  sel.disabled = true;

  while (sel.options.length > 1) sel.remove(1);
  const placeholder = sel.options[0];
  placeholder.text = '— Đang tải... —';

  try {
    const res = await authFetch(`/schedules/by-doctor/?doctor_id=${doctorId}`);
    const data = await res.json();
    const schedules = data.results || data;

    placeholder.text = schedules.length ? '— Chọn ngày —' : '— Không có lịch khả dụng —';

    schedules.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.work_date;
      opt.dataset.scheduleId = s.id;
      opt.textContent = formatDate(s.work_date);
      sel.appendChild(opt);
    });

    sel.disabled = schedules.length === 0;
  } catch {
    placeholder.text = 'Lỗi tải lịch';
  }
}

async function onDateChange(sel) {
  const opt = sel.options[sel.selectedIndex];
  state.date = sel.value;
  state.dateLabel = opt.textContent;
  state.scheduleId = opt.dataset.scheduleId;

  state.slotId = null;
  state.slotTime = '';
  document.getElementById('btn-confirm').disabled = true;

  await loadTimeSlots();
}


//Time Slots
async function loadTimeSlots() {
  if (!state.scheduleId) return;

  const empty = document.getElementById('timeslot-empty');
  const loading = document.getElementById('timeslot-loading');
  const content = document.getElementById('timeslot-content');

  empty.classList.add('d-none');
  content.classList.add('d-none');
  loading.classList.remove('d-none');

  try {
    const res = await authFetch(`/schedules/available-slots/?schedule_id=${state.scheduleId}`);
    const data = await res.json();

    renderSlots(data.results || data);

  } catch {
    showAlert("Không tải được lịch khám");
  } finally {
    loading.classList.add('d-none');
  }
}

function renderSlots(slots) {
  const loading = document.getElementById('timeslot-loading');
  const content = document.getElementById('timeslot-content');
  const morningGrid = document.getElementById('slots-morning');
  const afternoonGrid = document.getElementById('slots-afternoon');
  const noSlots = document.getElementById('no-slots');

  morningGrid.innerHTML = '';
  afternoonGrid.innerHTML = '';

  const morning = slots.filter(s => parseInt(s.start_time?.split(':')[0] || 0) < 12);
  const afternoon = slots.filter(s => parseInt(s.start_time?.split(':')[0] || 0) >= 12);

  loading.classList.add('d-none');
  content.classList.remove('d-none');

  if (slots.length === 0) {
    noSlots.classList.remove('d-none');
    morningGrid.parentElement.classList.add('d-none');
    afternoonGrid.parentElement.classList.add('d-none');
    return;
  }

  noSlots.classList.add('d-none');
  morningGrid.parentElement.classList.remove('d-none');
  afternoonGrid.parentElement.classList.remove('d-none');

  const renderBtn = (slot, container) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = slot.start_time?.slice(0, 5);

    if (slot.status === 'booked') {
      btn.className = 'btn btn-secondary slot-btn disabled';
      btn.disabled = true;
    } else {
      btn.className = 'btn btn-outline-primary slot-btn';
      btn.addEventListener('click', () => selectSlot(btn, slot));
    }

    container.appendChild(btn);
  };
  //sang chieu
  morning.forEach(s => renderBtn(s, morningGrid));
  afternoon.forEach(s => renderBtn(s, afternoonGrid));
}

function selectSlot(btn, slot) {
  document.querySelectorAll('.slot-btn').forEach(b => {
    b.classList.remove('active');
  });

  btn.classList.add('active');

  state.slotId = slot.id;
  state.slotTime = slot.start_time?.slice(0, 5) || slot.start_time;

  document.getElementById('btn-confirm').disabled = false;
}


//Submit Form
async function handleAppointment() {
  const btn = document.getElementById('btn-confirm');
  const btnText = document.getElementById('btn-confirm-text');
  const symptoms = document.getElementById('input-symptoms').value.trim();
  const notes = document.getElementById('input-notes').value.trim();

  if (!state.slotId) {
    showAlert('Vui lòng chọn giờ khám ở cột bên phải.');
    return;
  }
  if (!symptoms) {
    showAlert('Vui lòng điền triệu chứng của bạn.');
    return;
  }

  btn.disabled = true;
  btnText.textContent = 'Đang xử lý...';

  const payload = {
    time_slot: state.slotId,
    symptoms: symptoms,
    notes: notes || undefined
  };

  try {
    const res = await authFetch('/appointments/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    if (res.ok || res.status === 201) {
      document.getElementById('modal-desc').innerHTML = `Lịch khám ngày <b>${state.dateLabel}</b> lúc <b>${state.slotTime}</b> với <b>${state.doctorName}</b> đã được xác nhận.`;

      // Gọi Modal Bt
      const successModal = new bootstrap.Modal(document.getElementById('successModal'));
      successModal.show();
    } else {
      const err = await res.json();
      showAlert(err.detail || 'Đặt lịch thất bại. Vui lòng thử lại.');
      btn.disabled = false;
      btnText.textContent = 'Xác nhận đặt lịch';
    }
  } catch (e) {
    showAlert('Lỗi');
    btn.disabled = false;
    btnText.textContent = 'Xác nhận đặt lịch';
  }
}
function resetAfterDoctor() {
  state.date = null;
  state.scheduleId = null;
  state.slotId = null;
  state.slotTime = '';

  document.getElementById('select-date').innerHTML =
    '<option selected disabled value="">— Chọn ngày —</option>';

  document.getElementById('timeslot-empty').classList.remove('d-none');
  document.getElementById('timeslot-content').classList.add('d-none');

  document.getElementById('btn-confirm').disabled = true;
}


//init
document.addEventListener('DOMContentLoaded', async () => {
  await loadSpecialties();
  await loadDoctors();
});