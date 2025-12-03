const language_datatable = {
    "sProcessing": "Procesando...",
    "sLengthMenu": "Mostrar _MENU_ registros",
    "sZeroRecords": "No se encontraron resultados",
    "sEmptyTable": "Ningún dato disponible en esta tabla",
    "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_",
    "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0",
    "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
    "sSearch": "Buscar:",
    "oPaginate": {
        "sFirst": "<<",
        "sLast": ">>",
        "sNext": ">",
        "sPrevious": "<"
    },
};
/*
document.addEventListener("DOMContentLoaded", function() {

    const cardsPerPage = 6; // cantidad de tarjetas por página
    const cards = document.querySelectorAll(".user-card");
    const totalCards = cards.length;
    const totalPages = Math.ceil(totalCards / cardsPerPage);
    const pagination = document.getElementById("pagination");
    let currentPage = 1;

    function showPage(page) {
        currentPage = page;
        const start = (page - 1) * cardsPerPage;
        const end = start + cardsPerPage;
        cards.forEach((card, index) => {
            card.style.display = (index >= start && index < end) ? "block" : "none";
        });
        updatePagination();
    }

    function updatePagination() {
        pagination.innerHTML = "";
        const prevDisabled = currentPage === 1 ? "disabled" : "";
        const nextDisabled = currentPage === totalPages ? "disabled" : "";

        // Botón "Anterior"
        pagination.innerHTML += `
            <li class="page-item ${prevDisabled}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Anterior</a>
            </li>
        `;

        // Números de página
        for (let i = 1; i <= totalPages; i++) {
            const active = i === currentPage ? "active" : "";
            pagination.innerHTML += `
                <li class="page-item ${active}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        // Botón "Siguiente"
        pagination.innerHTML += `
            <li class="page-item ${nextDisabled}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Siguiente</a>
            </li>
        `;

        // Eventos de los botones
        document.querySelectorAll("#pagination a").forEach(link => {
            link.addEventListener("click", (e) => {
                e.preventDefault();
                const page = parseInt(e.target.getAttribute("data-page"));
                if (page >= 1 && page <= totalPages) showPage(page);
            });
        });
    }
    // Mostrar la primera página
    showPage(1);
});
*/

jQuery(document).ready(function ($) {

    $.fn.loadDataTableDocs = function () {
        var empresa = "{{ empresa }}";
        var url = '/' + empresa + '/manager/pasajeros/gettable';
        var data = {
            venta: $('[name=ventas]').find(':selected').val(),
        }
        var $table_fixed = $("#table-course");

        var table_fixed = $table_fixed.DataTable({
            "ajax": {
                "url": url,
                "type": "POST",
                "data": data
            },
            "ordering": false,
            "lengthMenu": [[10, 50, 100, 150, -1], [10, 50, 100, 150, "All"]],
            "pageLength": 50,
            "oLanguage": language_datatable,
            "columnDefs": [
                { targets: 0, className: 'cell-right' },
                { targets: 1, className: 'cell-right' },
                {
                    targets: 2, className: 'cell-left',
                    "render": function (data, type, row, meta) {
                        // Combina las columnas 8, 9 y 10 (recuerda que los índices comienzan en 0)
                        return `${row[2]} <br> ${row[3]}`;
                    }
                },
                {
                    targets: 3, // Especifica las columnas 8, 9 y 10
                    "visible": false  // Esto oculta las columnas 8, 9 y 10 en la tabla
                },
                { targets: 3, className: 'cell-right' },
                {
                    targets: 4, className: 'cell-left',
                    "render": function (data, type, row, meta) {
                        // Combina las columnas 8, 9 y 10 (recuerda que los índices comienzan en 0)
                        return `${row[4]}  <br> ${row[5]}`;
                    }

                },
                {
                    targets: 5, // Especifica las columnas 8, 9 y 10
                    "visible": false  // Esto oculta las columnas 8, 9 y 10 en la tabla
                },
                { targets: 5, className: 'cell-left' },
                {
                    targets: 6, className: 'cell-left',
                    "render": function (data, type, row, meta) {
                        // Combina las columnas 8, 9 y 10 (recuerda que los índices comienzan en 0)
                        return `Fono :${row[6]} <br> Email : ${row[7]}`;
                    }
                },
                {
                    targets: 7, // Especifica las columnas 8, 9 y 10
                    "visible": false  // Esto oculta las columnas 8, 9 y 10 en la tabla
                },
                { targets: 7, className: 'cell-right' },
                {
                    targets: 8, className: 'cell-left', // El target debe ser la columna en la que quieres mostrar el contenido combinado
                    "render": function (data, type, row, meta) {
                        // Combina las columnas 8, 9 y 10 (recuerda que los índices comienzan en 0)
                        return `Subtotal: ${row[8]}  Descuento: ${row[9]} <br> Total: ${row[10]}`;
                    }
                },
                {
                    targets: [9, 10], // Especifica las columnas 8, 9 y 10
                    "visible": false  // Esto oculta las columnas 8, 9 y 10 en la tabla
                },
                { targets: 9, className: 'cell-right' },
                { targets: 10, className: 'cell-center' },
                { targets: 11, className: 'cell-center' },
                { targets: 12, className: 'cell-center' },
                { targets: 13, className: 'cell-center' },
                { targets: 14, className: 'cell-center' }
            ],
            "initComplete": function (settings, json) {

            }
        });
    };

    $('body').loadDataTableDocs();

    $('#ventas').select2();

})

jQuery(document).on("click", ".delete-register", function () {

    e.preventDefault(); // Evita que el link navegue a "#"
    var id = jQuery(this).attr('data-id');
    var empresa = "{{ empresa }}";
    let baseUrl = "/" + empresa + "/manager/pasajeros/delete/";

    let url = `${baseUrl}${id}`;

    Swal.fire({
        title: "Eliminar Registro",
        text: "¿Está seguro que desea eliminar el registro seleccionado?",
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

jQuery(document).on("change", "select[name=ventas]", function () {

    if ($.fn.DataTable.isDataTable('#table-course')) {
        $('#table-course').DataTable().clear();
        $('#table-course').DataTable().destroy();
    }
    $('body').loadDataTableDocs();

    /*
     var table = $("#table-course").DataTable();
      table.ajax.reload();
      */
});