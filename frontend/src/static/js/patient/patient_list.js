document.addEventListener("DOMContentLoaded", function () {
    loadPatients();
    loadCurrentUser();
});

// Load Patients
async function loadPatients() {
    try {
        const query = document.getElementById("searchInput").value;
        const dob = document.getElementById("dobInput").value;

        let url = "/patients/";

        const params = new URLSearchParams();

        if (query) params.append("q", query);
        if (dob) params.append("dob", dob);

        if (params.toString()) {
            url += "?" + params.toString();
        }

        const res = await authFetch(url);
        const data = await res.json();

        const table = document.getElementById("patientTable");
        table.innerHTML = "";

        // Empty state
        if (!data.results || data.results.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        Không tìm thấy bệnh nhân
                    </td>
                </tr>
            `;
            return;
        }

        data.results.forEach(p => {
            table.innerHTML += `
                <tr>
                    <td>${p.user.fullname}</td>
                    <td>${p.user.phone_number || "-"}</td>
                    <td>${p.dob || "-"}</td>
                    <td>${p.address || "-"}</td>
                    <td>
                        <button class="btn btn-info btn-sm me-2"
                            onclick="viewProfile(${p.id})">
                            Details
                        </button>

                    </td>
                </tr>
            `;
        });

    } catch (err) {
        console.error("Load patients error:", err);
    }
}

// Navigation
function viewProfile(patientId) {
    window.location.href = `/doctor/patient/${patientId}`;
}

function viewAppointments(patientId) {
    window.location.href = `/doctor/patient/${patientId}/appointments`;
}