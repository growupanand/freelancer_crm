loading_spinner = '<div class="spinner-border spinner-border-sm mx-auto" role="status">' +
    '<span class="visually-hidden">Loading...</span>' +
    '</div>'

// for ajax
const request = new XMLHttpRequest()

// set global ajax start function
request.onloadstart = function () {
    if (document.body.contains(document.getElementById('ajax_loading'))) {
        fadein('ajax_loading')
    }
}

// set global ajax stop function
request.onloadend = function () {
    if (document.body.contains(document.getElementById('ajax_loading'))) {
        fadeout('ajax_loading')
    }
}

// set global ajax error for not connecting to server
request.onerror = function () {
    show_alert('Server not online!', 'error')
}

function validate_form(form, invalid_fields) {
    // clear invalid class from all input
    all_form_input = form.querySelectorAll('input, select')
    for (let i = 0; i < all_form_input.length; i++) {
        all_form_input[i].classList.replace('is-invalid', 'is-valid')
    }
    // if invalid_fields are without invalid msg
    if (Array.isArray(invalid_fields)) {
        for (i in invalid_fields) {
            form[invalid_fields[i]].classList.add('is-invalid')
        }
    } else {// if invalid_fields are with invalid msg
        for (i in invalid_fields) {
            form[i].classList.add('is-invalid')
            feedback_el = form[i].nextElementSibling
            if (feedback_el === null) {
                feedback_el = document.createElement('div')
                feedback_el.className = 'invalid-feedback'
                feedback_el.innerHTML = invalid_fields[i]
                form[i].after(feedback_el)
            } else {
                if (!feedback_el.classList.contains('invalid-feedback')) {
                    feedback_el = document.createElement('div')
                    feedback_el.className = 'invalid-feedback'
                    feedback_el.innerHTML = invalid_fields[i]
                    form[i].after(feedback_el)
                } else {
                    feedback_el.innerHTML = invalid_fields[i]
                }
            }

            feedback_el.innerHTML = invalid_fields[i]
        }
    }
}

function unvalidate_form(form) {
    // clear validation class from all input
    all_form_input = form.querySelectorAll('input, select')
    for (let i = 0; i < all_form_input.length; i++) {
        all_form_input[i].classList.remove('is-invalid', 'is-valid')
    }
}

var default_submit_btn_text = ''

function disable_form(form) {
    all_inputs = form.querySelectorAll('input, select')
    for (i = 0; i < all_inputs.length; i++) {
        all_inputs[i].readOnly = true
    }
    all_submits = form.querySelectorAll('[type=submit]')
    for (i = 0; i < all_submits.length; i++) {
        all_submits[i].disabled = true
        default_submit_btn_text = all_submits[i].innerText
        all_submits[i].innerHTML = loading_spinner
    }
    // all submit button outside form which linked to this form
    if (form.hasAttribute('id')) {
        all_submits = document.querySelectorAll('[form=' + form.id + ']')
        for (i = 0; i < all_submits.length; i++) {
            all_submits[i].disabled = true
            default_submit_btn_text = all_submits[i].innerText
            all_submits[i].innerHTML = loading_spinner
        }
    }
}

function enable_form(form) {

    all_inputs = form.querySelectorAll('input, select')
    for (i = 0; i < all_inputs.length; i++) {
        all_inputs[i].readOnly = false
    }
    all_submits = form.querySelectorAll('[type=submit]')
    for (i = 0; i < all_submits.length; i++) {
        all_submits[i].innerHTML = default_submit_btn_text
        all_submits[i].disabled = false
    }
    if (form.hasAttribute('id')) {
        all_submits = document.querySelectorAll('[form=' + form.id + ']')
        for (i = 0; i < all_submits.length; i++) {
            all_submits[i].innerHTML = default_submit_btn_text
            all_submits[i].disabled = false
        }
    }
}

function hide_modal(modal_id) {
    modal = bootstrap.Modal.getInstance(document.getElementById(modal_id))
    modal.hide()
}

function hide_offcanvas(offcanvas_id) {
    modal = bootstrap.Offcanvas.getInstance(document.getElementById(offcanvas_id))
    modal.hide()
}

function edit_control_toggle(id) {
    all_edit_controls = document.querySelectorAll('#' + id + ' .edit_control, ' + '#' + id + ' .edit_control_showing')
    for (let i = 0; i < all_edit_controls.length; i++) {
        all_edit_controls[i].classList.toggle('edit_control')
        all_edit_controls[i].classList.toggle('edit_control_showing')
    }
}

function show_alert(msg, type = null) {
    toast_class = {
        'error': 'toast bg-danger text-white',
        'success': 'toast bg-success text-white',
        'warning': 'toast bg-warning'
    }

    alert_el = document.createElement('div')
    if (type === null) {
        alert_el.className = "toast"
    } else {
        alert_el.className = toast_class[type]
    }
    alert_el.id = 'alert_toast'
    alert_el.setAttribute('role', 'alert')
    // create p element for alert msg so new line \n can be show in html
    alert_msg = document.createElement('p')
    alert_msg.innerText = msg
    alert_el.innerHTML = '<div class="d-flex justify-content-between">' +
        '<div class="toast-body fw-bold text-capitalize">' + alert_msg.innerHTML + '</div>' +
        '<button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>' +
        '</div>'
    document.getElementById('alert_container').append(alert_el)
    alert_toast = new bootstrap.Toast(alert_el)
    alert_el.addEventListener('hidden.bs.toast', function () {
        this.remove()
    })
    alert_toast.show()
}

function fadein(id) {
    el = document.getElementById(id)
    el.classList.remove('fadein_show', 'fadein_hide', 'fadeout_hide', 'fadeout_show')
    el.classList.add('fadein_show')
    el.classList.remove('fadein_hide')

}

function fadeout(id) {
    el = document.getElementById(id)
    el.classList.remove('fadein_show', 'fadein_hide', 'fadeout_hide', 'fadeout_show')
    el.classList.add('fadeout_hide');
    el.classList.remove('fadeout_show');
}

function format_mongo_date(date) {
    d = new Date(date['$date'])
    return d.toISOString().slice(0, 10).split('/').reverse().join('-')
}

function format_input_date(date) {
    d = new Date(date)
    day = d.toLocaleString('default', {day: '2-digit'})
    month = d.toLocaleString('default', {month: 'short'})
    year = d.toLocaleString('default', {year: 'numeric'})
    return [day, month, year].join('-')
}
