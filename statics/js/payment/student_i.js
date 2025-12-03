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
        errorElement: 'span',
        errorClass: 'validate-has-error',
        rules: {
            correo: { email:true },
            fono:{ phoneWithCode:true },
            celular:{ phoneWithCode:true },
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
                $('.nav-tabs a small.required').remove();
                var validatePane = $('.tab-content.tab-validate .tab-pane:has(input.error), .tab-content.tab-validate .tab-pane:has(select.error)').each(function() {
                    var id = $(this).attr('id');
                    $('.nav-tabs').find('a[href^="#' + id + '"]').append(' <small class="required">***</small>');
                    console.log(id);

                    $('.nav-tabs li').removeClass('active');
                    $('.tab-content div').removeClass('active');

                    $('.nav-tabs').find('a[href^="#' + id + '"]').parent().addClass('active');
                    $('.tab-content div#' + id + '').addClass('active');
                });
            });
        },
    });

    $("#venta_id").select2();
    $("#region_id").select2();
    $("#commune_id").select2(); 

    $('#region_id').change(function(){
     
        var region = $(this).val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/payment/getComune';
        var data = {
          region_id : region
          }
  
          $.ajax({
              type: "POST",
              encoding: "UTF-8",
              url: Url,
              data: data,
              dataType: 'json',
              success: function(response){
                //  $('#bodega').find('option').not('first').remove();
                  $('#commune_id option:not(:first)').remove();
  
                  $.each(response, function(index,data){
                      $('#commune_id').append('<option value="'+data['id']+'">'+data['description']+'</option>')
                  })
              }
          })
  
     });    

     $('#venta_id').change(function(){
     
        var venta = $(this).val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/payment/getVenta';
        var data = {
          venta_id : venta
          }
  
          $.ajax({
              type: "POST",
              encoding: "UTF-8",
              url: Url,
              data: data,
              dataType: 'json',
              success: function(response){
                $('#apagar').val(response.subtotal);
                $('#descto').val(response.descuento);
                $('#a_pagar').val(response.valor);

              }
          })
  
     });    
});
