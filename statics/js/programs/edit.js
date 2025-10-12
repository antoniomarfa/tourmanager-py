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

jQuery(document).on('click', '.insert-dynamic', function() {
    $('.dynamic-element:eq(0) .matriz-content:eq(1)').clone().insertAfter($(this).closest('.matriz-content')).show();
    $(this).closest('.panel-primary').find('.matriz-content').removeClass('hidden');
});

jQuery(document).on('click', '.delete-dynamic', function() {
    var number = $(this).closest('.panel-primary').find('.matriz-content').length;
    if(number > 2) {
        $(this).closest('.matriz-content').remove();
    }
});

    $('#origin').change(function(){
     
        var origin = $(this).val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/program/getOrigin';
        var data = {
          origin_id : origin
          }
  
          $.ajax({
              type: "POST",
              encoding: "UTF-8",
              url: Url,
              data: data,
              dataType: 'json',
              success: function(response){
                //  $('#bodega').find('option').not('first').remove();
                  $('#origincode option:not(:first)').remove();
  
                  $.each(response.data, function(index,data){
                      $('#origincode').append('<option value="'+data.iata+'">'+data.name+'</option>')
                  })
              }
          })
  
     });
     
    $('#destination').change(function(){
     
        var destination = $(this).val();
        var empresa = "{{ empresa }}";
        var Url = '/' + empresa + '/manager/program/destination';
        var data = {
          destination_id : destination
          }
  
          $.ajax({
              type: "POST",
              encoding: "UTF-8",
              url: Url,
              data: data,
              dataType: 'json',
              success: function(response){
                //  $('#bodega').find('option').not('first').remove();
                  $('#destinationcode option:not(:first)').remove();
  
                  $.each(response.data, function(index,data){
                      $('#destinationcode').append('<option value="'+data.iata+'">'+data.name+'</option>')
                  })
              }
          })
  
     });  