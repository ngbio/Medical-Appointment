document.addEventListener("DOMContentLoaded", loadMenu);

async function loadMenu() {
    const token = localStorage.getItem("access_token");

    try {
        const res = await fetch("/api/menu/", {
            headers: token
                ? { "Authorization": `Bearer ${token}` }
                : {}
        });

        const menus = await res.json();

        const container = document.getElementById("sidebarMenu");
        container.innerHTML = "";

        menus.forEach(item => {
            container.innerHTML += `
                <li class="nav-item mb-2">
                    <a href="${item.url}" class="nav-link text-white">
                        <i class="fa fa-circle me-2"></i> ${item.name}
                    </a>
                </li>
            `;
        });

        // Add logout riêng
        container.innerHTML += `
            <li class="nav-item mt-4">
                <a href="#" onclick="logout()" class="nav-link text-danger">
                    <i class="fa fa-sign-out-alt me-2"></i> Logout
                </a>
            </li>
        `;

    } catch (err) {
        console.error("Load menu failed:", err);
    }
}

// Logout
function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login/";
}