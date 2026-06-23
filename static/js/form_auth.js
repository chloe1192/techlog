
function updateAuthAllow(form){
    const crew_auth_id = document.getElementById("crew_auth_id");
    const crew_auth_sign = document.getElementById("crew_auth_sign");
    const requiredFields = form.querySelectorAll("[data-auth-required='true']");
    const formData = new FormData(form); 
    let can_sign = true
        console.log(requiredFields)

    requiredFields.forEach(field => {
        if (!field.value || field.value.trim().length === 0) {
            can_sign = false;
        }
    });
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    if (can_sign) {
        crew_auth_id.classList.remove("form-auth-red")
        crew_auth_id.classList.add("form-auth-green")

        if(crew_auth_id.value && crew_auth_id.value.trim().length > 0) {
            crew_auth_sign.classList.remove("form-auth-red")
            crew_auth_sign.classList.add("form-auth-green")
        } else {
            crew_auth_sign.classList.remove("form-auth-green")
            crew_auth_sign.classList.add("form-auth-red")
        }
    } 
    else {
        crew_auth_id.classList.remove("form-auth-green")
        crew_auth_id.classList.add("form-auth-red")
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form").forEach(form => {

        updateAuthAllow(form);

        form.addEventListener("input", () => updateAuthAllow(form));
        form.addEventListener("change", () => updateAuthAllow(form));
    });
});