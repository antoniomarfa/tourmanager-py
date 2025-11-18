const language_datatable = {
    "sProcessing":     "Procesando...",
    "sLengthMenu":     "Mostrar _MENU_ registros",
    "sZeroRecords":    "No se encontraron resultados",
    "sEmptyTable":     "Ningún dato disponible en esta tabla",
    "sInfo":           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_",
    "sInfoEmpty":      "Mostrando registros del 0 al 0 de un total de 0",
    "sInfoFiltered":   "(filtrado de un total de _MAX_ registros)",
    "sSearch":         "Buscar:",
    "oPaginate": {
        "sFirst":    "<<",
        "sLast":     ">>",
        "sNext":     ">",
        "sPrevious": "<"
    },
};
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
/*
document.addEventListener("DOMContentLoaded", () => {
    cargarUsuarios(1); // Carga inicial

    // Manejar clicks en la paginación dinámica
    document.addEventListener("click", (e) => {
        if (e.target.classList.contains("page-link")) {
            e.preventDefault();
            const page = e.target.getAttribute("data-page");
            if (page) cargarUsuarios(page);
        }
    });
});

// 🔹 Función que carga las tarjetas por fetch
async function cargarUsuarios(page = 1) {
    const container = document.getElementById("usuarios-container");
    container.innerHTML = "<div class='text-center py-5'>Cargando...</div>";

    $total_pages = getElementById("total_pages").value;
    var empresa = "{{ empresa }}";
    const response = await fetch(` "/" + empresa + "/manager/users?page=${page}&total_pages=${total_pages}`);
    const html = await response.text();

    container.innerHTML = html;
}

jQuery( document ).ready( function( $ ) {
    var $userTable = jQuery("#userTable");

    var userTable = $userTable.DataTable( {
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
        "oLanguage": language_datatable,
        //"order": [[9, "desc"]],
        "ordering": false,
    });

    // Initalize Select Dropdown after DataTables is created
    $userTable.closest( '.dataTables_wrapper' ).find( 'select' ).addClass('form-control');
    $('.dataTables_length label select').appendTo('.dataTables_length');

});

jQuery(document).on("click", ".delete-register", function(e) {
    e.preventDefault(); // Evita que el link navegue a "#"
    var id = jQuery(this).attr('data-id');
    var empresa = "{{ empresa }}";
    let baseUrl = "/" + empresa + "/manager/users/delete/";

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
*/
jQuery(document).on("click", ".change-status", function() {
    var $element = jQuery(this);
    var id = $element.attr('id');
    var empresa = "{{ empresa }}";
    var url = '/' + empresa + '/manager/users/status';
    var data = {
        user_id: id
    }

    jQuery.ajax({
        type: "POST",
        encoding:"UTF-8",
        url: url,
        data: data,
        dataType:'json',
        success: function(response){
            if(response.status == 1){
                var $badge = $element.find('span');
                $badge
                    .removeAttr('class')
                    .addClass('badge')
                    .addClass(response.class_status)
                    .text(response.text_status);
            }
        }
    });
});