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

# Ruta principal: mostrar usuarios
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    info_index = await  util.formPaymentCharge(request.session)

    return templates.TemplateResponse("payment/index.html", {"request": request, "session":request.session,"info_index":info_index,"empresa":empresa})
   

@router.get("/student", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    hoy = datetime.today()
    fecha_hoy = hoy.strftime("%d/%m/%Y")

    response = await api.get_data("comunas",schema="global")
    commune = response['data'] if response["status"] == "success" else []
            
    response = await api.get_data("region",schema="global")
    region = response['data'] if response["status"] == "success" else []
        
    saleid = request.session.get('sale')
    response = await api.get_data("sale",id=saleid,schema=schema_name)
    sale = response['data'] if response["status"] == "success" else []

    colegioid=int(sale['establecimiento_id']) 
    response = await api.get_data("colegio",id=colegioid,schema=schema_name)
    colegio=response['data'] if response["status"] == "success" else []

    info_index = await util.formPaymentCharge(request.session)
 
    course=[]
    if request.session.get('user_curso_id') and request.session.get('user_curso_id') != '':
        cursoid = request.session.get('user_curso_id')
        response = await api.get_data("curso",id=cursoid,schema=schema_name)
        course = response['data'] if response["status"] == "success" else []

    if course:
        colegio = colegio['nombre']
        sales = sale
        course = course
        communes = commune
        regions = region
        print("sali por e")
        return templates.TemplateResponse("payment/student_e.html", {"request": request, "session":request.session,"sales":sales,"course":course,"communes":communes,"regions":regions,"info_index":info_index,"helper":Helper,"empresa":empresa})
    else:
        colegio = colegio['nombre']
        sale = sale
        communes = commune
        regions = region;        
        print("sali por i")
        return templates.TemplateResponse("payment/student_i.html", {"request": request, "session":request.session,"colegio":colegio,"sale":sale,"communes":communes,"regions":regions,"fecha_hoy":fecha_hoy,"info_index":info_index,"helper":Helper,"empresa":empresa})

@router.get("/medicalrecordi", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")

    response = await api.get_data("region",schema="global")  # Suponiendo que el servicio se llama 'users'    
    regions = response["data"] if response["status"] == "success" else {}

    response = await api.get_data("comunas",schema="global")  # Suponiendo que el servicio se llama 'users'    
    communes = response["data"] if response["status"] == "success" else {}

    info_index = await  util.formPaymentCharge(request.session)

    consulta=f"sale_id={request.session.get('sale')}&rutalumn={request.session.get('user_ruta')}"
    response = await api.get_data("fmedica",query=consulta,schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    ficha = response["data"] if response["status"] == "success" else {}

    if ficha:
        return templates.TemplateResponse("payment/medical_record_i.html", {"request": request, "session":request.session,"communes":communes,"regions":regions,"info_index":info_index,"helper":Helper,"enpresa":empresa})
    else:
        return templates.TemplateResponse("payment/medical_record_e.html", {"request": request, "session":request.session,"communes":communes,"regions":regions,"info_index":info_index,"ficha":ficha,"helper":Helper,"empresa":empresa})

# Crear usuario vía API
@router.post("/insert_fm")
async def createfm(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    form_data = await request.form()

    switch_psico=int(form_data.get('switch_psico', 0))
    switch_medicacion=int(form_data.get('switch_medicacion',0))
    switch_enfermedadp=int(form_data.get('switch_enfermedadp',0))
    switch_vegetariano=int(form_data.get('switch_vegetariano',0))
    switch_celiaco=int(form_data.get('switch_celiaco',0))
    switch_vegano=int(form_data.get('switch_vegano',0))
    switch_lactosa=int(form_data.get('switch_lactosa',0))

    NroVta=request.session.get('sale')
    rutAlumno=form_data.get('rutpass')
      
    Dato1=form_data.get('colegio')
    Dato2=form_data.get('curso')
    fecha_obj = form_data.get('fecha')
    if fecha_obj:
        fecha = datetime.fromisoformat(fecha_obj).strftime('%Y-%m-%dT00:00:00Z')
    Dato31=fecha
    Dato32=form_data.get('destino')
    Dato4=form_data.get('alumno')
    Dato5=form_data.get('rutpass')
    fecha_obj = form_data.get('fecnac')
    if fecha_obj:
        fecnac = datetime.fromisoformat(fecha_obj).strftime('%Y-%m-%dT00:00:00Z')
    Dato6=fecnac
    Dato7=form_data.get('nacionalidad')
    Dato8=form_data.get('apoderado')
    Dato9=form_data.get('calle')
    Dato91=form_data.get('numdir')
    Dato92=form_data.get('numdepto')
    Dato10=form_data.get('region_id')
    Dato101=form_data.get('comuna_id')
    Dato11=form_data.get('fono')
    Dato111=form_data.get('celular')
    Dato12=form_data.get('correo')
    Dato13=form_data.get('factorsang')
    Dato141=switch_psico
    Dato142=form_data.get('psicol')
    Dato151=switch_medicacion
    Dato152=form_data.get('medicaciond')
    Dato161=switch_enfermedadp
    Dato162=form_data.get('enfermedadpr')
    Dato17=form_data.get('medalim')
    Dato18=form_data.get('alergias')
    Dato191=switch_celiaco
    Dato192=switch_vegetariano
    Dato193=switch_vegano
    Dato194=switch_lactosa
    Dato20=form_data.get('obs')
    Dato21=form_data.get('emergencia')
    Dato22=form_data.get('emergenciafono')

    data={
        "sale_id": NroVta,
        "rutalumn": rutAlumno,
        "dato1": Dato1,
        "dato2": Dato2,
        "dato31": Dato31,
        "dato32": Dato32,
        "dato4": Dato4,
        "dato5": Dato5,
        "dato6": Dato6,
        "dato7": Dato7,
        "dato8": Dato8,
        "dato9": Dato9,
        "dato91": Dato91,
        "dato92": Dato92,
        "dato10": Dato10,
        "dato101": Dato101,
        "dato11": Dato11,
        "dato111": Dato111,
        "dato12": Dato12,
        "dato13": Dato13,
        "dato141": Dato141,
        "dato142": Dato142,
        "dato151": Dato151,
        "dato152": Dato152,
        "dato161": Dato161,
        "dato162": Dato162,
        "dato17": Dato17,
        "dato18": Dato18,
        "dato191": Dato191,
        "dato192": Dato192,
        "dato193": Dato193,
        "dato194": Dato194,
        "dato20": Dato20,
        "dato21": Dato21,
        "dato22": Dato22,
        "company": int(request.session.get("company"))
        }

    response = await api.set_data("fmedica",body=json.dumps(data), schema=schema_name)
    #si la respuesta es ok , graba el nro de la venta en la cotizacion
    if response.get("status") == "success":
        sale_id = response["data"]["data"]["return_id"]
        
    return RedirectResponse(url=f"/{empresa}/manager/payment", status_code=303)  


# Actualizar Ficha Medica
@router.post("/update_fm")
async def update(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")

    form_data = await request.form()

    ficha_id = int(form_data.get('id'))

    switch_psico=int(form_data.get('switch_psico', 0))
    switch_medicacion=int(form_data.get('switch_medicacion',0))
    switch_enfermedadp=int(form_data.get('switch_enfermedadp',0))
    switch_vegetariano=int(form_data.get('switch_vegetariano',0))
    switch_celiaco=int(form_data.get('switch_celiaco',0))
    switch_vegano=int(form_data.get('switch_vegano',0))
    switch_lactosa=int(form_data.get('switch_lactosa',0))

    NroVta=request.session.get('sale')
    rutAlumno=form_data.get('rutpass')
      
    Dato1=form_data.get('colegio')
    Dato2=form_data.get('curso')
    fecha_obj = form_data.get('fecha')
    if fecha_obj:
        fecha = datetime.fromisoformat(fecha_obj).strftime('%Y-%m-%dT00:00:00Z')
    Dato31=fecha
    Dato32=form_data.get('destino')
    Dato4=form_data.get('alumno')
    Dato5=form_data.get('rutpass')
    fecha_obj = form_data.get('fecnac')
    if fecha_obj:
        fecnac = datetime.fromisoformat(fecha_obj).strftime('%Y-%m-%dT00:00:00Z')
    Dato6=fecnac
    Dato7=form_data.get('nacionalidad')
    Dato8=form_data.get('apoderado')
    Dato9=form_data.get('calle')
    Dato91=form_data.get('numdir')
    Dato92=form_data.get('numdepto')
    Dato10=form_data.get('region_id')
    Dato101=form_data.get('comuna_id')
    Dato11=form_data.get('fono')
    Dato111=form_data.get('celular')
    Dato12=form_data.get('correo')
    Dato13=form_data.get('factorsang')
    Dato141=switch_psico
    Dato142=form_data.get('psicol')
    Dato151=switch_medicacion
    Dato152=form_data.get('medicaciond')
    Dato161=switch_enfermedadp
    Dato162=form_data.get('enfermedadpr')
    Dato17=form_data.get('medalim')
    Dato18=form_data.get('alergias')
    Dato191=switch_celiaco
    Dato192=switch_vegetariano
    Dato193=switch_vegano
    Dato194=switch_lactosa
    Dato20=form_data.get('obs')
    Dato21=form_data.get('emergencia')
    Dato22=form_data.get('emergenciafono')

    data={
        "sale_id": NroVta,
        "rutalumn": rutAlumno,
        "dato1": Dato1,
        "dato2": Dato2,
        "dato31": Dato31,
        "dato32": Dato32,
        "dato4": Dato4,
        "dato5": Dato5,
        "dato6": Dato6,
        "dato7": Dato7,
        "dato8": Dato8,
        "dato9": Dato9,
        "dato91": Dato91,
        "dato92": Dato92,
        "dato10": Dato10,
        "dato101": Dato101,
        "dato11": Dato11,
        "dato111": Dato111,
        "dato12": Dato12,
        "dato13": Dato13,
        "dato141": Dato141,
        "dato142": Dato142,
        "dato151": Dato151,
        "dato152": Dato152,
        "dato161": Dato161,
        "dato162": Dato162,
        "dato17": Dato17,
        "dato18": Dato18,
        "dato191": Dato191,
        "dato192": Dato192,
        "dato193": Dato193,
        "dato194": Dato194,
        "dato20": Dato20,
        "dato21": Dato21,
        "dato22": Dato22,
        "company": int(request.session.get("company"))
        }

    response = await api.update_data("fmedica",id=ficha_id,body=json.dumps(data), schema=schema_name)
    #si la respuesta es ok , graba el nro de la venta en la cotizacion
    if response.get("status") == "success":
        sale_id = response["data"]["data"]["return_id"]
        
    return RedirectResponse(url=f"/{empresa}/manager/payment", status_code=303)  

@router.post("/getcomune")
async def status(request: Request,region_id: int = Form(...),):
    getQuery=f"regions_id={region_id}"
    response = await api.get_data("comunas",query=getQuery, schema="global")
    communes=response['data']
    return JSONResponse(
        content={
            "data": communes
        })

@router.post("/getventa")
async def status(request: Request,venta_id: int = Form(...),):
    schema_name = request.session.get("schema")
    getQuery=f"id={venta_id}"
    response = await api.get_data("sale",query=getQuery, schema=schema_name)
    print(response)
    sale = response['data'][0]
 
    subtotal=int(sale["subtotal"])
    descuento=int(sale["descm"])
    valor=int(sale["vprograma"])
    typesale=sale['type_sale']

    return JSONResponse(
        content={
            'subtotal': subtotal,
            'descuento': descuento,
            'valor': valor,
            'typesale': typesale
        })
