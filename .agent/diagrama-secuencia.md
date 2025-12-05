# Diagrama de Secuencia - TourManager

Este documento contiene los diagramas de secuencia de los flujos principales del sistema TourManager.

## 1. Flujo de Autenticación y Login

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser
    participant FastAPI as FastAPI App
    participant Middleware
    participant AuthRoutes as auth.py
    participant RenderAPI as RenderRequest
    participant Database as API Backend
    
    Usuario->>Browser: Accede a /{empresa}/manager
    Browser->>FastAPI: GET /{empresa}/manager
    FastAPI->>Middleware: detectar_empresa()
    Middleware->>Middleware: Extrae empresa de URL
    Middleware->>FastAPI: request.state.empresa = empresa
    FastAPI->>RenderAPI: get_data("company", query="identificador={empresa}")
    RenderAPI->>Database: GET /api/v3.5/company?identificador={empresa}
    Database-->>RenderAPI: Datos de empresa
    RenderAPI-->>FastAPI: {status: success, data: company}
    FastAPI->>FastAPI: Valida existencia de empresa
    FastAPI->>FastAPI: Guarda code_company en session
    FastAPI-->>Browser: Renderiza login.html
    Browser-->>Usuario: Muestra formulario de login
    
    Usuario->>Browser: Ingresa credenciales
    Browser->>AuthRoutes: POST /login (username, password, accesscode)
    AuthRoutes->>RenderAPI: get_data("users", query="username={username}")
    RenderAPI->>Database: GET /api/v3.5/users?username={username}
    Database-->>RenderAPI: Datos de usuario
    RenderAPI-->>AuthRoutes: {status: success, data: user}
    
    alt Usuario encontrado
        AuthRoutes->>AuthRoutes: Verifica password con bcrypt
        alt Password correcto
            AuthRoutes->>AuthRoutes: Valida accesscode si es necesario
            AuthRoutes->>AuthRoutes: Guarda datos en session (id, username, role_id, etc.)
            AuthRoutes->>AuthRoutes: Determina redirect según role_id
            AuthRoutes-->>Browser: RedirectResponse a dashboard/index
            Browser-->>Usuario: Acceso concedido
        else Password incorrecto
            AuthRoutes-->>Browser: Renderiza login con error
            Browser-->>Usuario: Muestra error de credenciales
        end
    else Usuario no encontrado
        AuthRoutes->>RenderAPI: get_data("cursos", query="username={username}")
        RenderAPI->>Database: GET /api/v3.5/cursos?username={username}
        Database-->>RenderAPI: Datos de curso
        alt Curso encontrado
            AuthRoutes->>AuthRoutes: Valida credenciales de curso
            AuthRoutes-->>Browser: RedirectResponse según tipo
        else No encontrado
            AuthRoutes-->>Browser: Error de autenticación
        end
    end
```

## 2. Flujo de Recuperación de Contraseña

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser
    participant AuthRoutes as auth.py
    participant RenderAPI as RenderRequest
    participant Database as API Backend
    participant SMTP as Servidor Email
    
    Usuario->>Browser: Click en "¿Olvidaste tu contraseña?"
    Browser->>AuthRoutes: GET /forgot-password
    AuthRoutes-->>Browser: Renderiza forgot_password.html
    Browser-->>Usuario: Muestra formulario de email
    
    Usuario->>Browser: Ingresa email
    Browser->>AuthRoutes: POST /forgot-password (email)
    AuthRoutes->>RenderAPI: get_data("users", query="email={email}")
    RenderAPI->>Database: GET /api/v3.5/users?email={email}
    Database-->>RenderAPI: Datos de usuario
    
    alt Email encontrado en users
        AuthRoutes->>AuthRoutes: Genera código aleatorio de 6 dígitos
        AuthRoutes->>AuthRoutes: Guarda en session (reset_code, reset_email, reset_expiry)
        AuthRoutes->>SMTP: send_verification_code(email, code, company_name)
        SMTP->>SMTP: Crea mensaje HTML con código y URL
        SMTP->>Usuario: Envía email con código
        AuthRoutes-->>Browser: RedirectResponse a /verify-code
        Browser-->>Usuario: Muestra formulario de verificación
    else Email no encontrado en users
        AuthRoutes->>RenderAPI: get_data("cursos", query="email={email}")
        RenderAPI->>Database: GET /api/v3.5/cursos?email={email}
        alt Email encontrado en cursos
            AuthRoutes->>AuthRoutes: Genera código y envía email
            AuthRoutes-->>Browser: RedirectResponse a /verify-code
        else Email no encontrado
            AuthRoutes-->>Browser: Renderiza con error
            Browser-->>Usuario: Email no encontrado
        end
    end
    
    Usuario->>Browser: Ingresa código recibido
    Browser->>AuthRoutes: POST /verify-code (code)
    AuthRoutes->>AuthRoutes: Valida código y expiración
    
    alt Código válido
        AuthRoutes->>AuthRoutes: Crea sesión automática
        AuthRoutes->>AuthRoutes: Limpia datos de reset
        AuthRoutes-->>Browser: RedirectResponse a dashboard
        Browser-->>Usuario: Acceso concedido
    else Código inválido o expirado
        AuthRoutes-->>Browser: Renderiza con error
        Browser-->>Usuario: Código incorrecto
    end
```

