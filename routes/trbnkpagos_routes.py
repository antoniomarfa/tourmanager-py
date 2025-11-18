from fastapi import FastAPI, Request, Form, Depends, APIRouter
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

urlTrbnk="https://webpay3gint.transbank.cl" 
#urlTrbnk="https://webpay3g.transbank.cl"    

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
        
    return templates.TemplateResponse("flowpagos/continuatrbnk.html", {"request": request, "session":request.session,"valorcuota":valorcuota,"nrocuotas":nrocuotas,"fechainicial":fechainicial,"mpagar":mpagar,"fecha":fecha,"identificador":identificador,"info_index":info_index,"helper":Helper,"empresa":empresa})

@router.get("/inicioPagotrbnk", response_class=HTMLResponse)
async def iniciopago(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))
    
    form_data = await request.form()

    result= await api.get_data("sale",id=int(request.session.get('sale')),schema=schema_name)
    venta = result['data'] if result["status"] == "success" else []

    if request.session.get('position')=='General':
        result= await api.get_data("curso",id=int(request.session.get('user_curso')),schema=schema_name)
        curso = result['data'] if result["status"] == "success" else []
            
    else:
        result= await api.get_data("curso",id=int(request.session.get('id')),schema=schema_name)
        curso = result['data'] if result["status"] == "success" else []
         

    NroVta = int(request.session.get('sale'))
    RutAl = int(request.session.get('user_ruta'))
    Monto = form_data.get('mpagar')
    identificador = form_data.get('identificador')
    correo = curso['correo'] 

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

     
    consulta = f'company_id={company_id}&gateway_id=3'
    result= await api.get_data("gateway",query=consulta,schema=schema_name)
    trbnkConn = result['data'][0] if result["status"] == "success" else []     
    #Acceder a los valores
    Tbk_Api_Key_Id = trbnkConn['additional_config']['trbk_commercialcode']
    Tbk_Api_Key_Secret = trbnkConn['additional_config']['trbk_keysecret']

    urlReturn="/trbnkpagos/returnTrbnk"
        
    transaction={
         "buy_order": identificador,
         "session_id": identificador,
         "amount": Monto,
         "return_url": urlReturn
        }
        
    url=f'{urlTrbnk}/rswebpaytransaction/api/webpay/v1.2/transactions'
    # Convertir transaction a JSON
    payload = json.dumps(transaction)

    headers = {
        "Tbk-Api-Key-Id": Tbk_Api_Key_Id,
        "Tbk-Api-Key-Secret": Tbk_Api_Key_Secret,
        "Content-Type": "application/json"
    }

    # Hacer la solicitud POST
    response = requests.post(url, data=payload, headers=headers, timeout=30)  # timeout opcional

    # Obtener la respuesta como diccionario
    result = response.json()

    # Si quieres ver el status y contenido
    status = response.status_code

    #antes de enviar a continuar el pago crear el ingreso comp pendiente
    data = {
            "tipocomp":"COW",
            "fecha":fecha_actual,
            "identificador":identificador,
            "sale_id":venta['id'],
            "curso_id":curso['id'],
            "rutapo": curso['rutapod'],
            "rutalum":curso['rutalumno'],
            "fpago":"FW",
            "monto":Monto,
            "activo":1,
            "status_pago":"En Proceso",
            "token_flow":result['token'],
            "author": request.session.get('user_name'),
            "company_id": request.session.get("company"),
            "valorcuota":valorcuota,
            "nrocuotas":nrocuotas,
            "fechainicial":fecha_inicial,
            "company_id":request.session.get("company"),
            }
        
    insert = await api.set_data("ingreso",body=json.dumps(data),schema=schema_name)

    id_ingreso = insert["data"]["data"]["return_id"]               
    request.session["id_ingreso"]= id_ingreso
    request.session["identificador"], identificador

    next_page=result['url']
    token=result['token']
        
    return templates.TemplateResponse("trbkpagos/continuarpago.html", {"request": request, "session":request.session,"valorcuota":valorcuota,"nrocuotas":nrocuotas,"next_page":next_page,"token":token,"empresa":empresa})


