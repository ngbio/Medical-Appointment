document.addEventListener("DOMContentLoaded", function () {
    loadDashboard();
    loadCurrentUser();
});

// Load Dashboard Data
async function loadDashboard() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "/login/";
        return;
    }

    try {
        const res = await fetch("/doctors/dashboard/", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (res.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "/login/";
            return;
        }

        if (res.status === 403) {
            alert("Bạn không phải Doctor!");
            window.location.href = "/";
            return;
        }

        const data = await res.json();

        // Count
        document.getElementById("todayCount").innerText = data.today_count;
        document.getElementById("upcomingCount").innerText = data.upcoming_count;

        // Table
        const table = document.getElementById("appointmentTable");
        document.getElementById("currentDate").innerText = new Date().toLocaleDateString();

        table.innerHTML = "";

        data.appointments.forEach(a => {
            table.innerHTML += `
                <tr>
                    <td>${a.time}</td>
                    <td>${a.patient}</td>
                    <td>${a.status}</td>
                    <td>
                        <button class="btn btn-primary btn-sm"
                            onclick="goToExamination(${a.id})">
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

// Load User Info
async function loadCurrentUser() {
    const token = localStorage.getItem("access_token");

    if (!token) return;

    const user = JSON.parse(token);
    document.getElementById("doctorName").innerText =
            `Welcome, Dr. ${user.username}`;
}


function goToExamination(appointmentId) {
    window.location.href = `/doctor/examination/?appointment_id=${appointmentId}`;
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login/";
}