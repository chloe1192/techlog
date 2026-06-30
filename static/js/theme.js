function syncButtonLoading() {
    document.getElementById('syncButton').classList.add('box-amber')
    document.getElementById('syncButton').classList.remove('box-green')
}

function syncButtonLoaded() {
    document.getElementById('syncButton').classList.add('box-green')
    document.getElementById('syncButton').classList.remove('box-amber')
}

function nilUplift(checkbox) {
    const elements = document.querySelectorAll('[data-nil-uplift]')

    elements.forEach(element => {
        if (checkbox.checked) {
            element.setAttribute('disabled', 'disabled')
            element.setAttribute('data-auth-required', 'false')
        } else {
            element.removeAttribute('disabled')
            element.setAttribute('data-auth-required', 'true')
        }
    })
    inputRequired()
}

function inputRequired() {
    const required_elements = document.querySelectorAll('[data-auth-required]')
    var all_required_inputs_set = []
    const submit_button = document.getElementById('submitButton')
    let checker = arr => arr.every(v => v === true);

    required_elements.forEach(element => {
        if (element.dataset.authRequired == "true" && element.value != false) {
            all_required_inputs_set.push(true)
        } else if (element.dataset.authRequired == "false") {
            all_required_inputs_set.push(true)
        } else {
            all_required_inputs_set.push(false)            
        }
    })

    if (checker(all_required_inputs_set)) {
        submit_button.removeAttribute('disabled')
    } else {
        submit_button.setAttribute('disabled', 'disabled')
    }
}