document.addEventListener("DOMContentLoaded", async () => {
    try {
        // Lấy token từ localStorage
        const token = localStorage.getItem("access_token");
        
        if (!token) {
            document.getElementById('userInfoContainer').innerHTML = 
                '<div class="alert alert-danger text-center mt-4">Vui lòng đăng nhập để xem thông tin!</div>';
            document.getElementById('patientsContainer').style.display = 'none';
            return;
        }

        // Fetch thông tin user hiện tại với Authorization header
        const userResponse = await fetch('/users/current-user/', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (userResponse.status === 404) {
            document.getElementById('userInfoContainer').innerHTML = 
                '<div class="alert alert-danger text-center mt-4">Tài khoản không hợp lệ!</div>';
            document.getElementById('patientsContainer').style.display = 'none';
            return;
        }

        if (userResponse.status === 401) {
            document.getElementById('userInfoContainer').innerHTML = 
                '<div class="alert alert-danger text-center mt-4">Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại!</div>';
            document.getElementById('patientsContainer').style.display = 'none';
            localStorage.removeItem('access_token');
            return;
        }

        if (!userResponse.ok) {
            throw new Error(`HTTP error! status: ${userResponse.status}`);
        }

        const userData = await userResponse.json();
        
        // Cập nhật thông tin user
        document.getElementById('userAvatar').src = userData.avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(userData.fullname || userData.username || 'User');
        document.getElementById('userFullname').textContent = userData.fullname || userData.first_name || 'N/A';
        document.getElementById('userUsername').textContent = userData.username || 'N/A';
        document.getElementById('userEmail').textContent = userData.email || 'N/A';
        document.getElementById('userPhone').textContent = userData.phone_number || 'N/A';
        
        // Chuyển đổi giới tính
        const genderMap = {
            'male': 'Nam',
            'female': 'Nữ',
            'm': 'Nam',
            'f': 'Nữ'
        };
        const genderText = genderMap[userData.gender?.toLowerCase()] || userData.gender || 'N/A';
        document.getElementById('userGender').textContent = genderText;

        // Ẩn phần patients nếu không có dữ liệu
        document.getElementById('patientsContainer').style.display = 'none';

    } catch (error) {
        console.error('Error fetching user data:', error);
        document.getElementById('userInfoContainer').innerHTML = 
            '<div class="alert alert-danger text-center mt-4">Lỗi tải dữ liệu: ' + error.message + '</div>';
    }
});

function deletePatient(patientId) {
    if (confirm('Bạn có chắc muốn xóa hồ sơ bệnh nhân này?')) {
        const token = localStorage.getItem("access_token");
        fetch(`/users/patients/${patientId}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => {
            if (response.ok) {
                const patientDiv = document.getElementById(`patient${patientId}`);
                if (patientDiv) {
                    patientDiv.remove();
                }
            } else {
                alert('Lỗi xóa bệnh nhân');
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
