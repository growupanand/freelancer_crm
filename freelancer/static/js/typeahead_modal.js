function select_user(f) {
    selected_username = null
    select_user_function = f
    result_table = document.getElementById('query_result_list')
    $(result_table).html('')
    $('#select_user_modal').modal('show');
}//endfunction


function submit_select_user_form(form) {
    event.preventDefault();
    query = form.query.value;

    $.ajax({
        type:'POST',
        url:'api/query_user',
        data:$(form).serialize(),
        dataType:'json',
        success: function (response) {
                html = ''
                for (i in response) {
                html += '<button value="'+response[i].username+'" onclick="result_list_select(this)" class="list-group-item list-group-item-action">'+response[i].first_name+'<small class="float-right">'+response[i].username+'</small></button>'
                }
                $(result_table).html(html);
        }

    });
}//end function


function result_list_select(username) {
    selected_username = username.value
    $('#select_user_modal').modal('hide');
    select_user_function();
}