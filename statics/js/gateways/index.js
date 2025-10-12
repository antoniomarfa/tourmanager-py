jQuery.noConflict();
document.addEventListener('DOMContentLoaded', function () {
  $('#Modaldato').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Bot贸n que activ贸 el modal
    var gatewayId = button.data('gateway-id');
    var gatewayType = button.data('gateway-type');
    // Asigna valores a elementos del modal
    $('#Modaldato input[name="gateway_id"]').val(gatewayId);
    $('#Modaldato .modal-title').text('Integrar con ' + gatewayType);
    
    // Mostrar u ocultar el panel seg煤n el ID
    //  $('.panel-flow, .panel-trbk, .panel-mp').addClass('d-none');

      switch (gatewayId.toString()) {
         case "3": $('.panel-flow').removeClass('d-none'); break;
         case "2": $('.panel-trbk').removeClass('d-none'); break;
         case "1": $('.panel-mp').removeClass('d-none'); break;
      }

  });
});


jQuery(document).on("click", ".delete-register", function(e) {
    e.preventDefault(); // Evita que el link navegue a "#"
    var id = jQuery(this).attr('data-id');
    var empresa = "{{ empresa }}";
    let baseUrl = "/" + empresa + "/manager/gateways/delete/";

    let url = `${baseUrl}${id}`;

        Swal.fire({
        title: "Eliminar Registro",
        text: "¿Está seguro que desea quitar la integracion seleccionada?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#43c613ff",
        cancelButtonColor: "#d33",
        confirmButtonText: "Si",
        cancelButtonText: "No"
        }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = url;        
        }
        });
});