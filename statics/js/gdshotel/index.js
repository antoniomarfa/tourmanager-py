jQuery( document ).ready( function( $ ) {  
    $('#execute_search').click(function(e){
       e.preventDefault()

        var empresa = "{{ empresa }}";
        let Url = "/" + empresa + "/manager/gdshotel/getOffers/";
         
        var origen_code =  $('#form_hotel select[name="origin"]').val();
        var adultos = $('#form_hotel select[name="adultos"]').val(); 
        var habitaciones = $('#form_hotel select[name="habitaciones"]').val(); 
        var start_date = $('#start_date').val(); 
        var sale = $('#form_hotel select[name="ventas"]').val();   
        var data = {
          origen_code : origen_code,    
          adultos : adultos,
          habitaciones : habitaciones,
          start_date : start_date,
          sale:sale
          }

           // Mostrar spinner
          $('#loading-overlay').removeClass('d-none');

          $.ajax({
              type: "POST",
              encoding: "UTF-8",
              url: Url,
              data: data,
              dataType: 'json',
              error: function(jqXHR, textStatus, errorThrown) {
                $('#loading-overlay').addClass('d-none');
                try {
                      const data = JSON.parse(jqXHR.responseText);
                      if (data.errors && data.errors[0].detail) {
                          bootbox.alert({
                              message: 'Error: ' + data.errors[0].detail,
                              size: 'small'
                          });
                      } else {
                          bootbox.alert({
                              message: 'Error desconocido',
                              size: 'small'
                          });
                      }
                  } catch(e) {
                      console.error('Error al parsear respuesta:', e);
                      console.error('Respuesta cruda:', jqXHR.responseText);
                  }                
              },
             success: function(response) 
             {
               $('#loading-overlay').addClass('d-none');

                if(response.error===0){
                    document.getElementById("result").innerHTML = response.cuerpo;
                }
                if(response.error===1){
                    bootbox.alert({
                        message: 'Error : '+response.cuerpo,
                        size: 'small' /* or 'sm' */
                    });                  
                }
             }
          })
  
         
         
     });
     
     $('#origin').select2();
 });     