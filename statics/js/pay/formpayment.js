jQuery(document).on('click', '.show-compact-entry', function() {
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager/getEntries';
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

    document.getElementById('Flow').addEventListener('click', function() {
        var empresa = "{{ empresa }}";
        var urlf='/'+ empresa + '/manager/flowpagos/inicioTransaccion';
        // Cambiar la acci贸n del formulario al endpoint de Flow
        document.getElementById('pagosweb').action = urlf
    });

    document.getElementById('TransBank').addEventListener('click', function() {
        var empresa = "{{ empresa }}";
        var urlt= '/'+ empresa + '/manager/trbnkpagos/inicioTransaccion';
        // Cambiar la acci贸n del formulario al endpoint de Trbnk
        document.getElementById('pagosweb').action = urlt
    });    

    document.getElementById('MercadoPago').addEventListener('click', function() {
        var empresa = "{{ empresa }}";
        var urlt='/' +empresa + '/manager/mercadopago/inicioTransaccion';
        // Cambiar la acci贸n del formulario al endpoint de Trbnk
        document.getElementById('pagosweb').action = urlt
    });    
    