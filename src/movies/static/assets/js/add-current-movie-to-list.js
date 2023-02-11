function ShowModalAddToList(username){
        $.ajax({
            type: "GET",
            url: window.location.href,
            data: {
                'operation': 'get_movielists_from_username',
                "username": username,
            },
            dataType: 'html',
            success: function(response) {
            $("#movielists").html('');
            res = JSON.parse(response);
            movielists = res.movielists;
            for(var i = 0 ; i < movielists.length ; i++)
            {
                btnLabel = "Thêm";
                btnClass = "btn-success";
                if (movielists[i].added){
                btnLabel = "Đã thêm";
                btnClass = "btn-secondary";
                }
                html = `<li class="list-group-item"><span class="fw-bold">${movielists[i].name}</span><br>${movielists[i].description}<button id="addToList${movielists[i].id}" class="btn ${btnClass} add-to-movielist float-end z-2"
                onclick="AddToList(${movielists[i].id})">${btnLabel}</button></li>`;
                $("#movielists").append(html);
            }
            }
        });
        $('#modalAddToList').modal('show');
    }

function AddToList(movielist_id)
{
	 $.ajax({
             type: "POST",
             url: window.location.href,
             data:{
                'operation':'add_to_list_submit',
                'csrfmiddlewaretoken': getCookie('csrftoken'),
                'movielist_id': movielist_id,
             },
             dataType: "json",
             success: function(response) {
                    selector = document.getElementById("addToList"+String(movielist_id));
                    if(response.added==true){
                      $(selector).removeClass("btn-success");
                      $(selector).addClass("btn-secondary");
                      $(selector).html("Đã thêm");
                    }
                    else if(response.added==false){
                        $(selector).removeClass("btn-secondary");
                      $(selector).addClass("btn-success");
                      $(selector).html("Thêm");
                    }
              }
                    });
        };
