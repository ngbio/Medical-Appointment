document.addEventListener("DOMContentLoaded", function () {
    setDefaultDate();
    loadSchedule(); // auto load hôm nay
});

function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById("scheduleDate").value = today;
}

function renderSchedule(data) {

    const table = document.getElementById("scheduleTable");
    const body = document.getElementById("scheduleBody");
    const noSchedule = document.getElementById("noSchedule");

    body.innerHTML = "";

    if (data.length === 0) {
        table.style.display = "none";
        noSchedule.style.display = "block";
        return;
    }

    noSchedule.style.display = "none";
    table.style.display = "table";

    data.forEach(s => {
        body.innerHTML += `
            <tr>
                <td>${s.work_date}</td>
                <td>${s.start_time}</td>
                <td>${s.end_time}</td>
            </tr>
        `;
    });
}
// Load Schedule
async function loadSchedule() {

    const date = document.getElementById("scheduleDate").value;

    try {
        const res = await authFetch(`/schedules/my-schedules/?date=${date}`)

        const data = await res.json();

        renderSchedule(data);

    } catch (err) {
        console.error("Load schedule error:", err);
    }
}