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
    
    getQuery=f'activo=1&state=V&company_id={company_id}'
    response = await api.get_data("sale",query=getQuery,schema=schema_name)
    ventas=response['data'] if response["status"] == "success" else []

    cant_access = {  
        "can_update": await rst.access_permission("course", "UPDATE", request.session),
        "can_delete": await rst.access_permission("course", "DELETE", request.session),
        "can_insert": await rst.access_permission("course", "INSERT", request.session),
        "can_export_report": True # await rst.access_permission("users", "EXPORT_REPORT", request.session)
    }

    return templates.TemplateResponse("voucher/index.html", {"request": request, "session":request.session, "cant_access":cant_access, "sales": ventas,"empresa":empresa})

#llena la tabla
@router.post("/gettable", response_class=HTMLResponse)
async def gettable(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))

    can_update = await rst.access_permission("course", "UPDATE", request.session),
    can_delete = await rst.access_permission("course", "DELETE", request.session),

    request.session['filter_sale']=""
    form_data = await request.form()
    venta = int(form_data.get('venta') or 0)

    request.session['filter_sale'] = venta
    table_body = []

    if venta ==0:
        response = await api.get_data("voucher",schema=schema_name)
        vouchers=response['data'] if response["status"] == "success" else []
    else:
        getQuery = f'sale_id={venta}'
        response = await api.get_data("voucher",query=getQuery,schema=schema_name)
        vouchers=response['data'] if response["status"] == "success" else []

        
    for voucher in vouchers:
        if voucher['used'] == 0:
            usado='<a style="cursor: pointer;"><span class="badge text-bg-danger">No Cobrado</span></a>';   
        else:
            usado='<a style="cursor: pointer;"><span class="badge text-bg-success">Cobrado</span></a>';   
            
        if can_delete and voucher['used'] == 0: 
               button=f"<a class='btn btn-sm btn-danger delete-register' data-id='{voucher['id']}'><i class='fa fa-trash'></i></a>"
        else:
             button=''

        table_body.append([
                voucher["sale_id"],
                voucher["voucher"],
                usado,
                button                                          
        ])   

    return JSONResponse(content={"data": table_body})

#Graba el Voucher
@router.post("/setvoucher", response_class=HTMLResponse)
async def setvoucher(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))

    can_update = await rst.access_permission("course", "UPDATE", request.session),
    can_delete = await rst.access_permission("course", "DELETE", request.session),

    form_data = await request.form()

    venta = int(form_data.get('venta'))
    voucher = str(form_data.get('voucher') or "")
    tbody=[]

    if venta and voucher:
        getQuery=f'sale_id={venta}&voucher={voucher}'
        response = await api.get_data("voucher",query=getQuery,schema=schema_name)
        existe=response['data'] if response["status"] == "success" else []

        if existe:
            error = 1
            message = 'Voucher Ingresado Existe.'
            data=""
        else:
            data={
                "sale_id":venta,
                "voucher":voucher,
                "used":0,
                "company_id": company_id
                }

            insert = await api.set_data("voucher",body=json.dumps(data), schema=schema_name)

            if insert['status']=='success': 
                error = 0
                message = 'Voucher Ingresado correctamente.'
                voucher_id = insert["data"]["data"]["return_id"]
                if can_delete: 
                    button=f'<a class="btn btn-sm btn-danger delete-register" data-id="{voucher_id}"><i class="fa fa-trash"></i></a>'
                else:
                    button=""

                usado='<a style="cursor: pointer;"><span class="badge text-badge-danger">No Cobrado</span></a>';   

                tbody=[
                    venta,
                    voucher,
                    usado,
                    button
                ]

            else:
                error = 1
                message = 'Falta Informacion.'

    return JSONResponse(
        content={
            'error': error,
            'message': message,
            'data': tbody,
        })

# Eliminar voucher
@router.get("/delete/{voucher_id}")
async def delete(request: Request,voucher_id: int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema") 
    print(" ",voucher_id)
    response=await api.delete_data("voucher", id=voucher_id, schema=schema_name)
    print("respusta ",response)
    message=response['status']
    error="Registro eliminado correctamente."
    if message != "success":
        error=response['error']
    request.session['flash_message'] = message    
    request.session['flash_error'] = error    

    return RedirectResponse(url=f"/{empresa}/manager/voucher/", status_code=303)