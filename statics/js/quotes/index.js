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
var ulploadVta=0;

jQuery( document ).ready( function( $ ) {

    $.fn.loadDataTableDocs = function(){
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager/quotes/gettable';
        var data = {
            start_date: $("input#start_date").val(),
            end_date: $("input#end_date").val(),
            vendedor: $('[name=vendedor]').find(':selected').val(),
        }
        var $table_fixed = $("#table-sale");

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
                {targets: 6, className: 'cell-right'},
                {targets: 7, className: 'cell-center'},
                {targets: 8, className: 'cell-right'},
                {targets: 9, className: 'cell-right'},
                {targets: 10, className: 'cell-right'},
                {targets: 11, className: 'cell-center'},
                {targets: 12, className: 'cell-center'},
                {targets: 13, className: 'cell-center'},
                {targets: 14, className: 'cell-center'},
                {targets: 15, className: 'cell-center'},
                {targets: 16, className: 'cell-center'},
                {targets: 17, className: 'cell-center'}
            ],
            "initComplete": function(settings, json) {
                $('.dataTables_length label select').appendTo('.dataTables_length');
            }
        });
    };

    $('body').loadDataTableDocs();

    $('#vendedor').select2();
   // $('#colegio').select2();

    $('#export-report').click(function() {
        var empresa = "{{ empresa }}";
        $('#form1').attr('action', '/' + empresa + '/manager/exportreport');
        $('#form1').submit();
        $('#form1').attr('action', '/' + empresa + 'manager/index');
    });    

    $('.search').click(function(){
        
        if ( $.fn.DataTable.isDataTable('#table-sale') ) {
            $('#table-sale').DataTable().clear();
            $('#table-sale').DataTable().destroy();
        }
        $('body').loadDataTableDocs();
        /*
       var table = $("#table-sale").DataTable();
       table.ajax.reload();
*/
    })

    jQuery(document).on("click", ".cancel-register", function(e) {
    e.preventDefault(); // Evita que el link navegue a "#"
    var id = jQuery(this).attr('data-id');
    var empresa = "{{ empresa }}";
    let baseUrl = "/" + empresa + "/manager/quotes/cancel/";

    let url = `${baseUrl}${id}`;

        Swal.fire({
        title: "Eliminar Registro",
        text: "¿Está seguro que desea Rechazar la cotizacion Nro: "+id,
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

    jQuery(document).on("click", ".change-status", function(e) {
        e.preventDefault(); // Evita que el link navegue a "#"
        var id = jQuery(this).attr('data-id');

        const swalWithBootstrapButtons = Swal.mixin({
        customClass: {
            confirmButton: "btn btn-success",
            cancelButton: "btn btn-danger"
        },
        buttonsStyling: false
        });
        swalWithBootstrapButtons.fire({
        title: "Cotizacion?",
        text: "Cambiar estado de la cotizacion Nro: "+id,
        icon: "question",
        showCancelButton: true,
        confirmButtonText: "Cotizacion Aceptada",
        cancelButtonText: "Cotizacion Rechazada",
        reverseButtons: true
        }).then((result) => {
        if (result.isConfirmed) {
           changesStatus(id,"A")  
        } else if (
            /* Read more about handling dismissals below */
            result.dismiss === Swal.DismissReason.cancel
        ) {
           changesStatus(id,"R")  
        }
        });        
        
    })

});

jQuery(document).on("change", "select[name=vendedor]", function() {
    /*
    if ( $.fn.DataTable.isDataTable('#table-sale') ) {
        $('#table-sale').DataTable().clear();
        $('#table-sale').DataTable().destroy();
    }
    $('body').loadDataTableDocs();
    */
    var table = $("#table-sale").DataTable();
     table.ajax.reload();

});

function changesStatus(id,new_status){
    var empresa = "{{ empresa }}";
    let baseUrl = "/" + empresa + "/manager/quotes/setstatus/";

    let url = `${baseUrl}`;

    var data = {
        status: new_status,
        id_quote: id,
    }
    
    $.ajax({
        type: "POST",
        encoding: "UTF-8",
        url: url,
        data: data,
        dataType: 'json',
        beforeSend: function(){
          //  $("body").prepend(ajax_loader);
    
              //  table.reload();
         },
        success:function(response){
            if(response.error == 0){
                Swal.fire({
                    title: "Cotizacion",
                    text: response.message,
                    icon: "success"
                });
                window.location.href = '/'+ empresa +'/manager/quotes'; 
            } else {
                Swal.fire({
                    title: "Cotizacion",
                    text: "Se produjo un error, vuelve a actualizar la pagina",
                    icon: "error"
                });
                window.location.href = '/quotes'; 
            }
        },
        error: function() {
            Swal.fire({
                title: "Cotizacion",
                text: "se produjo un error, vuelve a actualizar la pagina",
                icon: "error"
            });
            window.location.href = '/' + empresa + '/manager/quotes'; 
        }
     });

 }
