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

    $.fn.loadDataTableDocs = function(){
        var empresa = "{{ empresa }}";
        var url =  '/' + empresa + '/manager/pasajeros/gettable';
        var data = {
            venta: $('[name=ventas]').find(':selected').val(),
        }
        var $table_fixed = $("#table-course");

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
                {targets: 0, className: 'cell-right'},
                {targets: 1, className: 'cell-right'},
                {targets: 2, className: 'cell-left'},
                {targets: 3, className: 'cell-right'},
                {targets: 4, className: 'cell-left'},
                {targets: 5, className: 'cell-left'},
                {targets: 6, className: 'cell-left'},
                {targets: 7, className: 'cell-right'},
                {targets: 8, className: 'cell-right'},
                {targets: 9, className: 'cell-right'},
                {targets: 10, className: 'cell-center'},
                {targets: 11, className: 'cell-center'},
                {targets: 12, className: 'cell-center'},
                {targets: 13, className: 'cell-center'},
                {targets: 14, className: 'cell-center'}            ],
            "initComplete": function(settings, json) {

            }
        });
    };

    $('body').loadDataTableDocs();

    $('#ventas').select2();

})

jQuery(document).on("click", ".delete-register", function() {

    e.preventDefault(); // Evita que el link navegue a "#"
    var id = jQuery(this).attr('data-id');
    var empresa = "{{ empresa }}";
    let baseUrl = "/" + empresa + "/manager/pasajeros/delete/";

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

jQuery(document).on("change", "select[name=ventas]", function() {
    
    if ( $.fn.DataTable.isDataTable('#table-course') ) {
        $('#table-course').DataTable().clear();
        $('#table-course').DataTable().destroy();
    }
    $('body').loadDataTableDocs();
    
   /*
    var table = $("#table-course").DataTable();
     table.ajax.reload();
     */
});