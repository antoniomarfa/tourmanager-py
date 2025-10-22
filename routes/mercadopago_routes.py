from fastapi import FastAPI, Request, Form, Depends, APIRouter, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import json, uuid, os, bcrypt,re,base64, requests
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction
from libraries.utilities import Utilities
from docx2pdf import convert


router = APIRouter()

templates = Jinja2Templates(directory="templates")

api = RenderRequest()
rst = Restriction()
util = Utilities()

# Ruta principal: mostrar usuarios
@router.get("/iniciotransaccion", response_class=HTMLResponse)
async def transesccion(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    info_index = await util.formCharge(request.session)

    form_data = await request.form()

    mpagar=form_data.get('mpagar')
        
    if not mpagar or mpagar == 0:
        if request.session.get('position') =='General':
            return RedirectResponse(url=f"/{empresa}/manager/pay/formpayment_rsv", status_code=303)
        else:
            if request.session.get('encuotas')=='S':
                return RedirectResponse(url=f"/{empresa}/manager/pay/formpayment_ct", status_code=303)
            else:
                return RedirectResponse(url=f"/{empresa}/manager/pay/formpayment", status_code=303)



    if request.session.get('position') =='General':
        request.session['titulo_pago']= 'Pago viaje (reserva)'
    else:
        request.session['titulo_pago'] = 'Pago viaje'
        
        
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

    form_vew={}
    form_vew["valorcuota"] = valorcuota
    form_vew["nrocuotas"] = nrocuotas
    form_vew["fechainicial"] = fechainicial
    form_vew["mpagar"] = mpagar
    form_vew["fecha"] = fecha
    form_vew["identificador"] = identificador

    return templates.TemplateResponse("mercadopago/continuarmpago.html", {"request": request, "session":request.session,"form_vew":form_vew,"info_index":info_index,"helper":Helper,"empresa":empresa})

@router.get("/iniciopagomp", response_class=HTMLResponse)
async def iniciopago(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))
    form_data = await request.form()

    info_index = await util.formCharge(request.session)

    respuesta = await api.get_data("company",id=company_id,schema="global");  
    company = respuesta['data'][0] if respuesta["status"] == "success" else []

    result= await api.get_data("sale",id=int(request.session.get('sale')),schema=schema_name)
    venta = result['data'] if respuesta["status"] == "success" else []

    if request.session.get('position')=='General':
        result= await api.get_data("curso",id=int(request.session.get('user_curso_id')),schema=schema_name)
        curso = result['data'] if respuesta["status"] == "success" else []
            
    else:
        result= await api.get_data("curso",id=int(request.session.get('id')),schema=schema_name)
        curso = result['data'] if respuesta["status"] == "success" else []
     
        
    consulta= f"company_id={company_id}&gateway_id=1"
    result= await api.get_data("gateways",query=consulta,schema=schema_name)
    MpConn= result['data'][0] if respuesta["status"] == "success" else []

    #Acceder a los valores
    public_key = MpConn['additional_config']['mp_publickey']
    access_token = MpConn['additional_config']['mp_accesstoken']

    NroVta=request.session.get('sale')
    RutAl=request.session.get('user_ruta') 
    Monto=int(form_data.get('mpagar'))
    identificador=form_data.get('identificador')
    correo=curso['correo'] 

    #Configuración
    url = 'https://api.mercadopago.com/checkout/preferences'
        
    #Datos de la preferencia
    data = {
        "items": [
            {
                "id": identificador,
                "title": request.session.get("titulo_pago"),  # equivalente a Session::get()
                "quantity": 1,
                "unit_price": Monto,
                "currency_id": "CLP"  # MXN, USD, etc.
            }
        ],
        "statement_descriptor": company["razonsocial"],
        "external_reference": identificador,
        "back_urls": {
            "success": f"/mercadopago/verficarPago",
            "failure": f"/mercadopago/verficarPago",
            "pending": f"/mercadopago/verficarPago"
        },
        "auto_return": "approved",  # Opcional: redirección automática para pagos aprobados
        "binary_mode": True         # Opcional: evita estados pendientes
    }
        
    payload = json.dumps(data)

    auth = f"Bearer {access_token}" 
    headers = {
        "Authorization": auth,
        "Content-Type": "application/json"
    }

    # Hacer la solicitud POST
    response = requests.post(url, data=payload, headers=headers, timeout=30)  # timeout opcional

    # Obtener la respuesta como diccionario
    preference = response.json()

    # Si quieres ver el status y contenido
    status = response.status_code

    if "id" in preference: #equivale a issset        
        valorcuota = form_data.get("valorcuota")
        valorcuota = float(valorcuota) if valorcuota else 0

        nrocuotas=form_data.get('nrocuotas')
        nrocuotas = int(nrocuotas) if nrocuotas else 0   

        #Grabar el Ingreso con estado procesando
        fecha_actual = util.convertir_fecha(datetime.today().strftime("%d/%m/%Y"))
            
        fecha_inicial= form_data.get('fechainicial')
        if not fecha_inicial:  # equivale a empty() en PHP
            fecha_inicial = fecha_actual
        else:   
            fecha_inicial = util.convertir_fecha(fecha_inicial)
        
        data={
            "tipocomp": "COW",
            "fecha": fecha_actual,
            "identificador": identificador,
            "sale_id": venta['id'],
            "curso_id": curso['id'],
            "rutapo": curso['rutapod'],
            "rutalum": curso['rutalumno'],
            "fpago": "FW",
            "monto": Monto,
            "activo": 1,
            "status_pago": "En Proceso",
            "token_flow": "",
            "author": request.session.get('user_name'),
            "valorcuota":valorcuota,
            "nrocuotas":nrocuotas,
            "fechainicial":fecha_inicial,
            "company_id": company_id
         }
           
        insert = await api.set_data("ingreso",body=json.dumps(data),schema=schema_name)
        if insert['status'] == 'success':            
            inserted_id=insert['data']['data']['return_id']
            #Convertin en cookie
            request.session['id_ingreso'] = inserted_id
            request.session['identificador'] = identificador
            request.session['montopagado'] = Monto


            preference=preference['id']            
            

            return templates.TemplateResponse("mercadopago/botondepago.html", {"request": request, "session":request.session,"public_key":public_key,"preference":preference,"info_index":info_index,"helper":Helper,"empresa":empresa})

        else:
            error = f"Error al crear la preferencia: {preference}"
        


