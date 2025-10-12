var ulploadVta=0;
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

        var url = '/entry/getlistpay';
        var data = {
            venta: $('[name=ventas]').find(':selected').val(),
              
        }

        var $table_fixed = $("#table-pay");

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
                {targets: 1, className: 'cell-left'},
                {targets: 2, className: 'cell-left'},
                {targets: 3, className: 'cell-left'},
                {targets: 4, className: 'cell-left'},
                {targets: 5, className: 'cell-left'},
                {targets: 6, className: 'cell-right'},
                {targets: 7, className: 'cell-right'},
                {targets: 8, className: 'cell-center'},
                {targets: 9, className: 'cell-center'},
                {targets: 10, className: 'cell-center'},
                {targets: 11, className: 'cell-center'},
                {targets: 12, className: 'cell-center'},
                {targets: 13, visible: false}
            ],
            "initComplete": function(settings, json) {
                $('#wraper_ajax').remove();
            }
        });

    };



    $('body').loadDataTableDocs();
    
    $('#export-report').click(function() {
        $('#form').attr('action','/entry/exportreport');
        $('#form').submit();
        $('#form').attr('action', '/entry/listpay');
    });    
    

});

jQuery(document).on('click', '.show-compact-entry', function() {
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager/entry/getentries';
    var data = {
        id: jQuery(this).attr('id')
    }

    $.ajax({
        type: "POST",
        encoding: "UTF-8",
        url: url,
        data: data,
        dataType: 'json',
        success: function(response) {
            $('#wraper_ajax').remove();

            jQuery('body').addClass('modal-open-super');
            jQuery('#modal-compact-view').modal('show', {backdrop: 'static'});
            jQuery('#modal-compact-view .modal-body').html(response.data);
        }
    });
});

jQuery(document).on("change", "select[name=ventas]", function() {
    if ( $.fn.DataTable.isDataTable('#table-pay') ) {
        $('#table-pay').DataTable().clear();
        $('#table-pay').DataTable().destroy();
    }
    $('body').loadDataTableDocs();
});