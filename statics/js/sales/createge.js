
jQuery( document ).ready( function( $ ) {     
    $.validator.addMethod("validateRolUnicoTributario", function(value, element) {
        var label = element.id;
        return this.optional(element) || validaRut(value, label); // asegúrate de que validaRut esté definida
    }, "El RUT ingresado es inválido");

    // Reglas de clase para inputs con class="rut"
    $.validator.addClassRules({
        rut: { validateRolUnicoTributario: true }
    });

    // Inicialización del validador
    $('#form').validate({
        errorElement: 'span',
        errorClass: 'validate-has-error',
        highlight: function(element) {
            $(element).closest('.form-group').addClass('validate-has-error');
            $(element).addClass('error');
        },
        unhighlight: function(element) {
            $(element).closest('.form-group').removeClass('validate-has-error');
            $(element).removeClass('error');
        },
        errorPlacement: function(error, element) {
            if (element.closest('.has-switch').length) {
                error.insertAfter(element.closest('.has-switch'));
            }
            else if (element.parent('.checkbox, .radio').length || element.parent('.input-group').length) {
                error.insertAfter(element.parent());
            }
            else {
                error.insertAfter(element);
            }
        },
        ignore: [],
        invalidHandler: function() {
            setTimeout(function() {
                // lógica en caso de error global
            });
        } // 
    });
});

    $('#sel_cotizacion').select2();
    $('#sel_vendedor').select2();
    $('#sel_colegio').select2();
    $('#sel_programa').select2();
    $('#status').select2();

    $('#vdescuento').change(function(){
       var vtotalprog=0; 
       vdesc =  $(this).val();
       vprograma = $('#vprograma').val();
       vtotalprog=vprograma-vdesc;
       $('#vtotalprog').val(vtotalprog);    
    });

    $('#nroalumno').change(function(){
        var _valorPrograma=0;
        var program = isNaN($('#sel_programa').val()) ? 0 : $('#sel_programa').val();
        var nroalumno =$('#nroalumno').val();
        var tcambio = isNaN($('#tipocambio').val()) ? 0  : $('#tipocambio').val(); 
        tcambio= $('#tipocambio').val() == '' ? 1 : $('#tipocambio').val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/sales/getprogramvalue';
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
  


    $('#sel_programa').change(function(){
     
        var _valorPrograma=0;
        var program = $(this).val();
        var nroalumno =$('#nroalumno').val();
        var tcambio = (isNaN($('#tipocambio').val())===false ) ? 0  : $('#tipocambio').val(); 
        tcambio= $('#tipocambio').val() == '' ? 1 : $('#tipocambio').val();

        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/sales/getprogramvalue';
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
  
     });
  

});

jQuery(document).on("change", "#sel_cotizacion", function() {     
        var cotizacion = $(this).val();
        var typesale =$('#typesale').val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/sales/getquote';
        var data = {
            cotizacion : cotizacion,
            typesale : typesale
          }
  
          $.ajax({
              type: "POST",
              encoding: "UTF-8",
              url: Url,
              data: data,
              dataType: 'json',
              success: function(response){
                 $('#sel_vendedor').val(response.seller_id).trigger('change');
                 $('#sel_colegio').val(response.establecimiento_id).trigger('change');;
                 $('#tipocambio').val(response.tipocambio);
                 $('#curso').val(response.curso);
                 $('#idcurso').val(response.idcurso);
                 $('#nroalumno').val(response.pasajeros);
                 $('#sel_programa').val(response.programa_id).trigger('change');;
                 $('#vtotalprog').val(response.vprograma);
                 $('#vdescuento').val(response.desc);
                 $('#vprograma').val(response.subtotal);
                 $('#liberado').val(response.liberados);
              }
          })
  
     });

jQuery(document).on("click", ".btn-generaCodigo", function() {
        var empresa = "{{ empresa }}";
        var url = '/' + empresa + '/manager/sales/accesscode';
        var data = {
            url : url
        }
    
        $.ajax({
            type: "POST",
            encoding: "UTF-8",
            url: url,
            data: data,
            dataType: 'json',
            success:function(response){
                if(response.error == 0){
                    $('#accesscode').val(response.codigo);
                } else {
                    bootbox.confirm(configErrorGeneralBootbox);
                }
            },
            error: function() {
                bootbox.confirm(configErrorGeneralBootbox);
            }
        });
});

//java script valida solo numeros y numeros + puntos
function valideKey(evt){
    var c =(evt.which) ? evt.which : evt.keyCode;
    var rgx = /^[0-9]*\.?[0-9]*$/;
    key = String.fromCharCode(c);
    chars = "0123456789.";
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