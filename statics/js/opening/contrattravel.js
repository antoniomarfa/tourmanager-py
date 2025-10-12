jQuery( document ).ready( function( $ ) {
/*
    $('#acepto').click(function(){

        if($(this).attr('checked') == false){
             $('.descargar-contrato').attr("disabled","disabled");   
        }else{
            $('.descargar-contrato').removeAttr('disabled');
        }    
    });
*/
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