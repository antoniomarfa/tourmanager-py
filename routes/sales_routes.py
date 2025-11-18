from fastapi import FastAPI, Request, Form, Depends, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from io import BytesIO
from libraries.renderrequest import RenderRequest
from libraries.helper import Helper
import json, uuid, os, html, re
from datetime import datetime, timezone, timedelta
from libraries.restriction import Restriction
#Todo para el pdf
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
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

    getQuery = f"active=1&company_id={company_id}"
    response = await api.get_data("users",query= getQuery,schema=schema_name)
    sellers = response["data"] if response["status"] == "success" else []

    getQuery="company_id=0"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools0 = response["data"] if response["status"] == "success" else []

    getQuery=f"company_id={company_id}"
    response = await api.get_data("colegio",query= getQuery,schema=schema_name)
    schools1 = response["data"] if response["status"] == "success" else []

    schools0.extend(schools1)
    schools = schools0

    # Fecha de hoy
    hoy = datetime.today()
    now_date = hoy.strftime("%Y-%m-%d")

    # Fecha de hoy
    hoy = datetime.today()
    end_date = hoy.strftime("%Y-%m-%d")

    # Fecha de hace 15 días
    menos_15 = hoy - timedelta(days=15)
    start_date = menos_15.strftime("%Y-%m-%d")
     
    cant_access = {  
        "can_update": await rst.access_permission("users", "UPDATE", request.session),
        "can_delete": await rst.access_permission("users", "DELETE", request.session),
        "can_insert": await rst.access_permission("users", "INSERT", request.session),
        "can_export_report": True # await rst.access_permission("users", "EXPORT_REPORT", request.session)
    } 

    context ={"request": request, 
              "session":request.session, 
              "cant_access":cant_access,
              "_schools": schools,
              "schools": schools, 
              "sellers": sellers,
              "end_date":end_date,
              "start_date":start_date,
              "empresa":empresa}
    
    return templates.TemplateResponse("sales/index.html", context)

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

    response = await api.get_data("company",id=company_id,schema="global")
    company = response["data"] if response["status"]=='success' else []
    empresa=company['identificador']

    form_data = await request.form()
    start_date= form_data.get("start_date")
    end_date = form_data.get("end_date")
    vendedor = form_data.get("vendedor")
    colegio = form_data.get("colegion")

    getQuery=f'start_date={start_date}&end_date={end_date}&company_id={company_id}'
        
    if vendedor:
        getQuery +='&seller_id={vendedor}'

    if colegio:
        getQuery +='&establecimiento_id={colegio}'

    response = await api.get_data("sale/informe", query=getQuery,schema=schema_name)
    sales = response["data"] if response["status"] == "success" else []
    total_vta =0 

    table_body = []

    if sales:
        for sale in sales:
            # Select status
            if sale['state'] == 'V':
                select_status = f'''
                    <a style="cursor: pointer;" class="change-status" data-id="{sale['id']}">
                        <span class="badge text-bg-warning">Venta</span>
                    </a>
                '''

            else:
                select_status = f'''<span class="badge text-bg-danger">Rechazado</span>''' if sale['estado'] == 'R' else f'''<span class="badge text-bg-success">Cerrada</span>'''

            # Colegio
            colegio = "" if sale['establecimiento_id'] == 1 else sale.get('colegios', {}).get('nombre', '')
            # Actions
            actions = ""
            if can_update:  # reemplazar por tu módulo real
                if sale['state'] == "C":
                    if sale['type_sale'] == 'VG':
                        actions += f'<a class="btn btn-sm btn-warning" href="/sales/editvg/{sale["id"]}"><i class="fa fa-pencil"></i></a> '
                    else:
                        actions += f'<a class="btn btn-sm btn-warning" href="/sales/editge/{sale["id"]}"><i class="fa fa-pencil"></i></a> '
            if can_delete:
                actions += f'<a class="btn btn-sm btn-danger cancel-register" id="{sale["id"]}"><i class="fa fa-trash"></i></a>'
            
            alumnos_curso=sale["total_curso"]

            if sale["total_curso"] > 0:
                #ruta = f'http://127.0.0.1:8000/{empresa}/manager/sales/lstpasajerospdf/'
                #lstpsajeros=f'<a class="btn btn-black btn-sm tooltip-primary" data-toggle="tooltip" data-placement="bottom" title="" data-original-title="Listado Pasajeros" href="{ruta}{sale["id"]}" target="_blank" ><span class="badge text-bg-success">Listado</span></a>'
                lstpsajeros = f'<a style="cursor: pointer;" class="list-pdf" id="{sale["id"]}"><span class="badge text-bg-success">listado</span></a>'
            else:
                lstpsajeros=''

            if sale['sendemail']==0:
                sendemail = f'<a class="btn btn-sm btn-green" href="/sales/enviarCorreocurso/{sale["id"]}"><i class="fa fa-envelope-o"></i></a>'
            else:
                sendemail = f'<a class="btn btn-sm btn-green" href="/sales/enviarCorreocurso/{sale["id"]}"><i class="fa-regular fa-envelope-circle-check"></i></a>'

            curso = f"{sale['curso']}-{sale['idcurso']}"
            if sale["type_sale"] == 'VG':
                curso = ""    
            
            # Construcción de la fila
            fecha_iso = sale["fecha"]

            # Convertir y formatear
            fecha_formateada = datetime.strptime(fecha_iso, "%Y-%m-%dT%H:%M:%SZ").strftime("%d-%m-%Y")

            table_body.append([
                sale['id'],
                "Gira Estudio" if sale['type_sale'] == 'GE' else "Viaje Grupal",
                sale['identificador'],
                fecha_formateada,
                sale['establecimiento_nombre'],
                curso,
                sale['program_name'],
                sale['nroalumno'],
                sale['liberados'],
                Helper.formato_numero(sale['vprograma']),
                Helper.formato_numero(int(sale['vprograma']) * int(sale['nroalumno'])),
                sale['seller_name'],
                select_status,
                f"{alumnos_curso} / {sale['nroalumno']}",
                lstpsajeros,
                sendemail,
                sale['author'],
                actions
            ])

            if sale['state'] != 'R':
                total_vta +=(int(sale['vprograma']) * int(sale['nroalumno']))

        table_body.append([
             '',
             '',
             '',
             '',
             '',
             '',
             '',
             'Total Venta',
             '',
             '',
             Helper.formato_numero(total_vta),
             '',
             '',
             '',
             '',
             '',
             '',
             ''
        ])

        return JSONResponse(content={"data": table_body})
    else:
        return JSONResponse(content={"data": []})
       

