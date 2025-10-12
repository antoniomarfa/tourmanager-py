jQuery( document ).ready( function( $ ) {
    $.validator.addMethod("validateRolUnicoTributario", function(value, element) {
        var label = element.id;
        return this.optional(element) || validaRut(value, label);
    }, "El RUT ingresado es inválido");
    $.validator.addClassRules({
        rut : { validateRolUnicoTributario : true }
    });

    $('#form1').validate({
        errorElement: 'span',
        errorClass: 'validate-has-error',
        rules: {
     //       tipocambio:{number}
        },        
        highlight: function (element) {
            $(element).closest('.form-group').addClass('validate-has-error');
            $(element).addClass('error');
        },
        unhighlight: function (element) {
            $(element).closest('.form-group').removeClass('validate-has-error');
            $(element).removeClass('error');
        },
        errorPlacement: function (error, element)
        {
            if(element.closest('.has-switch').length)
            {
                error.insertAfter(element.closest('.has-switch'));
            }
            else
            if(element.parent('.checkbox, .radio').length || element.parent('.input-group').length)
            {
                error.insertAfter(element.parent());
            }
            else
            {
                error.insertAfter(element);
            }
        },
        ignore: [],
        invalidHandler: function() {
            setTimeout(function() {
            });
        },
    });
    
    $('#vdescuento').change(function(){
        var vtotalprog=0; 
        vdesc =  $(this).val();
        vprograma = $('#vprograma').val();
        vtotalprog=vprograma-vdesc;
        $('#vtotalprog').val(vtotalprog);    
     });
 
    $('#nroalumno').change(function(){
        var _valorPrograma=0;
        var program = $('#sel_programa').val();
        var nroalumno =$('#nroalumno').val();
        var tcambio = (isNaN($('#tipocambio').val())===false ) ? 0  : $('#tipocambio').val(); 
        tcambio= $('#tipocambio').val() == '' ? 1 : $('#tipocambio').val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/sale/getProgramValue';
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

    $('#sel_programa').change(function(){
     
        var _valorPrograma=0;
        var program = $(this).val();
        var nroalumno =$('#nroalumno').val();
        var tcambio = (isNaN($('#tipocambio').val())===false ) ? 0  : $('#tipocambio').val(); 
        tcambio= $('#tipocambio').val() == '' ? 1 : $('#tipocambio').val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/sale/getProgramValue';
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
  
     $('#sel_client').select2();
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