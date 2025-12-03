from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.restriction import Restriction
from datetime import datetime, timezone, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")
api = RenderRequest()
rst = Restriction()

# Ruta principal del dashboard
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    
    schema = request.session.get("schema")
    position = request.session.get("rol")
    
    raw_permisos = await rst.access_Menu(position, schema)
    permisos = {p["permission"]: True for p in raw_permisos}
    request.session["permisos"] = permisos
    
    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "empresa": empresa
    })

# API para obtener datos del dashboard
@router.get("/data")
async def get_dashboard_data(request: Request, year: int = None):
    empresa = request.state.empresa
    
    if not request.session.get("authenticated"):
        return JSONResponse({"error": "No autenticado"}, status_code=401)
    
    schema = request.session.get("schema")
    
    try:
        # Obtener todas las ventas
        sales_response = await api.get_data("sale", schema=schema)
        sales_data = sales_response.get('data', []) if sales_response.get('status') == 'success' else []

        # Obtener todas las cotizaciones
        quotes_response = await api.get_data("quotes", schema=schema)
        quotes_data = quotes_response.get('data', []) if quotes_response.get('status') == 'success' else []
        
        # Obtener usuarios (vendedores)
        users_response = await api.get_data("users", schema=schema)
        users_data = users_response.get('data', []) if users_response.get('status') == 'success' else []

        # Obtener programas
        programs_response = await api.get_data("programac", schema=schema)
        programs_data = programs_response.get('data', []) if programs_response.get('status') == 'success' else []
        
        # Filtrar por año si se proporciona
        if year:
            sales_data = [
                sale for sale in sales_data 
                if sale.get('fecha') and str(year) in sale.get('fecha', '')
            ]
            quotes_data = [
                quote for quote in quotes_data 
                if quote.get('fecha') and str(year) in quote.get('fecha', '')
            ]
        
        # Procesar datos de ventas
        sales_by_type = {}
        sales_by_seller = {}
        sales_by_program = {}
        sales_by_month = {}
        
        total_ventas = 0
        monto_total_ventas = 0
        
        for sale in sales_data:
            # Filtrar ventas anuladas
            if sale.get('activo') == '2':
                continue
                
            total_ventas += 1
            sale_total = float(sale.get('vprograma', 0)) * float(sale.get('nroalumno', 0))
            monto_total_ventas += sale_total
            
            # Agrupar por tipo
            sale_type = sale.get('type_sale', 'Sin tipo')
            if sale_type not in sales_by_type:
                sales_by_type[sale_type] = {'type': sale_type, 'cantidad': 0, 'total_monto': 0}
            sales_by_type[sale_type]['cantidad'] += 1
            sales_by_type[sale_type]['total_monto'] += sale_total
            
            # Agrupar por vendedor
            user_id = sale.get('seller_id')
            if user_id:
                # Convertir a string para asegurar comparación correcta
                user_id_str = str(user_id)
                user = next((u for u in users_data if str(u.get('id')) == user_id_str), None)
                vendedor = user.get('name', 'Sin vendedor') if user else 'Sin vendedor'
                if vendedor not in sales_by_seller:
                    sales_by_seller[vendedor] = {'vendedor': vendedor, 'cantidad': 0, 'total_monto': 0}
                sales_by_seller[vendedor]['cantidad'] += 1
                sales_by_seller[vendedor]['total_monto'] += sale_total
            
            # Agrupar por programa
            program_id = sale.get('program_id')
            if program_id:
                # Convertir a string para asegurar comparación correcta
                program_id_str = str(program_id)
                program = next((p for p in programs_data if str(p.get('id')) == program_id_str), None)
                programa = program.get('name', 'Sin programa') if program else 'Sin programa'
                if programa not in sales_by_program:
                    sales_by_program[programa] = {'programa': programa, 'cantidad': 0, 'total_monto': 0}
                sales_by_program[programa]['cantidad'] += 1
                sales_by_program[programa]['total_monto'] += sale_total
            
            # Agrupar por mes
            created_at = sale.get('fecha')
            if created_at:
                try:
                    # Intentar parsear la fecha
                    if isinstance(created_at, str):
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        date_obj = created_at
                    
                    month_key = date_obj.strftime('%Y-%m')
                    if month_key not in sales_by_month:
                        sales_by_month[month_key] = {'mes': date_obj.strftime('%Y-%m-01'), 'cantidad': 0, 'total_monto': 0}
                    sales_by_month[month_key]['cantidad'] += 1
                    sales_by_month[month_key]['total_monto'] += sale_total
                except:
                    pass
        
        # Procesar datos de cotizaciones
        quotes_by_status = {}
        total_cotizaciones = 0
        cotizaciones_con_venta = 0
        monto_convertido = 0
        
        for quote in quotes_data:
            total_cotizaciones += 1
            status = quote.get('estado', 'Sin estado')
            
            if status not in quotes_by_status:
                quotes_by_status[status] = {'status': status, 'cantidad': 0, 'total_monto': 0}
            quotes_by_status[status]['cantidad'] += 1
            quotes_by_status[status]['total_monto'] += float(quote.get('total', 0))
            
            # Verificar si la cotización tiene venta asociada
            quote_id = quote.get('id')
            if quote_id:
                sale_with_quote = next((s for s in sales_data if s.get('quote_id') == quote_id), None)
                if sale_with_quote:
                    cotizaciones_con_venta += 1
                    monto_convertido += float(quote.get('total', 0))
        
        # Ordenar y limitar resultados
        sales_by_seller_list = sorted(sales_by_seller.values(), key=lambda x: x['total_monto'], reverse=True)[:10]
        sales_by_program_list = sorted(sales_by_program.values(), key=lambda x: x['total_monto'], reverse=True)[:10]
        sales_by_month_list = sorted(sales_by_month.values(), key=lambda x: x['mes'])[-6:]  # Últimos 6 meses
        
        # Calcular promedio
        promedio_venta = monto_total_ventas / total_ventas if total_ventas > 0 else 0
        
        return JSONResponse({
            "sales_by_type": list(sales_by_type.values()),
            "sales_by_seller": sales_by_seller_list,
            "sales_by_program": sales_by_program_list,
            "quotes_data": list(quotes_by_status.values()),
            "quotes_conversion": {
                "total_cotizaciones": total_cotizaciones,
                "cotizaciones_con_venta": cotizaciones_con_venta,
                "monto_convertido": monto_convertido
            },
            "sales_by_month": sales_by_month_list,
            "totals": {
                "total_ventas": total_ventas,
                "monto_total_ventas": monto_total_ventas,
                "promedio_venta": promedio_venta
            }
        })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error en dashboard: {error_detail}")
        return JSONResponse({"error": str(e), "detail": error_detail}, status_code=500)
