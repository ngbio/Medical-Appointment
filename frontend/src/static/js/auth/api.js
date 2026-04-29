
function getToken() {
    return localStorage.getItem("access_token");
}

async function authFetch(url, options = {}) {
    const token = getToken();

    if (!token) {
        window.location.href = "/login/";
        return;
    }

    const res = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
            "Authorization": `Bearer ${token}`
        }
    });

    if (res.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        window.location.href = "/login/";
        throw new Error("Unauthorized");
    }

    if (res.status === 403) {
        alert("Bạn không có quyền!");
        window.location.href = "/";
        throw new Error("Forbidden");
    }
    return res;
}
