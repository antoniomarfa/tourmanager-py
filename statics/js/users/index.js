const language_datatable = {
    "sProcessing":     "Procesando...",
    "sLengthMenu":     "Mostrar _MENU_ registros",
    "sZeroRecords":    "No se encontraron resultados",
    "sEmptyTable":     "Ningún dato disponible en esta tabla",
    "sInfo":           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_",
    "sInfoEmpty":      "Mostrando registros del 0 al 0 de un total de 0",
    "sInfoFiltered":   "(filtrado de un total de _MAX_ registros)",
    "sSearch":         "Buscar:",
    "oPaginate": {
        "sFirst":    "<<",
        "sLast":     ">>",
        "sNext":     ">",
        "sPrevious": "<"
    },
};

jQuery( document ).ready( function( $ ) {
    var $userTable = jQuery("#userTable");

    var userTable = $userTable.DataTable( {
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
        "oLanguage": language_datatable,
        //"order": [[9, "desc"]],
        "ordering": false,
    });

    // Initalize Select Dropdown after DataTables is created
    $userTable.closest( '.dataTables_wrapper' ).find( 'select' ).addClass('form-control');
    $('.dataTables_length label select').appendTo('.dataTables_length');

});

jQuery(document).on("click", ".delete-register", function(e) {
    e.preventDefault(); // Evita que el link navegue a "#"
    var id = jQuery(this).attr('data-id');
    var empresa = "{{ empresa }}";
    let baseUrl = "/" + empresa + "/manager/users/delete/";

    let url = `${baseUrl}${id}`;

        Swal.fire({
        title: "Eliminar Registro",
        text: "¿Está seguro que desea eliminar el registro seleccionado?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#43c613ff",
        cancelButtonColor: "#d33",
        confirmButtonText: "Si",
        cancelButtonText: "No"
        }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = url;        
        }
        });
});

jQuery(document).on("click", ".change-status", function() {
    var $element = jQuery(this);
    var id = $element.attr('id');
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager//users/status';
    var data = {
        user_id: id
    }

    jQuery.ajax({
        type: "POST",
        encoding:"UTF-8",
        url: url,
        data: data,
        dataType:'json',
        success: function(response){
            if(response.status == 1){
                $element.find('span').removeAttr('class').attr('class', '');
                $element.find('span').addClass('badge');
                $element.find('span').addClass(response.class_status);
                $element.find('span').text(response.text_status);
            }
        }
    });
});