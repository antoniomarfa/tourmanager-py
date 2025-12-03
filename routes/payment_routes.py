from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import bcrypt
import json,os,re
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction
from libraries.utilities import Utilities
#Todo para el pdf
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

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

    ruta_image = f"/uploads/company/logo/login_logo_{request.session.get('code_company', 'GRL_999')}.png"
    ruta_image = os.path.abspath(ruta_image)
    user_name=request.session.get("user_name")

    info_index = await  util.formPaymentCharge(request.session)
    context = {
        "request": request, 
        "session":request.session,
        "info_index":info_index,
        "empresa":empresa,
        "ruta_image":ruta_image,
        "user_name":user_name
        }
    return templates.TemplateResponse("payment/index.html", context)
   

@router.get("/student", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    ruta_image = f"/uploads/company/logo/login_logo_{request.session.get('code_company', 'GRL_999')}.png"
    ruta_image = os.path.abspath(ruta_image)
    user_name=request.session.get("user_name")

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
    if request.session.get('id') and request.session.get('id') != '':
        cursoid = int(request.session.get('id'))
        response = await api.get_data("curso",id=cursoid,schema=schema_name)
        course = response['data'] if response["status"] == "success" else []

    if course:
        colegio = colegio['nombre']
        sales = sale
        course = course
        communes = commune
        regions = region
        context =  {"colegio":colegio,
                   "request": request, 
                    "session":request.session,
                    "sale":sales,
                    "course":course,
                    "communes":communes,
                    "regions":regions,
                    "info_index":info_index,
                    "helper":Helper,
                    "empresa":empresa,
                    "ruta_image":ruta_image,
                    "user_name":user_name
                    }
        print("sali por e")
        return templates.TemplateResponse("payment/student_e.html", context)
    else:
        colegio = colegio['nombre']
        sale = sale
        communes = commune
        regions = region
        context ={"request": request, 
                  "session":request.session,
                  "colegio":colegio,
                  "sale":sale,
                  "communes":communes,
                  "regions":regions,
                  "fecha_hoy":fecha_hoy,
                  "info_index":info_index,
                  "helper":Helper,
                  "empresa":empresa,
                  "ruta_image":ruta_image,
                   "user_name":user_name
                  }        
        print("sali por i")
        return templates.TemplateResponse("payment/student_i.html", context)

@router.get("/medicalrecordi", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")

    ruta_image = f"/uploads/company/logo/login_logo_{request.session.get('code_company', 'GRL_999')}.png"
    ruta_image = os.path.abspath(ruta_image)
    user_name=request.session.get("user_name")

    response = await api.get_data("region",schema="global")
    regions = response["data"] if response["status"] == "success" else []

    response = await api.get_data("comunas",schema="global")
    communes = response["data"] if response["status"] == "success" else []

    info_index = await util.formPaymentCharge(request.session)

    consulta = int(request.session.get('id'))
    response = await api.get_data("curso",id=consulta,schema=schema_name)
    course = response['data'] if response["status"] == "success" else []
    
    consulta = f"sale_id={request.session.get('sale')}&rutalumn={request.session.get('user_ruta')}"
    response = await api.get_data("ficha",query=consulta,schema=schema_name)
    # La API puede devolver una lista con elementos o un diccionario vacío
    ficha_data = response["data"] if response["status"] == "success" else []
    
    # Si es una lista con elementos, tomar el primer elemento; si no, diccionario vacío
    if isinstance(ficha_data, list) and len(ficha_data) > 0:
        ficha = ficha_data[0]
    elif isinstance(ficha_data, dict) and len(ficha_data) > 0:
        ficha = ficha_data
    else:
        ficha = {}

    context = {
        "request": request,
        "session": request.session,
        "regions":regions,
        "communes":communes,  
        "info_index": info_index,
        "helper": Helper,
        "empresa": empresa,
        "ruta_image":ruta_image,
        "course":course,
        "ficha":ficha
    }

    if len(ficha) > 0:
        print("sali por e")
        return templates.TemplateResponse("payment/medical_record_e.html", context)
    else:
        print("sali por i")
        return templates.TemplateResponse("payment/medical_record_i.html", context)

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
    Dato51=form_data.get('pasaportealumno')
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
    Dato141=str(switch_psico)
    Dato142=form_data.get('psicol')
    Dato151=str(switch_medicacion)
    Dato152=form_data.get('medicaciond')
    Dato161=str(switch_enfermedadp)
    Dato162=form_data.get('enfermedadpr')
    Dato17=form_data.get('medalim')
    Dato18=form_data.get('alergias')
    Dato191=str(switch_celiaco)
    Dato192=str(switch_vegetariano)
    Dato193=str(switch_vegano)
    Dato194=str(switch_lactosa)
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

    response = await api.set_data("ficha",body=json.dumps(data), schema=schema_name)
    print(response)
    #si la respuesta es ok , graba el nro de la venta en la cotizacion
    if response.get("status") == "success":
        ficha_id = response["data"]["data"]["return_id"]
        await fichamedica_pdf(request,ficha_id)

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
    Dato51=form_data.get('pasaportealumno')
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

    response = await api.update_data("ficha",id=ficha_id,body=json.dumps(data), schema=schema_name)
    #si la respuesta es ok , graba el nro de la venta en la cotizacion
    if response.get("status") == "success":
        #sale_id = response["data"]["data"]["return_id"]
        await fichamedica_pdf(request,ficha_id)
    return RedirectResponse(url=f"/{empresa}/manager/payment", status_code=303)  

async def fichamedica_pdf(request:Request,fichaid:int):
    empresa = request.state.empresa 
    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))

    getQuery=f"id={fichaid}"
    response = await api.get_data("fmedica",id=fichaid, schema=schema_name)
    ficha = response['data'] if response['status'] == "success" else []
    
    nomComuna="S/Comuna"
    response = await api.get_data("comunas",id=int(ficha['dato101']), schema="global")
    comunas=response['data'] if response['status'] == "success" else []

    if (len(comunas)>0):
        nomComuna=comunas['description']
    
        buffer = BytesIO()
    imagen1 = "/uploads/company/logo/login_logo_DET_7053186c-4188-4c9a-88af-fb12caa206bc.png"
    imagen1 = os.path.join(os.getcwd(), imagen1.lstrip("/"))
    
    Fm_Dato141 = "NO" if ficha['dato141'] =="0" else  "SI" 
    Fm_Dato151 = "NO" if ficha['dato1151']=="0" else "SI"
    Fm_Dato161 = "NO" if ficha['dato1161']=="0" else "SI"
    Fm_Dato19 = "NO" if ficha['dato19']=="0" else "SI"

    ra=ficha['dato5']

    rut = ficha['dato5']
    rut_limpio = rut.replace(".", "").replace("-", "")  # \D elimina todo lo que NO sea número
    # Crear documento
    output_path = f"/uploads/company/contrato/pasajeros/{company_id}/fmd/fichamedica-{ficha['sale_id']}-{rut_limpio}.pdf"
    output_path = os.path.join(os.getcwd(), output_path.lstrip("/"))
    #si el archivo existe lo elimina para que solo exista el ultimo
    if os.path.exists(output_path):
        os.remove(output_path)

