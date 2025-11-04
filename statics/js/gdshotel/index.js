     $('#execute_search').click(function(){
        var empresa = "{{ empresa }}";
        let Url = "/" + empresa + "/manager/gdhotel/getOffers/";
         
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
  
          $.ajax({
              type: "POST",
              encoding: "UTF-8",
              url: Url,
              data: data,
              dataType: 'json',
              error: function(jqXHR, textStatus, errorThrown) {
                console.error('Error en consulta:');
                console.error('Estado:', textStatus);
                console.error('Error lanzado:', errorThrown);
                console.error('Respuesta del servidor:', jqXHR.responseText);
              },
             success: function(response) {
                if(response.error===0){
                    document.getElementById("result").innerHTML = response.cuerpo;
                }
             }
          })
  
         
         
     });
     
     $('#origin').select2();