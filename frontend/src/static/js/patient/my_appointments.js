let currentCancelId = null;
let cancelModalInstance = null;
let currentStatus = 'scheduled';

// Biến phân trang
let nextPageUrl = null;
let prevPageUrl = null;


document.addEventListener('DOMContentLoaded', () => {
    cancelModalInstance = new bootstrap.Modal(document.getElementById('cancelModal'));

    // Tải dl
    loadAppointments();

    // đổi Tab
    document.querySelectorAll('#appointment-filters .nav-link').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelector('#appointment-filters .active').classList.remove('active');
            this.classList.add('active');
            currentStatus = this.dataset.status;
            
            loadAppointments();
        });
    });

    // phân trang
    document.getElementById('prev-btn').addEventListener('click', () => {
        if (prevPageUrl) loadAppointments(prevPageUrl);
    });
    
    document.getElementById('next-btn').addEventListener('click', () => {
        if (nextPageUrl) loadAppointments(nextPageUrl);
    });

    // hủy lịch
    document.getElementById('confirm-cancel-btn').addEventListener('click', handleCancelAppointment);
});

// Hàm gọi API 
async function loadAppointments(fetchUrl = null) {
    const listEl = document.getElementById('appointment-list');

    let url = fetchUrl || `/appointments/?status=${currentStatus}`;

    if (fetchUrl) {
        const parsed = new URL(fetchUrl);
        url = parsed.pathname + parsed.search;
    }

    try {
        const res = await authFetch(url);
        if (!res.ok) throw new Error("Lỗi mạng");
        const data = await res.json();
        
        nextPageUrl = data.next;
        prevPageUrl = data.previous;
        
        renderAppointments(data.results);
        updatePaginationUI();

    } catch (error) {
        listEl.innerHTML = `<div class="col-12 alert alert-danger text-center">Không thể kết nối. Vui lòng thử lại.</div>`;
        document.getElementById('pagination-controls').classList.add('d-none');
    }
}

function renderAppointments(appointments) {
    const listEl = document.getElementById('appointment-list');
    
    if (!appointments || appointments.length === 0) {
        listEl.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="text-muted bg-light rounded p-5">
                    <i class="bi bi-calendar-x fs-1"></i>
                    <p class="mt-3 mb-0">Chưa có lịch hẹn nào ở trạng thái này.</p>
                </div>
            </div>
        `;
        return;
    }

    const statusConfig = {
        'scheduled': { color: 'bg-warning text-dark', text: 'Sắp tới' },
        'completed': { color: 'bg-success', text: 'Đã khám' },
        'canceled':  { color: 'bg-danger', text: 'Đã hủy' }
    };

    listEl.innerHTML = appointments.map(app => {
        const config = statusConfig[app.status] || { color: 'bg-secondary', text: app.status };
        
        const actionBtn = app.status === 'scheduled' 
            ? `<hr><div class="text-end mt-3"><button class="btn btn-outline-danger btn-sm fw-semibold" onclick="openCancelModal(${app.id})">Hủy lịch</button></div>` 
            : '';

        return `
            <div class="col-md-6 col-lg-4">
                <div class="card shadow-sm h-100 border-0">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title fw-bold mb-0 text-primary">${app.doctor_name || 'Đang cập nhật'}</h5>
                            <span class="badge ${config.color}">${config.text}</span>
                        </div>
                        <p class="card-text text-muted mb-1">
                            <strong><i class="bi bi-calendar-event me-1"></i> Ngày:</strong> ${app.appointment_date || '—'}
                        </p>
                        <p class="card-text text-muted mb-0">
                            <strong><i class="bi bi-clock me-1"></i> Giờ:</strong> ${app.start_time ? app.start_time.slice(0, 5) : '—'}
                        </p>
                        ${actionBtn}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function updatePaginationUI() {
    const paginationDiv = document.getElementById('pagination-controls');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    if (!nextPageUrl && !prevPageUrl) {
        paginationDiv.classList.add('d-none');
        paginationDiv.classList.remove('d-flex');
        return;
    }
    
    paginationDiv.classList.remove('d-none');
    paginationDiv.classList.add('d-flex');

    prevBtn.disabled = !prevPageUrl;
    nextBtn.disabled = !nextPageUrl;
}

//Modal Hủy appointment
function openCancelModal(id) {
    currentCancelId = id;
    cancelModalInstance.show();
}

async function handleCancelAppointment() {
    if (!currentCancelId) return;
    
    const btn = document.getElementById('confirm-cancel-btn');
    btn.disabled = true;

    try {
        const res = await authFetch(`/appointments/${currentCancelId}/cancel/`, {
            method: 'PATCH',
        });

        if (res.ok) {
            cancelModalInstance.hide();
            loadAppointments();
            alert("Hủy Thành Công")
        } else {
            const data = await res.json();
            alert(data.detail || "Không thể hủy lịch");
        }
    } catch (e) {
        alert("Lỗi ");
    } finally {
        btn.disabled = false;
        btn.innerText = "Xác nhận hủy";
    }
}