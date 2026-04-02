document.addEventListener("DOMContentLoaded", async function(){

    const token = localStorage.getItem("access_token");

    if(!token)
        return;

    const guestMenu = document.getElementById("guestMenu");
    const userMenu = document.getElementById("userMenu");

    guestMenu.style.display = "none";
    userMenu.style.display = "block";

    try{

        const res = await fetch("/users/current-user/",{
            headers:{
                "Authorization": "Bearer " + token
            }
        });

        const user = await res.json();

        document.getElementById("username").innerText = user.username;

        // phân quyền
        if(user.role === "admin"){
            document.getElementById("adminMenu").style.display = "block";
        }

        if(user.role === "receptionist"){
            document.getElementById("invoiceMenu").style.display = "block";
        }

        if(user.role === "doctor"){
            document.getElementById("appointmentMenu").style.display = "none";
        }

    }catch(err){
        console.log(err);
    }

});
    function handleLogout(){
        localStorage.removeItem("access_token");
        // Gọi Django logout view để xóa server session
        fetch("/logout/", {method: "GET"})
            .then(() => {
                window.location.href = "/index/";
            })
            .catch(() => {
                window.location.href = "/index/";
            });
    }
