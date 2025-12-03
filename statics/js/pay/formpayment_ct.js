var total_cuotas = 0;
jQuery(document).ready(function ($) {

})

jQuery(document).on('click', '.show-compact-entry', function () {
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager/pay/getEntries';
    var data = {
        id: jQuery(this).attr('id')
    }

    $.ajax({
        type: "POST",
        encoding: "UTF-8",
        url: url,
        data: data,
        dataType: 'json',
        success: function (response) {
            $('#wraper_ajax').remove();

            jQuery('body').addClass('modal-open-super');
            jQuery('#modal-compact-view').modal('show', { backdrop: 'static' });
            jQuery('#modal-compact-view .modal-body').html(response.data);
        }
    });


});


$('.nrocuota').click(function () {

    valor = parseFloat($('.nrocuota').val());
    if ($(this).is(':checked')) {
        // valor=parseFloat($('#valorcuota').val()); 
        total_cuotas += valor;
    } else {
        // valor=parseFloat($('#valorcuota').val()); 
        total_cuotas -= valor;
    }
    let mpagar = total_cuotas.toLocaleString('es-ES')
    $('#fmpagar').val(mpagar);
    $('#mpagar').val(total_cuotas);

});

document.getElementById('Flow').addEventListener('click', function () {
    vempresaCode = document.getElementById('empresaCode').value;
    var urlf = '/' + empresaCode + 'manager/flowpagos/inicioTransaccion';
    // Cambiar la acci贸n del formulario al endpoint de Flow
    document.getElementById('pagosweb').action = urlf
});

document.getElementById('TransBank').addEventListener('click', function () {
    empresaCode = document.getElementById('empresaCode').value;
    var urlt = '/' + empresaCode + '/namager/trbnkpagos/inicioTransaccion';
    // Cambiar la acci贸n del formulario al endpoint de Trbnk
    document.getElementById('pagosweb').action = urlt
});

document.getElementById('MercadoPago').addEventListener('click', function () {
    empresaCode = document.getElementById('empresaCode').value;
    var urlt = '' + empresaCode + '/manager/mercadopago/inicioTransaccion';
    // Cambiar la acci贸n del formulario al endpoint de Trbnk
    document.getElementById('pagosweb').action = urlt
});

