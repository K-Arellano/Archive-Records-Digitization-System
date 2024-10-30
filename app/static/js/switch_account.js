document.addEventListener("DOMContentLoaded", function () {
    const elements = {
        switchRolesBtn: document.getElementById("switch_roles"),
        submitButton: document.getElementById('signin'),
        formTitle: document.getElementById("form-title"),
        usernameInput: document.getElementById("username"),
        passwordInput: document.getElementById("password"),
        captchaImage: document.getElementById("captcha-image"),
        captchaInput: document.getElementById("captcha"),
        errorMessage: document.getElementById("error_message"),
        userRole: document.getElementById("role"),
    };

    function emptyError() {
        if (elements.errorMessage) {
            elements.errorMessage.innerText = "";
        }
    }

    function updateFormForRole(isAdmin) {
        const role = isAdmin ? 'Admin' : 'Staff';
        const roleValue = isAdmin ? '1' : '2';
        const btnClassAdd = isAdmin ? 'btn-gray' : 'btn-red';
        const btnClassRemove = isAdmin ? 'btn-red' : 'btn-gray';
        const btnText = isAdmin ? 'Sign in as Staff' : 'Sign in as Admin';
        const formTitleText = isAdmin ? 'Sign in as Admin' : 'Sign in as Staff';

        elements.switchRolesBtn.innerText = btnText;
        elements.usernameInput.classList.remove("is-invalid");
        elements.passwordInput.classList.remove("is-invalid");
        elements.formTitle.innerText = formTitleText;
        elements.userRole.value = roleValue;
        elements.submitButton.classList.remove(btnClassRemove);
        elements.submitButton.classList.add(btnClassAdd);
        emptyError()

        console.log(isAdmin);
    }

    function clearErrorMessageIfValid() {
        const inputs = [elements.usernameInput, elements.passwordInput, elements.captchaInput];
        const allValid = inputs.every(input => !input.classList.contains("is-invalid")) &&
            elements.captchaInput.value.length === 6;
        if (allValid) {
            emptyError()
        }
    }

    function handleInputFocus(input) {
        input.classList.remove("is-invalid");
        clearErrorMessageIfValid();
    }

    function handleCaptchaKeyup() {
        if (elements.captchaInput.value.length === 6) {
            elements.captchaInput.classList.remove("is-invalid");
            elements.captchaImage.classList.remove("is-invalid");
            clearErrorMessageIfValid();
        }
    }

    elements.switchRolesBtn.addEventListener("click", () => {
        const isAdmin = elements.switchRolesBtn.innerText.includes("Admin");
        updateFormForRole(isAdmin);
    });

    elements.usernameInput.addEventListener("focus", () => handleInputFocus(elements.usernameInput));
    elements.passwordInput.addEventListener("focus", () => handleInputFocus(elements.passwordInput));
    elements.captchaInput.addEventListener("keyup", handleCaptchaKeyup);
});
