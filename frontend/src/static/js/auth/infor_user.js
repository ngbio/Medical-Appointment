const PROFILE_API_URL = '/patients/me/'; 
let editModalInstance = null;

let originalProfile = {};

document.addEventListener("DOMContentLoaded", () => {
    // Khởi tạo modal
    const modalEl = document.getElementById('editProfileModal');
    if (modalEl) {
        editModalInstance = new bootstrap.Modal(modalEl);
    }
    
    // Tải dữ liệu
    loadPatientProfile();

    // Sự kiện submit form
    const editForm = document.getElementById('editProfileForm');
    if (editForm) {
        editForm.addEventListener('submit', handleUpdateProfile);
    }
});

async function loadPatientProfile() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("Vui lòng đăng nhập!");
        window.location.href = "/login"; 
        return;
    }

    try {
        const res = await authFetch(PROFILE_API_URL);
        

        if (!res.ok) throw new Error("Không thể tải thông tin");

        const data = await res.json();
        const user = data.user || {}; 

        originalProfile = {
            fullname: user.fullname || '',
            phone_number: user.phone_number || '',
            gender: user.gender || '',
            dob: data.dob || '',
            address: data.address || ''
        };

        const avatarEl = document.getElementById('userAvatar');
        if (avatarEl) avatarEl.src = user.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.fullname || user.username || 'U')}`;
        
        const nameEl = document.getElementById('displayFullname');
        if (nameEl) nameEl.textContent = user.fullname || 'Chưa cập nhật';
        
        const userEl = document.getElementById('displayUsername');
        if (userEl) userEl.textContent = `@${user.username || 'user'}`;
        
        const emailEl = document.getElementById('displayEmail');
        if (emailEl) emailEl.textContent = user.email || 'Chưa cập nhật';
        
        const phoneEl = document.getElementById('displayPhone');
        if (phoneEl) phoneEl.textContent = user.phone_number || 'Chưa cập nhật';
        
        const genderMap = { 'male': 'Nam', 'female': 'Nữ'};
        const genderEl = document.getElementById('displayGender');
        if (genderEl) genderEl.textContent = genderMap[user.gender?.toLowerCase()] || user.gender || 'Chưa cập nhật';
        
        const dobEl = document.getElementById('displayDob');
        if (dobEl) dobEl.textContent = data.dob || 'Chưa cập nhật';
        
        const addressEl = document.getElementById('displayAddress');
        if (addressEl) addressEl.textContent = data.address || 'Chưa cập nhật';

        // === ĐIỀN SẴN FORM TRONG MODAL ===
        const inputFullname = document.getElementById('inputFullname');
        if (inputFullname) inputFullname.value = user.fullname || '';
        
        const inputPhone = document.getElementById('inputPhone');
        if (inputPhone) inputPhone.value = user.phone_number || '';
        
       const inputGender = document.getElementById('inputGender');
        if (inputGender) {
            inputGender.value = user.gender || '';
        }
        
        const inputDob = document.getElementById('inputDob');
        if (inputDob) inputDob.value = data.dob || '';
        
        const inputAddress = document.getElementById('inputAddress');
        if (inputAddress) inputAddress.value = data.address || '';

    } catch (error) {
        console.error("Lỗi tải dữ liệu:", error);
        alert("Lỗi tải dữ liệu hồ sơ. Vui lòng thử lại!");
    }
}

async function handleUpdateProfile(e) {
    e.preventDefault(); 
    
    const btnSave = document.getElementById('btnSaveProfile');
    const alertBox = document.getElementById('formAlert');
    
    btnSave.disabled = true;
    btnSave.innerText = "Đang lưu...";
    alertBox.classList.add('d-none');

    // gom data 
    const payload = {};
    const userPayload = {};

    const fullname = document.getElementById('inputFullname').value.trim();
    const phone = document.getElementById('inputPhone').value.trim();
    const gender = document.getElementById('inputGender').value.trim();
    const dob = document.getElementById('inputDob').value;
    const address = document.getElementById('inputAddress').value.trim();

    //cap nhat field thay doi
    if (fullname !== originalProfile.fullname) {
        userPayload.fullname = fullname;
    }

    if (phone !== originalProfile.phone_number) {
        userPayload.phone_number = phone;
    }

    if (gender !== originalProfile.gender) {
        userPayload.gender = gender;
    }

    if (Object.keys(userPayload).length > 0) {
        payload.user = userPayload;
    }

    if (dob !== originalProfile.dob) {
        payload.dob = dob;
    }

    if (address !== originalProfile.address) {
        payload.address = address;
    }

    //neu ko có gi thay doi
    if (Object.keys(payload).length === 0) {
        btnSave.disabled = false;
        btnSave.innerText = "Lưu thay đổi";
        if (editModalInstance) editModalInstance.hide();
        return;
    }

    try {
        const res = await authFetch(PROFILE_API_URL, {
            method: 'PATCH',
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(JSON.stringify(errorData));
        }

        //ẩn modal và reload thông tin
        if (editModalInstance) editModalInstance.hide();
        await loadPatientProfile(); 
        
    } catch (error) {
        console.error("Lỗi cập nhật:", error);
        alertBox.classList.remove('d-none');
        alertBox.innerText = "Cập nhật thất bại. Vui lòng kiểm tra lại thông tin!";
    } finally {
        btnSave.disabled = false;
        btnSave.innerText = "Lưu thay đổi";
    }
}