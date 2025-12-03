# 🎨 Guía de Estilos Dashboard - Tour Manager

Esta guía explica cómo aplicar los estilos modernos del dashboard a cualquier template de la aplicación.

## 📋 Tabla de Contenidos
- [Clases Disponibles](#clases-disponibles)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Componentes Reutilizables](#componentes-reutilizables)
- [Mejores Prácticas](#mejores-prácticas)

---

## 🎯 Clases Disponibles

### 1. **Contenedores de Página**

#### `.page-container`
Wrapper principal para todas las páginas. Centra el contenido y aplica padding.

```html
<div class="page-container">
  <!-- Contenido de la página -->
</div>
```

#### `.page-header`
Header moderno con gradiente para títulos de página.

```html
<div class="page-header">
  <h2>
    <i class="fas fa-icon"></i>
    Título de la Página
  </h2>
  <p class="subtitle">Descripción breve de la página</p>
</div>
```

### 2. **Cards de Contenido**

#### `.content-card`
Card genérico para cualquier contenido.

```html
<div class="content-card">
  <h4>Título del Card</h4>
  <!-- Contenido -->
</div>
```

#### `.modern-table-wrapper`
Wrapper especial para tablas con estilo moderno.

```html
<div class="modern-table-wrapper">
  <h4 class="mb-3">Título de la Tabla</h4>
  <div class="table-responsive">
    <table class="table table-bordered table-hover">
      <!-- Tabla -->
    </table>
  </div>
</div>
```

### 3. **Breadcrumbs**

#### `.breadcrumb-container`
Breadcrumb moderno con glassmorphism.

```html
<nav class="breadcrumb-container" aria-label="breadcrumb">
  <ol class="breadcrumb mb-0">
    <li class="breadcrumb-item">
      <a href="/home">
        <i class="bi bi-house-door-fill me-1"></i> Home
      </a>
    </li>
    <li class="breadcrumb-item active" aria-current="page">
      <i class="bi bi-pencil-square me-1"></i> Página Actual
    </li>
  </ol>
</nav>
```

### 4. **Botones**

Los botones Bootstrap se mejoran automáticamente con gradientes y animaciones.

```html
<!-- Botón Success -->
<button class="btn btn-success">
  <i class="fa fa-save me-2"></i> Guardar
</button>

<!-- Botón Primary -->
<button class="btn btn-primary">
  <i class="fa fa-edit me-2"></i> Editar
</button>

<!-- Botón Danger -->
<button class="btn btn-danger">
  <i class="fa fa-trash me-2"></i> Eliminar
</button>

<!-- Botón Info -->
<button class="btn btn-info">
  <i class="fa fa-info me-2"></i> Información
</button>
```

#### `.action-buttons`
Grupo de botones de acción alineados a la derecha.

```html
<div class="action-buttons">
  <a href="/create" class="btn btn-success">
    <i class="fa fa-plus me-2"></i> Nuevo
  </a>
  <button class="btn btn-primary">
    <i class="fa fa-download me-2"></i> Exportar
  </button>
</div>
```

### 5. **Botones de Iconos**

#### `.icon-btn`
Botones pequeños solo con icono para acciones en tablas.

```html
<!-- Botón Editar -->
<button class="icon-btn edit">
  <i class="fa fa-edit"></i>
</button>

<!-- Botón Eliminar -->
<button class="icon-btn delete">
  <i class="fa fa-trash"></i>
</button>

<!-- Botón Ver -->
<button class="icon-btn view">
  <i class="fa fa-eye"></i>
</button>
```

### 6. **Badges de Estado**

#### `.status-badge`
Badges modernos para mostrar estados.

```html
<!-- Estado Activo -->
<span class="status-badge active">Activo</span>

<!-- Estado Inactivo -->
<span class="status-badge inactive">Inactivo</span>

<!-- Estado Pendiente -->
<span class="status-badge pending">Pendiente</span>

<!-- Estado Completado -->
<span class="status-badge completed">Completado</span>
```

### 7. **Formularios**

Los formularios Bootstrap se mejoran automáticamente.

```html
<div class="row g-3">
  <div class="col-md-6">
    <label class="form-label fw-bold">Campo 1</label>
    <input type="text" class="form-control" placeholder="Ingrese valor">
  </div>
  
  <div class="col-md-6">
    <label class="form-label fw-bold">Campo 2</label>
    <select class="form-select">
      <option>Opción 1</option>
      <option>Opción 2</option>
    </select>
  </div>
</div>
```

### 8. **Tablas**

Las tablas Bootstrap se mejoran automáticamente con gradientes en el header.

```html
<table class="table table-bordered table-hover">
  <thead>
    <tr>
      <th>Columna 1</th>
      <th>Columna 2</th>
      <th>Acciones</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Dato 1</td>
      <td>Dato 2</td>
      <td>
        <button class="icon-btn edit"><i class="fa fa-edit"></i></button>
        <button class="icon-btn delete"><i class="fa fa-trash"></i></button>
      </td>
    </tr>
  </tbody>
</table>
```

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Página de Listado Simple

```html
{% extends "base.html" %}

{% block content %}

<nav class="breadcrumb-container" aria-label="breadcrumb">
  <ol class="breadcrumb mb-0">
    <li class="breadcrumb-item">
      <a href="/{{ empresa }}/manager/index">
        <i class="bi bi-house-door-fill me-1"></i> Home
      </a>
    </li>
    <li class="breadcrumb-item active" aria-current="page">
      <i class="bi bi-list me-1"></i> Mi Módulo
    </li>
  </ol>
</nav>

<div class="page-container">
  <!-- Header -->
  <div class="page-header">
    <h2>
      <i class="fas fa-list"></i>
      Listado de Elementos
    </h2>
    <p class="subtitle">Gestión de todos los elementos del sistema</p>
  </div>

  <!-- Botones de Acción -->
  <div class="action-buttons">
    <a href="/create" class="btn btn-success">
      <i class="fa fa-plus me-2"></i> Nuevo Elemento
    </a>
  </div>

  <!-- Tabla -->
  <div class="modern-table-wrapper">
    <div class="table-responsive">
      <table class="table table-bordered table-hover" id="mi-tabla">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <!-- Datos cargados por JS -->
        </tbody>
      </table>
    </div>
  </div>
</div>

{% endblock %}
```

### Ejemplo 2: Página con Formulario

```html
{% extends "base.html" %}

{% block content %}

<nav class="breadcrumb-container" aria-label="breadcrumb">
  <ol class="breadcrumb mb-0">
    <li class="breadcrumb-item">
      <a href="/{{ empresa }}/manager/index">
        <i class="bi bi-house-door-fill me-1"></i> Home
      </a>
    </li>
    <li class="breadcrumb-item active" aria-current="page">
      <i class="bi bi-plus-circle me-1"></i> Crear Elemento
    </li>
  </ol>
</nav>

<div class="page-container">
  <!-- Header -->
  <div class="page-header">
    <h2>
      <i class="fas fa-plus-circle"></i>
      Crear Nuevo Elemento
    </h2>
    <p class="subtitle">Complete el formulario para crear un nuevo elemento</p>
  </div>

  <!-- Formulario -->
  <div class="content-card">
    <h4><i class="fas fa-edit me-2"></i>Información del Elemento</h4>
    
    <form id="mi-formulario">
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label fw-bold">Nombre</label>
          <input type="text" class="form-control" name="nombre" required>
        </div>

        <div class="col-md-6">
          <label class="form-label fw-bold">Categoría</label>
          <select class="form-select" name="categoria" required>
            <option value="">Seleccionar</option>
            <option value="1">Categoría 1</option>
            <option value="2">Categoría 2</option>
          </select>
        </div>

        <div class="col-12">
          <label class="form-label fw-bold">Descripción</label>
          <textarea class="form-control" name="descripcion" rows="4"></textarea>
        </div>

        <div class="col-12">
          <div class="action-buttons">
            <button type="submit" class="btn btn-success">
              <i class="fa fa-save me-2"></i> Guardar
            </button>
            <a href="/listado" class="btn btn-secondary">
              <i class="fa fa-times me-2"></i> Cancelar
            </a>
          </div>
        </div>
      </div>
    </form>
  </div>
</div>

{% endblock %}
```

### Ejemplo 3: Dashboard con Stats

```html
{% extends "base.html" %}

{% block content %}

<div class="dashboard-container">
  <!-- Header -->
  <div class="dashboard-header">
    <h1>
      <i class="fas fa-chart-line"></i>
      Dashboard Principal
    </h1>
    <p>Resumen de actividad y métricas importantes</p>
  </div>

  <!-- Stats Cards -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-icon purple">
        <i class="fas fa-users"></i>
      </div>
      <div class="stat-label">Total Usuarios</div>
      <div class="stat-value">1,234</div>
      <div class="stat-change">
        <i class="fas fa-arrow-up"></i>
        <span>+12% este mes</span>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon blue">
        <i class="fas fa-dollar-sign"></i>
      </div>
      <div class="stat-label">Ingresos</div>
      <div class="stat-value">$45,678</div>
      <div class="stat-change">
        <i class="fas fa-arrow-up"></i>
        <span>+8% este mes</span>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon green">
        <i class="fas fa-shopping-cart"></i>
      </div>
      <div class="stat-label">Ventas</div>
      <div class="stat-value">567</div>
      <div class="stat-change">
        <i class="fas fa-arrow-down"></i>
        <span>-3% este mes</span>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon orange">
        <i class="fas fa-chart-bar"></i>
      </div>
      <div class="stat-label">Promedio</div>
      <div class="stat-value">$80.49</div>
      <div class="stat-change">
        <i class="fas fa-arrow-up"></i>
        <span>+5% este mes</span>
      </div>
    </div>
  </div>

  <!-- Tabla Reciente -->
  <div class="table-card">
    <h3>
      <i class="fas fa-list"></i>
      Actividad Reciente
    </h3>
    <table class="data-table">
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Usuario</th>
          <th>Acción</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>2025-12-02</td>
          <td>Juan Pérez</td>
          <td>Creó una venta</td>
          <td><span class="badge success">Completado</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

{% endblock %}
```

---

## 🎨 Componentes Reutilizables

### Stats Grid (Para Dashboards)

```html
<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-icon purple">
      <i class="fas fa-icon"></i>
    </div>
    <div class="stat-label">Etiqueta</div>
    <div class="stat-value">Valor</div>
    <div class="stat-change">
      <i class="fas fa-arrow-up"></i>
      <span>Cambio</span>
    </div>
  </div>
</div>
```

### Charts Grid (Para Gráficos)

```html
<div class="charts-grid">
  <div class="chart-card">
    <h3>
      <i class="fas fa-chart-pie"></i>
      Título del Gráfico
    </h3>
    <div class="chart-container">
      <canvas id="miGrafico"></canvas>
    </div>
  </div>
</div>
```

---

## ✅ Mejores Prácticas

1. **Siempre usa `page-container`** para envolver el contenido principal
2. **Usa `page-header`** para títulos de página con iconos descriptivos
3. **Aplica `modern-table-wrapper`** a todas las tablas para consistencia
4. **Usa `action-buttons`** para agrupar botones de acción
5. **Agrega iconos** a botones y títulos para mejor UX
6. **Usa `status-badge`** en lugar de badges genéricos para estados
7. **Aplica `content-card`** para secciones de formularios o contenido agrupado
8. **Mantén consistencia** en el uso de clases a través de todos los templates

---

## 🎯 Paleta de Colores

Los gradientes predefinidos son:

- **Purple**: `#667eea → #764ba2` (Principal)
- **Blue**: `#4facfe → #00f2fe` (Información)
- **Green**: `#43e97b → #38f9d7` (Éxito)
- **Orange**: `#fa709a → #fee140` (Advertencia)
- **Pink**: `#f093fb → #f5576c` (Alerta)

---

## 📱 Responsive

Todos los componentes son responsive automáticamente. En móviles:
- Los stats-grid se apilan en una columna
- Los botones se expanden al 100% del ancho
- Las tablas mantienen scroll horizontal
- Los headers reducen su tamaño de fuente

---

## 🚀 Próximos Pasos

Para aplicar estos estilos a un nuevo template:

1. Copia la estructura de breadcrumb
2. Envuelve el contenido en `page-container`
3. Agrega un `page-header` con título e icono
4. Usa `content-card` o `modern-table-wrapper` según el contenido
5. Aplica las clases de botones y formularios
6. ¡Listo! Tu página tendrá el look moderno del dashboard

---

**Creado**: 2025-12-02  
**Versión**: 1.0  
**Autor**: Tour Manager Development Team
