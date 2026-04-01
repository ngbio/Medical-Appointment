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
