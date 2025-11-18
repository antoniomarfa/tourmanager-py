from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import bcrypt
import json
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction
from libraries.mailutil import Mailutil

router = APIRouter()

templates = Jinja2Templates(directory="templates")

api = RenderRequest()
rst = Restriction()
snm = Mailutil()

# Ruta principal: mostrar usuarios
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")
    per_page=6

    response = await api.get_data("users",schema=schema_name)
    users = response["data"] if response["status"] == "success" else []
    total = len(users)

    cant_access = {  
        "can_update": await rst.access_permission("users", "UPDATE", request.session),
        "can_delete": await rst.access_permission("users", "DELETE", request.session),
        "can_insert": await rst.access_permission("users", "INSERT", request.session)
    }
    flash = Helper.get_flash(request)

    context = {
        "request": request, 
        "users": users, 
        "session":request.session, 
        "helper":Helper, 
        "cant_access":cant_access,
        "empresa":empresa,       
        "msg": flash.get("success"),
        "error": flash.get("error")
    }
    return templates.TemplateResponse("users/index.html", context )


# Mostrar formulario de creación
@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")
    response = await api.get_data("company",schema="global")  # Suponiendo que el servicio se llama 'users'    
    companys = response["data"] if response["status"] == "success" else []    

    response = await api.get_data("roles",schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    roles = response["data"] if response["status"] == "success" else []    

    context = {"request": request, "roles":roles, "companys":companys,"session": request.session,"empresa":empresa}

    return templates.TemplateResponse("users/create.html", context)

# Crear usuario vía API
@router.post("/create")
async def create(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    form_data = await request.form()
    payload = dict(form_data)  # convierte a dict para enviar como JSON o lo que sea

    if 'roles_id' in payload:
        payload['roles_id'] = int(payload.pop('roles_id'))

    if 'active' in payload:
        payload['active'] = int(payload.pop('active'))

    if 'user' in payload:
        payload['username'] = payload.pop('user')
     
    #Busca la compañia  
    response = await api.get_data("company",id=request.session.get("company"),schema="global")  # Suponiendo que el servicio se llama 'users'    
    company = response["data"] if response["status"] == "success" else []

    # Hashear el password si existe
    if "password" in payload:
        raw_password = payload["password"].encode('utf-8')
        hashed = bcrypt.hashpw(raw_password, bcrypt.gensalt())
        payload["password"] = hashed.decode('utf-8')  # guarda como string
    
    payload["company_id"] = request.session.get("company")
    payload["author"] = request.session.get("user_name")
    payload["reset_token"] =""
    # Fecha y hora actual con zona horaria
    fecha_actual = datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")
    payload["reset_token_expira"] =fecha_actual

    json_payload = json.dumps(payload)

    schema_name = request.session.get("schema")
    response=await api.set_data("users", body=json_payload,schema=schema_name)

    if response.get("status") == "success":
        inserted_id=response["data"]["data"]["return_id"]
        subject = f"Habilitación de usuario - {company['nomfantasia']} (PANEL DE ADMINISTRACIÓN)"
        title = 'Habilitación'
        message = 'Esto es una copia de su solicitud de habilitación de usuario.'
        respuestasnm = await snm.email_usuarios(inserted_id, payload["password"].encode('utf-8'), subject, title, message,request.session)
        Helper.flash_message(request, "success", "Usuario creado correctamente.") 
    else:
        Helper.flash_message(request, "error", response["message" ])       


    return RedirectResponse(url=f"/{empresa}/manager/users", status_code=303)

# Mostrar formulario de edición
@router.get("/edit/{user_id}", response_class=HTMLResponse)
async def edit_form(request: Request, user_id: int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    response = await api.get_data("company",id=request.session.get("company") ,schema="global")  # Suponiendo que el servicio se llama 'users'    
    if response["status"] == "success":
        company = response["data"]    

    schema_name = request.session.get("schema")
    response = await api.get_data("roles",schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    roles = response["data"] if response["status"] == "success" else []    

    response = await api.get_data("users", id=user_id, schema=schema_name)
    user = response["data"] if response["status"] == "success" else None
    print(response)
    context={"request": request, "roles":roles, "company":company, "user":user, "session": request.session,"empresa":empresa}
    
    return templates.TemplateResponse("users/edit.html", context)

# Actualizar usuario
@router.post("/update")
async def update(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")

    form_data = await request.form()
    payload = dict(form_data)  # convierte a dict para enviar como JSON o lo que sea

    user_id = int(payload.pop("id"))
    
    if 'roles_id' in payload:
        payload['roles_id'] = int(payload.pop('roles_id'))

    if 'active' in payload:
        payload['active'] = int(payload.pop('active'))

    if 'user' in payload:
        payload['username'] = payload.pop('user')

    # Hashear el password si existe
    if "change_password" in form_data and form_data["change_password"].strip():
        if "password" in payload:
            snm_password = payload["password"]
            raw_password = payload["password"].encode('utf-8')
            hashed = bcrypt.hashpw(raw_password, bcrypt.gensalt())
            payload["password"] = hashed.decode('utf-8')  # guarda como string
    
    #Busca la compañia  
    response = await api.get_data("company",id=request.session.get("company"),schema="global")  # Suponiendo que el servicio se llama 'users'    
    company = response["data"] if response["status"] == "success" else []

    payload["company_id"] = request.session.get("company")
    payload["author"] = request.session.get("user_name")
    payload["reset_token"] =""
    # Fecha y hora actual con zona horaria
    fecha_actual = datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")
    payload["reset_token_expira"] =fecha_actual

    json_payload = json.dumps(payload)

    response = await api.update_data("users", id=user_id, body=json_payload, schema=schema_name)

    if response.get("status") == "success":
        if "change_password" in form_data and form_data["change_password"].strip():
            subject = f"Habilitación de usuario - {company['nomfantasia']} (PANEL DE ADMINISTRACIÓN)"
            title = 'Habilitación'
            message = 'Esto es una copia de su solicitud de habilitación de usuario.'
            respuestasnm = await snm.email_usuarios(user_id, snm_password, subject, title, message,request.session)
    
        Helper.flash_message(request, "success", "Usuario Actualizado correctamente.") 
    else:
        Helper.flash_message(request, "error", response["message" ])       

    return RedirectResponse(url=f"/{empresa}/manager/users", status_code=303)

# Eliminar usuario
@router.get("/delete/{user_id}")
async def delete(request: Request,user_id: int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
        
    schema_name = request.session.get("schema") 
    response=await api.delete_data("users", id=user_id, schema=schema_name)

    if response.get("status") == "success":
        Helper.flash_message(request, "success", "Usuario elimina correctamente.") 
    else:
        Helper.flash_message(request, "error", response["message" ])       

    return RedirectResponse(url=f"/{empresa}/manager/users/", status_code=303)

@router.post("/status")
async def status(request: Request,user_id: int = Form(...),):
    schema_name = request.session.get("schema") 
    response = await api.get_data("users",id=user_id, schema=schema_name)
    user=response['data']
            
    _active = int(user["active"])
      
    if _active == 1:        
        active = 2
    else: 
        active = 1

    class_status = "text-bg-success" if active == 1 else "text-bg-secondary"
    text_status = "Activo" if active == 1 else "Inactivo"

    # Crear payload de actualización
    payload = {
        "active": active,
        "author": request.session.get("user_name")
    }
    json_payload = json.dumps(payload)
    
    response = await api.update_data("users", id=user_id, body=json_payload, schema=schema_name)
    
    return JSONResponse(
        content={
            "status": 1,
            "class_status": class_status,
            "text_status": text_status,
        })