async function loadMenu(token) {
    try {
        const headers = token
            ? { "Authorization": "Bearer " + token }
            : {};

        const res = await fetch("/api/menu/", { headers }); // Get menu for current user

        const menus = await res.json();

        const menuBar = document.getElementById("menuBar");
        menuBar.innerHTML = "";

        menus.forEach(menu => {
            const li = document.createElement("li");
            li.className = "nav-item";

            li.innerHTML = `
                <a class="nav-link fw-semibold" href="${menu.url}">
                    ${menu.name}
                </a>
            `;

            menuBar.appendChild(li);
        });

    } catch (err) {
        console.error("Load menu error:", err);
    }
}

document.addEventListener("DOMContentLoaded", async function () {

    const token = localStorage.getItem("access_token");
    const userStr = localStorage.getItem("user");

    const guestMenu = document.getElementById("guestMenu");
    const userMenu = document.getElementById("userMenu");

    // Not login
    if (!token) {
        guestMenu.style.display = "block";
        userMenu.style.display = "none";

        await loadMenu(null);
        return;
    }

    // Login
    guestMenu.style.display = "none";
    userMenu.style.display = "block";

    let user = null;

    if (userStr) {
        user = JSON.parse(userStr);
    } else {
        try {
            const res = await fetch("/users/current-user/", {
                headers: {
                    "Authorization": "Bearer " + token
                }
            });
            user = await res.json();

            // cache lại
            localStorage.setItem("user", JSON.stringify(user));

        } catch (err) {
            console.error(err);
        }
    }

    if (user) {
        document.getElementById("username").innerText = user.username;
    }

    await loadMenu(token);
});

function handleLogout() {
    localStorage.removeItem("access_token");
    // Gọi Django logout view để xóa server session
    fetch("/logout/", { method: "GET" })
        .then(() => {
            window.location.href = "/index/";
        })
        .catch(() => {
            window.location.href = "/index/";
        });
}

