$(document).ready(function(){
$(window).on('load', function() {

        $('.add_fav_btn').click(function(){
            $.ajax({
             type: "POST",
             url: window.location.href,
             data:{
                'operation':'add_to_favorite_submit',
                'csrfmiddlewaretoken': getCookie('csrftoken'),
             },
             dataType: "json",
             success: function(response) {
              selector = document.getElementsByName("add_fav_btn");
                    if(response.added==true){
                      $(selector).css("color","red");
                    }
                    else if(response.added==false){
                      $(selector).css("color","black");
                    }
              }
        });
  });

});

});