# ==========================
# Helpers de tu sistema
# ==========================

#def session_system_value(key: str):
#    # Equivalente a Helper::sessionSystemValue()
#    return "dummy_value"

#def get_session(key: str):
#    # Equivalente a Session::get()
#    return "dummy_value"

#class RenderRequest:
#    def getData(self, table, fields, consulta, extra="", schema=""):
#        # Simula tu llamada a DB
#        return {
#            "data": [
#                {
#                    "additional_config": {
#                        "mp_publickey": "public_key",
#                        "mp_accesstoken": "access_token",
#                        "mp_usersid": "users_id"
#                    }
#                }
#            ]
#        }

#    def updateData(self, table, data, extra, id, schema):
#        print(f"✅ Update en {table}: {data} (ID={id})")

#    def setData(self, table, data, extra1, extra2, extra3):
#        print(f"✅ Insert en {table}: {data}")

#render = RenderRequest()

# ==========================
# Controlador principal
# ==========================
@router.api_route("/mercadopago/verficarPago", methods=["GET", "POST"])
async def verificar_pago(request: Request):
    consulta = f"company_id={request.session.get('company')}&gateway_id=1"
    result = await api.getData("gateway",query=consulta,schema=request.session.get("schema"))
    MpConn = result["data"][0]

    public_key = MpConn["additional_config"]["mp_publickey"]
    access_token = MpConn["additional_config"]["mp_accesstoken"]
    users_id = MpConn["additional_config"]["mp_usersid"]

    if request.method == "POST":
        return await handle_webhook(request, access_token, users_id)
    elif request.method == "GET":
        return await handle_redirect(request, access_token, users_id)
    else:
        return Response(content="Método no permitido", status_code=405)

# ==========================
# Handlers
# ==========================
async def handle_webhook(request: Request, access_token, users_id):
    try:
        data = await request.json()
    except Exception:
        return Response(content="JSON inválido", status_code=400)

    if data.get("type") == "payment":
        payment_id = data.get("data", {}).get("id")
        if payment_id:
            return verify_payment(request,payment_id, "webhook", access_token, users_id)
        else:
            return Response(content="ID de pago no proporcionado", status_code=400)
    else:
        return Response(content="Tipo de notificación no soportado", status_code=400)

