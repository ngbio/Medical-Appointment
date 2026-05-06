document.addEventListener("DOMContentLoaded", function () {

    const loginBtn = document.getElementById('loginBtn');
    const loginForm = document.getElementById('loginForm');

    loginBtn.addEventListener('click', async () => {
        await login();
    });

    loginForm.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            login();
        }
    });
});

async function login() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

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
        formData.append("grant_type", "password");
        formData.append("username", username);
        formData.append("password", password);

        const basicAuth = btoa(
            "ixMj1leprQBGKdWuN9W5oHgoaHjvDRZyJF0Vrie1" +
            ":" +
            "qiqieoOL8tsHwMhuluVMujSC2J4vlsBzJrtMj6QqQkCzNrEkpf9pMOMeRdLnPV9rUL94bwFonfGibL8IUNvVR1WJw4hQ6WGvbN7bBwnGoiqUCdf5AqcdhkbyGEzQiI5o"
        );

        const response = await fetch("/o/token/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": `Basic ${basicAuth}`
            },
            body: formData.toString()
        });

        const data = await response.json();

        if (response.ok) {

            // save token
            localStorage.setItem("access_token", data.access_token);

            // get current user info
            const userRes = await fetch("/users/current-user/", {
                headers: {
                    "Authorization": `Bearer ${data.access_token}`
                }
            });

            const user = await userRes.json();
            localStorage.setItem("user", JSON.stringify(user));

            alertBox.innerHTML = `
            <div class="alert alert-success">
                Đăng nhập thành công!
            </div>`;

            

            // redirect based on role after short delay
            setTimeout(() => {
                const urlParams = new URLSearchParams(window.location.search);
                const next = urlParams.get("next");

                if (next && user.role === "patient") {
                    window.location.href = next;
                    return;
                }

                switch (user.role) {
                    case "doctor":
                        window.location.href = "/doctor/dashboard/";
                        break;

                    case "admin":
                        window.location.href = "/admin/";
                        break;

                    case "receptionist":
                        window.location.href = "/receptionist/dashboard/";
                        break;

                    default:
                        window.location.href = "/index/";
                }

            }, 500);

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