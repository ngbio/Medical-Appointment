document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const alertHome = document.getElementById("alert-home");

    if (params.get("success")) {
        if (params.get("success") === "1") {
            alertHome.textContent = "Đặt lịch khám thành công!";
            alertHome.classList.remove("alert-danger");
        }
        else {
            alertHome.textContent = "Lỗi hệ thống vui lòng thử lại sau!";
            alertHome.classList.add("alert-danger");
        }
        alertHome.classList.remove("d-none");
        history.replaceState({}, "", "/");
    }

    // Load carousel images
    const images = [
        "img1_gnq4er.jpg",
        "img3_cjt2ri.jpg",
        "img2_lj1frj.jpg"
    ];
    
    const carouselInner = document.getElementById('carouselInner');
    const baseUrl = 'https://res.cloudinary.com/dprwsgoeg/image/upload/v1774936912/';
    
    images.forEach((img, index) => {
        const carouselItem = document.createElement('div');
        carouselItem.className = 'carousel-item' + (index === 0 ? ' active' : '');
        
        carouselItem.innerHTML = `
            <div class="ratio ratio-16x9">
                <img src="${baseUrl}${img}" class="d-block w-100" style="object-fit: cover;" alt="Nha khoa Việt Nam">
            </div>
        `;
        
        carouselInner.appendChild(carouselItem);
    });
});
