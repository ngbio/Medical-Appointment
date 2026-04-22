document.addEventListener("DOMContentLoaded", function () {
    loadCurrentUser();
    loadDashboard();
});

function formatTime(timeStr) {
    // "08:00:00" -> "08:00"
    if (!timeStr) return "";
    return timeStr.slice(0, 5);
}

function renderError() {
    const table = document.getElementById("appointmentTable");
    table.innerHTML = `
        <tr>
            <td colspan="5" class="text-center text-danger">
                Failed to load data
            </td>
        </tr>
    `;
}

async function loadDashboard() {
    try {
        const res = await authFetch("/appointments/dashboard/");
        const data = await res.json();

        renderStats(data);
        renderTable(data.results);

    } catch (err) {
        console.error(err);
        renderError();
    }
}

function renderStats(data) {
    document.getElementById("totalCount").innerText = data.total || 0;
    document.getElementById("waitingCount").innerText = data.waiting || 0;
    document.getElementById("completedCount").innerText = data.completed || 0;
    document.getElementById("canceledCount").innerText = data.canceled || 0;
}

function renderTable(appointments) {
    const table = document.getElementById("appointmentTable");

    if (!appointments || appointments.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    No appointments today
                </td>
            </tr>
        `;
        return;
    }

    table.innerHTML = "";

    appointments.forEach(a => {
        const statusBadge = renderStatus(a.status);

        table.innerHTML += `
            <tr>
                <td>${formatTime(a.start_time)}</td>
                <td>${a.patient_name}</td>
                <td>${a.doctor_name}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    });
}

function renderStatus(status) {
    if (status === "completed") {
        return `<span class="badge bg-success">Completed</span>`;
    }
    if (status === "booked") {
        return `<span class="badge bg-primary">Waiting</span>`;
    }
    if (status === "canceled") {
        return `<span class="badge bg-danger">Canceled</span>`;
    }
    return `<span class="badge bg-secondary">${status}</span>`;
}

