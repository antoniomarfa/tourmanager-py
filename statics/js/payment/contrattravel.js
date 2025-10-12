jQuery( document ).ready( function( $ ) {
    var sig = $('#sig').signature({ syncField: '#signature64', syncFormat: 'PNG' });

	$('#clear').click(function() {
		sig.signature('clear');
	});
	
    $('#acepto').click(function() {
        if ($(this).is(':checked')) {
            $('.descargar-contrato').removeAttr('disabled');
            $('#sig').show();
            $('#clear').show();
            $('#linea').show();
        } else {
            $('.descargar-contrato').attr('disabled', 'disabled');
            $('#sig').hide();
            $('#clear').hide();
            $('#linea').hide();
        }
    });    
})