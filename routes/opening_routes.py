from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import json, uuid, os, bcrypt,re,base64
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
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    paso = request.session.get('paso')
    info_index = await formCharge(request.session)

    return templates.TemplateResponse("opening/index.html", {"request": request, "session":request.session,"paso":paso,"info_index":info_index,"empresa":empresa})
   
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

    info_index = await formCharge(request.session)
 
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
        return templates.TemplateResponse("opening/student_e.html", {"request": request, "session":request.session,"sales":sales,"course":course,"communes":communes,"regions":regions,"info_index":info_index,"helper":Helper,"empresa":empresa})
    else:
        colegio = colegio['nombre']
        sale = sale
        communes = commune
        regions = region;        
        print("sali por i")
        return templates.TemplateResponse("opening/student_i.html", {"request": request, "session":request.session,"colegio":colegio,"sale":sale,"communes":communes,"regions":regions,"fecha_hoy":fecha_hoy,"info_index":info_index,"helper":Helper,"empresa":empresa})

 #Crea la venta
@router.post("/create")
async def create(request:Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    schema_name = request.session.get("schema")
    form_data = await request.form()

    #print(RutApo[:4])     # "1234"
    #print(RutApo[2:6])    # "3456"  (equivalente a substr($RutApo,2,4))

    if form_data.get('typesale') == 'VG':
        RutApo = form_data.get('rutalumno')
    else:
        RutApo = form_data.get('rutapoderado')

    RutApo = re.sub(r'[.]', '', RutApo)
    RutApo =RutApo[:4]
    hashed = bcrypt.hashpw(RutApo.encode("utf-8"), bcrypt.gensalt())
    password = hashed.decode("utf-8")  # convertir bytes → str

    fecha_obj =  datetime.strptime(form_data.get('fechanac'), "%d/%m/%Y")
    fechanac = fecha_obj.strftime("%Y-%m-%d") + "T00:00:00Z"

    data={
        "sale_id": int(form_data.get('venta_id')),  
        "rutalumno": form_data.get('rutalumno'),
        "nombrealumno": form_data.get('nombrealumno'),
        "fechanac": fechanac,
        "rutapod": form_data.get('rutapoderado'),
        "nombreapod": form_data.get('nombreapoderado'),
        "dircalle": form_data.get('calle'),
        "dirnumero": form_data.get('numdir'),
        "nrodepto": form_data.get('numdepto'),
        "region_id": int(form_data.get('region_id')),   
        "comuna_id": int(form_data.get('commune_id')),  
        "fono": form_data.get('fono'),
        "celular": form_data.get('celular'),
        "correo": form_data.get('correo'),
        "vpagar": int(form_data.get('apagar')),
        "descto": int(form_data.get('descto')),
        "apagar": int(form_data.get('a_pagar')),
        "liberado": form_data.get('liberado') or 0,
        "enviado":"",
        "estado":"",
        "password": password,
        "acepta_contrato":0,
        "signature":"",
        "author": request.session.get('user_name'),
        "company_id": int(request.session.get("company")),
        "pasaporte": form_data.get('pasaporte') or ""
    }
    print("data ",json.dumps(data))
    response = await api.set_data("curso",body=json.dumps(data), schema=schema_name)
    print("grabar",response)
    if response.get("status") == "success":
       id = response["data"]["data"]["return_id"]   

       request.session["user_curso_id"]= id
       request.session["user_ruta"] = form_data.get('rutalumno')
       request.session["user_rut"] = form_data.get('rutapoderado')
       request.session["paso"] = "1"  
    
    return RedirectResponse(url=f"/{empresa}/manager/opening", status_code=303) 
           

@router.get("/contrattravel", response_class=HTMLResponse)
async def contrattravel(request: Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    #Directorio de paso con los cambios y sin firma
    directoryUpload = "uploads/opening"
    os.makedirs(directoryUpload, exist_ok=True)

    #Directorio de la compañia
    UPLOAD_DIR = "uploads/company"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    #Directorio donde se encuenta la plantilla del contrato
    contrato_doc = os.path.join(UPLOAD_DIR, "contrato", str(company_id))
    os.makedirs(contrato_doc, exist_ok=True)

    #directorio donde queda el pdf creaado con el contrato
    contrato_pdf = os.path.join(UPLOAD_DIR, "contrato_pdf", str(company_id))
    os.makedirs(contrato_pdf, exist_ok=True)

    response = await api.get_data("sale",id=request.session.get("sale"),schema=schema_name)
    venta = response['data'] if response["status"]=="success" else []

    response = await api.get_data("programac",id=int(venta['program_id']),schema=schema_name)
    programac = response['data'] if response["status"]=="success" else []

    response = await api.get_data("colegio",id=int(venta['establecimiento_id']),schema=schema_name)
    school = response['data'] if response["status"]=="success" else []
        
    response = await api.get_data("curso",id=int(request.session.get('user_curso_id')),schema=schema_name)
    curso = response['data'] if response["status"]=="success" else []

    response = await api.get_data("company",id=int(request.session.get('company')),schema="global")
    company= response['data'] if response["status"]=="success" else []

    # Supongamos que $venta['fecha'] es un string como '2025-09-01'
    fecha_str = venta['fecha']  # ejemplo: '2025-09-01'

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
    contrato = os.path.abspath(file_doc) 
    info_index = await formCharge(request.session)

    return templates.TemplateResponse("opening/contrattravel.html", {"request": request, "session":request.session,"info_index":info_index,"contrato":contrato,"documentname":documentname,"curso":curso,"rs":company['razonsocial'],"venta":venta,"empresa":empresa})

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
    directoryUpload = "uploads/opening"
    os.makedirs(directoryUpload, exist_ok=True)

    #directorio donde queda el pdf creaado con el contrato
    contrato_pdf = os.path.join(UPLOAD_DIR, "contrato_pdf", str(company_id))
    os.makedirs(contrato_pdf, exist_ok=True)
        
    response = await api.get_data("curso",id=int(request.session.get('user_curso_id')),schema=schema_name);
    curso = response['data'] if response["status"] == "success" else []
    
    firmaPng=form_data.get('signature64')
    # firma viene en formato "data:image/png;base64,iVBORw0K..."
    if firmaPng.startswith("data:image"):
        firmaPng = firmaPng.split(",")[1]  # quitar "data:image/png;base64,"

    # Guardar en archivo temporal
    firma_bytes = base64.b64decode(firmaPng)
    ruta_firma = f"uploads/company/{company_id}/firma.png"
    with open(ruta_firma, "wb") as f:
        f.write(firma_bytes)

    documentname = form_data.get('documentname')
    acepta_contrato = form_data.get('acepta_contrato')

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
        print("graba ",update)     
        if update['status']=='success':        
            #agregar la firma al contrato y convertirlo a pdf 
            #valores["signature"] = InlineImage(doc, "firma.png", width=Mm(40))
            ruta_firma = f"uploads/company/{company_id}/firma.png"
            ruta_firma = os.path.abspath(ruta_firma)

            # Forma segura de crear el nombre completo del archivo
            filedoc = os.path.join(directoryUpload, documentname)
            file_doc = os.path.abspath(filedoc)

            #Cambia las variables por datos del template por valores correcto 
            response =util.signature_doc(file_doc,ruta_firma)

            rut = curso["rutalumno"]
            rut_limpio = re.sub(r"\D", "", rut)  # \D elimina todo lo que NO sea número
            documentpdf=f'contrato-{curso["sale_id"]}-{rut_limpio}.pdf'
            filepdf = os.path.join(contrato_pdf, documentpdf)
            file_pdf = os.path.abspath(filepdf) 

            #util.docx_pdf(file_doc, file_pdf)
            # Elimina los archivos de paso      
            os.remove(ruta_firma)
            os.remove(file_doc)

            request.session["paso"]="2"
            request.session["user_contrato"]= "S"
            return RedirectResponse(url=f"/{empresa}/manager/opening", status_code=303)
        else:
            return RedirectResponse(url=f"/{empresa}/manager/opening", status_code=303)
             
    else:
        print("en el else de acepta contrato")
        #Obtener el contenido del PDF
        #url=$dircontratopdf.'/contrato'.$curso['sale_id'].str_replace(array('.', '-'), '',$curso['rutalumno']);
        #pdfContenido = file_get_contents($url);
            
        #Establecer cabeceras para forzar la descarga
        #header('Content-Type: application/pdf');
        #header('Content-Disposition: attachment; filename="archivo.pdf"');
        #header('Content-Length: ' . strlen($pdfContenido));
            
        #Enviar el contenido del PDF al navegador
        #echo $pdfContenido;
        return RedirectResponse(url=f"/{empresa}/manager/opening", status_code=303)


@router.post("/procesarpago")
async def procesarpago(request:Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")

    form_data = await request.form()
    schema_name = request.session.get("schema")
    company_id=int(request.session.get('company'))

    module='opening'

    nro_voucher=form_data.get('voucher')
        
    consulta = f"voucher={nro_voucher}&sale_id={request.session.get('sale')}&used=0"
    response = await api.get_data("voucher",query=consulta,schema=schema_name)
    voucher = response['data'] if response["status"] == "success" else [] 
        
    if voucher: 
        data=""
        #Buscar si exste el voucher existe en ventas
        consulta= f'nrotarjeta={nro_voucher}&sale_id={request.session.get("sale")}'
        response = await api.get_data("pagos",query=consulta,schema=schema_name)
        existe_pago = response['data']  if response["status"] == "success" else []
        
        if len(existe_pago) == 0:
            #grabar el ingreso
            response = await api.get_data("pagos",id=int(request.session.get('sale')),schema=schema_name)
            venta = response['data'] if response["status"] == "success" else []

            response = await api.get_data("curso",id=int(request.session.get('user_curso_id')),schema=schema_name);
            curso = response['data'] if response["status"] == "success" else []

            response = await api.get_data("program",id=int(venta['program_id']),schema=schema_name)
            program= response['data'] if response["status"] == "success" else []

            Monto=program["reserva"]
            identificador = uuid.uuid4().hex

            consulta=f'identificador={identificador}'
            response = await api.get_data("ingreso",query=consulta,schema=schema_name)
            ingresos = response['data'] if response["status"] == "success" else []

            if ingresos:
                contador=len(ingresos) + 1
                _identificador = f"identificador_{contador}"
            else:
                _identificador = identificador
                

            NroVta=request.session.get('sale')
            RutAl=request.session.get('user_ruta')

            # Fecha de hoy
            fecha_hoy = datetime.today()
            fecha_actual = fecha_hoy.strftime("%Y/%m/%d")

            dato= {
                    "tipocomp":"COW",
                    "fecha": fecha_actual,
                    "identificador": _identificador,
                    "sale_id": venta["id"],
                    "curso_id": curso["id"],
                    "rutapo": curso["rutapod"],
                    "rutalum": curso["rutalumno"],
                    "fpago":"FW",
                    "monto": Monto,
                    "activo":1,
                    "status_pago":"Pagado",
                    "author": curso["nombreapod"] 
                }
            
            insert = await api.set_data("ingreso",body=json.dumps(data), schema=schema_name)
            id_ingreso = insert["data"]["data"]["return_id"] if insert["status"] == "success" else 0
                
            #grabar el pago
            transaccion=0
            nroingreso=nro_voucher
            montoingreso=Monto
            fechaingreso= fecha_actual
            fechatrans= fecha_actual
            fechaauto= ""
            tipopago="IN"
            media="IN"
                
            dato={
                "tipocom":"COW",
                "ingreso_id": id_ingreso,
                "identificador": _identificador,
                "fecha": fechaingreso,
                "sale_id": venta["id"],
                "rutalumn": RutAl,
                "transaccion": transaccion, 
                "tipo": tipopago,
                "monto": montoingreso,
                "nrotarjeta": nro_voucher,
                "codigoAuto": "",
                "fechaAuto": fechaauto,
                "tipopago": media,
                "nrocuota":0,
                "fechatransac": fechatrans,
                "activo":1,
                "author":""
            }
            response = await api.set_data("pagos",body=json.dumps(data), schema=schema_name)
            #Update voucher
            dato='{"used":1}'
            resp = await api.update_data("programac", id=int(voucher["id"]), body=json.dumps(dato),schema=schema_name)
 
            request.session['paso']='3'
            request.session['user_pagado']='S'
        else:
            request.session['paso']='4'
            request.session['user_pagado']=''
        
    else:
        request.session['paso']='5'
        request.session['user_pagado']=''
        
    return RedirectResponse(url=f"/{empresa}/manager/opening", status_code=303)



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

async def formCharge(session: dict):
    info_index=[]
    schema_name = session.get("schema")
    company_id=int(session.get('company'))

    response = await api.get_data("company",id=company_id,schema="global")
    company = response['data'] if response["status"] == "success" else [] 

    getQuery=f"id={session.get('sale')}"
    response = await api.get_data("sale/informe",query=getQuery,schema=schema_name)
    venta=response['data'][0] if response["status"] == "success" else [] 

    programid=int(venta['program_id'])
    response = await api.get_data("programac",id=programid,schema=schema_name)
    program=response['data'] if response["status"] == "success" else []
    
    colegioid=int(venta['establecimiento_id'])
    response = await api.get_data("colegio",id=colegioid,schema=schema_name)
    colegio=response['data'] if response["status"] == "success" else []

    info_index = {
        "curso": f"{colegio['nombre']}-{venta['curso']}-{venta['idcurso']}",
        "programa": program["name"],
        "fechaultimo": Helper.formatear(venta["fecha_ultpag"]),
        "fechasalida": Helper.formatear(venta["fechasalida"]),
        "company": company["nomfantasia"],
    }

    return info_index 