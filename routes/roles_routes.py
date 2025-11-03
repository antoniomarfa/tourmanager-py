from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import json
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction

router = APIRouter()

templates = Jinja2Templates(directory="templates")

api = RenderRequest()
rst = Restriction()
#array de roles
array_descriptions_actions = {
    'INSERT': 'Agregar',
    'UPDATE': 'Editar',
    'DELETE': 'Eliminar',
    'VIEW': 'Ver',
    'IMPORT_COURSE': 'Importar Curso',
    'EXPORT_REPORT': 'Exportar Informe'
}

array_permissions = {
    'dashboard': {'label': 'Estadisticas', 'actions': 'VIEW'},
    'company': {'label': 'Empresa', 'actions': 'INSERT|UPDATE|DELETE'},
    'programas': {'label': 'Programas', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'roles': {'label': 'Roles', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'school': {'label': 'Colegios', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'users': {'label': 'usuarios', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'gatewaysconfig': {'label': 'Config Pasarelas de Pago', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'gateways': {'label': 'Pasarelas de Pago', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'gdsair': {'label': 'Ticket Aereos', 'actions': 'VIEW'},
    'gdshotel': {'label': 'Hoteles', 'actions': 'VIEW'},
    'quotes': {'label': 'Cotizacion Programa', 'actions': 'VIEW|INSERT|UPDATE|DELETE|EXPORT_REPORT'},
    'sales': {'label': 'Venta Programa', 'actions': 'VIEW|INSERT|UPDATE|DELETE|IMPORT_COURSE|EXPORT_REPORT'},
    'course': {'label': 'Cursos', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'entry': {'label': 'Ingresos', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'listpay': {'label': 'Pagos', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'voucher': {'label': 'Voucher', 'actions': 'VIEW|INSERT|UPDATE|DELETE'},
    'salesreport':{'label': 'Comisiones Vendedor', 'actions': 'VIEW|EXPORT_REPORT'},
}


# Ruta principal: mostrar roles
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")    
    response = await api.get_data("roles",schema=schema_name)
    roles = response["data"] if response["status"] == "success" else []

    cant_access = {  
        "can_update": await rst.access_permission("roles", "UPDATE", request.session),
        "can_delete": await rst.access_permission("roles", "DELETE", request.session),
        "can_insert": await rst.access_permission("roles", "INSERT", request.session)
    }
   
    return templates.TemplateResponse("roles/index.html", {"request": request, "roles": roles, "session":request.session, "helper":Helper,"array_permissions": array_permissions, "array_descriptions_actions": array_descriptions_actions,"cant_access":cant_access,"empresa":empresa})

# Mostrar formulario de creación
@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")
    response = await api.get_data("company",schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    companys = response["data"] if response["status"] == "success" else []    
    return templates.TemplateResponse("roles/create.html", {"request": request, "companys":companys,"session": request.session, "session":request.session, "array_permissions": array_permissions, "array_descriptions_actions": array_descriptions_actions})

# Crear roles vía API
@router.post("/create")
async def create(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    form_data = await request.form()
    schema_name = request.session.get("schema")

    # --- Cabecera (rol) ---
    role_payload = {
        "description": (form_data.get("description") or "").strip(),
        "company_id": request.session.get("company"),
        "author": request.session.get("user_name"),
        "active": 1,
    }
    resp = await api.set_data("roles", body=json.dumps(role_payload), schema=schema_name)
    if resp.get("status") != "success":
        request.session["flash_message"] = "error"
        request.session["flash_error"] = resp.get("error", "Error al crear el rol")
        return RedirectResponse(url=f"{empresa}/manager/roles", status_code=303)

    role_id = resp["data"]["data"]["return_id"]

    # --- Debug útil: ver exactamente qué keys llegaron ---
    print("Form keys:", list(form_data.keys()))
    for k, v in form_data.multi_items():
        print("FORM:", k, "=>", v)

    # --- Detalle (permissions) ---
    for perm_key in array_permissions.keys():
        # Intenta sin [] y con []
        values = form_data.getlist(perm_key) or form_data.getlist(f"{perm_key}[]")
        if values:
            actions = "|".join(values)
            det_payload = {
                "roles_id": int(role_id),
                "permission": perm_key,
                "actions": actions,
            }
            det_resp = await api.set_data("permission", body=json.dumps(det_payload), schema=schema_name)
            print("Insert permiso", perm_key, values, "->", det_resp)

    request.session["flash_message"] = "success"
    request.session["flash_error"] = "Registro grabado correctamente."
    return RedirectResponse(url=f"{empresa}/manager/roles", status_code=303)



# Mostrar formulario de edicion
@router.get("/edit/{rol_id}", response_class=HTMLResponse)
async def create_form(request: Request,rol_id:int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")
    response = await api.get_data("company",id=request.session.get("company"),schema="global")  # Suponiendo que el servicio se llama 'users'    
    companys = response["data"] if response["status"] == "success" else []    

    response = await api.get_data("roles",schema=schema_name,id=rol_id)
    perfil = response["data"] if response["status"] == "success" else []

    getQuery=f"roles_id={rol_id}"
    response = await api.get_data("permission", query=getQuery, schema=schema_name)
    roles_permissions = response["data"] if response["status"] == "success" else None
    array_roles_permissions = {}

    if len(roles_permissions) > 0:
        for roles_permission in roles_permissions:
            permission_key = roles_permission['permission']
            array_roles_permissions[permission_key] = {
               'permission': permission_key,
              'actions': roles_permission['actions'].split('|')
            }
  
    return templates.TemplateResponse("roles/edit.html", {"request": request, "companys":companys,"session": request.session, "session":request.session, "perfil": perfil, "array_permissions": array_permissions,"array_descriptions_actions": array_descriptions_actions, "_array_roles_permissions": array_roles_permissions, "helper":Helper,"empresa":empresa})

# Crear roles vía API
@router.post("/update")
async def create(request: Request):
    empresa = request.state.empresa 
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    form_data = await request.form()
    schema_name = request.session.get("schema")
    role_id = int(form_data.get("id"))

    # --- Cabecera (rol) ---
    role_payload = {
        "description": (form_data.get("description") or "").strip(),
        "author": request.session.get("user_name"),
    }

    resp = await api.update_data("roles",id=role_id, body=json.dumps(role_payload), schema=schema_name)
    if resp.get("status") != "success":
        request.session["flash_message"] = "error"
        request.session["flash_error"] = resp.get("error", "Error al crear el rol")
        return RedirectResponse(url=f"/{empresa}/manager/roles", status_code=303)

    #role_id = resp["data"]["data"]["return_id"]

    # --- Debug útil: ver exactamente qué keys llegaron ---
    for k, v in form_data.multi_items():
        print("FORM:", k, "=>", v)
    # --- Elimina todos los permisos y lo graba nuevamente
    getQuery=f"roles_id={role_id}"
    delete = api.delete_data("permission", query= getQuery, schema=schema_name)
    print("delete ",delete)
    # --- Detalle (permissions) ---
    for perm_key in array_permissions.keys():
        # Intenta sin [] y con []
        values = form_data.getlist(perm_key) or form_data.getlist(f"{perm_key}[]")
        if values:
            actions = "|".join(values)
            det_payload = {
                "roles_id": int(role_id),
                "permission": perm_key,
                "actions": actions,
            }
            det_resp = await api.set_data("permission", body=json.dumps(det_payload), schema=schema_name)
            print("Insert permiso", perm_key, values, "->", det_resp)

    request.session["flash_message"] = "success"
    request.session["flash_error"] = "Registro grabado correctamente."
    return RedirectResponse(url=f"/{empresa}/manager/roles", status_code=303)

# Eliminar usuario
@router.get("/delete/{rol_id}")
async def delete(request: Request,rol_id: int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema") 
    response=await api.delete_data("roles", id=rol_id, schema=schema_name)
    message=response['status']
    error="Registro eliminado correctamente."

    if message == "success":
        delete = api.delete_data("permission", id=rol_id, schema=schema_name)

    if message != "success":
        error=response['error']
    request.session['flash_message'] = message    
    request.session['flash_error'] = error    
    return RedirectResponse(url=f"/{empresa}/manager/roles/", status_code=303)