## 3. Flujo de Gestión de Ventas

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser
    participant SalesRoutes as sales_routes.py
    participant RenderAPI as RenderRequest
    participant Database as API Backend
    participant PDFGen as Generador PDF
    
    Usuario->>Browser: Accede a ventas
    Browser->>SalesRoutes: GET /sales/index
    SalesRoutes->>SalesRoutes: Verifica sesión (Restriction)
    SalesRoutes->>RenderAPI: get_data("programs")
    RenderAPI->>Database: GET /api/v3.5/programs
    Database-->>RenderAPI: Lista de programas
    SalesRoutes->>RenderAPI: get_data("users", query="role_id=3")
    RenderAPI->>Database: GET /api/v3.5/users?role_id=3
    Database-->>RenderAPI: Lista de vendedores
    SalesRoutes-->>Browser: Renderiza sales/index.html
    Browser-->>Usuario: Muestra interfaz de ventas
    
    Usuario->>Browser: Solicita tabla de ventas
    Browser->>SalesRoutes: POST /sales/gettable
    SalesRoutes->>RenderAPI: get_data("sales", query filtros)
    RenderAPI->>Database: GET /api/v3.5/sales?filters
    Database-->>RenderAPI: Lista de ventas
    SalesRoutes->>RenderAPI: get_data("programs")
    RenderAPI->>Database: GET /api/v3.5/programs
    Database-->>RenderAPI: Programas para lookup
    SalesRoutes->>SalesRoutes: Procesa y formatea datos
    SalesRoutes->>SalesRoutes: Genera HTML de tabla con acciones
    SalesRoutes-->>Browser: JSONResponse con HTML
    Browser-->>Usuario: Muestra tabla de ventas
    
    Usuario->>Browser: Click en "Nueva Venta"
    Browser->>SalesRoutes: GET /sales/create?type=sale
    SalesRoutes->>RenderAPI: get_data("programs")
    SalesRoutes->>RenderAPI: get_data("users", role_id=3)
    SalesRoutes-->>Browser: Renderiza formulario de venta
    Browser-->>Usuario: Muestra formulario
    
    Usuario->>Browser: Completa formulario y envía
    Browser->>SalesRoutes: POST /sales/create (form_data)
    SalesRoutes->>SalesRoutes: Valida datos del formulario
    SalesRoutes->>SalesRoutes: Prepara body con datos de venta
    SalesRoutes->>RenderAPI: set_data("sales", body)
    RenderAPI->>Database: POST /api/v3.5/sales
    Database-->>RenderAPI: Venta creada
    RenderAPI-->>SalesRoutes: {status: success, data: sale}
    SalesRoutes-->>Browser: RedirectResponse a /sales/index
    Browser-->>Usuario: Venta creada exitosamente
    
    Usuario->>Browser: Click en "Generar PDF Pasajeros"
    Browser->>SalesRoutes: POST /sales/pasajerospdf (saleid)
    SalesRoutes->>RenderAPI: get_data("sales", id=saleid)
    RenderAPI->>Database: GET /api/v3.5/sales/{saleid}
    Database-->>RenderAPI: Datos de venta
    SalesRoutes->>RenderAPI: get_data("pasajeros", query="venta_id={saleid}")
    RenderAPI->>Database: GET /api/v3.5/pasajeros?venta_id={saleid}
    Database-->>RenderAPI: Lista de pasajeros
    SalesRoutes->>PDFGen: Genera PDF con ReportLab
    PDFGen-->>SalesRoutes: BytesIO con PDF
    SalesRoutes-->>Browser: StreamingResponse (application/pdf)
    Browser-->>Usuario: Descarga PDF