@router.get("/create/{type}", response_class=HTMLResponse)
async def create_form(request: Request,type:str):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))
    response = await api.get_data("company",schema="global")  # Suponiendo que el servicio se llama 'users'    
    companys = response["data"] if response["status"] == "success" else []    

    #viaje grupal
    getQuery=f"active=1&company_id={company_id}"
    response = await api.get_data("users",query=getQuery,schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    sellers = response["data"] if response["status"] == "success" else []    

    getQuery=f"active=1&company_id={company_id}"
    response = await api.get_data("programac",query=getQuery,schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    programs = response["data"] if response["status"] == "success" else []    

    getQuery=f"estado=A&sale_id=0&type_sale={type.upper()}&company_id={company_id}"
    response = await api.get_data("quotes",query=getQuery,schema=schema_name)  # Suponiendo que el servicio se llama 'users'    
    quotes = response["data"] if response["status"] == "success" else []    

    if type == "ge":            
        getQuery="company_id=0"
        response = await api.get_data("colegio",query= getQuery,schema=schema_name)
        schools0 = response["data"] if response["status"] == "success" else []

        getQuery=f"company_id={company_id}"
        response = await api.get_data("colegio",query= getQuery,schema=schema_name)
        schools1 = response["data"] if response["status"] == "success" else []

        schools0.extend(schools1)
        schools = schools0
  

    hoy = datetime.today()
    fecha_hoy = hoy.strftime("%Y-%m-%d")

    if type == "vg":    
        return templates.TemplateResponse("sales/createvg.html", {"request": request, "sellers":sellers, "programs":programs,"quotes":quotes,"sales_date":fecha_hoy,"session": request.session,"empresa":empresa})
    else: 
        return templates.TemplateResponse("sales/createge.html", {"request": request, "sellers":sellers, "programs":programs,"schools":schools ,"quotes":quotes,"sales_date":fecha_hoy,"session": request.session,"empresa":empresa})

#Crea la venta
@router.post("/create")
async def create(request:Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")    
    schema_name = request.session.get("schema")
    form_data = await request.form()
    identificador = uuid.uuid4().hex
    form_data = await request.form()

    password="xx"
    cotizacion = int(form_data.get('sel_cotizacion') or 0)
    vdescuento = int(form_data.get('vdescuento') or 0) 
    typesale = form_data.get("typesale")
            
    colegio = int(form_data.get('sel_colegio') or 1)
    curso = int(form_data.get('curso') or 0)
    idcurso = form_data.get('idcurso')


    getQuery=f'establecimiento_id={colegio}&curso={curso}&idcurso={idcurso}&activo=1'
    response = await api.get_data("sale",query=getQuery,schema=schema_name)
    sales=response['data'] if response["status"] == "success" else []

    if sales:
        return RedirectResponse(url=f"/{empresa}/manager/sales", status_code=303)      
    
    if typesale == 'VG':
        colegio=1
        curso=0
        idcurso=""
    print("fecha ",form_data.get('fecha'))      
    # Convertir a objeto datetime
    fecha = form_data.get('fecha')
    if fecha:
        saledate = datetime.fromisoformat(fecha).strftime('%Y-%m-%dT00:00:00Z')

    fecha = form_data.get('fechasal')
    if fecha:
        fechasal = datetime.fromisoformat(fecha).strftime('%Y-%m-%dT00:00:00Z')

    fecha = form_data.get('fecha_ultpag')
    if fecha:
        fechaultpag = datetime.fromisoformat(fecha).strftime('%Y-%m-%dT00:00:00Z')

    fecha = form_data.get('fechacuota')
    if fecha:
        fechacuota = datetime.fromisoformat(fecha).strftime('%Y-%m-%dT00:00:00Z')

    data = {       
            "fecha" : saledate,
            "seller_id": int(form_data.get('sel_vendedor')),
            "identificador": identificador,
            "establecimiento_id": colegio,
            "program_id" : int(form_data.get('sel_programa')),
            "curso": curso,
            "idcurso": idcurso,
            "nroalumno": int(form_data.get('nroalumno')),
            "liberados": int(form_data.get('liberado')),
            "subtotal": int(form_data.get('vprograma')),
            "descm":  vdescuento,
            "vprograma": int(form_data.get('vtotalprog')),  
            "description": "",
            "obs": form_data.get('obs'),
            "fechasalida": fechasal,
            "activo": 1,
            "state": form_data.get('status'),
			"author": request.session.get('user_name'),
            "encargado": form_data.get('encargado'),
            "correo_encargado": form_data.get('correo_encargado'),
            "password": password,
            "fecha_ultpag": fechaultpag,
            "sendemail": 0,
            "comision": float(form_data.get('comision')),
            "tipocambio": float(form_data.get('tipocambio')),
            "comision_pagada": 0,
            "cuotas": int(form_data.get('cuotas')),
            "fechacuota": fechacuota,  
            "company_id": int(request.session.get("company")),
            "accesscode":form_data.get('accesscode'),
            "type_sale": typesale
        }
    print(json.dumps(data))
    response = await api.set_data("sale",body=json.dumps(data), schema=schema_name)
    #si la respuesta es ok , graba el nro de la venta en la cotizacion
    if response.get("status") == "success":
        sale_id = response["data"]["data"]["return_id"]
        
        if cotizacion != 0:
            data = {"sale_id":sale_id}
            response = await api.update_data("quotes",id=cotizacion,body=json.dumps(data),schema=schema_name)

    return RedirectResponse(url=f"/{empresa}/namager/sales", status_code=303)  


#Buscar valor de programa
@router.post("/getprogramvalue")
async def programvalue(request: Request):
    schema_name = request.session.get("schema")
    form_data = await request.form()
    program_id = int(form_data.get("program_id") or 0)
    nroalumno = int(form_data.get("nroalumno") or 0)

    getQuery=f"programa_id={program_id}"
    response = await api.get_data("programad",query=getQuery,schema=schema_name)
    programs = response["data"] if response["status"] == "success" else []

    programval = 0
    liberados = 0
    for program in programs:           
        desde = int(program['desde'])
        hasta = int(program['hasta'])
        if desde <= nroalumno <= hasta:
            programval = int(program['valor'])
            liberados = int(program['liberado'])
            break  # Ya encontramos la coincidencia     

    return JSONResponse(content={
        'programval': programval,
        'liberados': liberados
    })


#Cambio estado cotizacion
@router.post("/setstatus")
async def setstatus(request: Request):
    schema_name = request.session.get("schema")

    form_data = await request.form()
    status = form_data.get("status")
    id_sale = int(form_data.get("id_sale"))

    error = 1
    message = "Estado de Venta no se actualizó."
    
    if status:

       data = {"state" : status}
       response = await api.update_data("sale", id=id_sale ,body=json.dumps(data), schema=schema_name)
       message="Estado de Cotizacion  actualizado correctamente." if response["status"] == "success" else "Estado de Cotizacion  no set actualizo." 
       error = 0 if response["status"] == "success" else 1
       if status=='A':
            message = 'Cambio de estatus Venta.'
                            
    return JSONResponse(content={
        "error": error,
        "message": message
        })

# Anular Cotizacion 
@router.get("/cancel/{sale_id}")
async def delete(request: Request,sale_id: int):
    schema_name = request.session.get("schema")

    data = {"estado" : 'N'}
    response = await api.set_data("sale", id=sale_id ,body=json.dumps(data), schema=schema_name)
    message="Venta Anulada Correctamente" if response["status"] == "success" else "Cotizacion no fue Anulada." 
    error = 0 if response["status"] == "success" else 1
                            
    return JSONResponse(content={
        "error": error,
        "message": message
        })

@router.post("/accesscode")
def accesscode(request:Request):
    empresa = request.state.empresa 
    
    if not request.session.get("authenticated"):
        return RedirectResponse(url=f"/{empresa}/manager/login")
    
    token = os.urandom(5).hex()
    return JSONResponse(content={
        "error": 0,
        "codigo": token
        })

@router.post("/getquote")
async def getquote(request:Request):
    schema_name = request.session.get("schema")

    form_data = await request.form()
    quote_id = int(form_data.get("cotizacion") or 0)
    typesale = form_data.get("typesale")
 
    response = await api.get_data("quotes",id=quote_id,schema=schema_name)
    quote = response["data"] if response["status"] == "success" else []

    programa_id=int(quote['programa_id'] or 0)
    getQuery=f"programa_id={programa_id}"
    response = await api.get_data("programad",query=getQuery,schema=schema_name)
    programs = response["data"] if response["status"] == "success" else []

    liberados = 0
    for program in programs:           
        desde = int(program['desde'])
        hasta = int(program['hasta'])
        if desde <= quote['pasajeros'] <= hasta:
            liberados = int(program['liberado'])
            break  # Ya encontramos la coincidencia     


    return JSONResponse(content={
            'seller_id': quote['seller_id'],
            'curso':  quote['curso'],
            'idcurso':  quote['idcurso'],
            'establecimiento_id': quote['establecimiento_id'],
            'pasajeros': quote['pasajeros'],
            'programa_id': quote['programa_id'],
            'subtotal': quote['subtotal'],
            'desc': quote['desc'],
            'vprograma': quote['vprograma'],
            'tipocambio': quote['tipocambio'],
            'liberados': liberados,
            'contacto': quote['contacto'],
            'contactofono': quote['contactofono'],
            'contactoemail': quote['contactoemail'],
            'estado': quote['estado'],
            'obsestado': quote['obsestado']
        })

@router.post("/lstpasajerospdf")
async def pasajerospdf(request:Request,saleid:int = Form(...)):
    schema_name = request.session.get("schema")
    company_id = int(request.session.get("company"))
    print(saleid)
    response = await api.get_data("company",id=company_id,schema="global")
    company=response['data'] if response['status']=='success' else []

    consulta=f'sale_id={saleid}&company_id={company_id}'
    response = await api.get_data("curso",query=consulta,schema=schema_name)
    cursos=response['data'] if response['status']=='success' else []

    consulta=f'id={saleid}'
    response = await api.get_data("sale/informe",query=consulta,schema=schema_name)
    sale=response['data'][0] if response['status']=='success' else []
 
    data=""
    if len(cursos)>0:
        buffer = BytesIO()
        logo_path = "/uploads/company/logo/login_logo_DET_7053186c-4188-4c9a-88af-fb12caa206bc.png"
        logo_path = os.path.join(os.getcwd(), logo_path.lstrip("/"))
        # Asegura que la ruta sea absoluta
        #if not os.path.isabs(logo_path):
        #    logo_path = os.path.join(os.getcwd(), logo_path.lstrip("/"))

        # Crear documento
        output_path = f"/uploads/pasajeros/listado_pasajeros_{saleid}.pdf"
        output_path = os.path.join(os.getcwd(), output_path.lstrip("/"))
        #si el archivo existe lo elimina para que solo exista el ultimo
        if os.path.exists(output_path):
            os.remove(output_path)

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()

        # Estilos personalizados
        style_h3 = ParagraphStyle(
            "H3",
            fontSize=18,
            textColor=colors.HexColor("#000000"),
            spaceAfter=8,
            alignment=0,
        )
        style_table_header = ParagraphStyle(
            "Header",
            fontSize=12,
            textColor=colors.HexColor("#000066"),
            leading=14,
            alignment=TA_CENTER,
        )
        style_normal = ParagraphStyle("Normal", fontSize=11, leading=13)

        elements = []

        # --- ENCABEZADO CON LOGO Y NOMBRE ---
        header_table = []
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=3 * cm, height=3 * cm)
        else:
            print("⚠️ No se encontró la imagen del logo:", logo_path)
            logo = Paragraph("<b>Sin logo</b>", styles["Normal"])


        title = Paragraph(f"<b>{company['nomfantasia']}</b>", style_h3)
        header_table.append([logo, title])

        t_header = Table(header_table, colWidths=[4 * cm, 12 * cm])
        t_header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "LEFT"),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 0.5 * cm))

        # --- DATOS DEL PROGRAMA ---
        program_info = [
            ["Colegio:", sale["establecimiento_nombre"]],
            ["Curso:", f"{sale['curso']} - {sale['idcurso']}"],
            ["Programa:", sale["program_name"]],
        ]
        t_info = Table(program_info, colWidths=[3 * cm, 13 * cm])
        t_info.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 0.5 * cm))

        # --- TÍTULO DE TABLA ---
        title_table = Paragraph("<b>LISTADO DE PASAJEROS<br/>(Roaming List)</b>", style_table_header)
        elements.append(title_table)
        elements.append(Spacer(1, 0.3 * cm))

        # --- TABLA DE PASAJEROS ---
        data_table = [["Rut", "Nombre", "Fecha Nacimiento"]]

        for curso in cursos:
            nombre_alumno = curso["nombrealumno"].strip()
            nombre_alumno = " ".join(nombre_alumno.split())
            nombre_alumno = html.escape(nombre_alumno)
            nombre_alumno = re.sub(r"[^A-Za-zÁÉÍÓÚáéíóúÑñ ]", " ", nombre_alumno)
            curso["fechanac"] = datetime.strptime(curso["fechanac"], "%Y-%m-%d").strftime("%d-%m-%Y")

            data_table.append([
                curso["rutalumno"],
                nombre_alumno,
                curso["fechanac"] 
            ])

        table = Table(data_table, colWidths=[5 * cm, 8 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3ece4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8f5")]),
        ]))

        elements.append(table)

        # --- Generar PDF ---  
        #doc.build(elements)
        await run_in_threadpool(doc.build, elements)
        buffer.seek(0)

    if os.path.exists(output_path):
        ruta=f"/uploads/pasajeros/listado_pasajeros_{saleid}.pdf"
        msg="PDF generado correctamente en:", os.path.abspath(output_path)
        status=1    
    else:
       msg="No se generó el archivo PDF."
       status=0
       ruta=""

    return JSONResponse(
        content={
            "status": status,
            "mensaje": msg,
            "ruta": ruta
        })       