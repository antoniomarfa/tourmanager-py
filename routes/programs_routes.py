from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import bcrypt
import json
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction

router = APIRouter()

templates = Jinja2Templates(directory="templates")

api = RenderRequest()
rst = Restriction()

# Ruta principal: mostrar usuarios
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    response = await api.get_data("programac",schema=schema_name)
    programas = response["data"] if response["status"] == "success" else []

    cant_access = {  
        "can_update": await rst.access_permission("programas", "UPDATE", request.session),
        "can_delete": await rst.access_permission("programas", "DELETE", request.session),
        "can_insert": await rst.access_permission("programas", "INSERT", request.session)
    }    
    return templates.TemplateResponse("programs/index.html", {"request": request, "programs": programas, "session":request.session, "helper":Helper,"cant_access":cant_access,"empresa":empresa})

# Mostrar formulario de creación
@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    response = await api.get_data("company",schema="global")  # Suponiendo que el servicio se llama 'users'    
    companys = response["data"] if response["status"] == "success" else []    

    response = await api.get_data("country",schema="global")  # Suponiendo que el servicio se llama 'users'    
    countrys = response["data"] if response["status"] == "success" else []    
    response = await api.get_data("airports",schema="global")  # Suponiendo que el servicio se llama 'users'    
    airports = response["data"] if response["status"] == "success" else []      

    programd = []
    response = await api.get_data("roles",schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    roles = response["data"] if response["status"] == "success" else []    
    return templates.TemplateResponse("programs/create.html", {"request": request, "roles":roles, "countrys":countrys,"airports":airports,"programad":programd,"session": request.session,"empresa":empresa})


# Crear programas vía API
@router.post("/create")
async def create(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    form_data = await request.form()
    schema_name = request.session.get("schema")

    # --- Cabecera (Programa) ---
    data = {
        "code": (form_data.get("codigo") or "").strip(),
        "name": (form_data.get("nombre") or "").strip(),
        "active": int(form_data.get("active", 0)),
        "reserva": float(form_data.get("reserva", 0)),
        "author": request.session.get('user_name'),
        "company_id": request.session.get('company'),
        "origincode": form_data.get("origencode"),
        "destinationcode": form_data.get("destinationcode"),
        "origin": form_data.get("origen"),
        "destination": form_data.get("destination")
    }

    # Si usas FastAPI o Flask
    desde = form_data.getlist("desde[]") or []
    hasta = form_data.getlist("hasta[]") or []
    liberado = form_data.getlist("liberado[]") or []
    monto = form_data.getlist("monto[]") or []
    
    resp = await api.set_data("programac", body=json.dumps(data), schema=schema_name)
    if resp.get("status") != "success":
        request.session["flash_message"] = "error"
        request.session["flash_error"] = resp.get("error", "Error al crear el programa")
        return RedirectResponse(url=f"/{empresa}/manager/programs", status_code=303)

    program_id = resp["data"]["data"]["return_id"]
    if len(desde) > 0:
        for i in range(len(desde)):
            if desde[i]:  # equivalente a !empty($desde[$i])
                data = {
                    "programa_id": int(program_id),
                    "desde": int(desde[i]),
                    "hasta": int(hasta[i]),
                    "liberado": int(liberado[i]),
                    "valor": float(monto[i]),
                 }

                json_payload = json.dumps(data)  # convierte a JSON
                insert = await api.set_data("programad",body=json_payload, schema=schema_name)

    request.session["flash_message"] = "success"
    request.session["flash_error"] = "Registro grabado correctamente."
    return RedirectResponse(url=f"/{empresa}/manager/programs", status_code=303)

# Mostrar formulario de edicion
@router.get("/edit/{program_id}", response_class=HTMLResponse)
async def create_form(request: Request,program_id:int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    response = await api.get_data("company",id=request.session.get("company"),schema="global")  # Suponiendo que el servicio se llama 'users'    
    companys = response["data"] if response["status"] == "success" else []    

    response = await api.get_data("country",schema="global")  # Suponiendo que el servicio se llama 'users'    
    countrys = response["data"] if response["status"] == "success" else []    
    response = await api.get_data("airports",schema="global")  # Suponiendo que el servicio se llama 'users'    
    airports = response["data"] if response["status"] == "success" else []    

    response = await api.get_data("programac",schema=schema_name,id=program_id)
    programac = response["data"] if response["status"] == "success" else []

    getQuery=f"programa_id={program_id}"
    response = await api.get_data("programad", query=getQuery, schema=schema_name)
    programad = response["data"] if response["status"] == "success" else None  
    return templates.TemplateResponse("programs/edit.html", {"request": request, "companys":companys,"session": request.session, "session":request.session, "programac": programac, "programad":programad,"countrys":countrys,"airports":airports, "helper":Helper,"empresa":empresa})


# Crear programas vía API
@router.post("/update")
async def create(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    form_data = await request.form()
    schema_name = request.session.get("schema")

    program_id = int(form_data.get("id"))
    # --- Cabecera (Programa) ---
    data = {
        "code": (form_data.get("codigo") or "").strip(),
        "name": (form_data.get("nombre") or "").strip(),
        "active": int(form_data.get("active", 0)),
        "reserva": float(form_data.get("reserva", 0)),
        "author": request.session.get('user_name'),
        "origincode": form_data.get("origencode"),
        "destinationcode": form_data.get("destinationcode"),
        "origin": form_data.get("origen"),
        "destination": form_data.get("destination")
    }

    # Si usas FastAPI o Flask
    desde = form_data.getlist("desde[]") or []
    hasta = form_data.getlist("hasta[]") or []
    liberado = form_data.getlist("liberado[]") or []
    monto = form_data.getlist("monto[]") or []
    
    resp = await api.update_data("programac", id=program_id, body=json.dumps(data), schema=schema_name)
    if resp.get("status") != "success":
        request.session["flash_message"] = "error"
        request.session["flash_error"] = resp.get("error", "Error al crear el programa")
        return RedirectResponse(url=f"{empresa}/manager/programs", status_code=303)

    #Eliminar el detalle de los programas y grabar
    delete = await api.delete_data("programad", id=program_id, schema=schema_name)

    program_id = resp["data"]["data"]["return_id"]
    if len(desde) > 0:
        for i in range(len(desde)):
            if desde[i]:  # equivalente a !empty($desde[$i])
                data = {
                    "programa_id": int(program_id),
                    "desde": int(desde[i]),
                    "hasta": int(hasta[i]),
                    "liberado": int(liberado[i]),
                    "valor": float(monto[i]),
                 }

                json_payload = json.dumps(data)  # convierte a JSON
                insert = await api.set_data("programad",body=json_payload, schema=schema_name)

    request.session["flash_message"] = "success"
    request.session["flash_error"] = "Registro grabado correctamente."
    return RedirectResponse(url=f"{empresa}/manager/programs", status_code=303)

#Eliminar el programa y el detalle
@router.get("/delete/{program_id}")
async def delete(request: Request,program_id: int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema") 
    response=await api.delete_data("programac", id=program_id, schema=schema_name)

    #Eliminar el detalle de los programas y grabar
    delete = await api.delete_data("programad", id=program_id, schema=schema_name)
    print("det ",delete)
    return RedirectResponse(url=f"/{empresa}/manager/programs/", status_code=303)

#Busca aeropuertos de origen
@router.post("/origin")
async def getorigin(origin_id: str = Form(...)):
    getQuery=f"country={origin_id}"
    response = await api.get_data("airports",query=getQuery, schema="global")
    airport=response['data'] if response["status"] == "success" else []
    print("origin ",airport)
    return JSONResponse(content={"data": airport})

#Busca aeropuertos de destinos
@router.post("/destination")
async def getdestination(destination_id: str = Form(...),):
    getQuery=f"country={destination_id}"
    response = await api.get_data("airports",query=getQuery, schema="global")
    airport=response['data'] if response["status"] == "success" else []
    return JSONResponse(
        content={
            "data": airport
        })

#cambia esl status del programa
@router.post("/status")
async def status(request: Request,programa_id: int = Form(...),):
    schema_name = request.session.get("schema") 
    response = await api.get_data("programac",id=programa_id, schema=schema_name)
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
    
    response = await api.update_data("programac", id=programa_id, body=json_payload, schema=schema_name)
    
    return JSONResponse(
        content={
            "status": 1,
            "class_status": class_status,
            "text_status": text_status,
        })