async function loadMenu(token) {
    try {
        const res = await fetch("/api/menu/", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

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

    const guestMenu = document.getElementById("guestMenu");
    const userMenu = document.getElementById("userMenu");

    // Nếu chưa login
    if (!token) {
        guestMenu.style.display = "block";
        userMenu.style.display = "none";

        // Load menu guest
        await loadMenu(null);
        return;
    }

    // Nếu đã login
    guestMenu.style.display = "none";
    userMenu.style.display = "block";

    try {
        const res = await fetch("/users/current-user/", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const user = await res.json();

        document.getElementById("username").innerText = user.username;

        // Load menu theo role từ backend
        await loadMenu(token);

    } catch (err) {
        console.log(err);
    }

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