# ----------- ESTILOS --------------
    normal = styles["Normal"]
    bold_center = ParagraphStyle(
        "bold_center",
        parent=normal,
        alignment=1,
        fontSize=10,
        spaceAfter=6,
        spaceBefore=6,
        fontName="Helvetica-Bold"
    )

    # ----------- DOCUMENTO --------------
    pdf = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=30, leftMargin=30,
        topMargin=50, bottomMargin=50
    )

    story = []

    # ----------- IMAGEN SUPERIOR --------------
    try:
        story.append(Image(imagen1, width=100, height=40))
    except:
        pass

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>FICHA MEDICA ALUMNOS VIAJE ESTUDIO</b>", bold_center))
    story.append(Spacer(1, 12))

    # ----------- TABLA PRINCIPAL --------------
    data = [
        ["Colegio", ficha['dato1']],
        ["Curso", ficha['dato2']],
        ["Fecha y Destino", f"{ficha['dato31']} {ficha['dato32']}"],
        ["Alumno (Nombres y Apellidos)", ficha['dato4']],
        ["Rut / Pasaporte", ficha['dato5']],
        ["Fecha Nacimiento", ficha['dato6']],
        ["Nacionalidad", ficha['dato7']],
        ["Nombre Completo Apoderado", ficha['dato8']],
        ["Dirección", ficha['dato9']],
        ["Comuna", nomComuna],
        ["Telefono - Correo", f"{ficha['dato11']} {ficha['dato12']}"],

        ["<b>Antecedentes Médicos</b>", "<b>Datos Confidenciales</b>"],

        ["Grupo y Factor Sanguíneo", ficha['dato13']],
        ["¿Tratamientos médicos/psicológicos?",
         f"{Fm_Dato141}<br/>Cual(es): {ficha['dato142']}"],
        ["Medicación", f"{Fm_Dato151} — Dosis: {ficha['dato152']}"],
        ["Enfermedades", f"{Fm_Dato161}<br/>Cual(es): {ficha['dato162']}"],
        ["Contraindicaciones", ficha['dato17']],
        ["Alergias", ficha['dato18']],
        ["Vegetariano", Fm_Dato19],
        ["Observaciones", ficha['dato20']],
        ["Emergencia avisar a:", ficha['dato21']],
        ["Teléfono(s)", ficha['dato22']],
    ]

    # Convierte celdas HTML a Paragraph
    table_data = []
    for row in data:
        new_row = []
        for cell in row:
            new_row.append(Paragraph(str(cell), normal))
        table_data.append(new_row)

    table = Table(table_data, colWidths=[150, 300])

    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,12), (1,12), colors.lightgrey),    # Cabecera doble
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))

    story.append(table)

    story.append(Spacer(1, 40))
    story.append(Paragraph("Cédula de Identidad y Firma del Apoderado", ParagraphStyle("i", parent=normal, alignment=1, fontStyle="italic")))

    # ----------- GENERAR PDF --------------
    pdf.build(story)

    return FileResponse(output_path, media_type="application/pdf")


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
@router.get("/contrat_travel", response_class=HTMLResponse)
async def contrat_travel(request: Request):
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    ruta_image = f"/uploads/company/logo/login_logo_{request.session.get('code_company', 'GRL_999')}.png"
    ruta_image = os.path.abspath(ruta_image)
    
    #Directorio de paso con los cambios y sin firma
    directoryUpload = "uploads/opening"
    os.makedirs(directoryUpload, exist_ok=True)

    #Directorio de la compañia
    UPLOAD_DIR = "uploads/company"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    #Directorio donde se encuenta la plantilla del contrato
    contrato_doc = os.path.join(UPLOAD_DIR, "contrato/", str(company_id))
    os.makedirs(contrato_doc, exist_ok=True)

    response = await api.get_data("sale",id=request.session.get("sale"),schema=schema_name)
    venta = response['data'] if response["status"]=="success" else []
    
    response = await api.get_data("programac",id=int(venta['program_id']),schema=schema_name)
    programac = response['data'] if response["status"]=="success" else []

    response = await api.get_data("colegio",id=int(venta['establecimiento_id']),schema=schema_name)
    school = response['data'] if response["status"]=="success" else []
   
    response = await api.get_data("curso",id=int(request.session.get('id')),schema=schema_name)
    curso = response['data'] if response["status"]=="success" else []

    response = await api.get_data("company",id=int(request.session.get('company')),schema="global")
    company= response['data'] if response["status"]=="success" else []
    empresa = company['identificador']

    #si el contrato esta aceptado y fiermado mostrarlo
    #si el contrato no esta aceptado mostrarlo para aceptacion

    if curso['acepta_contrato'] ==  1:
        #directorio donde queda el wrd creaado con el contrato
        contrato_wrd = os.path.join(UPLOAD_DIR, "contrato", "pasajeros", str(company_id), 'wrd')
        os.makedirs(contrato_wrd, exist_ok=True)

        rut = curso["rutalumno"]
        rut_limpio = rut.replace(".", "").replace("-", "")  # \D elimina todo lo que NO sea número

        if venta['type_sale']=='GE':
            documentwrd=f'contratoge-{curso["sale_id"]}-{rut_limpio}.docx'
            namewrd=f'contratoge-{curso["sale_id"]}-{rut_limpio}'
        else:
            documentwrd=f'contratovg-{curso["sale_id"]}-{rut_limpio}.docx'
            namewrd=f'contratovg-{curso["sale_id"]}-{rut_limpio}'
   
        #archivo creado enviado al navegador para que lo vea el cliente
        file_doc_html=f'http://127.0.0.1/{contrato_wrd}/{namewrd}.docx'
        documentname=""

    else:
        
        # Convertir string a datetime
        fecha_str = venta['fecha']  # '2025-09-01T00:00:00Z'
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%SZ")

        # Día, mes, año
        vtaDia = fecha_obj.day
        vtaMes = fecha_obj.month   # devuelve número 1-12
        vtaAgno = fecha_obj.year

        vtaMesNombre = Helper.nombre_mes(fecha_obj.month - 1)
        vtaMes = vtaMesNombre

        type_sale=venta['type_sale']
    
        valores = {
            "vtaDia": vtaDia,
            "vtaMes": vtaMes,
            "vtaAño": vtaAgno,
            "rute": company['rut'],
            "rsocial": company['razonsocial'],
            "nfantasia": company['nomfantasia'],
            "rlegal": company['rutreplegal'],
            "nlegal": company['nomreplegal'],
            "edireccion": company['direccion'],
            "colegio": school['nombre'],
            "idcurso": f"{venta['curso']}/{venta['idcurso']}",
            "programa": programac['name'],
            "reserva": programac['reserva'],
            "tprograma": venta['vprograma'],
            "tc": venta['tipocambio'],
            "liberados": venta['liberados'],
            "fsalida": venta['fechasalida'],
            "fpago": venta['fecha_ultpag'],
        }

        # Forma segura de crear el nombre completo del archivo
        fileplantilla = os.path.join(contrato_doc, f"Contratoge_{company['identificador']}.docx")
        file_plantilla = os.path.abspath(fileplantilla)

        # Crear el archivo donde quedara el archivo a firmar
        documentname = "documento_" + os.urandom(16).hex() + ".docx"
        file_doc = os.path.join(directoryUpload, documentname)
        #Cambia las variables por datos del template por valores correcto 
        response =util.docx_to_html(file_plantilla,file_doc,valores)

        #archivo creado enviado al navegador para que lo vea el cliente
        file_doc_html=f'http://127.0.0.1/uploads/payment/{documentname}'

    info_index = await util.formPaymentCharge(request.session)
    context ={"request": request, 
              "session":request.session,
              "info_index":info_index,
              "documentname":documentname,
              "curso":curso,
              "rs":company['razonsocial'],
              "contrato":file_doc_html,
              "venta":venta,
              "empresa":empresa,
              "ruta_image":ruta_image}
    
    return templates.TemplateResponse("payment/contrattravel.html", context)

