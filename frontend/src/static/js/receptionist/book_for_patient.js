const state = {
  phone: '',
  fullname: '',
  email: '',

  specialtyId: null,
  doctorId: null,
  doctorName: '',

  date: null,
  scheduleId: null,

  slotId: null,
  slotTime: ''
};

function showAlert(msg) {
  alert(msg); 
}

async function searchPatient() {
  const phone = document.getElementById("inputPhone").value;

  if (!phone) {
    showAlert("Enter phone number");
    return;
  }

  try {
    const res = await authFetch(`/patients/?q=${phone}`);
    const data = await res.json();

    const patients = data.results || data;

    if (patients.length === 0) {
      showAlert("No patient found");
      return;
    }

    const p = patients[0];

    document.getElementById("inputName").value = p.user.fullname;
    document.getElementById("inputEmail").value = p.user.email;

  } catch {
    showAlert("Error searching patient");
  }
}

async function loadSpecialties() {
  const res = await authFetch('/specialties/');
  const data = await res.json();

  const sel = document.getElementById("specialtySelect");

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

  const res = await authFetch(url);
  const data = await res.json();

  const sel = document.getElementById("doctorSelect");
  sel.innerHTML = '<option value="">-- Select Doctor --</option>';

  (data.results || data).forEach(d => {
    const opt = document.createElement("option");
    opt.value = d.id;
    opt.textContent = d.fullname;
    sel.appendChild(opt);
  });
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

  resetAfterDoctor();

  await loadDates(state.doctorId);
}

async function loadDates(doctorId) {
  const sel = document.getElementById("dateSelect");
  sel.disabled = true;
  sel.innerHTML = '<option>Loading...</option>';

  const res = await authFetch(`/schedules/by-doctor/?doctor_id=${doctorId}`);
  const data = await res.json();

  const schedules = data.results || data;

  sel.innerHTML = '<option value="">-- Select Date --</option>';

  schedules.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.work_date;
    opt.dataset.scheduleId = s.id;
    opt.textContent = s.work_date;
    sel.appendChild(opt);
  });

  sel.disabled = false;
}

async function onDateChange(sel) {
  const opt = sel.options[sel.selectedIndex];

  state.date = sel.value;
  state.scheduleId = opt.dataset.scheduleId;

  state.slotId = null;

  await loadSlots();
}

async function loadSlots() {
  const container = document.getElementById("slotContainer");
  container.innerHTML = "Loading...";

  const res = await authFetch(`/schedules/available-slots/?schedule_id=${state.scheduleId}`);
  const data = await res.json();

  const slots = data.results || data;

  if (slots.length === 0) {
    container.innerHTML = "<p>No slots available</p>";
    return;
  }

  container.innerHTML = "";

  slots.forEach(s => {
    const btn = document.createElement("button");
    btn.className = "btn btn-outline-dark m-2";
    btn.textContent = s.start_time.slice(0,5);

    btn.onclick = () => selectSlot(btn, s);

    container.appendChild(btn);
  });
}

function selectSlot(btn, slot) {
  document.querySelectorAll("#slotContainer button")
    .forEach(b => b.classList.remove("active"));

  btn.classList.add("active");

  state.slotId = slot.id;
  state.slotTime = slot.start_time;

  document.getElementById("btnSubmit").disabled = false;
}

async function handleBooking() {
  const phone = document.getElementById("inputPhone").value;
  const fullname = document.getElementById("inputName").value;
  const email = document.getElementById("inputEmail").value;
  const symptoms = document.getElementById("inputSymptoms").value;
  const notes = document.getElementById("inputNotes").value;

  if (!phone || !fullname || !state.slotId || !symptoms) {
    showAlert("Missing required fields");
    return;
  }

  const payload = {
    phone_number: phone,
    fullname: fullname,
    email: email,
    time_slot: state.slotId,
    symptoms: symptoms,
    notes: notes
  };

  try {
    const res = await authFetch('/appointments/book-for-patient/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.ok) {
      alert("Booked successfully!");
      location.reload();
    } else {
      showAlert(data.detail || "Booking failed");
    }

  } catch {
    showAlert("Error booking appointment");
  }
}

function resetAfterDoctor() {
  state.date = null;
  state.scheduleId = null;
  state.slotId = null;

  document.getElementById("dateSelect").innerHTML =
    '<option value="">-- Select Date --</option>';

  document.getElementById("slotContainer").innerHTML =
    "<p>Please select doctor and date</p>";

  document.getElementById("btnSubmit").disabled = true;
}

document.addEventListener("DOMContentLoaded", async () => {
  loadCurrentUser();
  await loadSpecialties();
  await loadDoctors();
});