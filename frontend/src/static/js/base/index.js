function handleBookingRedirect() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "/login/?next=/booking/";
        return;
    }

    window.location.href = "/booking/";
}