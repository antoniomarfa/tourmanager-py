from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import json, uuid, os, bcrypt,re
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
    company_id=int(request.session.get('company'))

    response = await api.get_data("gatewaysc",schema="global")
    gatewaysc = response['data'] if response['status']=='success' else []

    for i in range(len(gatewaysc)):
        item = gatewaysc[i]

        consulta=f'company_id={company_id}&gateway_id={item["id"]}'
        response = await api.get_data("gateways",query=consulta,schema=schema_name)
        gateways= response['data'] if response['status']=='success' else []
        if len(gateways)>0:
            gatewaysc[i]['existe']='S'                
        else:
            gatewaysc[i]['existe']='N'
 
    return templates.TemplateResponse("gateways/index.html", {"request": request,"gatewaysc":gatewaysc,"empresa":empresa})            


#Ingresa los datos de la pasarela
@router.post("/create")
async def create(request:Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    form_data = await request.form()

    data={
        "company_id": form_data.get('company'),
        "gateway_id": form_data.get('gateway_id'),
        "additional_config": {
            "flow_apikey": form_data.get('apikey'),
            "flow_secretkey": form_data.get('secretkey'),
            "trbk_commercialcode": form_data.get('commercialcode'),
            "trbk_keysecret": form_data.get('keysecret'),
            "mp_publickey": form_data.get('publickey'),     
            "mp_accesstoken": form_data.get('accesstoken'),      
            "mp_usersid": form_data.get('usersid')          
        },
       "active": 1
    }

    response = await api.set_data("gateways",body=json.dumps(data), schema=schema_name)
    if response.get("status") == "success":
        message = ""
    
    return RedirectResponse(url=f"/{empresa}/manager/gateways", status_code=303) 

@router.get("/delete/{gtw_id}", response_class=HTMLResponse)
async def edit_form(request: Request,gtw_id:int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id = request.session.get("company")

    response=await api.delete_data("gateways", id=gtw_id, schema=schema_name)
    print(response)
    message=response['status']
    error="Registro eliminado correctamente."
    if message != "success":
        error=response['error']

    return RedirectResponse(url=f"/{empresa}/manager/gateways/", status_code=303)