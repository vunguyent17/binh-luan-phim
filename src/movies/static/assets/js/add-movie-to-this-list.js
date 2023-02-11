function AddMovieToThisList(movie_id)
{
    console.log("AddMovieToThisList")
    var movie_list_body = $(".movie_list_detail_body")
	 $.ajax({
             type: "POST",
             url: window.location.href,
             data:{
                'operation':'add_movie_to_this_list_submit',
                'csrfmiddlewaretoken': getCookie('csrftoken'),
                'movie_id': parseInt(movie_id)
             },
             dataType: "json",
             success: function(response) {
                    if(response.added==true){
                      movie = response.movie_added;
                      html = `<div id="movie${movie.id}" class="item">
    <h4><a href="/movie/${movie.id}">${movie.title}</a>
        <button id="delete${movie.id}"
                class="btn btn-link delete-movie text-decoration-none float-end"
                data-movie-id="${movie.id}" onclick="DeleteMovieInList(${movie.id})">Xóa
        </button>
    </h4>
    <p>Năm: ${movie.year} | Thể loại: ${movie.genres}</p>
</div>`;

                      if (parseInt(response.moviescount) == 1){
                      movie_list_body.html('');
                      }
                      movie_list_body.append(html);
                      $("#add"+movie.id).prop('disabled', true);
                      $("#add"+movie.id).html("Đã thêm")
                    }


              }
        });
}