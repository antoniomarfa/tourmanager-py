jQuery(document).ready(function ($) {
    var paso = $('#paso').val();

    const mensajes = {
        "1": { text: "Ok Ingresaste el alumno ahora continua con el paso 2 Contrato.", icon: "success" },
        "2": { text: "Contrato Firmado Bienvenido a la Familia\nFavor avanzar con el paso 3 pago reserva", icon: "success" },
        "3": { text: "Hemos enviado un correo a la dirección ingresada en alumnos indicando su usuario y clave del Panel de Apoderados.", icon: "success" },
        "4": { text: "Nro de ingreso ya existe en nuestros registros, favor verifique y vuelva a ingresar el pago.", icon: "warning" },
        "5": { text: "Nro de ingreso no existe en nuestros registros o está cobrado, favor verifique y vuelva a ingresar el pago.", icon: "warning" }
    };

    if (mensajes[paso]) {
        Swal.fire({
            title: "",
            text: mensajes[paso].text,
            icon: mensajes[paso].icon
        });
    }

});