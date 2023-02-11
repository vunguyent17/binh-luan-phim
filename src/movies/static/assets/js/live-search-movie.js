$(document).ready(function(){
 $('#search-movies').on('input', function() {
 var search_result = $('#search-results')

        $.ajax({
            type: "GET",
            url: window.location.href,
            data: {
                'operation': 'live_search_movies',
                'search_text' : $('#search-movies').val(),
            },

            success: function(response) {
            search_result.html('')
            res = JSON.parse(response);
            movies = res.movies_live_result;
            for(var i = 0 ; i < movies.length ; i++)
            {
                btnLabel = "Thêm";
                btnAttr = "";
                if (movies[i].added){
                btnLabel = "Đã Thêm";
                btnAttr = " disabled";
                }
                html = `<li>${movies[i].title}<button id="add${movies[i].id}" class="btn btn-success add-to-movielist float-end z-2"
                onclick="AddMovieToThisList(${movies[i].id})" ${btnAttr}>${btnLabel}</button></li>`;
                search_result.append(html);
            }
            },
            dataType: 'html'
        });
    });
});
