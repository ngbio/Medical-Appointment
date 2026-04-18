document.addEventListener("DOMContentLoaded", function () {
    setDefaultDate();
    loadAppointments();
});

function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById("appointmentDate").value = today;
}

// Load Appointments
async function loadAppointments() {
    try {
        const date = document.getElementById("appointmentDate").value;
        const res = await authFetch(`/appointments/?from=${date}&to=${date}`);
        const data = await res.json();

        const table = document.getElementById("appointmentTable");
        table.innerHTML = "";

        if (!data.results || data.results.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        Không có lịch khám
                    </td>
                </tr>
            `;
            return;
        }

        data.results.forEach(a => {

            // Status style
            const statusClass =
                a.status === "completed" ? "text-success fw-bold" :
                a.status === "canceled" ? "text-danger fw-bold" :
                "text-primary fw-bold";

            // Disable button nếu completed
            const buttonDisabled =
                a.status === "completed" || a.status === "canceled" || a.appointment_date > new Date().toISOString().split('T')[0]
                ? "disabled d-none"
                : "";

            table.innerHTML += `
                <tr>
                    <td>${a.start_time}</td>
                    <td>${a.patient_name}</td>
                    <td class="${statusClass}">${a.status}</td>
                    <td>${a.symptoms || "-"}</td>
                    <td>
                        <button class="btn btn-primary btn-sm"
                            onclick="goToExamination(${a.id})"
                            ${buttonDisabled}>
                            Khám bệnh
                        </button>
                    </td>
                </tr>
            `;
        });

    } catch (err) {
        console.error("Load appointments error:", err);
    }
}

function goToExamination(appointmentId) {
    window.location.href = `/doctor/examination/${appointmentId}`;
}