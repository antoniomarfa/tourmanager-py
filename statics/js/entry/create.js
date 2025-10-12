jQuery( document ).ready( function( $ ) {
    $.validator.addMethod("validateRolUnicoTributario", function(value, element) {
        var label = element.id;
        return this.optional(element) || validaRut(value, label);
    }, "El RUT ingresado es inválido");
    $.validator.addClassRules({
        rut : { validateRolUnicoTributario : true }
    });

    jQuery.validator.addMethod("notOnlyZero", function(value, element) {
        if (value.trim() === "") return true; // si está vacío, lo maneja require_from_group
        return parseFloat(value) > 0;
    }, "El valor no puede ser 0");

    $('#form').validate({
        rules: {
                voucher: {
                    require_from_group: [1, ".grupo-obligatorio"],
                    notOnlyZero: true
                },
                apagar: {
                    require_from_group: [1, ".grupo-obligatorio"],
                    notOnlyZero: true
                }
            },
            messages: {
                voucher: {
                    require_from_group: "Debe ingresar al menos Nro Voucher o Valor",
                    notOnlyZero: "El valor no puede ser 0"
                },
                apagar: {
                    require_from_group: "Debe ingresar al menos Nro Voucher o Valor",
                    notOnlyZero: "El valor no puede ser 0"
                }
        },
        errorElement: 'span',
        errorClass: 'validate-has-error',
        rules: {
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

    $('#rutalumno').focusout(function(){
        
        var rut = $(this).val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/entry/getporcurso';
        var data = {
        rut_al : rut,
        rut_ap : ''
        }

        $.ajax({
            type: "POST",
            encoding: "UTF-8",
            url: Url,
            data: data,
            dataType: 'json',
            success: function(response){
               $("#nroventa").val(response.venta);
               $("#nombrealumno").val(response.nombreal);
               $("#rutapoderado").val(response.rutapo);
               $("#nombreapoderado").val(response.nombreapo);
               $("#vviaje").val(response.monto);
               $('#vsaldo').val(response.saldo);
               $('#apagar').val(0);
               $('#curso_id').val(response.curso_id);
            }
        })

    });

    $('#rutapoderado').focusout(function(){
        
        var rut = $(this).val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/entry/getporcurso';
        var data = {
        rut_ap : rut,
        rut_al : ''
        }

        $.ajax({
            type: "POST",
            encoding: "UTF-8",
            url: Url,
            data: data,
            dataType: 'json',
            success: function(response){
               $("#nroventa").val(response.venta);
               $("#rutalumno").val(response.rutal);
               $("#nombrealumno").val(response.nombreal);
               $("#nombreapoderado").val(response.nombreapo);
               $("#vviaje").val(response.monto);
               $('#vsaldo').val(response.saldo);
               $('#apagar').val(0);
               $('#curso_id').val(response.curso_id);
            }
        })

    });    

    $('#apagar').change(function(){
        /*
        var apagar = $(this).val();
        var saldo =$('#vsaldo').val();
        saldo= saldo.replace(".", "");

        $('#apagar').val(apagar);
        if (apagar==0){
            $('#apagar').val(saldo);
        }
        if (apagar>=saldo){
            $('#apagar').val(saldo);
        }
        */
    })

    $('#voucher').focusout(function(){
    
        var tipo= $('[name=fpago]').find(':selected').val();
        var voucher = $(this).val();

        if (tipo=='VO'){
            var empresa = "{{ empresa }}";
            var Url = '/' + empresa + '/manager/entry/getvoucher';
            var data = {
            voucher : voucher,
            venta : $("#nroventa").val()
            }
    
            $.ajax({
                type: "POST",
                encoding: "UTF-8",
                url: Url,
                data: data,
                dataType: 'json',
                success: function(response){
                    if (response.error=1){
                        bootbox.confirm({
                            message: response.message,
                            closeButton: false,
                            buttons: {
                                cancel: { label: 'NO', className: 'hidden' },
                                confirm: { label: 'ACEPTAR', className: 'btn-danger' },
                            },
                            callback: function (result){}
                        });
                    }
                }
            })
    
        }

    })
});    