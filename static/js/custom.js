function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function deleteSuccessful(response) {
    var replies = response;
    $('div#'+response.id).remove();
    // $('div#'+response.id).remove();
    // var reply_html = "<div class='comment_area clearfix mb-50'><ul class='replies''>";
    // for (var i = 0; replies[i]; i++){
    //     reply_html += "<li class='single_comment_area'><div class='comment-content d-flex'><div class='comment-author'><img src='#' alt='author'></div><div class='comment-meta'><a href='#' class='comment-date'>" + replies[i].date + "</a><h6>" + replies[i].username + "</h6><p>" + replies[i].text + "</p><div class='d-flex align-items-center'><a href='#' class='like'>likes: "  + replies[i].likes + "</a></div></div></div></li>";
    // }
    // reply_html += "</ul></div>";
    // $(".modal-body").html(reply_html);
    // console.log("hello world");
}
function deleteFailed() {
    window.alert("did not work");
}
function editSuccessful() {
    
}
function deleteItem(id, code) {
    $.ajax({
        type : 'POST',
        url : '/delete-item/' + id + '/' + code,
        data : null,
        dataType : 'json',
        success: deleteSuccessful,
        error: deleteFailed,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}
//also editing stuff
function editItem(id, dataString) {
    $.ajax({
        type : 'POST',
        url : '/update-drive/' + id,
        data : dataString,
        dataType : 'json',
        success: editSuccessful,
        error: editFailed,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}


$('#delete').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var recipient = button.data('id'); // Extract info from data-* attributes
    var code = button.data('code'); // Extract info from data-* attributes
    document.forms.delete_drive.elements.drive_id.value = recipient;
    document.forms.delete_drive.elements.code.value = code;
    // (recipient, '/replies/');
})
$("form[name=delete_drive]").submit( function (e) {
    console.log("preventing default");
    e.preventDefault();
    console.log("prevented default");
    var id = $('form[name=delete_drive] input:hidden[name=drive_id]').val();
    var code = $('form[name=delete_drive] input:hidden[name=code]').val();;
    // var userSlug = location.href.split('/')[3];
    deleteItem(id, code);
})

//for editin stuffs
$('#edit').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var itemId = button.data('id'); // Extract info from data-* attributes
    var itemName = button.data('name');
    var itemPictureUrl = button.data('url');
    document.forms.edit_drive.elements.drive_id.value = itemId;
    document.forms.edit_drive.elements.id_name.value = itemName;
    document.forms.edit_drive.elements.id_cover_picture.value = itemPictureUrl;
})

$("form[name=edit_drive]").submit( function (e) {
    console.log("preventing default");
    e.preventDefault();
    console.log("prevented default");
    var id = $('form[name=edit_drive] input:hidden[name=drive_id]').val();
    var name = $('form[name=edit_drive] input:text[name=drive_name]').val();
    var picture = $('form[name=edit_drive] input:hidden[name=drive_image]').val();
    var dataString = 'id_name=' + name + '&id_cover_picture=' + picture;
    editItem(id, dataString);
})