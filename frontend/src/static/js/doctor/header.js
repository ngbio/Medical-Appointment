async function loadCurrentUser() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    let user = null;
    const userStr = localStorage.getItem("user");

    if (userStr) {
        user = JSON.parse(userStr);
    } else {
        try {
            const res = await authFetch("/users/current-user/");
            user = await res.json();

            // cache lại
            localStorage.setItem("user", JSON.stringify(user));
        } catch (err) {
            console.error("Cannot fetch user:", err);
            return;
        }
    }

    if (user) {
        document.getElementById("employeeUserName").innerText =
            `Welcome, ${user.username}`;
    }
}