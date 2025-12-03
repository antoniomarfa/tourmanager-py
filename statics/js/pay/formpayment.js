jQuery(document).on('click', '.show-compact-entry', function () {
    var url = '/' + empresaCode + '/manager/getEntries';
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

document.getElementById('mpagar').addEventListener('blur', function () {
    if (document.getElementById('mpagar').value > document.getElementById('sfapagar').value) {
        Swal.fire("Monto no puede ser mayor al saldo pendiente");
    }
})


document.getElementById('Flow').addEventListener('click', function () {
    empresaCode = document.getElementById('empresaCode').value;
    var urlf = '/' + empresaCode + '/manager/flowpagos/inicioTransaccion';
    // Cambiar la acción del formulario al endpoint de Flow
    document.getElementById('pagosweb').action = urlf
});

document.getElementById('TransBank').addEventListener('click', function () {
    empresaCode = document.getElementById('empresaCode').value;
    var urlt = '/' + empresaCode + '/manager/trbnkpagos/inicioTransaccion';
    // Cambiar la acción del formulario al endpoint de Trbnk
    document.getElementById('pagosweb').action = urlt
});

document.getElementById('MercadoPago').addEventListener('click', function () {
    empresaCode = document.getElementById('empresaCode').value;
    var urlt = '/' + empresaCode + '/manager/mercadopago/inicioTransaccion';
    // Cambiar la acción del formulario al endpoint de Trbnk
    document.getElementById('pagosweb').action = urlt
});
function valideKey(evt) {
    var c = (evt.which) ? evt.which : evt.keyCode;
    var rgx = /^[0-9]*\.?[0-9]*$/;
    key = String.fromCharCode(c);
    chars = "0123456789.";
    if (key.match(rgx)) {
        return true;
    } else {
        return false;
    }
}

function FunctioonlyNum(evt) {
    var c = (evt.which) ? evt.which : evt.keyCode;
    var rgx = /^[0-9]*$/;
    key = String.fromCharCode(c);
    chars = "0123456789";
    if (key.match(rgx)) {
        return true;
    } else {
        return false;
    }
}