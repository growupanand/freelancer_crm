//function for display alert box
function show_alert(msg, type = 'default', id = 'alert', alert_type = 'toast') {
    alert_e = document.getElementById(id)
    $(alert_e).hide()
    if (alert_type == 'toast') {
        alert_class = {
            'default': 'bg-white text-dark',
            'error': 'bg-danger text-white',
            'success': 'bg-success text-white',
            'warning': 'bg-warning text-dark'
        }
        html = '<div class="toast-body ">' + msg +
            '<button type="button" class="btn-close text-white float-end" data-bs-dismiss="toast" aria-label="Close"></button>'
            + '</div>'
        alert_e.innerHTML = html
        alert_e.className = 'toast fw-bold top-0 start-0 fixed-top ' + alert_class[type];
        $(alert_e).show()
        $(alert_e).toast('show');
    } else {
        alert_class = {
            'default': 'alert-primary',
            'error': 'alert-danger',
            'success': 'alert-success',
            'warning': 'alert-warning'
        }
        html = '<div class="alert alert-dismissible fade show ' + alert_class[type] + '" role="alert">' +
            msg + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
            '</div>'
        alert_e.innerHTML = html
        $(alert_e).fadeIn()
    }

}

//function for hide alert box
function hide_alert(id = 'alert', alert_type = 'default') {
    alert_e = document.getElementById(id)
    if (alert_type == 'toast') {
        $(alert_e).toast('hide');
    } else {
        $(alert_e).fadeOut()
    }
}

var loading_html = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'


function formatdate(date) {
    now = new Date()
    var now = new Date(date + now.getTimezoneOffset() * 60000);
    var day = ("0" + now.getDate()).slice(-2);
    var month = ("0" + (now.getMonth() + 1)).slice(-2);
    var formatedate = (day) + "-" + (month) + "-" + now.getFullYear();
    return formatedate;
}


function formatdateinput(date) {
    now = new Date()
    var now = new Date(date + now.getTimezoneOffset() * 60000);
    var day = ("0" + now.getDate()).slice(-2);
    var month = ("0" + (now.getMonth() + 1)).slice(-2);
    var formatedate = now.getFullYear() + '-' + (month) + "-" + (day);
    return formatedate;
}

function format_timestamp(timestamp) {
    t = new Date(Date.parse(timestamp))
    new_timestamp = ''
    var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    new_timestamp += t.getDate() + '/' + months[t.getMonth()] + '/' + t.getFullYear() + ' - ' + t.getHours() + ':' + t.getMinutes()
    return new_timestamp
}

function check_select(e) {
    select_value = e.value
    $(e).next('input').prop('disabled', true).hide()
    if (select_value == 'other') {
        $(e).next('input').prop('disabled', false).show()
    }
}


$(document).ajaxError(function myErrorHandler(event, xhr, ajaxOptions, thrownError) {
    show_alert('Server error', 'error', 'alert', 'toast')
});