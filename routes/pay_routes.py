from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import bcrypt
import json,os
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction
from libraries.utilities import Utilities

router = APIRouter()

templates = Jinja2Templates(directory="templates")

api = RenderRequest()
rst = Restriction()
util = Utilities()

# Mostrar Pago reserva
@router.get("/formpayment_rsv", response_class=HTMLResponse)
async def formpaymentrsv(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id = request.session.get("company")

    ruta_image = f"/uploads/company/logo/login_logo_{request.session.get('code_company', 'GRL_999')}.png"
    ruta_image = os.path.abspath(ruta_image)

    response = await api.get_data("gatewaysc",schema="global")
    gatewaysc = response['data'] if response["status"] == "success" else []
    hasta = len(gatewaysc) - 1

    for i in range(hasta + 1):
        item = gatewaysc[i]
        getQuery=f'company_id={company_id}&gateway_id={item["id"]}'
        response = await api.get_data("gateways",query=getQuery,schema=schema_name)
        gateways=response['data']  if response["status"] == "success" else []
        if gateways:
            gatewaysc[i]['existe']='S'
            ruta_logo=f"http://localhost:8000/static/{gatewaysc[i]['gateway_image']}"
            gatewaysc[i]['image']=ruta_logo                
        else:
            gatewaysc[i]['existe']='N';                
            
        
    request.session["encuotas"]= "N"

    valorv = 0
    saldopen = 0    
    apagar = 0  
    pagad= 0
    #Valor Viaje
    result = await api.get_data("sale",id=int(request.session.get('sale')),schema=schema_name)
    sale = result['data'] if result["status"] == "success" else []

    if sale:
        result= await api.get_data("programac",id=sale['program_id'],schema=schema_name)
        progamac = result['data']
        valorv = progamac['reserva']
        apagar = progamac['reserva']
       
    valorv=Helper.formato_numero(valorv)
    info_index = await util.formCharge(request.session)

    return templates.TemplateResponse("pay/formpayment_rsv.html", {"request": request, "session":request.session,"valorv":valorv,"apagar":apagar,"gatewaysc":gatewaysc,"info_index":info_index,"empresa":empresa,"ruta_image":ruta_image})

# Mostrar Pago reserva general
@router.get("/formpayment", response_class=HTMLResponse)
async def formpayment(request: Request):
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id = request.session.get("company")
    
    ruta_logo = f"/uploads/company/logo/login_logo_{request.session.get('code_company', 'GRL_999')}.png"
    ruta_logo = os.path.abspath(ruta_logo)
        
    info_index = await util.formPaymentCharge(request.session)
    empresa=info_index['identificador']

    response = await api.get_data("gatewaysc",schema="global")
    gatewaysc = response['data'] if response["status"] == "success" else []
    hasta = len(gatewaysc) - 1

    for i in range(hasta + 1):
        item = gatewaysc[i]
        getQuery=f'company_id={company_id}&gateway_id={item["id"]}'
        response = await api.get_data("gateways",query=getQuery,schema=schema_name)
        gateways=response['data']  if response["status"] == "success" else []
        if gateways:
            gatewaysc[i]['existe']='S'
            ruta_image=f"http://localhost:8000/static/{gatewaysc[i]['gateway_image']}"
            gatewaysc[i]['image']=ruta_image   
        else:
            gatewaysc[i]['existe']='N';                
       
    valorv = 0
    saldopen = 0
    apagar = 0
    pagado= 0
    #Valor Viaje
    result = await api.get_data("sale",id=int(request.session.get('sale')),schema=schema_name)
    sale = result['data'] if result["status"] == "success" else []

    if sale:
        valorv=sale['vprograma'] 

    #moto pagado
    consulta=f'curso_id={int(request.session.get("id"))}&status_pago=Pagado&activo=1'
    result= await api.get_data("ingreso",query=consulta,schema=schema_name)
    pagos=result['data'] if result["status"] == "success" else []

    # Sumar todos los montos en una sola línea (Pythonic)
    # sin usa if y foreach 
    pagado = sum(p['monto'] for p in pagos) if pagos else 0

    saldopen= valorv - pagado
        
    form_view={}
    form_view["gatewaysc"] = gatewaysc        
    form_view["valorv"]=Helper.formato_numero(valorv)
    form_view["saldopen"]=Helper.formato_numero(saldopen)
    form_view["apagar"]=Helper.formato_numero(saldopen)
    form_view["sfapagar"]=saldopen

    user_name=request.session.get("user_name")

    context={
        "request": request, 
        "session":request.session,
        "form_view":form_view,
        "info_index":info_index,
        "empresa":empresa,
        "ruta_image":ruta_logo,
        "position":request.session.get("position"),
        "user_name":user_name
    }

    return templates.TemplateResponse("pay/formpayment.html", context)


# Mostrar Pago reserva general
@router.get("/formpayment_ct", response_class=HTMLResponse)
async def formpaymentct(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id = request.session.get("company")
    
    info_index = await util.formCharge(request.session)
        
    response = await api.get_data("gatewaysc",schema="global")
    gatewaysc = response['data'] if response["status"] == "success" else []
    hasta = len(gatewaysc) - 1

    for i in range(hasta + 1):
        item = gatewaysc[i]
        getQuery=f'company_id={company_id}&gateway_id={item["id"]}'
        response = await api.get_data("gateways",query=getQuery,schema=schema_name)
        gateways=response['data']  if response["status"] == "success" else []
        if gateways:
            gatewaysc[i]['existe']='S'
            ruta_image=f"http://localhost:8000/static/{gatewaysc[i]['gateway_image']}"
            gatewaysc[i]['image']=ruta_image                
        else:
            gatewaysc[i]['existe']='N';      
        
        venta=0
        fechac=""
        fechaf=""
        cuotas=0
        pasajero=int(request.session.get('id'))

        request.session['encuotas']= "S"
        #curso
        result= await api.get_data("curso",id=pasajero,schema=schema_name)
        curso=result['data'] if result["status"] == "success" else []
        if curso:
            venta=int(curso['sale_id'])
        
        
        
        diferencia=0
        valor_pagos=0

        result= await api.get_data("sale",id=venta,schema=schema_name)
        sale=result['data'] if result["status"] == "success" else []
        if sale:
            programs = sale['program_id']
            cuotas = sale["cuotas"]
            fechac = sale["fechacuota"]
            dt = datetime.strptime(fechac, "%Y-%m-%d %H:%M:%S")
            fechac = dt.strftime("%d-%m-%Y")
            fechaf = sale["fecha_ultpag"]
            dt = datetime.strptime(fechaf, "%Y-%m-%d %H:%M:%S")
            fechaf = dt.strftime("%d-%m-%Y")
            vprograma = sale['vprograma']-programs['reserva']
            valor_cuota = round(vprograma/cuotas,0)
            total_cuotas = valor_cuota*cuotas
            diferencia = vprograma-total_cuotas

    consulta=f'curso_id={pasajero}&status_pago=Pagado&activo=1'
    result= await api.get_data("ingreso/informe",query=consulta,schema=schema_name)
    ingresos=result['data'] if result["status"] == "success" else []
      
    cuotaspagadas=[]
    count_pagos=0
    for ingreso in ingresos:
        pagos=ingreso['pago']
        for pago in pagos:
            if not pago['cuotapagada']:
                valor_pagos+=pago['monto']
            else:
                cuotaspagadas.append(pago['cuotafecha'])
                count_pagos += 1
                
              
        
    if valor_pagos != 0:
        vprograma=vprograma-valor_pagos
        valor_cuota=round(vprograma/cuotas,0)
        total_cuotas=valor_cuota*cuotas
        diferencia=vprograma-total_cuotas
        
        # Variables equivalentes al PHP
        nrocuotas=count_pagos
        dia = fechac[0:2]    # "05"
        mes = fechac[3:5]    # "09"
        agno = fechac[6:10]  # "2025"

        data_cuotas = []
        i = 1
        if nrocuotas == 0:
            # === caso cuando $this->nrocuotas == 0 ===
            while i <= cuotas:
                monto = valor_cuota
                if i == cuotas:
                    monto += diferencia
                data_cuotas.append({
                    "nro": i,
                    "mes_agno": f"{str(mes).zfill(2)}-{agno}",
                    "monto": monto
                })
                # avanzar mes/año
                mes += 1
                if mes > 12:
                    mes = 1
                    agno += 1
                i += 1
        else:
            # === caso cuando $this->nrocuotas != 0 ===
            while i <= cuotas:
                search = f"{agno}{str(mes).zfill(2)}"
                if search not in cuotaspagadas:
                    monto = valor_cuota
                    if i == cuotas:
                        monto += diferencia
                    data_cuotas.append({
                        "nro": i,
                        "mes_agno": f"{str(mes).zfill(2)}-{agno}",
                        "monto": monto
                    })
                # avanzar mes/año
                mes += 1
                if mes > 12:
                    mes = 1
                    agno += 1
                i += 1  
       
    return templates.TemplateResponse("pay/formpayment_ct.html", {"request": request, "session":request.session,"cuotas": data_cuotas,"info_index":info_index, "gatewaysc":gatewaysc,"empresa":empresa})

# Mostrar Pago reserva general
@router.get("/getentries")
async def entries(request: Request,curso_id: int = Form(...),):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")

    cuota=1
    content_pagos=""
    result= await api.get_data("curso",id=curso_id,schema=schema_name)
    curso = result['data'] if result["status"] == "success" else []
    alumno = curso['nombrealumno']

    result= await api.get_data("sale",id=int(curso['sale_id']),schema=schema_name)
    sale=result['data'] if result["status"] == "success" else []
    cuotas=sale['cuotas']
        
    consulta=f'curso_id={curso_id}&status_pago=Pagado&activo=1'
    result= await api.get_data("ingreso/informe",query=consulta,schema=schema_name)
    ingresos=result['data'] if result["status"] == "success" else []
     
    if ingresos:
        content_pagos += f'''
            <tr>
                <td colspan="3" align="center">SIN INGRESOS</td>
            </tr>
            '''
    else:
        for ingreso in ingresos:
            pagos=ingreso['pago']
            for pago in pagos:
                content_pagos += f'''
                    <tr>
                        <td align="right">{pago['ingreso_id']}</td>
                        <td align="right">{pago['fecha']}</td>
                        <td align="right">{pago['transaccion']}</td>
                        <td align="right">{pago['fechatransac']}</td>
                        <td>{pago['tipopago']}</td>
                        <td align="right">{Helper.formato_numero(pago['monto'])}</td>'''
                if cuotas>1:
                    content_pagos+=f'''
                        <th>'.$cuota.'</th>
                        <th>'.substr($pago['cuotafecha'],4,2).'-'.substr($pago['cuotafecha'],0,4).'</th>
                        '''
                cuota+=1
                        
                content_pagos +=f'''</tr>'''

    data = f'''
        <div class="row">
            <div class="col-sm-12 invoice-left">
                <h3>Alumno : {alumno} </h3>
            </div>
        </div>

        <hr class="margin" />

        <h4><i class="fa fa-chevron-right" aria-hidden="true"></i> Detalle de Ingresos</h4>
        <table class="table table-bordered table-hover table-condensed">
            <thead>
            <tr>
                <th>Nro Ingreso</th>
                <th>Fecha</th>
                <th>Tansaccion</th>
                <th>Fecha</th>
                <th>Tipo Pago</th>
                <th>Monto</th> '''
                
    if cuotas>1:
        data+=f'''
                <th>Cuota</th>
                <th>Fecha</th>
            '''; 
    
    data += f'''</tr>
            </thead>
            <tbody>{content_pagos}</tbody>
        </table>
        '''
    return JSONResponse(content={"data": data})

    
   
# Mostrar Pago reserva general
@router.get("/getcuotas")
async def entries(request: Request,curso_id: int = Form(...),):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")

    data = ""
    venta = 0
    fechac = ""
    fechaf = ""
    cuotas = 0

    #curso
    result= await api.get_data("curso",id=int(curso_id),schema=schema_name)
    curso = result['data'] if result["status"] == "success" else []
    venta = curso['sale_id']
        
    result= await api.get_data("sale",id=int(venta),schema=schema_name)
    sale=result['data'] if result["status"] == "success" else []
    if sale >1:
        cuotas=sale['cuotas']
        fechac=sale['fechacuota']
        fechaf=sale['fecha_ultpag']
        valor_cuota=sale['vprograma']/cuotas
    

    consulta=f'curso_id={curso_id}&status_pago=Pagado&activo=1'
    result= await api.get_data("ingreso/informe",query=consulta,schema=schema_name)
    ingresos=result['data'] if result["status"] == "success" else []
        
    i=1
    _mes=fechac[3:5]
    _agno=fechac[6:10]

    if ingresos == 0:
        while i <= cuotas:
            data += f'''|<tr>
                <td><input type="checkbox" name="nrocuota[]" id="nrocuota" class="nrocuota" value="{valor_cuota}"></td>
                <td>{i}</td>
                <td>{_mes}-{_agno}</td>
                <td>{Helper.formato_numero(valor_cuota)}</td>
                </tr>'''

            _mes+=1
            if _mes > 12:
                _mes=1
                _agno+=1
            
            i+=1;    
        
        data += f'''<tr>
            <td></td>
            <td></td>
            <td></td>
            <td><input type="text" id="total_cuotas" value="0"/></td>
            </tr>'''


    #else:
        #foreach($pagos as $pago){

    return JSONResponse(content={"data": data})
