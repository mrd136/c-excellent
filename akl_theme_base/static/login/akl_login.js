// toggle the password display

$(document).ready(function () {
    var togglePassword = document.getElementById("toggle-password");
    togglePassword.addEventListener('click', function() {
        var x = document.getElementById("password");
        if (x.type === "password") {
            x.type = "text";
        } else {
            x.type = "password";
        }
    });
})
