jQuery( document ).ready( function( $ ) {
    $.validator.addMethod("validateRolUnicoTributario", function(value, element) {
        var label = element.id;
        return this.optional(element) || validaRut(value, label);
    }, "El RUT ingresado es inválido");
    $.validator.addClassRules({
        rut : { validateRolUnicoTributario : true }
    });

    $.validator.addMethod('phoneWithCode', function(value, element) {
        var validator = this;
        var phone = value;
        var rule_phone = /^\+([0-9]{11})$/;

        if(phone.length == 0){
            return true;
        } else {
            if (phone.match(rule_phone)) {
                return true;
            } else {
                $.validator.messages.phone = "Debes ingresar un número de teléfono válido. Ej: +56961234567";
                return false;
            }
        }

    }, 'Debes ingresar un número de teléfono válido. Ej: +56961234567');

    $('#form').validate({
        rules: {
            contactofono:{ phoneWithCode:true },
        },         
        errorElement: 'span',
        errorClass: 'validate-has-error',
        highlight: function (element) {
            $(element).closest('.form-group').addClass('validate-has-error');
            $(element).addClass('error');
        },
        unhighlight: function (element) {
            $(element).closest('.form-group').removeClass('validate-has-error');
            $(element).removeClass('error');
        },
        errorPlacement: function (error, element) {
            if (element.closest('.has-switch').length) {
                error.insertAfter(element.closest('.has-switch'));
            } else if (element.parent('.checkbox, .radio').length || element.parent('.input-group').length) {
                error.insertAfter(element.parent());
            } else {
                error.insertAfter(element);
            }
        },
        ignore: [],
            invalidHandler: function() {
                setTimeout(function() {
                });
            },
    });



});

$(document).ready(function() {
    $('#sel_vendedor').select2();
    $('#sel_programa').select2();
    $('#sel_colegio').select2();

    $('#quote_date').datepicker({
        format: "dd/mm/yyyy",
        language: "es",
        minDate: 0,
        autoclose: true,
        todayHighlight: true
    });
});

jQuery(document).on("change", "#nroalumno", function() {
    var _valorPrograma=0;
    var program = (isNaN($('#sel_programa').val())===false ) ? 0  : $('#sel_programa').val() 
    var nroalumno =$('#nroalumno').val();
    var tcambio = (isNaN($('#tipocambio').val())===false ) ? 0  : $('#tipocambio').val(); 
    tcambio= $('#tipocambio').val() == '' ? 1 : $('#tipocambio').val();
    var empresa = "{{ empresa }}";
    var Url = '/' + empresa + '/manager/quotes/getprogramvalue';
    var data = {
        program_id : program,
        nroalumno : nroalumno
    }

    $.ajax({
        type: "POST",
        encoding: "UTF-8",
        url: Url,
        data: data,
        dataType: 'json',
        success: function(response){
            _valorPrograma=Math.ceil(response.programval*tcambio);

                  $('#vprograma').val(_valorPrograma);
                  $('#vtotalprog').val(_valorPrograma);
                  $('#liberado').val(response.liberados)
              }
          })
    })

    jQuery(document).on("change", "#sel_programa", function() {
    var _valorPrograma=0;
    var program = $('#sel_programa').val();
    var nroalumno =$('#nroalumno').val();
    var tcambio = (isNaN($('#tipocambio').val())===false ) ? 0  : $('#tipocambio').val(); 
    tcambio= $('#tipocambio').val() == '' ? 1 : $('#tipocambio').val();
    var empresa = "{{ empresa }}";
    var Url = '/' + empresa + '/manager/quotes/getprogramvalue';
    var data = {
        program_id : program,
        nroalumno : nroalumno
    }

    $.ajax({
        type: "POST",
        encoding: "UTF-8",
        url: Url,
        data: data,
        dataType: 'json',
        success: function(response){
            _valorPrograma=Math.ceil(response.programval*tcambio);

            $('#vprograma').val(_valorPrograma);
            $('#vtotalprog').val(_valorPrograma);
            $('#liberado').val(response.liberados)
        }
    })
})

    jQuery(document).on("change", "#vdescuento", function() {
       var vtotalprog=0; 
       vdesc =  $(this).val();
       vprograma = $('#vprograma').val();
       vtotalprog=vprograma-vdesc;
       $('#vtotalprog').val(vtotalprog);    
    });

     //java script valida solo numeros y numeros + puntos
     function valideKey(evt){
        var c =(evt.which) ? evt.which : evt.keyCode;
        var rgx = /^[0-9]*\.?[0-9]*$/;
        key = String.fromCharCode(c);
        chars = "0123456789";
        if (key.match(rgx)){
            return true;
        }else{
            return false; 
        }
    }
    
    function FunctioonlyNum(evt) {
        var c =(evt.which) ? evt.which : evt.keyCode;
        var rgx = /^[0-9]*$/;
        key = String.fromCharCode(c);
        chars = "0123456789.";
        if (key.match(rgx)){
            return true;
        }else{
            return false; 
        }
    }