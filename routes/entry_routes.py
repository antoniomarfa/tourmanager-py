from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import json, uuid, smtplib
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction
from email.message import EmailMessage

router = APIRouter()

templates = Jinja2Templates(directory="templates")

api = RenderRequest()
rst = Restriction()

fpago={
    "EF": "Efectivo",
    "CH": "Cheque",
    "TC": "tarj. Credito",
    "TR": "Transferencia",
    "IN": "Ingreso",
    "VO": "Voucher",
    "FW": "Flow"
    }


# Ruta principal: mostrar usuarios
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
        
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))


    cant_access = {  
       # "can_update": await rst.access_permission("quotes", "UPDATE", request.session),
       # "can_delete": await rst.access_permission("quotes", "DELETE", request.session),
        "can_insert": await rst.access_permission("quotes", "INSERT", request.session)
    }
    return templates.TemplateResponse("entry/index.html", {"request": request, "session":request.session,"cant_access":cant_access,"empresa":empresa})


#llena la tabla
@router.post("/gettable", response_class=HTMLResponse)
async def gettable(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))
    can_update= await rst.access_permission("quotes", "UPDATE", request.session),
    can_delete= await rst.access_permission("quotes", "DELETE", request.session),

    _schools={}
    consulta=f"company_id=0"
    response = await api.get_data("colegio",query=consulta,schema=schema_name)
    schools1=response['data'] if response['status']=="success" else []
    consulta=f"company_id={company_id}"
    response = await api.get_data("colegio",query=consulta,schema=schema_name)
    schools2=response['data'] if response['status']=="success" else []
    schools1.extend(schools2)   
    schools = schools1
    
    for school in schools:
        _schools[school['id']]=school['nombre']
        
    consulta=f'company_id={company_id}'    
    response = await api.get_data("ingreso/informe",query=consulta,schema=schema_name)
    ingresos=response['data'] if response['status']=='success' else []
    table_body = [] 
    if ingresos:
        for ingreso in ingresos: 

                sale=ingreso['sale']
                cursos=ingreso['curso']

                class_status = "success" if ingreso['activo'] == 1 else  "default"
                text_status = "Activo" if ingreso['activo'] == 1 else "Inactivo"

                status=f'<span class="badge text-bg-{class_status}">{text_status}</span>'
                colegio=_schools.get(sale['establecimiento_id'], "Desconocido")
                curso=f"{sale['curso']} / {sale['idcurso']}"

                alumno=""
                apoderado=""

                alumno=cursos["nombrealumno"]
                apoderado=cursos["nombreapod"]   

                actions=""
                if can_delete:
                    if ingreso['activo'] == 1:
                      actions = f'<a type="button" class="btn btn-sm btn-danger cancel-register" data-toggle="tooltip" data-placement="top" title="" data-original-title="Eliminar" id="{ingreso["id"]}"><i class="fa fa-trash-o"></i></a>'
                                
                            

                table_body.append([
                    ingreso['identificador'],
                    ingreso['tipocomp'],
                    Helper.formatear(ingreso['fecha']),
                    ingreso['sale_id'],
                    alumno,
                    apoderado,
                    colegio,
                    curso,
                    Helper.formato_numero(ingreso['monto']),
                    ingreso['fpago'],
                    status,
                    actions
                ]) 
            
        return JSONResponse(content={"data": table_body})
    else:
        return JSONResponse(content={"data": []})   
    

