from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import json, uuid, os, bcrypt,re,base64
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction
from libraries.utilities import Utilities
from libraries.flowapi import FlowApi
from docx2pdf import convert

router = APIRouter()

templates = Jinja2Templates(directory="templates")

api = RenderRequest()
rst = Restriction()
util = Utilities()
flowapi = FlowApi()

#APIURL="https://www.flow.cl/api",
APIURL="https://sandbox.flow.cl/api",

# Ruta principal: mostrar usuarios
@router.post("/inicioTransaccion", response_class=HTMLResponse)
async def transesccion(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    info_index = await util.formCharge(request.session)

    ruta_image = f"/uploads/company/logo/login_logo_{request.session.get('code_company', 'GRL_999')}.png"
    ruta_image = os.path.abspath(ruta_image)

    form_data = await request.form()
    mpagar=form_data.get('mpagar')
    print("mpagar ",mpagar)
    if not mpagar or mpagar == 0:
        if request.session.get('position') =='General':
            return RedirectResponse(url=f"/{empresa}/manager/pay/formpayment_rsv", status_code=303)
        else:
            if request.session.get('encuotas')=='S':
                return RedirectResponse(url=f"/{empresa}/manager/pay/formpayment_ct", status_code=303)
            else:
                return RedirectResponse(url=f"/{empresa}/manager/pay/formpayment", status_code=303)

    identificador = uuid.uuid4().hex

    consulta = f"identificador={identificador}"
    result = await api.get_data("ingreso",query=consulta,schema=schema_name);
    contador=len(result['data']) if result["status"] == "success" else 0        

    if contador > 1:
        identificador+=f"-{contador}"
        

    # Fecha de hoy
    hoy = datetime.today()
    fecha = hoy.strftime("%d/%m/%Y")

    fechainicial=""
    nrocuota = form_data.getlist("nrocuota")

    if nrocuota and isinstance(nrocuota, list):
        # aquí es el equivalente a tu if PHP
        print("Cuotas recibidas:", nrocuota)
        nrocuotas = len(form_data.getlist('nrocuota'))
        primera='N'
        for value in form_data.getlist('nrocuota'):
            if primera=="N": 
                fechainicial=form_data.get('fechainicial')
                primera='S'
    else:
        print("No se recibieron cuotas")
        nrocuotas=0
        fechainicial=form_data.get('fechainicial')
    valorcuota=form_data.get('valorcuota')
        
    context = {"request": request, 
               "session":request.session,
               "valorcuota":valorcuota,
               "nrocuotas":nrocuotas,
               "fechainicial":fechainicial,
               "mpagar":mpagar,
               "fecha":fecha,
               "identificador":identificador,
               "info_index":info_index,
               "helper":Helper,
               "empresa":empresa,
               "ruta_image":ruta_image
               }    
    return templates.TemplateResponse("flowpagos/continuaflow.html", context)


@router.post("/iniciopagoflow", response_class=HTMLResponse)
async def iniciopago(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))
    form_data = await request.form()

    result= await api.get_data("company",id=company_id,schema='global')
    company = result['data'] if result["status"] == "success" else []

    result= await api.get_data("sale",id=int(request.session.get('sale')),schema=schema_name)
    venta = result['data'] if result["status"] == "success" else []

    if request.session.get('position')=='General':
        result= await api.get_data("curso",id=int(request.session.get('user_curso_id')),schema=schema_name)
        curso = result['data'] if result["status"] == "success" else []
            
    else:
        result= await api.get_data("curso",id=int(request.session.get('id')),schema=schema_name)
        curso = result['data'] if result["status"] == "success" else []
         
    consulta = f'company_id={company_id}&gateway_id=3'
    result= await api.get_data("gateways",query=consulta,schema=schema_name)
    flowConn = result['data'][0] if result["status"] == "success" else []

    #Acceder a los valores
    flow_apikey = flowConn['additional_config']['flow_apikey']
    flow_secretkey = flowConn['additional_config']['flow_secretkey']

    NroVta = venta['id']
    RutAl = request.session.get('user_ruta') 
    Monto = form_data.get('mpagar')
    identificador = form_data.get('identificador')
    correo = curso['correo']

    if venta['type_sale']=='GE':
        subject = f'pago cuota o reserva vieje estudio de {company["nomfantasia"]}'
    else:
        subject = f'pago cuota o reserva vieje grupal de {company["nomfantasia"]}'

    array={'venta': NroVta ,'alumno':RutAl, 'empresa':company["nomfantasia"]}
    optional = json.dumps(array) 
    params={
        'commerceOrder': identificador,
        'subject':  subject,
        'currency': 'CLP',
        'amount': Monto,
        'email': correo,
        'paymentMethod': 9,
        'urlConfirmation': "https://flowresponse.onrender.com/token",
        'urlReturn': f"{empresa}/manager/pagosflow/returnFlow",
        'optional': optional
        }

    service="payment/create"
    method="POST"

    flowapi.set_api_key(flow_apikey)
    flowapi.set_secret_key(flow_secretkey)
    flowapi.set_api_url(APIURL)
   
    response=flowapi.send(service,params,method)
    
    valorcuota=0 if not form_data.get("valorcuota") else form_data.get("valorcuota")
    nrocuotas=0 if not form_data.get('nrocuotas') else form_data.get('nrocuotas')

    #Grabar el Ingreso con estado procesando
    # Fecha de hoy
    fecha_actual = util.convertir_fecha(datetime.today().strftime("%d/%m/%Y"))

    fecha_inicial= form_data.get('fechainicial')
       
    if not fecha_inicial:  # equivale a empty() en PHP
        fecha_inicial = fecha_actual
    else:   
        fecha_inicial = util.convertir_fecha(fecha_inicial)
        
    data = {
        "tipocomp":"COW",
        "fecha": fecha_actual,
        "identificador": identificador,
        "sale_id": venta['id'],
        "curso_id": curso['id'],
        "rutapo": curso['rutapod'],
        "rutalum": curso['rutalumno'],
        "fpago":"FW",
        "monto": Monto,
        "activo":1,
        "status_pago":"En Proceso",
        "token_flow": response['token'],
        "author": request.session.get('user_name'),
        "company_id": request.session.get("company"),
        "valorcuota": valorcuota,
        "nrocuotas": nrocuotas,
        "fechainicial": fecha_inicial,
        "company_id": request.session.get("company")
    }
        
    insert = await api.set_data("ingreso",body=json.dumps(data),schema=schema_name)

    id_ingreso = insert["data"]["data"]["return_id"]        
    request.session["id_ingreso"] = id_ingreso
    request.session["identificador"]= identificador

    destination=f"{response['url']}?token={response['token']}"
    return RedirectResponse(url=destination)



