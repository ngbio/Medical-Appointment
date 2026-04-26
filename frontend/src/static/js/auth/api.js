
function getToken() {
    return localStorage.getItem("access_token");
}

async function authFetch(url, options = {}) {
    const token = getToken();

    if (!token) {
        window.location.href = "/login/";
        return;
    }

    const res = await fetch(`https://medical-appointment-q26y.onrender.com/${url}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
            "Authorization": `Bearer ${token}`
        }
    });

    if (res.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login/";
        return;
    }

    if (res.status === 403) {
        alert("Bạn không có quyền!");
        window.location.href = "/";
        return;
    }

    return res;
}