@router.get("/create", response_class=HTMLResponse)
async def create(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")


    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    hoy = datetime.today()
    fecha_hoy = hoy.strftime("%Y-%m-%d")

    cant_access = {  
       # "can_update": await rst.access_permission("quotes", "UPDATE", request.session),
       # "can_delete": await rst.access_permission("quotes", "DELETE", request.session),
        "can_insert": await rst.access_permission("quotes", "INSERT", request.session)
    }
    return templates.TemplateResponse("entry/create.html", {"request": request, "session":request.session,"cant_access":cant_access,"fpago":fpago,"fecha_hoy":fecha_hoy,"empresa":empresa})

#Crea los pasajeros
@router.post("/create")
async def create(request:Request):
    empresa = request.state.empresa 
    
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    form_data = await request.form()

    #if form_data.get('typesale') == 'VG':
    nro_venta=int(form_data.get('nroventa'))

    response = await api.get_data("sale",id=nro_venta,schema=schema_name)
    sales=response['data'] if response['status'] == 'success' else []        
        
    nombreapod = correo =""

    id_curso=int(form_data.get('curso_id'))
    response = await api.get_data("curso",id=id_curso,schema=schema_name)
    curso=response['data'] if response['status'] == 'success' else []          
    if curso:
        nombreapod=curso['nombreapod']
        correo=curso['correo']
        curso_id=curso['id']
        

    identificador = 'ING_'+ uuid.uuid1().hex

    fecha_obj = form_data.get('fecha')
    if fecha_obj:
        fecha = datetime.fromisoformat(fecha_obj).strftime('%Y-%m-%dT00:00:00Z')
        
    data={
        "tipocomp": "COF",
        "fecha":  fecha,
        "identificador": identificador,
        "sale_id": int(form_data.get('nroventa')),
        "curso_id": int(curso_id),
        "rutapo": form_data.get('rutapoderado'),
        "rutalum": form_data.get('rutalumno'),
        "fpago": form_data.get('fpago'),
        "monto": int(form_data.get('apagar')),
        "activo": 1,
        "status_pago": "Pagado",
        "author":  request.session.get('user_name'),
        "token_flow":"",
        "nrocuotas":0,
        "valorcuota":0,
        "fechainicial": fecha,                
        "company_id": company_id,
    }
    print("json ",json.dumps(data))      
    insert = await api.set_data("ingreso",body=json.dumps(data), schema=schema_name)
    print("ingresos ",insert)
    if insert['status']=='success':            
        
        inserted_id=insert['data']['data']['return_id']
             
        dato_p={
            "tipocom": "COF",
            "ingreso_id": int(inserted_id),
            "identificador": identificador,
            "fecha": fecha,
            "sale_id":int(form_data.get('nroventa')),
            "rutalumn":form_data.get('rutalumno'),
            "transesccion":"",
            "tipo":form_data.get('fpago'),
            "monto":int(form_data.get('apagar')),
            "nrotarjeta":form_data.get('voucher'),
            "codigoAuto":"",
            "fechaAuto":"",
            "tipopago":"",
            "nrocuota": 0,
            "fechatransac": fecha,
            "activo": 1,
            "author": request.session.get('user_name'),
            "company_id":0,
            "cuotapagada":0,
            "cuotafecha":"",
            "company_id":company_id,
        }
             
        insert = await api.set_data("pagos",body=json.dumps(dato_p), schema=schema_name)

        #if Helper.format_date_action('fpago')=='VO' :
           #enviarCorreo(inserted_id,nombreapod,correo,company_id)

    return RedirectResponse(url=f"/{empresa}/manager/entry", status_code=303) 

@router.get("/listpay", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    response = await api.get_data("sale",schema=schema_name)
    ventas = response['data'] if response['status'] == 'success' else []
            
    cant_access = {  
       # "can_update": await rst.access_permission("quotes", "UPDATE", request.session),
       # "can_delete": await rst.access_permission("quotes", "DELETE", request.session),
        "can_insert": await rst.access_permission("quotes", "INSERT", request.session)
    }
    return templates.TemplateResponse("entry/listpay.html", {"request": request, "session":request.session,"cant_access":cant_access,"sales":ventas,"empresa":empresa})

#llena la tabla
@router.post("/getlistpay", response_class=HTMLResponse)
async def getlistpay(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))
    
    request.session['filter_sales']=""
    table_body = []
    form_data = await request.form()
    venta = int(form_data.get('venta') or 0)

    getQuery="company_id=0"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools0 = response["data"] if response["status"] == "success" else []

    getQuery=f"company_id={company_id}"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools1 = response["data"] if response["status"] == "success" else []

    schools0.extend(schools1)   
    schools = schools0
     # después de combinar schools0 y schools1
    schools_dict = {s["id"]: s["nombre"] for s in schools}


    if venta != 0:    
        request.session['filter_sales']=venta
        consulta=f'sale_id{venta}&company_id={company_id}'
        response = await api.get_data("curso/informe",query=consulta,schema=schema_name)
        cursos = response['data'] if response['status'] == 'success' else []
        
        if cursos:
           for curso in cursos:
              
                #Buscar lo pagado
                pagado=0;  
                Ult_ingredo=''
                fec_ingreso=''
                monto_ingreso=''

                #Venta
                colegio=curso['sale']['establecimiento_id']
                cursoid= cursoid = f"{curso['sale']['curso']}/{curso['sale']['idcurso']}"

                for  saldo in curso['pago']:
                    if saldo['activo']== 1 and saldo['status_pago']=='Pagado':
                        pagado +=saldo['monto']
                        Ult_ingredo =saldo['id']
                        fec_ingreso =saldo['fecha']
                        monto_ingreso =saldo['monto']
                    
                

                pendiente=curso['apagar']-pagado

                table_body.append([
                    f'<a style="cursor:pointer" class="show-compact-entry" id="{curso["id"]}"><i class="fa fa-file" ></i></a>',
                    schools_dict[colegio],
                    cursoid,
                    curso['rutapod'],
                    curso['nombreapod'],
                    curso['nombrealumno'],
                    Helper.formato_numero(curso['apagar']),
                    Helper.formato_numero(pagado),
                    Helper.formato_numero(pendiente),
                    Ult_ingredo,
                    Helper.formatear(fec_ingreso),
                    Helper.formato_numero(monto_ingreso),
                    curso['sale_id'],
                    curso['id'],
                ])
            
        return JSONResponse(content={"data": table_body})
    else:
        return JSONResponse(content={"data": []})


@router.post("/getentries")
async def entradas(request: Request,curso_id:int=Form(...)):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    content_pagos ="" 
    monto_pagado = saldo_apagar =0

    consulta=f"company_id={company_id}&status_pago=Pagado&curso_id={curso_id}&activo=1"
    response = await api.get_data("ingreso/informe",query=consulta,schema=schema_name)
    pagos=response['data'] if response['status'] == 'success' else []
       
    if pagos:
        content_pagos += f'''
            <tr>
                <td colspan="3" align="center">SIN INGRESOS</td>
            </tr>
            '''
    else:
        for item in pagos:
            valor_programa = item['sale']['vprograma']
            alumno= item['curso']['nombrealumno']

            for  pago in item['pago']:
                content_pagos += f'''
                    <tr>
                        <td>{pago['ingreso_id']}</td>
                        <td>{Helper.formatear_modificador(pago['fecha'])}</td>
                        <td>{pago['transaccion']}</td>
                        <td>{Helper.formatear_modificador(pago['fechatransac'])}</td>
                        <td>{pago['tipopago']}</td>
                        <td>{pago['nrotarjeta']}</td>
                        <td>{Helper.formato_numero(pago['monto'])}</td>
                    </tr>
                    '''
                monto_pagado += pago['monto']
            
        saldo_apagar=valor_programa - monto_pagado

        data = f'''
        <div class="row">
            <div class="col-sm-12 invoice-left">
                <h3>Alumno : {alumno} </h3>
            </div>
        </div>

        <hr class="margin" />

        <h4><i class="fa fa-chevron-right" aria-hidden="true"></i> Detalle</h4>
        <table class="table table-bordered table-hover table-condensed">
            <thead>
            <tr>
                <th>Nro Ingreso</th>
                <th>Fecha</th>
                <th>Tansaccion</th>
                <th>Fecha</th>
                <th>Tipo Pago</th>
                <th>Docto Pago</th>
                <th>Monto</th>
            </tr>
            </thead>
            <tbody>
            {content_pagos} 
            </tbody>
        </table>
        <br>
        <hr>
        <table class="table table-bordered table-hover table-condensed">
            <tr>
            <td> <b>Valor Programa</b></td>
            <td> <b>{Helper.formato_numero(valor_programa)}</b></td>
            <td> <b>Valor Pagado</b></td>
            <td> <b>{Helper.formato_numero(monto_pagado)}</b></td>
            <td> <b>Saldo por pagar</b></td>
            <td> <b>{Helper.formato_numero(saldo_apagar)}</b></td>
            </tr>
        </table>
        '''
    return JSONResponse(content={"data": data})


@router.post("/getporcurso")
async def procurso(request: Request,rut_ap:str=Form(...),rut_al:str=Form(...)):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    venta = monto = pagado= saldo=0
    rutal = nombreal= rutapo = nombreapo = ""

 # Mapear valores
    rutap = rut_ap
    rutal = rut_al

    # Construir consulta
    consulta = ""
    if rutal:
        consulta = f"rutalumno={rutal}"
    elif rutap:
        consulta = f"rutapod={rutap}"

    result = await api.get_data("curso", query=consulta, schema=schema_name)
    curso = result['data'][0] if result['status'] == 'success' and result['data'] else None

    if curso:
        # Buscar pagos
        consulta = f'curso_id={curso["id"]}&status_pago=Pagado&activo=1'
        result = await api.get_data("ingreso", query=consulta, schema=schema_name)
        pagos = result['data'] if result['status'] == 'success' else []

        for pago in pagos:
            pagado += pago['monto']

        saldo = curso['apagar'] - pagado
        venta = curso['sale_id']
        rutal = curso['rutalumno']
        nombreal = curso['nombrealumno']
        rutapo = curso['rutapod']
        nombreapo = curso['nombreapod']
        monto = curso['apagar']
        curso_id = curso['id']

    return JSONResponse(
        content={
            'venta': venta,
            'rutal': rutal,
            'nombreal': nombreal,
            'rutapo': rutapo,
            'nombreapo': nombreapo,
            'saldo': Helper.formato_numero(saldo),
            'monto': Helper.formato_numero(monto),
            'curso_id': curso_id,
        })

@router.post("/getvoucher")
async def voucher(request: Request,voucher:int=Form(...),venta:int=Form(...)):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    error=0
    message=""

    nro_voucher=voucher
    nro_venta=venta
        
    consulta = f'voucher={nro_voucher}&sale_id={nro_venta}&used=0'
    response = await api.get_data("voucher",query=consulta,schema=schema_name)
    voucher = response['data'] if response['status'] == 'success' else []     
        
    if voucher:
        data=""
        #Buscar si exste el voucher existe en ventas
        consulta=f'nrotarjeta={nro_voucher}&sale_id={nro_venta}'
        response = await api.get_data("pagos",query=consulta,schema=schema_name)
        existe_pago= response['data'] if response['status'] == 'success' else []  
        
        if existe_pago:
            error=1
            message="Voucher esta cobrado"
        else:
            error=1
            message="Vocuher ok, Una vez grabado, se enviara correo al apoderado con su usuario y clave"
                
    else:
        error=1
        message="Voucher No Existe o ya esta cobrado, Verificar para continuar"
        
     
    return JSONResponse(
        content={
            'error': error,
            'message': message
         })

@router.post("/status")
async def status(request: Request,id_ingreso:int=Form(...)):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    class_status = text_status = ''
    status = 0

    response = await api.get_data("ingreso",id=id_ingreso,schema=schema_name)
    ingreso=response['data'] if response['status'] == 'success' else []

    active = 1 if ingreso['estado'] == 2 else 1

    post = {
        "activo": active,
        "author": request.session.get('user_name')
        }

    update = await api.update_data("ingreso",body=json.dumps(post),id=id_ingreso,schema=schema_name)
    if update['status']=='success':            
        class_status = "badge-success" if active == 1 else "badge-default"
        text_status ="Activo" if active == 1 else "Inactivo"
        status = 1
        
    return JSONResponse(
        content={"status": status, "class_status": class_status, "text_status": text_status})


@router.post("/cancel/{ingreso_id}")
async def cancel(request: Request,ingreso_id:int):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")


    schema_name = request.session.get("schema")

    response = await api.get_data("ingreso",id=ingreso_id,schema=schema_name)
    ingreso= response['data'] if response['status'] == 'success' else []
            
    post = {
        "activo": 2,
        "author": request.session.get('user_name')
        }

    update = await api.update_data("ingreso",body=json.dumps(post),id=ingreso_id,schema=schema_name)
    if update['status']=='success':            
        consulta=f"ingreso_id={ingreso_id}"
        await api.update_data("pagos",body=json.dumps(post),id=ingreso_id,schema=schema_name)

    return RedirectResponse(url=f"/{empresa}/manager/entry", status_code=303) 

@staticmethod
async def enviar_correo(id, name, correo,company_id):

    response = await api.get_data("company",id=company_id,schema='global')
    companys = response['data'] if response['status'] == 'success' else []     

    _title = 'Habilitación'
    asunto=f'Habilitación de usuario - {companys["nomfantasia"]} (PANEL DE APODERADOS)'
    message = f"""espero se encuentre bien, a cuntinuacion le detallo los dato de acceso al plataforma de apoderados,
        desde el cual podra revisar los datos de sub hijo(a), completar la ficha medica, aceptar el contrato, pagar o hacer abonos al valor del viaje"""

    CSS_TABLE_MAIN = 'style="margin-left: auto; margin-right: auto; padding: 0; box-shadow: 0 0 10px rgba(0,0,0,.2); font-family: sans-serif; font-size: 14px; background: #FFF; border: 1px solid #ddd; width: 635px; color: #555555; line-height: 18px; border-spacing: 0; border-radius: 6px;"'
    CSS_H1_MAIN = 'style="margin: 10px 0; color: "#2e58a6" font-size: 26px;"'
    CSS_H1_MAIN_STRONG = 'style="color:#555"'
    CSS_HR = 'style="display: block; border: none; border-top: 2px solid #f2f2f2;"'
    CSS_TABLE_SECONDARY = 'style="width: 100%; border: 1px solid #ddd; border-bottom: 0; border-spacing: 0; font-size: 12px; line-height: 16px;"'
    CSS_FOOTER = 'style="display: block; padding: 10px; margin: 0; background: "#2e58a6"; color: #FFF; text-align: center;font-size:12px;"'
    CSS_FOOTER_LINK = 'style="color: #FFF; text-decoration:none;"'
    CSS_TABLE_SECONDARY_BODY_TH = 'style="border-bottom: 1px solid #ddd; padding: 5px; background-color:"#f6f6f6" text-align: left; border-right: 1px solid #ddd;"'
    CSS_TABLE_SECONDARY_BODY_TD = 'style="border-bottom: 1px solid #ddd; padding: 5px; background-color: #fff; text-align: left; border-right: 1px solid #ddd;"'

    cuerpo= f'''
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http: //www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html xmlns="http: //www.w3.org/1999/xhtml">
            
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <title>Documento sin título</title>
            </head>
            
            <body style="background: #f4f4f4; padding: 20px;">
                <table width="635" border="0" valign="top" {CSS_TABLE_MAIN}>
                    <tbody>
                        <tr>
                        <td style="padding: 0; margin: 0; border: 0; width: 635px;">
                            <img src="cid:imgHeader" style="border-radius: 6px 6px 0 0; border-bottom:1px solid #f2f2f2">
                        </td>
                        </tr>
                        <tr><!-- TITULAR -->
                        <td style="display: block; padding: 5px 15px; text-align: center;">
                            <h1 {CSS_H1_MAIN}>{_title}<strong {CSS_H1_MAIN_STRONG}>Usuario</strong></h1>
                        </td>
                        </tr>
            
                        <tr><!-- SEPARADOR -->
                        <td style="display: block; padding: 0 15px;"><hr {CSS_HR}></td>
                        </tr>
            
                        <tr><!-- CONTENIDO TITULAR -->
                        <td style="display: block; padding: 5px 15px;">
                            <p style="font-size:12px;">Estimado Sr(a) {name} , {message} </p>
                            <p style="font-size:12px;">Para iniciar sesión en el panel de apoderados, introduce tu usuario y contraseña <a href="{companys['website']}" target="_self">aquí</a>:</p>
                        </td>
                        </tr>
            
                        <tr><!-- CONTENIDO -->
                        <td style="display: block; padding: 5px 15px;">
                            <table width="100%" border="0" {CSS_TABLE_SECONDARY}>
                                <tbody>
                                    <tr style="border-bottom: 1px solid #ddd; vertical-align: top;">
                                    <th width="30%" {CSS_TABLE_SECONDARY_BODY_TH}>Usuario : </th>
                                    <td width="70%" {CSS_TABLE_SECONDARY_BODY_TD}>Su usuario es su rut sin puntos y sin guion</td>
                                    </tr>
                                    <tr style="border-bottom: 1px solid #ddd; vertical-align: top;">
                                    <th {CSS_TABLE_SECONDARY_BODY_TH}>Contraseña :</th>
                                    <td {CSS_TABLE_SECONDARY_BODY_TD}>Su clave son lo primeros cuatro digitos de su rut</td>
                                    </tr>                                      
                                </tbody>
                            </table>
                        </td>
                        </tr>
            
                        <tr><!-- SEPARADOR -->
                        <td style="display: block; padding: 15px;"><hr ' . $CSS_HR . '></td>
                        </tr>
            
                        <tr><!-- AVISO RESPUESTA AUTOMATICA -->
                        <td style="display: block; padding: 10px; background: #f6f6f6; color:#999; margin-top: 20px; text-align: center; font-size:11px;">
                            Este correo se ha generado de forma automatica, favor no responder.
                        </td>
                        </tr>
            
                        <tr ><!-- FOOTER -->
                        </tr>
                    </tbody>
                </table>
            
            </body>
            </html>
            '''




    
     # Configuración del mensaje
    msg = EmailMessage()
    msg['From'] = companys["email"]       # tu correo
    msg['To'] = correo
    msg['Subject'] = asunto
    msg.set_content(cuerpo)

    # Conexión con servidor SMTP (Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    usuario = "antonoomarfa@gmail.com"
    password = "Soandaso99"

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # cifrado
            server.login(usuario, password)
            server.send_message(msg)
        print("Correo enviado correctamente")
    except Exception as e:
        print("Error al enviar correo:", e)