@router.post("/create_sale", response_class=HTMLResponse)
async def createsale(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    form_data = await request.form()
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    #Directorio de la compañia
    UPLOAD_DIR = "uploads/company"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    #Directorio de paso con los cambios y sin firma
    directoryUpload = "uploads/payment"
    os.makedirs(directoryUpload, exist_ok=True)

    #directorio donde queda el pdf creaado con el contrato
    contrato_pdf = os.path.join(UPLOAD_DIR, "contrato", "pasajeros", str(company_id), 'pdf')
    os.makedirs(contrato_pdf, exist_ok=True)

    #directorio donde queda el wrd creaado con el contrato
    contrato_wrd = os.path.join(UPLOAD_DIR, "contrato", "pasajeros", str(company_id), 'wrd')
    os.makedirs(contrato_pdf, exist_ok=True)
        
    response = await api.get_data("curso",id=int(request.session.get('user_curso_id')),schema=schema_name)
    curso = response['data'] if response["status"] == "success" else []
    
    firmaPng=form_data.get('signature64')
    typesale=form_data.get('typesale')
    # firma viene en formato "data:image/png;base64,iVBORw0K..."
    if firmaPng.startswith("data:image"):
        firmaPng = firmaPng.split(",")[1]  # quitar "data:image/png;base64,"

    # Guardar en archivo temporal
    firma_bytes = base64.b64decode(firmaPng)
    ruta_firma = os.path.join(UPLOAD_DIR, "firma.png")
   
    with open(ruta_firma, "wb") as f:
        f.write(firma_bytes)

    documentname = form_data.get('documentname')
    acepta_contrato = form_data.get('acepta_contrato') or "0"
    print("acepta cntrato ",int(acepta_contrato))
    if int(acepta_contrato) == 0: 

        parameters= {
                'rutal': curso['rutalumno'],
                'rutap': curso['nombrealumno'],
                'nomal': curso['rutapod'],
                'nomap': curso['nombreapod'],
             }
        Signature = Helper.signature(parameters);       
    
        dato={
            "acepta_contrato":1,
            "signature": Signature,
            "autor":request.session.get('name'),
            "signaturepng":""
            }
    
        update = await api.update_data("curso",id=int(request.session.get('user_curso_id')) ,body=json.dumps(dato), schema=schema_name)

        if update['status']=='success':        
            #agregar la firma al contrato y convertirlo a pdf 
            #valores["signature"] = InlineImage(doc, "firma.png", width=Mm(40))
            ruta_firma = f"uploads/company/firma.png"
            ruta_firma = os.path.abspath(ruta_firma)

            # Forma segura de crear el nombre completo del archivo
            filedoc = os.path.join(directoryUpload, documentname)
            file_doc = os.path.abspath(filedoc)

            #Cambia las variables por datos del template por valores correcto 
            response =util.signature_doc(file_doc,ruta_firma)

            rut = curso["rutalumno"]
            rut_limpio = rut.replace(".", "").replace("-", "")  

            if typesale=='GE':
                documentwrd=f'contratoge-{curso["sale_id"]}-{rut_limpio}.docx'
                documentpdf=f'contratoge-{curso["sale_id"]}-{rut_limpio}.pdf'
                namewrd=f'contratoge-{curso["sale_id"]}-{rut_limpio}'
            else:
                documentwrd=f'contratovg-{curso["sale_id"]}-{rut_limpio}.docx'
                documentpdf=f'contratovg-{curso["sale_id"]}-{rut_limpio}.pdf'
                namewrd=f'contratovg-{curso["sale_id"]}-{rut_limpio}'

            filepdf = os.path.join(contrato_pdf, documentpdf)
            file_pdf = os.path.abspath(filepdf)

            # Mover y renombrar
            filewrd = os.path.join(contrato_wrd, documentwrd)
            file_wrd = os.path.abspath(filewrd)

            shutil.move(file_doc, file_wrd)
            #convertir word a pdf con libreria http
            clientId = '90da2604-7052-4d85-8686-9e6e687e2990'
            clientSecret = '38c9a7c7f5813dd387043f50212a802f'
            
            #Rutas de archivos
            localDocxPath = file_wrd   #Ruta real en tu servidor
            remoteDocxName = namewrd+'.docx'  #Nombre en Aspose Cloud
            remotePdfName = namewrd+'.pdf'   #Nombre destino
            
            #Flujo completo
            token = convertpdf.get_aspose_token(clientId, clientSecret)
            
            convertpdf.upload_to_aspose(token, localDocxPath, remoteDocxName)
            
            convertpdf.convert_docx_to_pdf(token, remoteDocxName, remotePdfName, file_pdf)
            

            # Elimina los archivos de paso      
            os.remove(ruta_firma)
            os.remove(file_doc)

            request.session["paso"]="2"
            request.session["user_contrato"]= "S"
            return RedirectResponse(url=f"/{empresa}/manager/payment", status_code=303)
        else:
            return RedirectResponse(url=f"/{empresa}/manager/payment", status_code=303)
             
    else:
        print("en el else de acepta contrato")
        #rut = curso["rutalumno"]
        #rut_limpio = rut.replace(".", "").replace("-", "")  # \D elimina todo lo que NO sea número

        #if typesale=='GE':
        #    documentpdf=f'contratoge-{curso["sale_id"]}-{rut_limpio}.pdf'
        #    namewrd=f'contratoge-{curso["sale_id"]}-{rut_limpio}'
        #else:
        #    documentpdf=f'contratovg-{curso["sale_id"]}-{rut_limpio}.pdf'
        #    namewrd=f'contratovg-{curso["sale_id"]}-{rut_limpio}'

        #filepdf = os.path.join(contrato_pdf, documentpdf) tiene que ser la url del archivo
        #file_pdf =  os.path.abspath(filepdf)

        ## Obtener contenido del PDF
        #pdf = requests.get(file_pdf)

        #if pdf.status_code != 200:
        #    return {"error": "No se pudo descargar el PDF"}

        ## Responder como archivo descargable
        #return response(
        #    content=pdf.content,
        #    media_type="application/pdf",
        #    headers={
        #    "Content-Disposition": 'attachment; filename="contrato.pdf"'
        #    }
        #)
        return RedirectResponse(url=f"/{empresa}/manager/opening", status_code=303)
