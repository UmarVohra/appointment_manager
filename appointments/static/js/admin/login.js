function togglePassword() {
    const passwordInput = document.getElementById("password");
    const toggleIcon = document.getElementById("password-toggle");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleIcon.classList.remove("fa-eye");
        toggleIcon.classList.add("fa-eye-slash");
    } else {
        passwordInput.type = "password";
        toggleIcon.classList.remove("fa-eye-slash");
        toggleIcon.classList.add("fa-eye");
    }
}

// Form submission handler
document
    .getElementById("login-form")
    .addEventListener("submit", function (e) {
        console.log("Form is submitting...");
        const button = document.getElementById("login-button");
        const originalText = button.innerHTML;

        button.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Logging in...';
        button.disabled = true;

        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
    });

// Add floating animation to illustration
const illustration = document.querySelector("#illustration-section img");
if (illustration) {
    setInterval(() => {
        illustration.style.transform = "translateY(-10px)";
        setTimeout(() => {
            illustration.style.transform = "translateY(0px)";
        }, 1000);
    }, 3000);
}