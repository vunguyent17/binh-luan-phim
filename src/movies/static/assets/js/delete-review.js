$(document).ready(function(){

    $('.confirm-delete').on('click', function(e) {
    // prevent form submit
    e.preventDefault();

    // get the current image/form id
    var link_delete = $(this).attr("data-delete-link")

    // assign the current id to the modal
    $('#btnDelete').attr("href", link_delete)
    $('#myModal').modal('show');
});
});
