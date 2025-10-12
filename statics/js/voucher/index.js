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
}
jQuery( document ).ready( function( $ ){

    $.fn.loadDataTableDocuments = function(){
        var empresa = "{{ empresa }}";
        var url = '/' + empresa + '/manager/voucher/gettable';
        var data = {
            venta: $('[name=search_venta]').find(':selected').val(),
        }

        var $table_fixed = $("#table-voucher");
        var table_fixed = $table_fixed.DataTable( {
            "ajax": {
                url: url,
                type: "POST",
                data: data, 
            },
            'destroy': true,
            "ordering": false,
            "lengthMenu": [[10, 50, 100, 150, -1], [10, 50, 100, 150, "All"]],
            "pageLength": 50,
            "oLanguage": language_datatable,
            "columnDefs": [
                {targets: 0, className: 'cell-right'},
                {targets: 1, className: 'cell-right'},
                {targets: 2, className: 'cell-center'},
                {targets: 3, className: 'cell-center'}
            ],
            "initComplete": function(settings, json) {
            }
        });
        
    };

    $('body').loadDataTableDocuments();
    
     $('#search_venta').select2();

});

jQuery(document).on("click", ".delete-register", function(e) {
    e.preventDefault(); // Evita que el link navegue a "#"
    var id = jQuery(this).attr('data-id');
    var empresa = "{{ empresa }}";
    let baseUrl = "/" + empresa + "/voucher/delete/";

    let url = `${baseUrl}${id}`;

        Swal.fire({
        title: "Eliminar Registro",
        text: "¿Está seguro que desea eliminar el registro seleccionado?",
        icon: "question",
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


jQuery(document).on("click", ".btn-add", function() {
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager/voucher/setvoucher';

    var venta = 0;
    $('[name="search_venta"]').find(':selected').each(function() {
        if($(this).val() != '') {
            venta= $(this).val();
        }
    });

    var data = {               
        venta: venta,
        voucher:$('#voucher').val(),
        url : url
    }

    $.ajax({
        type: "POST",
        encoding: "UTF-8",
        url: url,
        data: data,
        dataType: 'json',
        beforeSend: function(){
        },
        success:function(response){

            if(response.error == 0){

            var table = new DataTable('#table-voucher');
 
            table.row
                .add(response.data)
                .draw();               
                $("#voucher").val("")
                Swal.fire({
                    title: "Voucher",
                    text: response.message,
                    icon: "success"
                });
               // window.location.href = '/voucher';                 
            } else {
                Swal.fire({
                    title: "Voucher",
                    text: response.message,
                    icon: "success"
                });
                window.location.href = '/'+ empresa +'/manager/voucher';                 
            }
        },
        error: function() {
                Swal.fire({
                    title: "Voucher",
                    text: response.message,
                    icon: "success"
                });
                window.location.href = '/' + empresa + '/manager/voucher';
        }
    });
});


function fncnewdate(){
    var _node_fecha = 1;
    var element = $('#table-3').closest("tr");
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager/voucher/setDate';
    var data = {               
        e_date: $('#e_date').val(),
        url : url
    }

    $.ajax({
        type: "POST",
        encoding: "UTF-8",
        url: url,
        data: data,
        dataType: 'json',
        beforeSend: function(){
        },
        success:function(response){

            if(response.error == 0){
                element.find('td:eq(' + _node_fecha + ')').html(response.fecha);

                $('body').loadModalBootbox(response.message, false, 'btn-primary');
            } else {
                bootbox.confirm(configErrorGeneralBootbox);
            }
        },
        error: function() {
            $('#wraper_ajax').remove();
            bootbox.confirm(configErrorGeneralBootbox);
        }
    });
}

jQuery(document).on("change", "select[name=search_venta]", function() {
    if ( $.fn.DataTable.isDataTable('#table-voucher') ) {
        $('#table-voucher').DataTable().clear();
        $('#table-voucher').DataTable().destroy();
    }
    $('body').loadDataTableDocuments();
});