@router.get("/returntrbnk")
async def returntrbnk(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    info_index = await util.formCharge(request.session)
    
    form_data = await request.form()

    consulta=f"company_id={request.session.get('company')}&gateway_id=2"
    result= await api.get_data("gateway",query=consulta,schema=schema_name)
    trbnkConn = result['data'][0] if result["status"] == "sucxcess" else []
    
    #Acceder a los valores
    Tbk_Api_Key_Id = trbnkConn['additional_config']['trbk_commercialcode']
    Tbk_Api_Key_Secret = trbnkConn['additional_config']['trbk_keysecret']

    motivo=[]
    motivo[-1]='Rechazo - Posible error en el ingreso de datos de la transacción'
    motivo[-2]='Rechazo - Se produjo fallo al procesar la transacción, este mensaje de rechazo se encuentra relacionado a parámetros de la tarjeta y/o su cuenta asociada'
    motivo[-3]='Rechazo - Error en Transacción'
    motivo[-4]='Rechazo - Rechazada por parte del emisor'
    motivo[-5]='Rechazo - Transacción con riesgo de posible fraude'

    tpago=[]    
    tpago["VD"] = 'Venta Débito.'
    tpago["VN"] = 'Venta Normal.'
    tpago["VC"] = 'Venta en cuotas.'
    tpago["SI"] = '3 cuotas sin interés.'
    tpago["S2"] = '2 cuotas sin interés.'
    tpago["NC"] = 'N Cuotas sin interés.'
    tpago["VP"] = 'Venta Prepago.'

    token = request.query_params.get("token_ws", None)
    

    if token=="":
        message = " Pago N Completado por webpay "
        mensage1=message
        mensage2=""

        return templates.TemplateResponse("opening/errortransaccion.html", {"request": request, "session":request.session,"info_index":info_index,"mensage1":mensage1,"mensage2":mensage2})

 
    url=f'{urlTrbnk}/rswebpaytransaction/api/webpay/v1.2/transactions/{token}'

    headers = {
        "Tbk-Api-Key-Id": Tbk_Api_Key_Id,
        "Tbk-Api-Key-Secret": Tbk_Api_Key_Secret,
        "Content-Type": "application/json"
    }

    # Hacer la solicitud POST
    response = requests.post(url, headers=headers, timeout=30)  # timeout opcional

    # Obtener la respuesta como diccionario
    result = response.json()

    # Si quieres ver el status y contenido
    status = response.status_code

    #Verificamos resultado  de transacci璐竛 */
    if result['response_code'] == 0:
            
        #Crea el pago en la tabla pagos  **/    
        transaction_date = result["transaction_date"]
        montoingreso= result["amount"]
        nroingreso= result["buy_order"]
        nrotarjeta= result["card_detail"]["card_number"]
        fechaauto= transaction_date
        codigoauto= result["authorization_code"]
        tipopago=tpago[result["payment_type_code"]]
        fechatrans= transaction_date
        fechaingreso=transaction_date
        nrocuotas=result['installments_number']

        #grabar pago si esta ok
        consulta =f'identificador={nroingreso}&company_id={request.session.get("company")}'
        response = await api.get_data("ingreso",query=consulta,schema=schema_name)
        ingresos =response['data'][0] if response["status"] == "success" else []

        response = await api.get_data("curso",id=int(ingresos['curso_id']),schema=schema_name)
        curso = response['data']

        media="TRBNK"

        _ingreso = ingresos['id']
        id = ingresos['id']
        _venta = ingresos['sale_id']
        _RutAl = ingresos['rutalum']
        _nrocuotas = ingresos['nrocuotas']
        _valorcuota = ingresos['valorcuota']
        _fechainicial = ingresos['fechainicial']

        if _nrocuotas>0:
            _dia = _fechainicial[8:10]
            _mes = _fechainicial[5:7]
            _agno = _fechainicial[0:4]

            for i in range(_nrocuotas):
                cuota = i + 1
                
                dato = {
                    "tipocom": "COW",
                    "ingreso_id": _ingreso,
                    "identificador": nroingreso,
                    "fecha": fechaingreso,
                    "sale_id": _venta,
                    "rutalumn": _RutAl,
                    "transaccion": "",
                    "tipo": tipopago,
                    "monto": montoingreso,
                    "nrotarjeta": nrotarjeta,
                    "codigoAuto": codigoauto,
                    "fechaAuto": fechaauto,
                    "tipopago": media,
                    "nrocuota": nrocuotas,
                    "fechatransac": fechatrans,
                    "activo": 1,
                    "author": request.session.get("user_name"),   # equivalente a Helper::sessionSystemValue("user_name")
                    "cuotapagada": cuota,
                    "cuotafecha": f"{_agno}{str(_mes).zfill(2)}",
                    "company_id": request.session.get("company"), # equivalente a Helper::sessionSystemValue("company")
                }

                # convertir a JSON si necesitas mandarlo como string
                dato_json = json.dumps(dato)

                # simular insert con tu método (equivalente a $render->setData(...))
                insert = await api.set_data("pagos", body=dato_json,schema=schema_name)

                # actualizar mes y año
                _mes += 1
                if _mes > 12:
                    _mes = 1
                    _agno += 1

                _mes = str(_mes).zfill(2)
            else:
                dato={
                    "tipocom":"COW",
                    "ingreso_id":_ingreso,
                    "identificador":nroingreso,
                    "fecha":fechaingreso,
                    "sale_id":_venta,
                    "rutalumn":_RutAl,
                    "transaccion":"", 
                    "tipo":tipopago,
                    "monto":montoingreso,
                    "nrotarjeta":nrotarjeta,
                    "codigoAuto":codigoauto,
                    "fechaAuto":fechaauto,
                    "tipopago":media,
                    "nrocuota": nrocuotas,
                    "fechatransac":fechatrans,
                    "activo":1,
                    "author":request.session.get('user_name'),
                    "cuotapagada":0,
                    "cuotafecha":"",
                    "company_id":request.session.get("company"),
                }
                insert = await api.set_data("pagos",body=json.dumps(dato),schema=schema_name)
             
            
            dato = {
               "status_pago":"Pagado"
            }
    
            update = await api.update_data("ingreso",body=json.dumps(dato),id=id,schema=schema_name)
        
            objBody = {}
            objBody["nroingreso"]=result["buy_order"]
            objBody["transaccion"]=result["buy_order"]
            objBody["comprobante"]=""
            objBody["monto"]=result["amount"]
            transaction_date_str = result["transaction_date"]
            dt = datetime.strptime(transaction_date_str, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d-%m-%Y")
            objBody["fecha"]= formatted_date
            transaction_date_str = result["transaction_date"]  # por ejemplo "2025-09-03 14:30:00"
            dt = datetime.strptime(transaction_date_str, "%Y-%m-%d %H:%M:%S")
            formatted_time = dt.strftime("%I:%M:%S")
            objBody["hora"]= formatted_time
            objBody["rut"]=curso['rutapod']
            objBody["media"]=media
            objBody["email"]=curso["correo"]
            
            #self::enviarCorreo($objBody);
            
            form_view = {  
                "estado":"Pagado",
                "nrotarjeta":nrotarjeta,
                "tipopago":tipopago,
                "nrocuotas":nrocuotas,
                "transaccion":result["buy_order"],
                "comprobante":result["buy_order"],
                "monto":result["amount"],
                "fecha": formatted_date,
                 "hora": formatted_time,
                "rut":curso['rutapod'],
                "media":media
            }
            request.session["user_pagado"]="S"
            request.session["paso"] = "3"
        
            return templates.TemplateResponse("flowpagos/vouchertrbk.html", {"request": request, "session":request.session,"form_view":form_view,"empresa":empresa})
        else:
           
            message1= f"""Estimado Cliente, le informamos que su orden {result['buy_order']} 
            realizado el {result['transaction_date']} termino de forma inesperada 
            (Rechazo en Transaccion)"""
            message2= f" Motivo {motivo[result['response_code']]}"

            return templates.TemplateResponse("flowpagos/errortransaccion.html", {"request": request, "session":request.session,"message1":message1,"message2":message2,"empresa":empresa})
