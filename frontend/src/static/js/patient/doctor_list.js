const DOCTOR_API_BASE = '/doctors/'; 
const SPECIALTY_API_BASE = '/specialties/'; 

let nextPageUrl = DOCTOR_API_BASE; 

document.addEventListener("DOMContentLoaded", () => {
    loadSpecialties();
    loadDoctors(nextPageUrl);
//xem thêm
    const btnLoadMore = document.getElementById('btnLoadMore');
    btnLoadMore.addEventListener('click', () => {
        if (nextPageUrl) {
            loadDoctors(nextPageUrl);
        }
    });

  // Tìm kiếm
    const btnSearch = document.getElementById('btnSearch');
    btnSearch.addEventListener('click', () => {
        const specialtyId = document.getElementById('specialtySelect').value;
        const date = document.getElementById('dateInput').value;

        document.getElementById('doctorListContainer').innerHTML = '';

        // Tạo query
        const params = new URLSearchParams();
        if (specialtyId) params.append('speciality_id', specialtyId);
        if (date) params.append('date', date);

        // Reset lại trang đầu tiên của kết quả tìm kiếm mới
        nextPageUrl = `${DOCTOR_API_BASE}?${params.toString()}`;
        
        loadDoctors(nextPageUrl);
    });
});

async function loadSpecialties() {
    try {
        const response = await fetch(SPECIALTY_API_BASE);

        if (!response.ok) throw new Error("Lỗi tải danh sách chuyên khoa");

        const data = await response.json();
        const select = document.getElementById('specialtySelect');
        
        const specialties = data.results || [];

        specialties.forEach(spec => {
            const option = document.createElement('option');
            option.value = spec.id;
            option.textContent = spec.name; 
            select.appendChild(option);
        });

    } catch (error) {
        console.error("Lỗi lấy danh sách khoa:", error);
    }
}

async function loadDoctors(url) {
    const spinner = document.getElementById('loadingSpinner');
    const loadMoreContainer = document.getElementById('loadMoreContainer');

    // Hiện spinner, ẩn nút xem thêm khi đang load
    spinner.classList.remove('d-none');
    loadMoreContainer.classList.add('d-none');

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Lỗi tải dữ liệu bác sĩ");

        const data = await response.json();
        
        nextPageUrl = data.next
            ? new URL(data.next).pathname + new URL(data.next).search
            : null;

        // Render dữ liệu
        const doctors = data.results || [];
        if (doctors.length > 0) {
            renderDoctorCards(doctors);
        } else if (document.getElementById('doctorListContainer').innerHTML === '') {
            document.getElementById('doctorListContainer').innerHTML = `
                <div class="col-12 text-center text-muted mt-4">
                    Không tìm thấy bác sĩ nào phù hợp.
                </div>
            `;
        }

        if (nextPageUrl) {
            loadMoreContainer.classList.remove('d-none');
        } else {
            loadMoreContainer.classList.add('d-none');
        }

    } catch (error) {
        console.error("Lỗi:", error);
        alert("Không thể tải danh sách bác sĩ.");
    } finally {
        spinner.classList.add('d-none');
    }
}

// vẽ Card
function renderDoctorCards(doctors) {
    const container = document.getElementById('doctorListContainer');
    
    doctors.forEach(doc => {
        const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(doc.fullname || 'D')}&background=0D8ABC&color=fff`;
        
        const cardHtml = `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100 shadow-sm border-0 rounded-4">
                    <div class="card-body text-center p-4">
                        <img src="${avatarUrl}" class="rounded-circle mb-3" width="80" height="80">
                        <h5 class="card-title fw-bold">${doc.fullname || 'Bác sĩ'}</h5>
                        <p class="text-primary small mb-2">Kinh nghiệm: ${doc.experience_years} năm</p>
                        <p class="card-text text-muted small">${doc.bio || ''}</p>
                    </div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', cardHtml);
    });
}