@router.post("/returnFlow")
async def returnflow(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id = request.session.get("company")

    info_index = await util.formCharge(request.session)

    data = await request.json()
    token = data.get("token")

    consulta =f"token_flow={token}"
    result = await api.get_data("ingreso",query=consulta,schema=schema_name)
    ingreso = result['data'][0] if result["status"] == "success" else []
         
    #Session::set('sale',$ingreso['sale_id']);
    #Session::set('user_curso_id',$ingreso['curso_id']);
    #Session::set('company', $ingreso["company_id"]);
    #Session::set('user_rut',$ingreso['rutapo']);
        
    consulta =f"company_id={company_id}&gateway_id=3"
    result = await api.get_data("gateway",query=consulta,schema=schema_name)
    flowConn = result['data'][0] if result["status"] == "success" else []
    #Acceder a los valores
    flow_apikey = flowConn['additional_config']['flow_apikey']
    flow_secretkey = flowConn['additional_config']['flow_secretkey']


    #Mostrar al clientes si esta ok o no el pago
    flowapi.set_api_key(flow_apikey)
    flowapi.set_secret_key(flow_secretkey)
    flowapi.set_api_url(APIURL)

    service ="payment/getStatus"
    method ="GET"
    params ={'token' : token}

    respuesta=flowapi.send(service,params,method);

    status=int(respuesta["status"])
    if status == 2:
        nroingreso=respuesta["commerceOrder"]
        montoingreso=respuesta["amount"]
        fechaingreso= Helper.convertir_fecha(respuesta["requestDate"])
        fechatrans= Helper.convertir_fecha(respuesta["requestDate"])
        fechaauto= respuesta["requestDate"]
        tipopago='FW'
        media=respuesta["paymentData"]["media"]
        NroVta=respuesta["optional"]["venta"]
        RutAl=respuesta["optional"]["alumno"] 

        objBody = {}
        objBody["nroingreso"]=respuesta["commerceOrder"]
        objBody["transaccion"]=respuesta["flowOrder"]
        objBody["comprobante"]=respuesta["commerceOrder"]
        objBody["monto"]=respuesta["amount"]
        request_date_str = respuesta["requestDate"]
        dt = datetime.strptime(request_date_str, "%Y-%m-%d %H:%M:%S")
        formatted_date = dt.strftime("%d-%m-%Y")
        objBody["fecha"]= formatted_date
        request_date_str = respuesta["requestDate"]  # por ejemplo "2025-09-03 14:30:00"
        dt = datetime.strptime(request_date_str, "%Y-%m-%d %H:%M:%S")
        formatted_time = dt.strftime("%I:%M:%S")
        objBody["hora"]= formatted_time
        objBody["rut"]=respuesta.get("optional", {}).get("RUT", "")
        objBody["media"]=respuesta["paymentData"]["media"]
        objBody["email"]=respuesta["payer"]
            
        enviarCorreo(objBody,request.session)
            
        form_view = {       
            "estado": "Pagado",
            "transaccion": respuesta["flowOrder"],
            "comprobante": respuesta["commerceOrder"],
            "monto": respuesta["amount"],
            "fecha": formatted_date,
            "hora": formatted_time,
            "rut": respuesta.get("optional", {}).get("RUT", ""),
            "media": respuesta["paymentData"]["media"]
        }

        request.session["user_pagado"]="S"
        request.session["paso"] = "3"

        return templates.TemplateResponse("flowpagos/flowresponse.html", {"request": request, "session":request.session,"info_index":info_index,"form_view":form_view,"empresa":empresa})
    else:

        #Devolver a la pagina y mostrar si esta ok o rechazado al cliente
        message1= "Error en pago por flow "
        message2=""

        if status == 1:
            message2= "Pendiente de Pago "
        
        if status == 3:
            message2= "Transaccion Rechazada "
        
        if status == 4:
            message2= "Transaccion Anulada "
        
        request.session["user_pagado"] = ""
        request.session["paso"] = "3"
            
        return templates.TemplateResponse("flowpagos/errortransaccion.html", {"request": request, "session":request.session,"info_index":info_index,"message1":message1,"message2":message2,"empresa":empresa})
        


def enviarCorreo(objBody,session):
    #envio de correo
    schema_name = session.get("schema")