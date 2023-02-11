

function DeleteMovieInList(data_movie_id){
    $.ajax({
             type: "POST",
             url: window.location.href,
             data:{
                'operation':'delete_movie_in_list',
                'csrfmiddlewaretoken': getCookie('csrftoken'),
                'movie_id': data_movie_id
             },
             dataType: "json",
             success: function(response) {
              selector = $("#movie"+response.movie_id);
              if(response.deleted==true){
                  $(selector).remove();
                  if (parseInt(response.moviescount) == 0){
                      $(".movie_list_detail_body").html('<p class="text-white text-center p-3">Danh sách trống</p>');
                }
                }

              }
        });
  }

  $(document).ready(function(){
    // AJAX CALL
$('.delete-movie').click(function() {
    data_movie_id = $(this).attr('data-movie-id');
    DeleteMovieInList(data_movie_id);
    });
});