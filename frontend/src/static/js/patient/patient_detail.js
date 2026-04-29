document.addEventListener("DOMContentLoaded", function () {
    loadCurrentUser();
    const patientId = getPatientId();

    if (!patientId) {
        alert("Missing patient_id");
        window.location.href = "/doctor/patient-list";
        return;
    }

    loadPatient(patientId);

    
    document.getElementById("backPatientBtn")
        .addEventListener("click", () => {
            window.location.href = "/doctor/patient-list";
        });
});

// lấy patient_id 
function getPatientId() {
    const path = window.location.pathname; 
    const parts = path.split("/");

    return parts[parts.length - 1];
}

async function loadPatient(id) {
    try {
        const res = await authFetch(`/patients/${id}/`);
        const data = await res.json();

        document.getElementById("patientName").innerText = data.user.fullname;
        document.getElementById("patientPhone").innerText = data.user.phone_number || "-";
        document.getElementById("patientDOB").innerText = data.dob || "-";
        document.getElementById("patientAddress").innerText = data.address || "-";

    } catch (err) {
        console.error(err);
    }
}

async function loadAppointmentsRecords() {
    const id = getPatientId();

    try {
        const res = await authFetch(`/patients/${id}/appointments/`);
        const data = await res.json();

        const table = document.getElementById("appointmentTable");
        const body = document.getElementById("appointmentBody");
        const empty = document.getElementById("noAppointment");

        body.innerHTML = "";

        if (!data.appointments || data.appointments.length === 0) {
            table.style.display = "none";
            empty.style.display = "block";
            return;
        }

        table.style.display = "table";
        empty.style.display = "none";

        data.appointments.forEach(a => {
            const statusClass =
                a.status === "completed" ? "text-success" :
                a.status === "canceled" ? "text-danger" :
                "text-primary";

            body.innerHTML += `
                <tr>
                    <td>${a.appointment_date}</td>
                    <td>${a.start_time}</td>
                    <td>${a.doctor_name}</td>
                    <td class="${statusClass}">${a.status}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewDetailsAppointment(${a.id})">View</button>
                    </td>
                </tr>
            `;
        });

    } catch (err) {
        console.error(err);
    }
}

async function viewDetailsAppointment(id) {
    try {
        const res = await authFetch(`/appointments/${id}/`);
        const data = await res.json();

        document.getElementById("modalPatient").innerText = data.patient_name;
        document.getElementById("modalDoctor").innerText = data.doctor_name;
        document.getElementById("modalDate").innerText = data.appointment_date;
        document.getElementById("modalTime").innerText = data.start_time;
        document.getElementById("modalSymptoms").innerText = data.symptoms || "-";
        document.getElementById("modalStatus").innerText = data.status;

        //show modal
        const modal = new bootstrap.Modal(document.getElementById('appointmentModal'));
        modal.show();

    } catch (err) {
        console.error(err);
    }
}