// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function () {
    initializeYearFilter();
    loadDashboardData();

    // Add event listener for year filter
    document.getElementById('yearFilter').addEventListener('change', function () {
        loadDashboardData();
    });
});

let charts = {};

function initializeYearFilter() {
    const yearSelect = document.getElementById('yearFilter');
    const currentYear = new Date().getFullYear();

    // Agregar los últimos 4 años más el año actual (total 5 años)
    for (let i = 0; i < 5; i++) {
        const year = currentYear - i;
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        if (i === 0) {
            option.selected = true; // Seleccionar el año actual por defecto
        }
        yearSelect.appendChild(option);
    }
}


async function loadDashboardData() {
    try {
        // Get empresa from URL path
        const pathParts = window.location.pathname.split('/');
        const empresa = pathParts[1]; // Assumes /{empresa}/manager/dashboard

        // Get selected year
        const yearFilter = document.getElementById('yearFilter');
        const selectedYear = yearFilter.value;

        // Build URL with year parameter
        let url = `/${empresa}/manager/dashboard/data`;
        if (selectedYear) {
            url += `?year=${selectedYear}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            console.error('Error loading dashboard data:', data.error);
            showError('Error al cargar los datos: ' + data.error);
            return;
        }



        // Update stats cards
        updateStatsCards(data.totals, data.quotes_data);

        // Create charts
        createSalesByTypeChart(data.sales_by_type);
        createSalesByMonthChart(data.sales_by_month);
        createSalesBySellerChart(data.sales_by_seller);
        createSalesByProgramChart(data.sales_by_program);

        // Update conversion table
        updateConversionTable(data.quotes_conversion);

    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        showError('Error al conectar con el servidor. Por favor, intente nuevamente.');
    }
}

function showError(message) {
    // Simple error display - you can enhance this with a modal or toast
    alert(message);
}

function updateStatsCards(totals, quotesData) {
    const totalVentas = totals.total_ventas || 0;
    const montoTotal = totals.monto_total_ventas || 0;
    const promedioVenta = totals.promedio_venta || 0;

    // Calculate total quotes
    let totalCotizaciones = 0;
    if (quotesData && Array.isArray(quotesData)) {
        totalCotizaciones = quotesData.reduce((sum, item) => sum + (item.cantidad || 0), 0);
    }

    document.getElementById('total-ventas').textContent = totalVentas.toLocaleString();
    document.getElementById('monto-total').textContent = '$' + montoTotal.toLocaleString('es-CL');
    document.getElementById('total-cotizaciones').textContent = totalCotizaciones.toLocaleString();
    document.getElementById('promedio-venta').textContent = '$' + Math.round(promedioVenta).toLocaleString('es-CL');

    // Update stat changes to show loaded
    document.querySelectorAll('.stat-change').forEach(el => {
        el.innerHTML = '<i class="fas fa-check"></i><span>Actualizado</span>';
    });
}

function createSalesByTypeChart(data) {
    const ctx = document.getElementById('salesByTypeChart');

    if (charts.salesByType) {
        charts.salesByType.destroy();
    }

    const labels = data.map(item => item.type || 'Sin tipo');
    const values = data.map(item => item.total_monto || 0);

    charts.salesByType = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monto por Tipo',
                data: values,
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(79, 172, 254, 0.8)',
                    'rgba(0, 242, 254, 0.8)',
                    'rgba(67, 233, 123, 0.8)',
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(118, 75, 162, 1)',
                    'rgba(79, 172, 254, 1)',
                    'rgba(0, 242, 254, 1)',
                    'rgba(67, 233, 123, 1)',
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '$' + context.parsed.toLocaleString('es-CL');
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function createSalesByMonthChart(data) {
    const ctx = document.getElementById('salesByMonthChart');

    if (charts.salesByMonth) {
        charts.salesByMonth.destroy();
    }

    const labels = data.map(item => {
        const date = new Date(item.mes);
        return date.toLocaleDateString('es-CL', { month: 'short', year: 'numeric' });
    });
    const values = data.map(item => item.total_monto || 0);

    charts.salesByMonth = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas Mensuales',
                data: values,
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return '$' + context.parsed.y.toLocaleString('es-CL');
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return '$' + value.toLocaleString('es-CL');
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createSalesBySellerChart(data) {
    const ctx = document.getElementById('salesBySellerChart');

    if (charts.salesBySeller) {
        charts.salesBySeller.destroy();
    }

    const labels = data.map(item => item.vendedor || 'Sin vendedor');
    const values = data.map(item => item.total_monto || 0);

    charts.salesBySeller = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monto por Vendedor',
                data: values,
                backgroundColor: 'rgba(79, 172, 254, 0.8)',
                borderColor: 'rgba(79, 172, 254, 1)',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return '$' + context.parsed.x.toLocaleString('es-CL');
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return '$' + value.toLocaleString('es-CL');
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createSalesByProgramChart(data) {
    const ctx = document.getElementById('salesByProgramChart');

    if (charts.salesByProgram) {
        charts.salesByProgram.destroy();
    }

    const labels = data.map(item => item.programa || 'Sin programa');
    const values = data.map(item => item.total_monto || 0);

    charts.salesByProgram = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monto por Programa',
                data: values,
                backgroundColor: 'rgba(67, 233, 123, 0.8)',
                borderColor: 'rgba(67, 233, 123, 1)',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return '$' + context.parsed.y.toLocaleString('es-CL');
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return '$' + value.toLocaleString('es-CL');
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

function updateConversionTable(conversionData) {
    const tbody = document.getElementById('conversion-table-body');

    const totalCotizaciones = conversionData.total_cotizaciones || 0;
    const cotizacionesConVenta = conversionData.cotizaciones_con_venta || 0;
    const montoConvertido = conversionData.monto_convertido || 0;
    const tasaConversion = totalCotizaciones > 0
        ? ((cotizacionesConVenta / totalCotizaciones) * 100).toFixed(2)
        : 0;

    tbody.innerHTML = `
        <tr>
            <td>Total Cotizaciones</td>
            <td><strong>${totalCotizaciones.toLocaleString()}</strong></td>
            <td><span class="badge info">Total</span></td>
        </tr>
        <tr>
            <td>Cotizaciones Convertidas a Venta</td>
            <td><strong>${cotizacionesConVenta.toLocaleString()}</strong></td>
            <td><span class="badge success">Convertidas</span></td>
        </tr>
        <tr>
            <td>Tasa de Conversión</td>
            <td><strong>${tasaConversion}%</strong></td>
            <td><span class="badge ${tasaConversion >= 50 ? 'success' : 'warning'}">
                ${tasaConversion >= 50 ? 'Excelente' : 'Mejorable'}
            </span></td>
        </tr>
        <tr>
            <td>Monto Total Convertido</td>
            <td><strong>$${montoConvertido.toLocaleString('es-CL')}</strong></td>
            <td><span class="badge success">Ingresos</span></td>
        </tr>
    `;
}
