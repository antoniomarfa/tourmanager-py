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

# Ruta principal: mostrar colegios
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")
    getQuery="company_id=0"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools0 = response["data"] if response["status"] == "success" else []

    company_id=int(request.session.get('company'))
    getQuery=f"company_id={company_id}"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools1 = response["data"] if response["status"] == "success" else []

    schools0.extend(schools1)
    schools = schools0
    flash_respuesta = request.session.get("flash_respuesta")

    cant_access = {  
        "can_update": await rst.access_permission("school", "UPDATE", request.session),
        "can_delete": await rst.access_permission("school", "DELETE", request.session),
        "can_insert": await rst.access_permission("school", "INSERT", request.session)
    }
    flash = Helper.get_flash(request)


    context = {
        "request": request, 
        "schools": schools, 
        "session":request.session, 
        "helper":Helper,
        "cant_access":cant_access,
        "empresa":empresa,
        "msg": flash.get("success"),
        "error": flash.get("error")
        }

    return templates.TemplateResponse("schools/index.html", context)

# Mostrar formulario de creación
@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")
    response = await api.get_data("region",schema="global")  # Suponiendo que el servicio se llama 'users'    
    regions = response["data"] if response["status"] == "success" else []

    response = await api.get_data("comunas",schema="global")  # Suponiendo que el servicio se llama 'users'    
    communes = response["data"] if response["status"] == "success" else []

    response = await api.get_data("company",schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    companys = response["data"] if response["status"] == "success" else []

    context = {"request": request, "companys":companys,"session": request.session, "session":request.session, "regions":regions, "communes":communes,"empresa":empresa} 
 
    return templates.TemplateResponse("schools/create.html", context)

# Crear colegios vía API
@router.post("/create", response_class=HTMLResponse)
async def create(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")
    form_data = await request.form()

    data = {
        "codigo": form_data.get('codigo'),
        "nombre": form_data.get('colegio'),
        "direccion": form_data.get('direccion'),
        "comuna": "",
        "latitud": 0,
        "longitud": 0,
        "region_id": int(form_data.get('region_id')),
        "comuna_id": int(form_data.get('commune_id')),
        "company_id": request.session.get("company_id", 0)
	}
    resp = await api.set_data("colegio", body=json.dumps(data), schema=schema_name)

    if resp.get("status") == "success":
        Helper.flash_message(request, "success", "Colegio creado correctamente.") 
    else:
        Helper.flash_message(request, "error", resp["message" ])       

    return RedirectResponse(url=f"/{empresa}/manager/schools", status_code=303)


# Mostrar formulario de edición
@router.get("/edit/{colegio_id}", response_class=HTMLResponse)
async def edit_form(request: Request, colegio_id: int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")

    response = await api.get_data("region",schema="global")  # Suponiendo que el servicio se llama 'users'    
    regions = response["data"] if response["status"] == "success" else []

    response = await api.get_data("comunas",schema="global")  # Suponiendo que el servicio se llama 'users'    
    communes = response["data"] if response["status"] == "success" else []

    response = await api.get_data("colegio",id=colegio_id ,schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    school = response["data"] if response["status"] == "success" else []

    context={"request": request, "school": school, "regions":regions, "communes":communes,"session": request.session,"empresa":empresa}
    return templates.TemplateResponse("schools/edit.html", context)

# Actualizar compañia
@router.post("/update")
async def update(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")
    form_data = await request.form()

    colegio_id = int(form_data.get("id"))

    data = {
        "codigo": form_data.get('codigo'),
        "nombre": form_data.get('colegio'),
        "direccion": form_data.get('direccion'),
        "comuna":"",
        "latitud":0,
        "longitud":0,
        "region_id": int(form_data.get('region_id')),
        "comuna_id": int(form_data.get('commune_id')),
        "company_id": request.session.get("company_id", 0)
	}

    resp = await api.update_data("colegio", id=colegio_id, body=json.dumps(data), schema=schema_name)

    if resp.get("status") == "success":
        Helper.flash_message(request, "success", "Colegio actualizado correctamente.") 
    else:
        Helper.flash_message(request, "error", resp["message" ])     
            
        return RedirectResponse(url=f"/{empresa}/manager/schools", status_code=303)

# Eliminar colegio
@router.get("/delete/{user_id}")
async def delete(request: Request,user_id: int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
        
    schema_name = request.session.get("schema") 
    response=await api.delete_data("colegio", id=user_id, schema=schema_name)

    if response.get("status") == "success":
        Helper.flash_message(request, "success", "Colegio eliminado correctamente.") 
    else:
        Helper.flash_message(request, "error", response["message" ])       

    return RedirectResponse(url=f"/{empresa}/manager/schools/", status_code=303)

@router.post("/getcomune")
async def status(request: Request,region_id: int = Form(...),):
    getQuery=f"regions_id={region_id}"
    response = await api.get_data("comunas",query=getQuery, schema="global")
    communes=response['data']
    return JSONResponse(
        content={
            "data": communes
        })