async def handle_redirect(request: Request, access_token, users_id):
    params = dict(request.query_params)

    if "payment_id" in params:
        return verify_payment(request,params["payment_id"], "redirect", access_token, users_id)
    elif "preference_id" in params:
        return verify_preference(request,params["preference_id"], access_token, users_id)
    else:
        return Response(content="Parámetros requeridos no encontrados", status_code=400)

# ==========================
# Verificar pago y preferencia
# ==========================
def verify_payment(request: Request,payment_id, source, access_token, users_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return Response(content="Error al consultar el pago", status_code=resp.status_code)

    payment = resp.json()

    # Registrar log
    with open("payments.log", "a") as f:
        f.write(f"[{datetime.now()}] {source} - Payment ID: {payment_id}, Status: {payment['status']}\n")

    return process_payment_status(request,payment, source, users_id)

def verify_preference(request: Request,preference_id, access_token, users_id):
    url = f"https://api.mercadopago.com/checkout/preferences/{preference_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    resp = requests.get(url, headers=headers)
    preference = resp.json()

    if "id" in preference:
        search_url = f"https://api.mercadopago.com/v1/payments/search?sort=date_created&criteria=desc&external_reference={preference_id}"
        resp = requests.get(search_url, headers=headers)
        search_data = resp.json()

        if "results" in search_data and len(search_data["results"]) > 0:
            latest_payment = search_data["results"][0]
            return process_payment_status(request,latest_payment, "redirect", users_id)
        else:
            return Response(content="No se encontraron pagos para esta preferencia", status_code=404)
    else:
        return Response(content="Preferencia no válida", status_code=400)

# ==========================
# Procesar estado del pago
# ==========================
def process_payment_status(request: Request,payment, source, users_id):
    if not validate_payment(payment, users_id):
        return Response(content="Pago no válido para esta cuenta", status_code=403)

    status = payment.get("status")
    message = ""

    if status == "approved":
        message = f"Pago aprobado! ID: {payment['id']}"
        complete_order(request,payment)
    elif status == "pending":
        message = f"Pago pendiente: {payment.get('status_detail')}"
        pending_order(request,payment)
    elif status == "rejected":
        message = f"Pago rechazado: {payment.get('status_detail')}"
        cancel_order(request,payment)
    else:
        message = f"Estado desconocido: {status}"

    if source == "webhook":
        return {"status": "success", "message": message}
    else:
        return Response(show_payment_status_page(payment, message), media_type="text/html")

# ==========================
# Validaciones y lógica de negocio
# ==========================
def validate_payment(request: Request,payment, users_id):
    collector_id = payment.get("collector_id")
    if collector_id != users_id:
        return False

    expected_amount = get_expected_amount(request,payment.get("external_reference"))
    if expected_amount and payment.get("transaction_amount") != expected_amount:
        return False

    return True

def get_expected_amount(request: Request,order_id):
    return request.session.get("montopagado")

# ==========================
# Funciones de órdenes
# ==========================
async def complete_order(request:Request,payment):
    print("✅ Orden completada:", payment["id"])
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))
    #Marcar orden como completada en tu base de datos

    identificador= payment["external_reference"]

    #Buscar el ingreso yla venta 
    consulta=f'identificador={identificador}&company_id={company_id}'
    response = await api.get_data("ingreso",query=consulta,schema=schema_name)
    ingreso=response['data'][0] if response['status']=='success' else []
        
    transaccion= payment["order"]["id"]
    montoingreso=ingreso["monto"]
    fechaingreso = datetime.fromisoformat(payment["date_created"].replace("Z", "+00:00")).date()
    fechatrans= datetime.fromisoformat(payment["date_created"].replace("Z", "+00:00")).date()
    fechaauto=datetime.fromisoformat(payment["date_created"].replace("Z", "+00:00")).date()
    codigoauto=payment["authorization_code"]
    nrotarjeta=payment["last_four_digits"]
    tipopago='MP'
    media=payment["payment_method_id"]
    NroVta=ingreso["sale_id"]
    RutAl=ingreso["rutalum"] 

    if len(ingreso)>0:
        _ingreso=ingreso['id']
        id=ingreso['id']
        _venta=ingreso['sale_id']
        _nrocuotas=ingreso['nrocuotas']
        _valorcuota=ingreso['valorcuota']
        _fechainicial=ingreso['fechainicial']
     

    if _nrocuotas>0:
        _dia=_fechainicial[8:10]
        _mes=_fechainicial[5:7]
        _agno=_fechainicial[:4]

        for i in range(_nrocuotas):
            cuota=i+1
            dato={
                "tipocom":"COW",
                "ingreso_id":_ingreso,
                "identificador":identificador,
                "fecha":fechaingreso,
                "sale_id":_venta,
                "rutalumn":RutAl,
                "transaccion":transaccion, 
                "tipo":tipopago,
                "monto":_valorcuota,
                "nrotarjeta":nrotarjeta,
                "codigoAuto": codigoauto,
                "fechaAuto":fechaauto,
                "tipopago":media,
                "nrocuota": 0,
                "fechatransac":fechatrans,
                "activo":1,
                "author":"",
                "cuotapagada":cuota,
                "cuotafecha":_agno + _mes
                }
                
            insert = await api.set_data("pagos",body=json.dumps(dato), schema=schema_name)
            _mes+=1

            if _mes>12:
                _mes=1
                _agno+=1
            

            _mes=_mes.zfill(2)

                
    else:
        dato={
            "tipocom":"COW",
            "ingreso_id":'.$_ingreso.',
            "identificador":"'.$nroingreso.'",
            "fecha":"'.$fechaingreso.'",
            "sale_id":'.$_venta.',
            "rutalumn":"'.$RutAl.'",
            "transaccion":"'.$transaccion.'", 
            "tipo":"'.$tipopago.'",
            "monto":'.$montoingreso.',
            "nrotarjeta":"",
            "codigoAuto":"",
            "fechaAuto":"'.$fechaauto.'",
            "tipopago":"'.$media.'",
            "nrocuota": 0,
            "fechatransac":"'.$fechatrans.'",
            "activo":1,
            "author":"",
            "cuotapagada":0,
            "cuotafecha":""
        }

        insert = await api.set_data("pagos",body=json.dumps(dato), schema=schema_name)

        _status= "Pagado"
        dato = {
               "status_pago":_status
            }

        update = await api.update_data("ingreso",body=json.dumps(dato),id=ingreso["id"],schema=schema_name)
            
    # Aquí implementa lógica de actualización en DB (render.updateData / render.setData)

