var jq = jQuery.noConflict();
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
 })
 
jQuery(document).on("change", "#region_id", function() {
    var $element = jQuery(this);
    var region = $element.val();

    var empresa = "{{ empresa }}";
    var Url = '/' + empresa + '/manager/company/getcomune';
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


 jQuery(document).on("click", ".change-plan-2", function() {
    var plan=2
    var $element = jQuery(this);
    var company_id = $element.attr('id');       
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager/company/upgrade';
    var data = {
        module_name: module_name,
        company_id: company_id,
        plan: plan
    }

    jQuery.ajax({
        type: "POST",
        encoding:"UTF-8",
        url: url,
        data: data,
        dataType:'json',
        success: function(response){
            if(response.status == 1){
                window.location.href ='/' + empresa + 'manager/company/edit/' + company_id
            }
        }
    });
});

 jQuery(document).on("click", ".change-plan-3", function() {

    var plan=3
    var $element = jQuery(this);
    var company_id = $element.attr('id');
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager/company/upgrade';
    var data = {
        module_name: module_name,
        company_id: company_id,
        plan: plan
    }

    jQuery.ajax({
        type: "POST",
        encoding:"UTF-8",
        url: url,
        data: data,
        dataType:'json',
        success: function(response){
            if(response.status == 1){
                window.location.href ='/' + empresa + 'manager/company/edit/' + company_id
            }
        }
    });
});

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
