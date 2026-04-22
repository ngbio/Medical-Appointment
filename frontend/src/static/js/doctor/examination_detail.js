document.addEventListener("DOMContentLoaded", function () {
    const appointmentId = getAppointmentId();

    if (!appointmentId) {
        alert("Missing appointment_id");
        window.location.href = "/doctor/dashboard/";
        return;
    }

    loadAppointment(appointmentId);

    document.getElementById("completeBtn")
        .addEventListener("click", () => {
            completeAppointment(appointmentId);
            const disableBtn = document.getElementById("completeBtn");
            disableBtn.disabled = true;
            disableBtn.classList.add("d-none");
        });
    document.getElementById("backBtn")
        .addEventListener("click", () => {
            window.location.href = "/doctor/dashboard/";
        });
    
        loadCurrentUser();
});

// Get appointment_id from URL
function getAppointmentId() {
    const path = window.location.pathname; 
    const parts = path.split("/");

    return parts[parts.length - 1];
}

// Load appointment details
async function loadAppointment(id) {

    try {
        const res = await authFetch(`/appointments/${id}/`)
        const data = await res.json();

        // Render UI
        document.getElementById("patientName").innerText = data.patient_name;
        document.getElementById("doctorName").innerText = data.doctor_name;
        document.getElementById("appointmentDate").innerText = data.appointment_date;
        document.getElementById("startTime").innerText = data.start_time;
        document.getElementById("symptoms").innerText = data.symptoms || "Không có";
        document.getElementById("status").innerText = data.status;
        const statusClass = data.status === "completed" ? "text-success" : "text-primary";
        document.getElementById("status").className = `fw-bold ${statusClass}`;

    } catch (err) {
        console.error(err);
    }
}

// Complete appointment
async function completeAppointment(id) {

    if (!confirm("Xác nhận hoàn thành khám?")) return;

    try {
        const res = await authFetch(`/appointments/${id}/complete/`, {
            method: "PATCH"
        });

        alert("Đã hoàn thành!");

        // reload
        loadAppointment(id);

    } catch (err) {
        console.error(err);
    }
}