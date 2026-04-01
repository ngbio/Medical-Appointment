document.addEventListener("DOMContentLoaded", function () {

    const loginBtn = document.getElementById("loginBtn");

    loginBtn.addEventListener("click", login);

});

async function login() {

    console.log("Button clicked");

    const form = document.getElementById("loginForm");
    const formDataObj = new FormData(form);

    const username = formDataObj.get("username");
    const password = formDataObj.get("password");

    const alertBox = document.getElementById("alertMessage");

    alertBox.innerHTML = "";

    if (!username || !password) {
        alertBox.innerHTML = `
        <div class="alert alert-danger">
            Vui lòng nhập đầy đủ thông tin!
        </div>`;
        return;
    }

    try {
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);
        formData.append("client_id", "LV6sCYhLWSH0ayMdfgO0c3CMLZn7zFUSDMJmOsOc");
        formData.append("client_secret", "vpCYtTFRsFy47xmlNQ6Gpv1NAo9RgUmTYRfAr2UsaqwvsYCtD5Y5C9yRnYFOfVqZsbxDQKDooNHPXPoYr93YmVKHl1hM0M4wJNNaE0LmVXPt0FW1Yg8GiqUkPpLoGLmq");
        formData.append("grant_type", "password");

        const response = await fetch("/o/token/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("access_token", data.access_token);

            alertBox.innerHTML = `
            <div class="alert alert-success">
                Đăng nhập thành công!
            </div>`;

            setTimeout(() => {
                window.location.href = "/index/";
            }, 800);

        } else {
            alertBox.innerHTML = `
            <div class="alert alert-danger">
                Sai tài khoản hoặc mật khẩu!
            </div>`;
        }

    } catch (error) {
        console.error(error);
        alertBox.innerHTML = `
        <div class="alert alert-danger">
            Lỗi kết nối server!
        </div>`;
    }
}