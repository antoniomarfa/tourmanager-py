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

var configErrorGeneralBootbox = {
    message: "<strong>Se ha producido un error, vuelve actualizar la página.</strong>",
    closeButton: false,
    buttons: {
        cancel: { label: 'No', className: 'hidden' },
        confirm: { label: 'Aceptar', className: 'btn-danger'
        },
    },
    callback: function (result){}
}

$.fn.loadModalBootbox = function(message, isCloseButton = false, classNameButtonAcept = 'btn-danger')
{
    bootbox.confirm({
        message: "<strong>" + message + "</strong>",
        closeButton: isCloseButton,
        buttons: {
            cancel: { label: 'No', className: 'hidden' },
            confirm: { label: 'Aceptar', className: classNameButtonAcept },
        },
        callback: function (result){}
    });
};

jQuery( document ).ready( function( $ ) {

    $.fn.loadDataTableDocs = function(){
        var empresa = "{{ empresa }}";
        var url = '/' + empresa + '/manager/entry/gettable';
        var data="";
        /*        var data = {
            tipo: $('[name=tipo]').find(':selected').val(),
            proyecto: $('[name=proyecto]').find(':selected').val(),
            estado: $('[name=estado]').find(':selected').val(),
        }
*/
        var $table_fixed = $("#table-ing");

        var table_fixed = $table_fixed.DataTable( {
            "ajax": {
                "url": url,
                "type": "POST",
                "data": data
            },
            "ordering": false,
            "lengthMenu": [[10, 50, 100, 150, -1], [10, 50, 100, 150, "All"]],
            "pageLength": 50,
            "oLanguage": language_datatable,
            "columnDefs": [
                {targets: 0, className: 'cell-center'},
                {targets: 1, className: 'cell-center'},
                {targets: 2, className: 'cell-center'},
                {targets: 3, className: 'cell-center'},
                {targets: 4, className: 'cell-center'},
                {targets: 5, className: 'cell-center'},
                {targets: 6, className: 'cell-center'},
                {targets: 7, className: 'cell-center'},
                {targets: 8, className: 'cell-center'},
                {targets: 9, className: 'cell-center'},
                {targets: 10, className: 'cell-center'},
                {targets: 11, className: 'cell-center'}
            ],
            "initComplete": function(settings, json) {
                $('#wraper_ajax').remove();
                // Initalize Select Dropdown after DataTables is created
          //      $table_fixed.closest( '.dataTables_wrapper' ).find( 'select' ).addClass('form-control');
          //      $('.dataTables_length label select').appendTo('.dataTables_length');
            }
        });
    };

    $('body').loadDataTableDocs();

    jQuery(document).on("click", ".cancel-register", function() {
        var empresa = "{{ empresa }}";

        var id = jQuery(this).attr('id');
    
        bootbox.confirm({
            message: "<strong>¿Está seguro que desea anular el registro seleccionado?</strong>",
            buttons: {
                cancel: {
                    label: '<i class="fa fa-times"></i> Cancelar'
                },
                confirm: {
                    label: '<i class="fa fa-check"></i> Confirmar',
                    className: 'btn-danger'
                }
            },
    
            callback: function (result) {
                if(result == true) {
                    jQuery(location).attr('href', '/' + empresa + '/manager/entry/cancel/' + id);
                }
            }
        });
    });
    


});
