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
            codigo: { required: true, minlength: 6 },
            nombre: { required: true},
            direccion: { required: true},
            commune_id: { required: true},
            region_id: { required: true}
        },
        messages: {
            codigo: { required: "Ingrese Codigo", minlength: "Mínimo 6 caracteres" },
            nombre: { required: "Ingrese nombre Colegio" },
            direccion: { required: "Ingrese direccion" },
            commune_id: { required: "Ingrese comuna" },
            region_id: { required: "Ingrese region" }
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

jQuery(document).on("change", "#region_id", function() {
    var $element = jQuery(this);
    var region = $element.val();
    var empresa = "{{ empresa }}";
    var Url = '/' + empresa + '/manager/schools/getcomune';
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

            $('#commune_id option:not(:first)').remove(); 
            $.each(response.data, function(index,data){
                $('#commune_id').append('<option value="'+data.id+'">'+data.description+'</option>')
             })
        }
    })
})    