async def pending_order(request: Request,payment):
    print("⌛ Orden pendiente:", payment["id"])
    # Actualiza estado a "Pendiente de Pago"
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    identificador= payment["external_reference"]
    consulta=f'identificador={identificador}&company_id={company_id}'
    response = await api.get_data("ingreso",query=consulta,schema=schema_name)
    ingreso=response['data'][0] if response['status']=='success' else []    

    _status= "Pendiente de Pago "

    _status= "Pagado"
    dato = {
               "status_pago":_status
            }

    update = await api.update_data("ingreso",body=json.dumps(dato),id=ingreso["id"],schema=schema_name)
 
async def cancel_order(request: Request,payment):
    print("❌ Orden cancelada:", payment["id"])
    # Actualiza estado a "Transacción Rechazada"
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    identificador= payment["external_reference"]
    consulta=f'identificador={identificador}&company_id={company_id}'
    response = await api.get_data("ingreso",query=consulta,schema=schema_name)
    ingreso=response['data'][0] if response['status']=='success' else []    

    _status= "Transaccion Rechazada "

    _status= "Pagado"
    dato = {
               "status_pago":_status
            }

    update = await api.update_data("ingreso",body=json.dumps(dato),id=ingreso["id"],schema=schema_name)

async def show_payment_status_page(request: Request,payment, message):

    info_index = await util.formCharge(request.session)
    form_view = {}
    form_view["message"]=message;            
    form_view["payment"]=payment['id'];    
    form_view["transaction_amount"]=payment['transaction_amount'];            
    form_view["external_reference"]=payment['external_reference'];    

    return templates.TemplateResponse(
        "mercadopago/success.html",
        {
            "request": request,
            "session": request.session,
            "form_vew": form_view,
            "info_index": info_index,
            "helper": Helper,
            "message": message,
            "payment": payment.get("id"),
            "transaction_amount": payment.get("transaction_amount"),
            "external_reference": payment.get("external_reference"),
        })