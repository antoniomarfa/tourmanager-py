function formatoRut(rut,label)

{
    var sRut1 = rut;      
    var nPos = 0;
    var sInvertido = ""; 
    var sRut = "";
    for(var i = sRut1.length - 1; i >= 0; i-- )
    {
        sInvertido += sRut1.charAt(i);
        if (i == sRut1.length - 1 )
            sInvertido += "-";
        else if (nPos == 3)
        {
            sInvertido += ".";
            nPos = 0;
        }
        nPos++;
    }

    for(var j = sInvertido.length - 1; j >= 0; j-- )
    {
        if (sInvertido.charAt(sInvertido.length - 1) != ".")
            sRut += sInvertido.charAt(j);
        else if (j != sInvertido.length - 1 )
            sRut += sInvertido.charAt(j);
    }

    $("input#"+label).val(sRut.toUpperCase());
}

function validaRut(campo,label){
	
	if ( campo.length == 0 ){ return false; }
	if ( campo.length < 8 ){ return false; }
	 
	campo = campo.replace('-','')
	campo = campo.replace(/\./g,'')

	
	var suma = 0;
	var caracteres = "1234567890kK";
	var contador = 0;
	for (var i=0; i < campo.length; i++){
	u = campo.substring(i, i + 1);
	if (caracteres.indexOf(u) != -1)
	contador ++;
	}

	if ( contador==0 ) { return false }
	var rut = campo.substring(0,campo.length-1)
	var drut = campo.substring( campo.length-1 )
	var dvr = '0';
	var mul = 2;
	for (i= rut.length -1 ; i >= 0; i--) {
	suma = suma + rut.charAt(i) * mul
	if (mul == 7) mul = 2
	else	mul++
	}
	res = suma % 11
	if (res==1)	dvr = 'k'
	else if (res==0) dvr = '0'
	else {
	dvi = 11-res
	dvr = dvi + ""
	}

	if ( dvr != drut.toLowerCase() ) { return false; }
	else { 
		formatoRut(campo,label);
		return true; 
	}

}

function esEntero(numero){
	if (isNaN(numero)){
		return false;
	} else {
		if (numero % 1 == 0) {
			return true;
		} else {
			return true;
		}
	}
}

function reemplazar(texto, buscar, nuevo)
{
	var temp = '';
	var long = texto.length;
	for (j=0; j<long; j++) {
		if (texto[j] == buscar)
		{
			temp += nuevo;
		} else
			temp += texto[j];
	}
	return temp;
}

function formato_numero(numero, decimales, separador_decimal, separador_miles)
{
	numero=parseFloat(numero);
	if(isNaN(numero)){
		return "";
	}

	if(decimales!==undefined){
		// Redondeamos
		numero=numero.toFixed(decimales);
	}

	// Convertimos el punto en separador_decimal
	numero=numero.toString().replace(".", separador_decimal!==undefined ? separador_decimal : ",");

	if(separador_miles){
		// Añadimos los separadores de miles
		var miles=new RegExp("(-?[0-9]+)([0-9]{3})");
		while(miles.test(numero)) {
			numero=numero.replace(miles, "$1" + separador_miles + "$2");
		}
	}
	return numero;
}

var formatNumber = {
	separador: ".", // separador para los miles
	sepDecimal: ',', // separador para los decimales
	formatear:function (num){
		num +='';
		var splitStr = num.split('.');
		var splitLeft = splitStr[0];
		var splitRight = splitStr.length > 1 ? this.sepDecimal + splitStr[1] : '';
		var regx = /(\d+)(\d{3})/;
		while (regx.test(splitLeft)) {
			splitLeft = splitLeft.replace(regx, '$1' + this.separador + '$2');
		}
		return this.simbol + splitLeft +splitRight;
	},
	new:function(num, simbol){
		this.simbol = simbol ||'';
		return this.formatear(num);
	}
}

/*
jQuery(document).on("click", ".sidebar-collapse", function() {

	if ($('.sidebar-collapsedx').hasClass('sidebar-collapsed')){
		sidebar_collapsed = 1;
	} else {
		sidebar_collapsed = 0;
	}

	var data = {
		sidebar_collapsed: sidebar_collapsed
	}

	$.ajax({
		type: "POST",
		encoding:"UTF-8",
		url: _base_url_ + _url_friendly_base_ + 'index/sidebar',
		data: data,
		dataType:'json',
		success: function(response){
		}
	});
});

jQuery(document).on("keydown", "#cantidad-agregar, .cantidad-agregar", function(event) {

	if(event.shiftKey){
		event.preventDefault();
	}

	if (event.keyCode == 46 || event.keyCode == 8){

	} else {
		if (event.keyCode < 95) {
			if (event.keyCode < 48 || event.keyCode > 57) {
				event.preventDefault();
			}
		} else {
			if (event.keyCode < 96 || event.keyCode > 105) {
				event.preventDefault();
			}
		}
	}
});
*/
//var contenido_loader = '<div id="wraper_ajax"><div class="loadding_ajaxcart"><img src="public/themes/neon/images/loader.gif"></div></div>';