$(document).ready(function(){

    $('.confirm-delete').on('click', function(e) {
    // prevent form submit
    e.preventDefault();

    $('#btnDelete').click(function(){
        $.ajax({
             type: "POST",
             url: window.location.href,
             data:{
                'operation':'delete_movielist',
                'csrfmiddlewaretoken': getCookie('csrftoken'),
             },
             dataType: "json",
             success: function(response) {
             window.location.href = response.link_to_redirect
              }
        });
    })

    $('#myModal').modal('show');
    });
});

