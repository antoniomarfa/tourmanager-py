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
            user: { required: true, minlength: 3 },
            name: { required: true, minlength: 3 },
            email: { required: true, email: true }
           // password: { required: true, minlength: 6 }
        },
        messages: {
            user: { required: "Ingrese usuario", minlength: "Mínimo 3 caracteres" },
            name: { required: "Ingrese nombre usuario", minlength: "Mínimo 3 caracteres" },
            email: { required: "Ingrese correo", email: "Formato inválido" }
           // password: { required: "Ingrese clave" }
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

    $('#perfil').select2();
});