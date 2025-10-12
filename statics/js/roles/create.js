jQuery( document ).ready( function( $ ) {
    $.validator.addMethod("validateRolUnicoTributario", function(value, element) {
        var label = element.id;
        return this.optional(element) || validaRut(value, label);
    }, "El RUT ingresado es inválido");
    $.validator.addClassRules({
        rut : { validateRolUnicoTributario : true }
    });

    $('#form').validate({
        ignore: [],
        errorElement: 'span',
        errorClass: 'validate-has-error',
        rules: {
            description: { required: true, minlength: 6 },
        },
        messages: {
            description: { required: "Ingrese descripcion", minlength: "Mínimo 6 caracteres" },
        },
        highlight: function (element) {
            $(element).closest('.form-group').addClass('validate-has-error');
            $(element).addClass('error');
        },
        unhighlight: function (element) {
            $(element).closest('.form-group').removeClass('validate-has-error');
            $(element).removeClass('error');
        },
        errorPlacement: function (error, element) {
            error.insertAfter(element);
        }
    });  
});