```

## 4. Flujo de Dashboard y Visualización

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser
    participant DashboardRoutes as dashboard_routes.py
    participant RenderAPI as RenderRequest
    participant Database as API Backend
    
    Usuario->>Browser: Accede al dashboard
    Browser->>DashboardRoutes: GET /dashboard/index
    DashboardRoutes->>DashboardRoutes: Verifica sesión (Restriction)
    DashboardRoutes-->>Browser: Renderiza dashboard/index.html
    Browser-->>Usuario: Muestra interfaz de dashboard
    
    Browser->>DashboardRoutes: GET /dashboard/data?year={year}
    DashboardRoutes->>DashboardRoutes: Obtiene año actual si no se especifica
    DashboardRoutes->>DashboardRoutes: Calcula rango de fechas (inicio y fin de año)
    
    par Consultas paralelas
        DashboardRoutes->>RenderAPI: get_data("sales", query con filtros de fecha)
        RenderAPI->>Database: GET /api/v3.5/sales?filters
        Database-->>RenderAPI: Ventas del período
        
        DashboardRoutes->>RenderAPI: get_data("entry", query con filtros)
        RenderAPI->>Database: GET /api/v3.5/entry?filters
        Database-->>RenderAPI: Entradas del período
        
        DashboardRoutes->>RenderAPI: get_data("programs")
        RenderAPI->>Database: GET /api/v3.5/programs
        Database-->>RenderAPI: Lista de programas
        
        DashboardRoutes->>RenderAPI: get_data("users", role_id=3)
        RenderAPI->>Database: GET /api/v3.5/users?role_id=3
        Database-->>RenderAPI: Lista de vendedores
    end
    
    DashboardRoutes->>DashboardRoutes: Procesa ventas por mes
    DashboardRoutes->>DashboardRoutes: Calcula totales y estadísticas
    DashboardRoutes->>DashboardRoutes: Agrupa por programa
    DashboardRoutes->>DashboardRoutes: Agrupa por vendedor
    DashboardRoutes->>DashboardRoutes: Calcula entradas por mes
    
    DashboardRoutes-->>Browser: JSONResponse con datos procesados
    Browser->>Browser: Renderiza gráficos con Chart.js
    Browser-->>Usuario: Muestra visualizaciones actualizadas
```

## 5. Flujo de Proceso de Pago

```mermaid
sequenceDiagram
    actor Usuario
    participant Browser
    participant PaymentRoutes as payment_routes.py
    participant RenderAPI as RenderRequest
    participant Database as API Backend
    participant FlowAPI as Flow/MercadoPago
    
    Usuario->>Browser: Accede a proceso de pago
    Browser->>PaymentRoutes: GET /payment/index
    PaymentRoutes->>PaymentRoutes: Verifica sesión
    PaymentRoutes->>RenderAPI: get_data("sales", id=sale_id)
    RenderAPI->>Database: GET /api/v3.5/sales/{sale_id}
    Database-->>RenderAPI: Datos de venta
    PaymentRoutes-->>Browser: Renderiza formulario de pago
    Browser-->>Usuario: Muestra opciones de pago
    
    Usuario->>Browser: Selecciona método y monto
    Browser->>PaymentRoutes: POST /payment/create
    PaymentRoutes->>PaymentRoutes: Valida datos del formulario
    PaymentRoutes->>PaymentRoutes: Prepara datos de ficha médica
    
    PaymentRoutes->>RenderAPI: set_data("fichamedica", body)
    RenderAPI->>Database: POST /api/v3.5/fichamedica
    Database-->>RenderAPI: Ficha médica creada
    
    alt Pago con Flow
        PaymentRoutes->>FlowAPI: Crea orden de pago
        FlowAPI-->>PaymentRoutes: URL de pago
        PaymentRoutes-->>Browser: RedirectResponse a Flow
        Browser-->>Usuario: Redirige a pasarela de pago
    else Pago con MercadoPago
        PaymentRoutes->>FlowAPI: Crea preferencia de pago
        FlowAPI-->>PaymentRoutes: URL de pago
        PaymentRoutes-->>Browser: RedirectResponse a MercadoPago
    else Pago con Transferencia
        PaymentRoutes->>RenderAPI: update_data("sales", status)
        RenderAPI->>Database: PATCH /api/v3.5/sales/{id}
        PaymentRoutes-->>Browser: Muestra datos para transferencia
    end
    
    Usuario->>FlowAPI: Completa pago
    FlowAPI->>PaymentRoutes: Callback de confirmación
    PaymentRoutes->>RenderAPI: update_data("sales", status="paid")
    RenderAPI->>Database: PATCH /api/v3.5/sales/{id}
    PaymentRoutes->>RenderAPI: set_data("entry", payment_data)
    RenderAPI->>Database: POST /api/v3.5/entry
    PaymentRoutes-->>Browser: RedirectResponse a confirmación
    Browser-->>Usuario: Pago confirmado
```

