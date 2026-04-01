document.addEventListener("DOMContentLoaded", function() {
    const registerBtn = document.getElementById('registerBtn');
    const registerForm = document.getElementById('registerForm');
    const alertMessage = document.getElementById('alertMessage');

    registerBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        // Lấy dữ liệu từ form
        const formData = new FormData(registerForm);
        const data = {
            username: formData.get('username'),
            fullname: formData.get('fullname'),
            email: formData.get('email'),
            phone_number: formData.get('phone_number'),
            gender: formData.get('gender'),
            password: formData.get('password')
        };

        // Kiểm tra password
        if (data.password !== formData.get('confirm_password')) {
            alertMessage.innerHTML = '<div class="alert alert-danger">Mật khẩu xác nhận không khớp!</div>';
            return;
        }

        if (data.password.length < 6) {
            alertMessage.innerHTML = '<div class="alert alert-danger">Mật khẩu phải có ít nhất 6 ký tự!</div>';
            return;
        }

        try {
            const response = await fetch('/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (response.status === 201) {
                alertMessage.innerHTML = '<div class="alert alert-success">Đăng ký thành công! Vui lòng <a href="/login">đăng nhập</a>.</div>';
                registerForm.reset();
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else if (response.status === 400) {
                const errors = await response.json();
                let errorMsg = 'Lỗi đăng ký:<ul>';
                for (const [field, messages] of Object.entries(errors)) {
                    if (Array.isArray(messages)) {
                        messages.forEach(msg => {
                            errorMsg += `<li><strong>${field}</strong>: ${msg}</li>`;
                        });
                    } else {
                        errorMsg += `<li><strong>${field}</strong>: ${messages}</li>`;
                    }
                }
                errorMsg += '</ul>';
                alertMessage.innerHTML = `<div class="alert alert-danger">${errorMsg}</div>`;
            } else {
                alertMessage.innerHTML = `<div class="alert alert-danger">Lỗi: ${response.statusText}</div>`;
            }
        } catch (error) {
            console.error('Error:', error);
            alertMessage.innerHTML = `<div class="alert alert-danger">Lỗi: ${error.message}</div>`;
        }
    });

    // Optional: Kiểm tra password real-time
    const confirmPassword = document.getElementById('confirm_password');
    const password = document.getElementById('password');
    
    confirmPassword.addEventListener('input', () => {
        if (password.value && confirmPassword.value && password.value !== confirmPassword.value) {
            confirmPassword.classList.add('is-invalid');
            confirmPassword.classList.remove('is-valid');
        } else if (password.value && confirmPassword.value && password.value === confirmPassword.value) {
            confirmPassword.classList.add('is-valid');
            confirmPassword.classList.remove('is-invalid');
        }
    });
});
