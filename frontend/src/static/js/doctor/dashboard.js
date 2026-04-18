document.addEventListener("DOMContentLoaded", function () {
    loadDashboard();
    loadCurrentUser();
});

async function loadDashboard() {
    try {
        const res = await authFetch("/doctors/dashboard/");
        const data = await res.json();

        document.getElementById("todayCount").innerText = data.today_count;
        document.getElementById("scheduledCount").innerText = data.scheduled_count;

        const table = document.getElementById("appointmentTable");
        table.innerHTML = "";

        data.results.forEach(a => {
            const statusClass = a.status === "completed" ? "text-success" : "text-primary";

            const buttonDisabled = a.status === "completed" ? "disabled d-none" : "";
            table.innerHTML += `
                <tr>
                    <td>${a.start_time}</td>
                    <td>${a.patient_name}</td>
                    <td class="fw-bold ${statusClass}">${a.status}</td>
                    <td>
                        <button class="btn btn-primary btn-sm"
                            onclick="goToExamination(${a.id})" ${buttonDisabled}>
                            Khám bệnh
                        </button>
                    </td>
                </tr>
            `;
        });

    } catch (err) {
        console.error(err);
    }
}

async function loadCurrentUser() {
    const token = localStorage.getItem("access_token");

    if (!token) return;

    const user = JSON.parse(token);
    document.getElementById("doctorUserName").innerText =
            `Welcome, Dr. ${user.username}`;
}

function goToExamination(appointmentId) {
    window.location.href = `/doctor/examination/${appointmentId}`;
}