## 6. Arquitectura General del Sistema

```mermaid
sequenceDiagram
    participant Client as Cliente/Browser
    participant FastAPI as FastAPI App (main.py)
    participant Middleware as Middleware Multi-tenant
    participant Routes as Routes (auth, sales, etc.)
    participant Libraries as Libraries (RenderRequest, Utilities)
    participant API as API Backend (DigitalOcean)
    participant DB as Base de Datos PostgreSQL
    
    Client->>FastAPI: HTTP Request
    FastAPI->>Middleware: Procesa request
    Middleware->>Middleware: Extrae empresa de URL
    Middleware->>Middleware: Establece X-Tenant-Schema
    Middleware->>Routes: Enruta a controlador
    Routes->>Routes: Valida sesión y permisos
    Routes->>Libraries: Llama a RenderRequest
    Libraries->>API: HTTP Request con schema header
    API->>DB: Query con schema específico
    DB-->>API: Resultados
    API-->>Libraries: JSON Response
    Libraries-->>Routes: Datos procesados
    Routes->>Routes: Procesa lógica de negocio
    Routes-->>FastAPI: Response (HTML/JSON/Redirect)
    FastAPI-->>Client: HTTP Response
```

## Componentes Principales

### 1. **main.py**
- Punto de entrada de la aplicación
- Configura FastAPI y middleware
- Gestiona multi-tenancy por URL (/{empresa}/manager)
- Incluye todos los routers dinámicamente

### 2. **Middleware**
- `detectar_empresa()`: Extrae identificador de empresa de la URL
- Valida existencia de empresa en base de datos
- Establece contexto de empresa en request.state

### 3. **Routes**
- **auth.py**: Autenticación, login, logout, recuperación de contraseña
- **sales_routes.py**: Gestión de ventas y cotizaciones
- **dashboard_routes.py**: Visualización de métricas y estadísticas
- **payment_routes.py**: Proceso de pago y fichas médicas
- **programs_routes.py**: Gestión de programas de viaje
- **users_routes.py**: Gestión de usuarios
- Y más...

### 4. **Libraries**
- **RenderRequest**: Cliente HTTP para comunicación con API backend
- **Restriction**: Validación de sesión y permisos
- **Utilities**: Funciones auxiliares
- **MailUtil**: Envío de correos electrónicos

### 5. **API Backend**
- Endpoint: https://stingray-app-trnzb.ondigitalocean.app/api/v3.5
- Soporta multi-tenancy mediante header `X-Tenant-Schema`
- Operaciones CRUD: GET, POST, PATCH, DELETE

## Flujos de Datos

### Multi-tenancy
1. URL: `/{empresa}/manager/*`
2. Middleware extrae `{empresa}`
3. Consulta datos de empresa en schema `global`
4. Todas las operaciones subsecuentes usan schema específico de la empresa

### Autenticación
1. Login con username/password
2. Validación contra tabla `users` o `cursos`
3. Verificación de password con bcrypt
4. Almacenamiento de datos en session
5. Redirección según role_id

### Gestión de Ventas
1. Listado con filtros (fecha, vendedor, programa)
2. Creación de venta con datos de pasajeros
3. Generación de documentos PDF
4. Cambio de estados (cotización → venta → pagada)

### Proceso de Pago
1. Selección de método de pago
2. Creación de ficha médica
3. Integración con pasarelas (Flow, MercadoPago, Transbank)
4. Confirmación y registro de entrada

---

**Generado para**: TourManager Python
**Fecha**: 2025-12-05
**Versión**: 1.0
