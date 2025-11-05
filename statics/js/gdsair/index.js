jQuery( document ).ready( function( $ ) {

    $('#origin').select2();
    $('#destination').select2();
    $('#origincode').select2();
    $('#destinationcode').select2();

    
    $('#origin').change(function(){
     
        var origin = $(this).val();
        var empresa = "{{ empresa }}";
        let Url = "/" + empresa + "/manager/gdsair/getOrigin/";

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
  
                  $.each(response, function(index,data){
                      $('#origincode').append('<option value="'+data['iata']+'">'+data['name']+'</option>')
                  })
              }
          })
  
     });
     
    $('#destination').change(function(){
     
        var destination = $(this).val();
  
        var empresa = "{{ empresa }}";
        let Url = "/" + empresa + "/manager/gdsair/getDestination/";
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
  
                  $.each(response, function(index,data){
                      $('#destinationcode').append('<option value="'+data['iata']+'">'+data['name']+'</option>')
                  })
              }
          })
  
     });    
     
     $('#execute_search').click(function(e){
        e.preventDefault();

        var empresa = "{{ empresa }}";
        let Url = "/" + empresa + "/manager/gdsair/getflights/";
         
        var origincode = $('#form_air').find('select[name="origincode"]').find(':selected').val(); 
        var destinationcode = $('#form_air').find('select[name="destinationcode"]').find(':selected').val(); 
        var origin = $('#form_air').find('select[name="origin"]').find(':selected').val(); 
        var destination = $('#form_air').find('select[name="destination"]').find(':selected').val(); 
        var sale = $('#form_air').find('select[name="ventas"]').find(':selected').val();   
        var cnt_offers = $('#form_air').find('select[name="cnt_offers"]').find(':selected').val();
        var start_date =$('#start_date').val();
        var data = {
          origincode: origincode,
          destinationcode:destinationcode,
          origin : origin,    
          destination : destination,
          sale:sale,
          cnt_offers:cnt_offers,
          start_date:start_date
          }

          // Mostrar spinner
          $('#loading-overlay').removeClass('d-none');

          $.ajax({
              type: "POST",
              encoding: "UTF-8",
              url: Url,
              data: data,
              dataType: 'json',
              error: function() {
                console.log('error en consulta');
                $('#loading-overlay').addClass('d-none');
            },
             success: function(response) {
                $('#loading-overlay').addClass('d-none');
                if(response.error == 0){
                    $('#result').html(response.cuerpo);
                }
             }
          })
  
         
         
     })
});    
